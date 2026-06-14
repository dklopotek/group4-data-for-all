// pollen_map.js — deck.gl pollen viewer: heatmap + buildings + streamlines + tooltips

import { MAPBOX_TOKEN } from './tokens.js';
import { ParticleSystem }    from './particles.js';
import { WindStreamlines }   from './wind_streamlines.js';
import { BitmapLayer, ScatterplotLayer, PolygonLayer, ColumnLayer } from '@deck.gl/layers';
import { MapboxOverlay } from '@deck.gl/mapbox';

// ── Constants ────────────────────────────────────────────────────────────────
const BOUNDS = [2.1490, 41.3820, 2.1700, 41.3960]; // [W, S, E, N]
const CENTER = [2.1594, 41.3888];

const SCENARIOS = {
  no_wind:   { label: 'No Wind',    icon: '○', file: 'pollen_grid_no_wind.json',                windSpeed: 0,  windDir: 0   },
  sea_breeze:{ label: 'Sea Breeze', icon: '↙', file: 'pollen_grid_march_april_sea_breeze.json', windSpeed: 4,  windDir: 135 },
  tramontane:{ label: 'Tramontane', icon: '↗', file: 'pollen_grid_tramontane.json',             windSpeed: 6,  windDir: 315 },
  calm:      { label: 'Calm S',     icon: '↑', file: 'pollen_grid_calm.json',                   windSpeed: 2,  windDir: 180 },
};

