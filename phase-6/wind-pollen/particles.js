// particles.js — canvas-based pollen particle system
// Particles spawn from a tree's screen position and drift with wind.

const MAX_PARTICLES = 300;
const SPAWN_RATE     = 4;   // new particles per frame
const MAX_AGE        = 180; // frames (~3s at 60fps)

export class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext('2d');
    this.particles = [];
    this._raf   = null;
    this._frame = 0;

    // Wind state (set by caller)
    this.windDx    = 0;    // screen-space x component (px/frame)
    this.windDy    = 0;    // screen-space y component (px/frame)
    this.windOn    = true;

    // Tree anchor in screen space (updated by caller on map move)
    this.originX   = 0;
    this.originY   = 0;
  }

  setWind(directionDeg, speedMs) {
    // Convert geographic wind travel direction → screen-space dx/dy.
    // Map screen: x = east, y = south (y increases downward).
    // Wind travel direction (where pollen goes):
    const travelRad = (directionDeg + 180) * Math.PI / 180; // from bearing to math angle
    const px_per_frame = speedMs * 0.8; // scale m/s → px/frame (tunable)
    this.windDx =  Math.sin(travelRad) * px_per_frame;
    this.windDy = -Math.cos(travelRad) * px_per_frame; // flip y for screen
  }

  start() {
    if (this._raf) return;
    const loop = () => {
      this._update();
      this._draw();
      this._raf = requestAnimationFrame(loop);
    };
    this._raf = requestAnimationFrame(loop);
  }

  stop() {
    if (this._raf) { cancelAnimationFrame(this._raf); this._raf = null; }
    this.particles = [];
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  _spawn() {
    const spread = 12; // px — crown radius approximation
    const angle  = Math.random() * Math.PI * 2;
    const r      = Math.random() * spread;
    this.particles.push({
      x:    this.originX + Math.cos(angle) * r,
      y:    this.originY + Math.sin(angle) * r,
      vx:   (Math.random() - 0.5) * 0.6,  // Brownian noise
      vy:   (Math.random() - 0.5) * 0.6,
      age:  0,
      size: 2 + Math.random() * 3,
    });
  }

  _update() {
    this._frame++;

    // Spawn new particles
    if (this.particles.length < MAX_PARTICLES) {
      for (let i = 0; i < SPAWN_RATE; i++) this._spawn();
    }

    const W = this.canvas.width;
    const H = this.canvas.height;
    const windDx = this.windOn ? this.windDx : 0;
    const windDy = this.windOn ? this.windDy : 0;

    this.particles = this.particles.filter(p => {
      p.age++;
      p.vx += (Math.random() - 0.5) * 0.15; // slight Brownian each frame
      p.vy += (Math.random() - 0.5) * 0.15;
      // Gentle drag so velocity doesn't grow unbounded
      p.vx *= 0.98;
      p.vy *= 0.98;
      p.x += windDx + p.vx;
      p.y += windDy + p.vy;
      // Remove if off canvas or too old
      return p.age < MAX_AGE && p.x > -20 && p.x < W + 20 && p.y > -20 && p.y < H + 20;
    });
  }

  _draw() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    for (const p of this.particles) {
      const life  = 1 - p.age / MAX_AGE;          // 1 = young, 0 = dying
      const alpha = Math.pow(life, 0.7) * 0.85;   // fade out gently
      const size  = p.size * (0.4 + 0.6 * life);  // shrink as it ages

      // Color: bright yellow-green when fresh → pale yellow when old
      const g = Math.round(200 + 55 * life);
      const r = Math.round(255);
      const b = Math.round(0 + 100 * (1 - life));

      ctx.beginPath();
      ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${r},${g},${b},${alpha.toFixed(2)})`;
      ctx.fill();
    }

    // Draw origin marker (the tree)
    ctx.beginPath();
    ctx.arc(this.originX, this.originY, 8, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(100,220,80,0.9)';
    ctx.lineWidth   = 2;
    ctx.stroke();
    ctx.fillStyle   = 'rgba(100,220,80,0.25)';
    ctx.fill();
  }

  resize() {
    this.canvas.width  = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }
}
