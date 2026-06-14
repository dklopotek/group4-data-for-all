// block_particles.js — Pollen particle system for block-scale CFD wind viewer
//
// Collision detection uses the Infrared SDK wind speed grid directly:
// cells inside buildings have speed ≈ 0 in the CFD output, so
// speed < BLOCK_THRESHOLD → treat as solid. This is correct at any
// pitch/zoom because map.unproject() handles the perspective projection.
//
// A screen-space speed cache is built once at init (O(1) lookups at runtime).

const MAX_PTCLS       = 900;
const TRAIL_LEN       = 18;
const SPEED_MULT      = 5.0;   // visual speedup (real 4 m/s → moves visibly at 60 fps)
const SPAWN_EVERY     = 1;     // frames between spawns
const BLOCK_THRESHOLD = 0.25;  // m/s — below this = building interior
const CACHE_STEP      = 5;     // px per cache cell (balance accuracy vs build cost)

class BlockParticles {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext('2d');
    this.W = canvas.width;
    this.H = canvas.height;

    this.pool = Array.from({ length: MAX_PTCLS }, () => ({
      x: 0, y: 0, age: 9999, maxAge: 0, emission: 0.7,
      trail: new Float32Array(TRAIL_LEN * 2),
      ti: 0,
    }));

    this.trees      = [];
    this.windField  = null;
    this.windVec    = [0, -1];
    this.pixPerM    = 10;
    this.map        = null;
    this.spawnTick  = 0;
    this.frameId    = null;