// Pollen colour ramp — green (low) → yellow → orange → deep red (peak)
const COLOR_RAMP = [
  [0,    [0,   0,   0,   0  ]],
  [0.05, [80,  200, 60,  60 ]],
  [0.2,  [200, 220, 0,   130]],
  [0.4,  [255, 180, 0,   165]],
  [0.65, [255, 80,  0,   205]],
  [1.0,  [200, 0,   0,   245]],
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
let activeScenario    = 'sea_breeze';
let is3D              = true;
let gridCache         = {};
let treesData         = null;
let buildingsData     = null;
let particles         = null;
let particleCanvas    = null;
let particlesVisible  = false;
let particleWindOn    = true;
let streamlines       = null;
let streamCanvas      = null;

// ── Bitmap builder ────────────────────────────────────────────────────────────
function buildBitmap(data) {
  const { grid, grid_shape } = data;
  const [nRows, nCols] = grid_shape;

  const native = document.createElement('canvas');
  native.width  = nCols;
  native.height = nRows;
  const nctx = native.getContext('2d');
  const img  = nctx.createImageData(nCols, nRows);

  // Grid row 0 = south; image row 0 = north → flip.
  // Log10 scale stretches low values so the gradient is visible.
  for (let r = 0; r < nRows; r++) {
    const imgRow = nRows - 1 - r;
    for (let c = 0; c < nCols; c++) {
      const raw = grid[r][c];
      const idx = (imgRow * nCols + c) * 4;
      if (raw < 0.005) { img.data[idx + 3] = 0; continue; }
      const v = Math.log10(1 + raw * 99) / 2;
      const [R, G, B, A] = lerpColor(COLOR_RAMP, v);
      img.data[idx]     = R;
      img.data[idx + 1] = G;
      img.data[idx + 2] = B;
      img.data[idx + 3] = A;
    }
  }
  nctx.putImageData(img, 0, 0);

  // 4× upscale with bilinear smoothing to avoid nearest-neighbour blocky pixels
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

// ── Fetch helpers ─────────────────────────────────────────────────────────────
async function loadGrid(key) {
  if (gridCache[key]) return gridCache[key];
  const r = await fetch(SCENARIOS[key].file);
  if (!r.ok) throw new Error(`Cannot load ${SCENARIOS[key].file}`);
  gridCache[key] = await r.json();
  return gridCache[key];
}

async function loadTrees() {
  if (treesData) return treesData;
  const r = await fetch('platanus_trees.geojson');
  if (!r.ok) return null;
  const fc = await r.json();
  treesData = fc.features.map(f => ({
    position:  f.geometry.coordinates,
    emission:  f.properties.emission_weight ?? 0.7,
    address:   f.properties.address  ?? '',
    species:   f.properties.species  ?? 'Platanus × acerifolia',
    categoria: f.properties.categoria_arbrat ?? '',
  }));
  return treesData;
}

async function loadBuildings() {
  if (buildingsData) return buildingsData;
  const r = await fetch('buildings.geojson');
  if (!r.ok) return null;
  const fc = await r.json();
  buildingsData = fc.features;
  return buildingsData;
}

// ── deck.gl layers ────────────────────────────────────────────────────────────
async function buildLayers(scenarioKey) {
  const [data, trees, buildings] = await Promise.all([
    loadGrid(scenarioKey), loadTrees(), loadBuildings()
  ]);
  const bitmap = buildBitmap(data);
  const layers = [];

  // 1 — Buildings: always extruded=true to avoid shader recompile on toggle.
  //     In 2D mode elevation is set to 0 (flat footprints, same shader path).
  if (buildings) {
    layers.push(new PolygonLayer({
      id:           'buildings',
      data:         buildings,
      getPolygon:   d => d.geometry.coordinates[0],
      extruded:     true,
      getElevation: d => is3D ? (d.properties.height || 20) : 0,
      getFillColor: d => {
        const h = Math.min(d.properties.height || 20, 50);
        const b = Math.round(28 + h * 0.6);
        return [b, b + 2, b + 12, 220];
      },
      getLineColor:       [100, 108, 140, 180],
      getLineWidth:       1,
      lineWidthMinPixels: 0.7,
      material:           { ambient: 0.15, diffuse: 0.65, shininess: 20 },
      pickable:           false,
    }));
  }

  // 2 — Pollen heatmap (ground plane)
  layers.push(new BitmapLayer({
    id:       'pollen-heatmap',
    bounds:   BOUNDS,
    image:    bitmap,
    opacity:  0.62,
    pickable: false,
  }));

  // 3 — Trees: cylinders in 3D, flat dots in 2D
  if (trees) {
    const mature = trees.filter(t => t.emission > 0.75);
    if (is3D) {
      // ColumnLayer — green cylinders, height = maturity proxy (5–22 m)
      layers.push(new ColumnLayer({
        id:             'platanus-trees',
        data:           mature,
        getPosition:    d => d.position,
        getElevation:   d => d.emission * 22,
        getFillColor:   d => {
          const g = Math.round(140 + d.emission * 90);
          return [30, g, 25, 240];
        },
        radius:         3.5,
        diskResolution: 8,
        pickable:       true,
        onHover: ({ object, x, y }) => showTooltip(object, x, y),
        onClick: ({ object, x, y }) => {
          if (object) activateParticles(object, x, y, scenarioKey);
        },
      }));
    } else {
      layers.push(new ScatterplotLayer({
        id:              'platanus-trees',
        data:            mature,
        getPosition:     d => d.position,
        getRadius:       4,
        getFillColor:    [60, 230, 50, 230],
        stroked:         false,
        pickable:        true,
        radiusMinPixels: 1.5,
        radiusMaxPixels: 7,
        onHover: ({ object, x, y }) => showTooltip(object, x, y),
        onClick: ({ object, x, y }) => {
          if (object) activateParticles(object, x, y, scenarioKey);
        },
      }));
    }
  }

  return layers;
}

// ── Wind arrow ────────────────────────────────────────────────────────────────
function updateWindArrow(key) {
  const sc  = SCENARIOS[key];
  const el  = document.getElementById('wind-arrow');
  if (!el) return;
  if (sc.windSpeed === 0) { el.textContent = '—'; el.style.transform = ''; return; }
  const travel = (sc.windDir + 180) % 360;
  el.style.transform = `rotate(${travel}deg)`;
  el.textContent     = '↑';
  el.title           = `${sc.label}: ${sc.windSpeed} m/s → ${travel}°`;
}

// ── Tooltip ──────────────────────────────────────────────────────────────────
function showTooltip(obj, x, y) {
  const el = document.getElementById('tree-tooltip');
  if (!el) return;
  if (!obj) { el.style.display = 'none'; return; }

  const cat = obj.categoria || '—';
  const catLabel = { EXEMPLAR: '★ EXEMPLAR', PRIMERA: '● PRIMERA', SEGONA: '◉ SEGONA', TERCERA: '○ TERCERA' }[cat] ?? cat;
  const addr = obj.address  ? `<div class="tt-addr">${obj.address}</div>` : '';
  el.innerHTML = `
    ${addr}
    <div class="tt-sp">${obj.species}</div>
    <div class="tt-cat">${catLabel} · emission <b>${obj.emission.toFixed(2)}</b></div>
    <div class="tt-hint">Click → pollen particles</div>`;
  el.style.display = 'block';

  // Keep tooltip inside the viewport
  const W = window.innerWidth, H = window.innerHeight;
  const tw = 220, th = 90;
  el.style.left = Math.min(x + 14, W - tw - 4) + 'px';
  el.style.top  = Math.min(y - 8,  H - th - 4) + 'px';
}

// ── Map update ────────────────────────────────────────────────────────────────
async function updateMap(key) {
  document.getElementById('loading').style.display = 'block';
  try {
    const layers = await buildLayers(key);
    if (!deckOverlay) {
      deckOverlay = new MapboxOverlay({ layers });
      map.addControl(deckOverlay);
    } else {
      deckOverlay.setProps({ layers });
    }
    updateWindArrow(key);

    // Update streamlines
    if (streamlines) {
      const sc = SCENARIOS[key];
      streamlines.updateWind(sc.windDir, sc.windSpeed);
      if (sc.windSpeed > 0) streamlines.start(); else streamlines.stop();
    }

    document.querySelectorAll('.scenario-btn').forEach(b =>
      b.classList.toggle('active', b.dataset.scenario === key));

  } catch (err) {
    console.error(err);
    document.getElementById('loading').textContent = 'Error loading data — run scripts first.';
    return;
  }
  document.getElementById('loading').style.display = 'none';
}

// ── Particle animation (per-tree click) ──────────────────────────────────────
function activateParticles(treeObj, sx, sy, key) {
  if (!particleCanvas) return;
  particlesVisible = true;
  particleCanvas.style.display = 'block';

  if (!particles) { particles = new ParticleSystem(particleCanvas); particles.resize(); }
  particles.stop();
  particles.originX = sx;
  particles.originY = sy;
  const sc = SCENARIOS[key];
  particles.windOn = particleWindOn;
  particles.setWind(sc.windDir, sc.windSpeed);
  particles.start();

  const panel = document.getElementById('particle-panel');
  if (panel) {
    panel.style.display = 'block';
    const info = document.getElementById('particle-info');
    if (info) {
      info.textContent =
        `${treeObj.address || 'Platanus tree'} · ${treeObj.categoria} · emission ${treeObj.emission.toFixed(2)}`;
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

// ── Init ─────────────────────────────────────────────────────────────────────
async function init() {
  if (!window.mapboxgl) { alert('Mapbox GL failed to load.'); return; }

  mapboxgl.accessToken = MAPBOX_TOKEN;
  map = new mapboxgl.Map({
    container: 'map',
    style:     'mapbox://styles/mapbox/dark-v11',
    center:    CENTER,
    zoom:      14.5,
    pitch:     50,
    bearing:   -20,
  });
  map.addControl(new mapboxgl.NavigationControl(), 'top-right');

  // Canvases
  particleCanvas = document.getElementById('particle-canvas');
  streamCanvas   = document.getElementById('streamlines-canvas');

  if (particleCanvas) {
    particleCanvas.width  = window.innerWidth;
    particleCanvas.height = window.innerHeight;
  }

  if (streamCanvas) {
    streamCanvas.width  = window.innerWidth;
    streamCanvas.height = window.innerHeight;
    streamlines = new WindStreamlines(streamCanvas);
    const sc0 = SCENARIOS[activeScenario];
    streamlines.setWind(sc0.windDir, sc0.windSpeed);
  }

  window.addEventListener('resize', () => {
    if (particles)   particles.resize();
    if (streamlines) streamlines.resize();
  });

  // Scenario buttons
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      activeScenario = btn.dataset.scenario;
      if (particles && particlesVisible) {
        const sc = SCENARIOS[activeScenario];
        particles.setWind(sc.windDir, sc.windSpeed);
      }
      updateMap(activeScenario);
    });
  });

  document.getElementById('close-particles')?.addEventListener('click', closeParticles);

  document.getElementById('toggle-3d')?.addEventListener('click', () => {
    is3D = !is3D;
    document.getElementById('toggle-3d').textContent = is3D ? '3D' : '2D';
    map.easeTo({ pitch: is3D ? 50 : 0, bearing: is3D ? -20 : 0, duration: 600 });
    // Rebuild layers from cache — no loading spinner, no re-fetch
    buildLayers(activeScenario).then(layers => {
      if (deckOverlay) deckOverlay.setProps({ layers });
    });
  });

  document.getElementById('toggle-wind')?.addEventListener('click', () => {
    particleWindOn = !particleWindOn;
    if (particles) particles.windOn = particleWindOn;
    const btn = document.getElementById('toggle-wind');
    btn.textContent = particleWindOn ? 'Wind: ON' : 'Wind: OFF';
    btn.classList.toggle('wind-off', !particleWindOn);
  });

  map.on('load', () => {
    if (streamlines) streamlines.start();
    updateMap(activeScenario);
  });
}

init();
