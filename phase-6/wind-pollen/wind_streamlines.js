// wind_streamlines.js — city-wide wind particle streamlines
// Each particle draws a tail line from its previous position so the
// canvas stays transparent — no fillRect accumulation that blacks out the map.

const N_PARTICLES = 220;
const BASE_PX_PER_MS = 0.55; // px/frame per m/s
const TAIL_FRAMES    = 10;   // how many frames back the tail extends

export class WindStreamlines {
  constructor(canvas) {
    this.canvas    = canvas;
    this.ctx       = canvas.getContext('2d');
    this.particles = [];
    this._raf      = null;
    this.windDx    = 0;   // px/frame east
    this.windDy    = 0;   // px/frame south (positive = down)
    this.windSpeed = 0;
  }

  setWind(directionDeg, speedMs) {
    this.windSpeed = speedMs;
    if (speedMs < 0.3) { this.windDx = 0; this.windDy = 0; return; }
    const rad      = (directionDeg + 180) * Math.PI / 180; // travel direction
    const pxF      = speedMs * BASE_PX_PER_MS;
    this.windDx    =  Math.sin(rad) * pxF;
    this.windDy    = -Math.cos(rad) * pxF;
  }

  updateWind(directionDeg, speedMs) {
    this.setWind(directionDeg, speedMs);
    this._initParticles();
  }

  start() {
    if (this._raf) return;
    this._initParticles();
    const loop = () => {
      this._update();
      this._draw();
      this._raf = requestAnimationFrame(loop);
    };
    this._raf = requestAnimationFrame(loop);
  }

  stop() {
    if (this._raf) { cancelAnimationFrame(this._raf); this._raf = null; }
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.particles = [];
  }

  resize() {
    this.canvas.width  = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this._initParticles();
  }

  _initParticles() {
    const W = this.canvas.width  || window.innerWidth;
    const H = this.canvas.height || window.innerHeight;
    this.particles = [];
    for (let i = 0; i < N_PARTICLES; i++) {
      this.particles.push(this._spawn(W, H, true));
    }
  }

  _spawn(W, H, stagger = false) {
    const maxAge = 160 + Math.random() * 100;
    return {
      x:      Math.random() * W,
      y:      Math.random() * H,
      age:    stagger ? Math.floor(Math.random() * maxAge) : 0,
      maxAge,
    };
  }

  _update() {
    const W = this.canvas.width;
    const H = this.canvas.height;
    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      // Small perpendicular wobble for organic look
      const perp = (Math.random() - 0.5) * 0.35;
      p.x += this.windDx - this.windDy * perp;
      p.y += this.windDy + this.windDx * perp;
      p.age++;
      // Wrap screen edges
      p.x = ((p.x % W) + W) % W;
      p.y = ((p.y % H) + H) % H;
      if (p.age > p.maxAge) {
        this.particles[i] = this._spawn(W, H, false);
      }
    }
  }

  _draw() {
    const ctx = this.ctx;
    // Full clear each frame — canvas stays transparent so the map shows through
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    if (this.windSpeed < 0.3) return;

    const alphaBase = Math.min(1, this.windSpeed / 6) * 0.5;

    for (const p of this.particles) {
      const t    = p.age / p.maxAge;
      // Bell-shaped fade: born invisible, bright mid-life, fades at death
      const fade = t < 0.15 ? t / 0.15 : t > 0.75 ? (1 - t) / 0.25 : 1.0;
      const alpha = fade * alphaBase;
      if (alpha < 0.02) continue;

      // Tail: from where the particle was TAIL_FRAMES ago → current pos
      const tx = p.x - this.windDx * TAIL_FRAMES;
      const ty = p.y - this.windDy * TAIL_FRAMES;

      const grad = ctx.createLinearGradient(tx, ty, p.x, p.y);
      grad.addColorStop(0, `rgba(120,210,255,0)`);
      grad.addColorStop(1, `rgba(160,235,255,${alpha.toFixed(3)})`);

      ctx.beginPath();
      ctx.moveTo(tx, ty);
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = grad;
      ctx.lineWidth   = 1.3;
      ctx.stroke();
    }
  }
}