    // Speed cache (built once at init)
    this.speedCache  = null;
    this.cacheCols   = 0;
    this.cacheRows   = 0;
  }

  // ── Init / reinit ─────────────────────────────────────────────────────────
  init(map, windField /* buildings param kept for API compat but unused */) {
    this.map       = map;
    this.windField = windField;
    this.trees     = windField.trees;

    // Screen-space wind travel vector
    const c    = map.getCenter();
    const tDeg = (windField.wind_direction_deg + 180) % 360;
    const tRad = tDeg * Math.PI / 180;
    const OFF  = 0.005;
    const p0   = map.project([c.lng, c.lat]);
    const p1   = map.project([c.lng + Math.sin(tRad) * OFF,
                               c.lat + Math.cos(tRad) * OFF]);
    const dx = p1.x - p0.x, dy = p1.y - p0.y;
    const len = Math.hypot(dx, dy);
    this.windVec = len > 0.001 ? [dx / len, dy / len] : [0, -1];

    // Pixels per metre
    const pA = map.project([c.lng,         c.lat]);
    const pB = map.project([c.lng + 0.001, c.lat]);
    this.pixPerM = Math.abs(pB.x - pA.x) /
                   (0.001 * 111_000 * Math.cos(c.lat * Math.PI / 180));

    // Build screen-space speed cache
    this._buildSpeedCache();

    // Reset particles
    for (const p of this.pool) p.age = 9999;
    this.spawnTick = 0;
  }

  // ── Speed cache ───────────────────────────────────────────────────────────
  // Build once at init so per-frame lookups are cheap array reads.
  // Uses map.unproject() → correct for any pitch/zoom/bearing.
  _buildSpeedCache() {
    const cols = Math.ceil(this.W / CACHE_STEP);
    const rows = Math.ceil(this.H / CACHE_STEP);
    this.speedCache = new Float32Array(cols * rows);
    this.cacheCols  = cols;
    this.cacheRows  = rows;

    for (let cy = 0; cy < rows; cy++) {
      for (let cx = 0; cx < cols; cx++) {
        this.speedCache[cy * cols + cx] =
          this._speedGeo(cx * CACHE_STEP, cy * CACHE_STEP);
      }
    }
  }

  // Geographic speed lookup (bilinear interpolation in CFD grid).
  // Used only at cache-build time.
  _speedGeo(sx, sy) {
    if (!this.windField || !this.map) return 0;
    const ll = this.map.unproject([sx, sy]);
    const { bbox, grid_shape, speed_grid } = this.windField;
    const [bW, bS, bE, bN] = bbox;
    const [rows, cols]      = grid_shape;
    const u = (ll.lng - bW) / (bE - bW);
    const v = (ll.lat - bS) / (bN - bS);
    if (u < 0 || u > 1 || v < 0 || v > 1) return 0;
    const cf = u * (cols - 1), rf = v * (rows - 1);
    const c0 = cf | 0, c1 = Math.min(cols - 1, c0 + 1);
    const r0 = rf | 0, r1 = Math.min(rows - 1, r0 + 1);
    const fc = cf - c0, fr = rf - r0;
    return (speed_grid[r0][c0] * (1-fc) + speed_grid[r0][c1] * fc) * (1-fr)
         + (speed_grid[r1][c0] * (1-fc) + speed_grid[r1][c1] * fc) * fr;
  }

  // Fast per-frame speed read from cache.
  _speed(sx, sy) {
    if (!this.speedCache) return this.windField?.wind_speed_ms ?? 2;
    const cx = (sx / CACHE_STEP) | 0;
    const cy = (sy / CACHE_STEP) | 0;
    if (cx < 0 || cx >= this.cacheCols || cy < 0 || cy >= this.cacheRows) return 0;
    return this.speedCache[cy * this.cacheCols + cx];
  }

  // ── Collision & steering ──────────────────────────────────────────────────
  // Inside a building → CFD speed ≈ 0. Use that as the block test.
  _blocked(sx, sy) {
    return this._speed(sx, sy) < BLOCK_THRESHOLD;
  }

  // Probe 6 directions and pick the one with the best combination of
  // wind speed AND alignment with the global wind direction.
  // This makes particles channel through street corridors naturally.
  _dir(x, y) {
    const [gx, gy] = this.windVec;
    const sq = Math.SQRT1_2;
    const PROBES = [
      [gx,  gy],                             // straight along global wind
      [-gy,  gx],                            // 90° left
      [ gy, -gx],                            // 90° right
      [(gx-gy)*sq, (gy+gx)*sq],             // 45° left
      [(gx+gy)*sq, (gy-gx)*sq],             // 45° right
      [-gx, -gy],                            // reverse (last resort)
    ];
    const LOOK = 22; // pixels ahead per probe

    let bestScore = -Infinity, bestDir = [gx, gy];
    for (const [dx, dy] of PROBES) {
      const s = this._speed(x + dx * LOOK, y + dy * LOOK);
      if (s < BLOCK_THRESHOLD) continue;
      // Score biases toward high speed AND alignment with global wind
      const dot   = dx * gx + dy * gy;             // −1 … +1
      const score = s * (0.45 + 0.55 * Math.max(0, dot));
      if (score > bestScore) { bestScore = score; bestDir = [dx, dy]; }
    }
    return bestScore > -Infinity ? bestDir : [-gx, -gy];
  }

  // ── Spawn ─────────────────────────────────────────────────────────────────
  _spawn(tree) {
    for (const p of this.pool) {
      if (p.age < p.maxAge) continue;
      const pt = this.map.project(tree.position);
      // Spread spawn over a small radius so not all from same pixel
      const angle = Math.random() * Math.PI * 2;
      const dist  = Math.random() * 7;
      p.x   = pt.x + Math.cos(angle) * dist;
      p.y   = pt.y + Math.sin(angle) * dist;
      if (this._blocked(p.x, p.y)) return; // don't spawn inside building
      p.age     = 0;
      p.maxAge  = 220 + Math.random() * 180;
      p.emission = tree.emission;
      p.trail.fill(0);
      p.ti = 0;
      return;
    }
  }

  // ── Main loop ─────────────────────────────────────────────────────────────
  tick() {
    this.spawnTick++;
    if (this.spawnTick % SPAWN_EVERY === 0 && this.trees.length > 0) {
      const t = this.trees[(Math.random() * this.trees.length) | 0];
      this._spawn(t);
    }

    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.W, this.H);

    for (const p of this.pool) {
      if (p.age >= p.maxAge) continue;
      p.age++;

      const lifeT = p.age / p.maxAge;
      const alpha = (1 - lifeT) * Math.min(1, p.age / 20) * 0.92;
      const spd   = this._speed(p.x, p.y) * this.pixPerM * SPEED_MULT * 0.016;
      const [dx, dy] = this._dir(p.x, p.y);

      // Tiny Brownian wobble
      const wx = dx + (Math.random() - 0.5) * 0.4;
      const wy = dy + (Math.random() - 0.5) * 0.4;
      const wl = Math.hypot(wx, wy) || 1;

      const npx = p.x + (wx / wl) * spd;
      const npy = p.y + (wy / wl) * spd;

      if (!this._blocked(npx, npy)) {
        p.x = npx; p.y = npy;
      } else {
        // Try steering to the best open direction
        const [bx, by] = this._dir(p.x, p.y);
        const sx2 = p.x + bx * spd * 0.6;
        const sy2 = p.y + by * spd * 0.6;
        if (!this._blocked(sx2, sy2)) { p.x = sx2; p.y = sy2; }
        // else: stuck, will age out
      }

      // Record trail
      const ti2 = (p.ti % TRAIL_LEN) * 2;
      p.trail[ti2] = p.x; p.trail[ti2 + 1] = p.y;
      p.ti++;

      // ── Trail ─────────────────────────────────────────────────────────────
      const tLen = Math.min(p.ti, TRAIL_LEN);
      if (tLen > 2) {
        ctx.beginPath();
        let first = true;
        for (let k = tLen - 1; k >= 0; k--) {
          const ki = ((p.ti - 1 - k + TRAIL_LEN) % TRAIL_LEN) * 2;
          const tx = p.trail[ki], ty = p.trail[ki + 1];
          if (first) { ctx.moveTo(tx, ty); first = false; }
          else ctx.lineTo(tx, ty);
        }
        const sN    = Math.min(1, spd / 3.5);
        const trailA = alpha * (0.28 + sN * 0.32);
        ctx.strokeStyle = `rgba(155,255,15,${trailA})`;
        ctx.lineWidth   = 1.1 + p.emission * 0.9;
        ctx.lineCap     = 'round';
        ctx.stroke();
      }

      // ── Glow disc ─────────────────────────────────────────────────────────
      const sN    = Math.min(1, spd / 3.5);
      const rr    = (118 + sN * 102) | 0;
      const gg    = (228 + sN * 27)  | 0;
      const pulse = 1 + 0.10 * Math.sin(p.age * 0.20);
      const core  = (2.6 + p.emission * 1.8) * pulse;
      const halo  = core * 3.8;

      const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, halo);
      grad.addColorStop(0,    `rgba(${rr},${gg},25,${alpha})`);
      grad.addColorStop(0.22, `rgba(${rr},${gg},18,${alpha * 0.88})`);
      grad.addColorStop(0.55, `rgba(${rr},${gg}, 8,${alpha * 0.42})`);
      grad.addColorStop(1,    `rgba(${rr},${gg}, 0,0)`);

      ctx.beginPath();
      ctx.arc(p.x, p.y, halo, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();
    }
  }

  start() {
    if (this.frameId) return;
    const loop = () => { this.tick(); this.frameId = requestAnimationFrame(loop); };
    this.frameId = requestAnimationFrame(loop);
  }

  stop() {
    if (this.frameId) { cancelAnimationFrame(this.frameId); this.frameId = null; }
    this.ctx.clearRect(0, 0, this.W, this.H);
  }

  resize() {
    this.W = this.canvas.width  = window.innerWidth;
    this.H = this.canvas.height = window.innerHeight;
    // Caller should call init() again after resize to rebuild cache
  }
}

export { BlockParticles };
