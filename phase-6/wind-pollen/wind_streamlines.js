// wind_streamlines.js — city-wide wind particle streamlines
// Subtle animated streaks showing wind direction across the whole map.

const N_PARTICLES  = 220;
const BASE_SPEED   = 0.55;   // px/frame per m/s of wind
const MAX_AGE      = 200;    // frames before a particle resets

export class WindStreamlines {
  constructor(canvas) {
    this.canvas  = canvas;
    this.ctx     = canvas.getContext('2d');
    this.particles = [];
    this._raf    = null;
    this.windDx  = 0;
    this.windDy  = 0;
    this.windSpeed = 0;
  }

  setWind(directionDeg, speedMs) {
    this.windSpeed = speedMs;
    if (speedMs < 0.5) { this.windDx = 0; this.windDy = 0; return; }
    const travelRad = (directionDeg + 180) * Math.PI / 180;
    const pxF = speedMs * BASE_SPEED;
    this.windDx =  Math.sin(travelRad) * pxF;
    this.windDy = -Math.cos(travelRad) * pxF;
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

  updateWind(directionDeg, speedMs) {
    this.setWind(directionDeg, speedMs);
    // Re-scatter particles so they don't all cluster
    this._initParticles();
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

  _spawn(W, H, randomAge = false) {
    return {
      x:      Math.random() * W,
      y:      Math.random() * H,
      age:    randomAge ? Math.floor(Math.random() * MAX_AGE) : 0,
      maxAge: MAX_AGE * (0.6 + Math.random() * 0.8),
    };
  }

  _update() {
    const W = this.canvas.width;
    const H = this.canvas.height;
    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      // Small Brownian wobble perpendicular to wind so streaks are organic
      const perp = (Math.random() - 0.5) * 0.4;
      p.x += this.windDx - this.windDy * perp;
      p.y += this.windDy + this.windDx * perp;
      p.age++;
      // Wrap around edges
      p.x = ((p.x % W) + W) % W;
      p.y = ((p.y % H) + H) % H;
      if (p.age > p.maxAge) {
        this.particles[i] = this._spawn(W, H, false);
      }
    }
  }

  _draw() {
    const ctx = this.ctx;
    // Fade trail so old streaks dissolve without full clear (motion-blur feel)
    ctx.fillStyle = 'rgba(0,0,0,0.18)';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    const base = Math.min(1, this.windSpeed / 6) * 0.55;  // opacity scales with speed

    for (const p of this.particles) {
      const t = p.age / p.maxAge;
      // Bell-shaped fade: bright in the middle, fade at birth and death
      const fade = t < 0.15 ? t / 0.15 : t > 0.75 ? (1 - t) / 0.25 : 1.0;
      const alpha = fade * base;
      if (alpha < 0.02) continue;

      // Tail length proportional to speed
      const tail = Math.max(3, this.windSpeed * 2.5);
      const tx = p.x - this.windDx / BASE_SPEED / this.windSpeed * tail * 0.5;
      const ty = p.y - this.windDy / BASE_SPEED / this.windSpeed * tail * 0.5;

      const grad = ctx.createLinearGradient(tx, ty, p.x, p.y);
      grad.addColorStop(0, `rgba(120,210,255,0)`);
      grad.addColorStop(1, `rgba(160,230,255,${alpha.toFixed(2)})`);

      ctx.beginPath();
      ctx.moveTo(tx, ty);
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = grad;
      ctx.lineWidth   = 1.2;
      ctx.stroke();
    }
  }
}
