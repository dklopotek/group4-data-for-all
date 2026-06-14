// pollen_map.js — deck.gl pollen viewer for Barcelona Platanus dispersion
// Scenarios: No Wind | Sea Breeze (SE) | Tramontane (NW) | Calm (S)
// BitmapLayer for pollen heatmap + ScatterplotLayer for trees + particle overlay on click.

import { MAPBOX_TOKEN } from './tokens.js';
import { ParticleSystem } from './particles.js';
import { BitmapLayer, ScatterplotLayer } from '@deck.gl/layers';
import { MapboxOverlay } from '@deck.gl/mapbox';

// ── Constants ────────────────────────────────────────────────────────────────
const BOUNDS = [2.1490, 41.3820, 2.1700, 41.3960]; // [W, S, E, N]
const CENTER = [2.1594, 41.3888];

const SCENARIOS = {
  no_wind:   { label: 'No Wind',    icon: '○', file: 'pollen_grid_no_wind.json',                  windSpeed: 0,  windDir: 0 },
  sea_breeze:{ label: 'Sea Breeze', icon: '↙', file: 'pollen_grid_march_april_sea_breeze.json',   windSpeed: 4,  windDir: 135 },
  tramontane:{ label: 'Tramontane', icon: '↗', file: 'pollen_grid_tramontane.json',               windSpeed: 6,  windDir: 315 },
  calm:      { label: 'Calm S',     icon: '↑', file: 'pollen_grid_calm.json',                     windSpeed: 2,  windDir: 180 },
};

// Pollen heatmap color ramp (0 = transparent, 1 = deep red)
const COLOR_RAMP = [
  [0,   [0,   0,   0,   0  ]],
  [0.05,[80,  200, 60,  60 ]],
  [0.2, [200, 220, 0,   120]],
  [0.4, [255, 180, 0,   160]],
  [0.65,[255, 80,  0,   200]],
  [1.0, [200, 0,   0,   240]],
];

function lerpColor(ramp, t) {
  t = Math.max(0, Math.min(1, t));
  for (let i = 0; i < ramp.length - 1; i++) {
    const [t0, c0] = ramp[i];
    const [t1, c1] = ramp[i + 1];
    if (t >= t0 && t <= t1) {
      const f = (t - t0) / (t1 - t0);
      return c0.map((v, j) => Math.round(v + f * (c1[j] - v)));
    }
  }
  return ramp[ramp.length - 1][1];
}

// ── State ────────────────────────────────────────────────────────────────────
let map, deckOverlay;
let activeScenario = 'sea_breeze';
let gridCache = {};
let treesData = null;
let particles = null;
let particleCanvas = null;
let particlesVisible = false;
let particleWindOn = true;

// ── Build BitmapLayer canvas from pollen grid ─────────────────────────────
function buildBitmap(data) {
  const { grid, grid_shape } = data;
  const [nRows, nCols] = grid_shape;

  // Draw at native grid resolution, then upscale 4× with smoothing so
  // WebGL / canvas doesn't nearest-neighbour the 5m cells into big squares.
  const native = document.createElement('canvas');
  native.width  = nCols;
  native.height = nRows;
  const nctx = native.getContext('2d');
  const img  = nctx.createImageData(nCols, nRows);

  // Grid row 0 = south → image row (nRows-1) = bottom.
  // BitmapLayer expects image row 0 = north, so we flip vertically.
  for (let r = 0; r < nRows; r++) {
    const imgRow = nRows - 1 - r;
    for (let c = 0; c < nCols; c++) {
      const raw = grid[r][c];
      const idx = (imgRow * nCols + c) * 4;
      if (raw < 0.005) { img.data[idx + 3] = 0; continue; }
      // Log10 scale: spreads low values, compresses the saturated peak.
      // log10(1 + raw*99) / 2  maps 0→0, 0.01→0.15, 0.1→0.52, 1→1
      const v = Math.log10(1 + raw * 99) / 2;
      const [R, G, B, A] = lerpColor(COLOR_RAMP, v);
      img.data[idx]     = R;
      img.data[idx + 1] = G;
      img.data[idx + 2] = B;
      img.data[idx + 3] = A;
    }
  }
  nctx.putImageData(img, 0, 0);

  // 4× upscale with bilinear smoothing
  const SCALE = 4;
  const out   = document.createElement('canvas');
  out.width   = nCols * SCALE;
  out.height  = nRows * SCALE;
  const octx  = out.getContext('2d');
  octx.imageSmoothingEnabled = true;
  octx.imageSmoothingQuality = 'high';
  octx.drawImage(native, 0, 0, out.width, out.height);
  return out;
}

// ── Fetch helpers ─────────────────────────────────────────────────────────
async function loadGrid(scenarioKey) {
  if (gridCache[scenarioKey]) return gridCache[scenarioKey];
  const url = SCENARIOS[scenarioKey].file;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Failed to load ${url}: ${r.status}`);
  const data = await r.json();
  gridCache[scenarioKey] = data;
  return data;
}

async function loadTrees() {
  if (treesData) return treesData;
  const r = await fetch('platanus_trees.geojson');
  if (!r.ok) return null;
  const fc = await r.json();
  treesData = fc.features.map(f => ({
    position: f.geometry.coordinates,
    emission: f.properties.emission_weight ?? 0.7,
  }));
  return treesData;
}

// ── deck.gl layers ─────────────────────────────────────────────────────────
async function buildLayers(scenarioKey) {
  const [data, trees] = await Promise.all([loadGrid(scenarioKey), loadTrees()]);
  const bitmap = buildBitmap(data);

  const layers = [
    new BitmapLayer({
      id: 'pollen-heatmap',
      bounds: BOUNDS,
      image: bitmap,
      opacity: 0.62,
      pickable: false,
    }),
  ];

  if (trees) {
    // Only show mature trees (emission > 0.75) to avoid dense grid artefact.
    const matureTrees = trees.filter(t => t.emission > 0.75);
    layers.push(new ScatterplotLayer({
      id: 'platanus-trees',
      data: matureTrees,
      getPosition: d => d.position,
      getRadius: 4,           // metres — constant so they stay small
      getFillColor: [60, 230, 50, 230],
      stroked: false,
      pickable: true,
      radiusMinPixels: 1.5,
      radiusMaxPixels: 7,
      onClick: ({ object, x, y }) => {
        if (object) activateParticles(object, x, y, scenarioKey);
      },
    }));
  }

  return layers;
}

// ── Wind arrow overlay ────────────────────────────────────────────────────
function updateWindArrow(scenarioKey) {
  const sc = SCENARIOS[scenarioKey];
  const el = document.getElementById('wind-arrow');
  if (!el) return;
  if (sc.windSpeed === 0) {
    el.textContent = '—';
    el.title = 'No wind';
    return;
  }
  // CSS rotate: arrow points in direction pollen travels (FROM source direction + 180°)
  const travelDeg = (sc.windDir + 180) % 360;
  el.style.transform = `rotate(${travelDeg}deg)`;
  el.textContent = '↑';
  el.title = `${sc.label}: ${sc.windSpeed} m/s, pollen travels ${travelDeg}°`;
}

// ── Update map ─────────────────────────────────────────────────────────────
async function updateMap(scenarioKey) {
  document.getElementById('loading').style.display = 'block';
  try {
    const layers = await buildLayers(scenarioKey);
    if (!deckOverlay) {
      deckOverlay = new MapboxOverlay({ layers });
      map.addControl(deckOverlay);
    } else {
      deckOverlay.setProps({ layers });
    }
    updateWindArrow(scenarioKey);
    document.querySelectorAll('.scenario-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.scenario === scenarioKey);
    });
  } catch (err) {
    console.error('Failed to load scenario:', err);
    document.getElementById('loading').textContent = 'Error loading data. Run scripts first.';
    return;
  }
  document.getElementById('loading').style.display = 'none';
}

// ── Particle animation on tree click ─────────────────────────────────────
function activateParticles(treeObj, screenX, screenY, scenarioKey) {
  if (!particleCanvas) return;
  particlesVisible = true;
  particleCanvas.style.display = 'block';

  if (!particles) {
    particles = new ParticleSystem(particleCanvas);
    particles.resize();
  }

  particles.stop();
  particles.originX = screenX;
  particles.originY = screenY;

  const sc = SCENARIOS[scenarioKey];
  particles.windOn = particleWindOn;
  particles.setWind(sc.windDir, sc.windSpeed);
  particles.start();

  // Show the particle panel
  const panel = document.getElementById('particle-panel');
  if (panel) {
    panel.style.display = 'block';
    const info = document.getElementById('particle-info');
    if (info) {
      const ew = treeObj.emission.toFixed(2);
      info.textContent = `Tree at ${treeObj.position[1].toFixed(4)}°N, ${treeObj.position[0].toFixed(4)}°E | emission weight ${ew}`;
    }
  }
}

function closeParticles() {
  if (particles) particles.stop();
  particlesVisible = false;
  if (particleCanvas) particleCanvas.style.display = 'none';
  const panel = document.getElementById('particle-panel');
  if (panel) panel.style.display = 'none';
}

// ── Init ──────────────────────────────────────────────────────────────────
async function init() {
  // Validate the importmap loaded deck.gl correctly via the pre-assigned globals
  // (set in viewer.html script tags before this module runs).
  if (!window.mapboxgl) {
    alert('Mapbox GL failed to load. Check your network connection.');
    return;
  }

  mapboxgl.accessToken = MAPBOX_TOKEN;
  map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v11',
    center: CENTER,
    zoom: 14.5,
    pitch: 0,
    bearing: 0,
  });

  map.addControl(new mapboxgl.NavigationControl(), 'top-right');

  // Set up particle canvas
  particleCanvas = document.getElementById('particle-canvas');
  if (particleCanvas) {
    particleCanvas.width  = window.innerWidth;
    particleCanvas.height = window.innerHeight;
    window.addEventListener('resize', () => {
      if (particles) particles.resize();
    });
  }

  // Scenario buttons
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      activeScenario = btn.dataset.scenario;
      // Update particles wind if active
      if (particles && particlesVisible) {
        const sc = SCENARIOS[activeScenario];
        particles.setWind(sc.windDir, sc.windSpeed);
      }
      updateMap(activeScenario);
    });
  });

  // Close particle panel
  document.getElementById('close-particles')?.addEventListener('click', closeParticles);

  // Wind toggle in particle panel
  document.getElementById('toggle-wind')?.addEventListener('click', () => {
    particleWindOn = !particleWindOn;
    if (particles) {
      particles.windOn = particleWindOn;
    }
    const btn = document.getElementById('toggle-wind');
    btn.textContent = particleWindOn ? 'Wind: ON' : 'Wind: OFF';
    btn.classList.toggle('wind-off', !particleWindOn);
  });

  map.on('load', () => updateMap(activeScenario));
}

init();
