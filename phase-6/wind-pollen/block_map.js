// block_map.js — Eixample block-scale pollen viewer
// Real Infrared SDK wind field (CFD between buildings) + pollen particle animation

import { MAPBOX_TOKEN } from './tokens.js';
import { BlockParticles } from './block_particles.js';
import { BitmapLayer, PolygonLayer, ColumnLayer, PointCloudLayer } from '@deck.gl/layers';
import { MapboxOverlay } from '@deck.gl/mapbox';

// ── Scenarios ─────────────────────────────────────────────────────────────────
const SCENARIOS = {
  sea_breeze: {
    label: 'Sea Breeze',
    icon:  '↙',
    file:  'block_wind_field_sea_breeze.json',
    color: '#22ccff',
  },
  tramontane: {
    label: 'Tramontane',
    icon:  '↗',
    file:  'block_wind_field_tramontane.json',
    color: '#ff9a30',
  },
  calm: {
    label: 'Calm S',
    icon:  '↑',
    file:  'block_wind_field_calm.json',
    color: '#50ef70',
  },
};

// ── State ─────────────────────────────────────────────────────────────────────
let map, overlay;
let particles   = null;
let buildings   = null;
let windCache   = {};
let activeKey   = 'sea_breeze';
let is3D        = true;

// ── Load helpers ──────────────────────────────────────────────────────────────
async function loadBuildings() {
  if (buildings) return buildings;
  const r = await fetch('buildings.geojson');
  buildings = (await r.json()).features;
  return buildings;
}

async function loadWind(key) {
  if (windCache[key]) return windCache[key];
  const r = await fetch(SCENARIOS[key].file);
  if (!r.ok) throw new Error(`Wind file not found: ${SCENARIOS[key].file} — run wind_field_block.py --wind ${key}`);
  const wf = await r.json();
  // Compute CFD max once and attach so the legend can show the true range
  let maxSpd = 0;
  for (const row of wf.speed_grid) for (const v of row) if (v > maxSpd) maxSpd = v;
  wf.grid_max_ms = Math.round(maxSpd * 10) / 10;
  windCache[key] = wf;
  return wf;
}

// ── Crown sphere helper (same as main viewer) ─────────────────────────────────
function makeCrownPoints(trees, treeH) {
  const DIRS = [
    [0, 0],
    [0, 38], [72, 38], [144, 38], [216, 38], [288, 38],
    [36, 68], [108, 68], [180, 68], [252, 68], [324, 68],
  ];
  const MLAT = 1 / 111_000;
  const pts  = [];
  for (const t of trees) {
    const h    = treeH(t);
    const r    = 2 + t.emission * 3;
    const lat  = t.position[1];
    const MLNG = 1 / (111_000 * Math.cos(lat * Math.PI / 180));
    for (const [az, ze] of DIRS) {
      const azR = az * Math.PI / 180, zeR = ze * Math.PI / 180;
      pts.push({
        ...t,
        position: [
          t.position[0] + r * Math.sin(zeR) * Math.sin(azR) * MLNG,
          lat            + r * Math.sin(zeR) * Math.cos(azR) * MLAT,
          h + 1 + r * Math.cos(zeR),
        ],
      });
    }
  }
  return pts;
}

// ── deck.gl layers ────────────────────────────────────────────────────────────
async function buildLayers(windField) {
  const bldgs = await loadBuildings();
  const trees = windField.trees;

  // Filter to block bbox
  const [bW, bS, bE, bN] = windField.bbox;
  const blockBldgs = bldgs.filter(b => {
    const c = b.geometry?.coordinates?.[0];
    if (!c) return false;
    return c.some(([lng, lat]) => lng >= bW && lng <= bE && lat >= bS && lat <= bN);
  });

  const layers = [];

  // 1 — 3D buildings (always extruded=true to avoid shader recompile)
  layers.push(new PolygonLayer({
    id:           'block-buildings',
    data:         blockBldgs,
    getPolygon:   d => d.geometry.coordinates[0],
    extruded:     true,
    getElevation: d => is3D ? (d.properties.height || 18) : 0,
    getFillColor: d => {
      const h = Math.min(d.properties.height || 18, 50);
      const t = h / 50;
      // Slate-indigo: shorter = darker, taller = lighter cool-blue
      return [(48 + t * 42) | 0, (53 + t * 46) | 0, (95 + t * 58) | 0, 240];
    },
    getLineColor:       [170, 185, 240, 220],
    getLineWidth:       1,
    lineWidthMinPixels: 1,
    material:           { ambient: 0.50, diffuse: 0.60, shininess: 8 },
    pickable:           false,
  }));

  // 2 — Trees
  if (trees.length > 0) {
    if (is3D) {
      const treeH = t => 4 + t.emission * 16;

      layers.push(new ColumnLayer({
        id:             'block-trunks',
        data:           trees,
        getPosition:    t => t.position,
        getElevation:   treeH,
        getFillColor:   [110, 72, 30, 255],
        radius:         1.8,
        diskResolution: 10,
        pickable:       false,
      }));

      const crown = makeCrownPoints(trees, treeH);
      layers.push(new PointCloudLayer({
        id:          'block-crowns',
        data:        crown,
        getPosition: d => d.position,
        getColor:    d => {
          const g = (140 + d.emission * 115) | 0;
          return [20, g, 28, 230];
        },
        pointSize:   10,
        pickable:    false,
      }));
    } else {
      layers.push(new ColumnLayer({
        id:             'block-trees-2d',
        data:           trees,
        getPosition:    t => t.position,
        getElevation:   0.5,
        getFillColor:   [40, 210, 50, 240],
        radius:         3,
        diskResolution: 8,
        extruded:       true,
        pickable:       false,
      }));
    }
  }

  return layers;
}

// ── Wind direction arrow ───────────────────────────────────────────────────────
function updateArrow(windField, scenarioKey) {
  const el = document.getElementById('wind-arrow');
  if (!el) return;
  if (!windField || windField.wind_speed_ms < 0.5) { el.textContent = '—'; return; }
  const travel = (windField.wind_direction_deg + 180) % 360;
  el.style.transform = `rotate(${travel}deg)`;
  el.style.color = SCENARIOS[scenarioKey]?.color ?? '#7de8ff';
  el.textContent = '↑';

  // Update speed ramp label to actual CFD max for this scenario
  const maxEl = document.querySelector('.spd-labels span:last-child');
  if (maxEl && windField.grid_max_ms != null) {
    maxEl.textContent = windField.grid_max_ms.toFixed(1) + ' m/s';
  }
}

// ── Status label ──────────────────────────────────────────────────────────────
function setStatus(msg) {
  const el = document.getElementById('status');
  if (el) el.textContent = msg;
}

// ── Activate a scenario ───────────────────────────────────────────────────────
async function activate(key) {
  activeKey = key;
  document.querySelectorAll('.sc-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.scenario === key));

  setStatus('Loading wind field…');
  let windField;
  try {
    windField = await loadWind(key);
  } catch (e) {
    setStatus('Wind file missing — run wind_field_block.py --wind ' + key);
    return;
  }

  // Update 3D layers
  const layers = await buildLayers(windField);
  if (!overlay) {
    overlay = new MapboxOverlay({ layers });
    map.addControl(overlay);
  } else {
    overlay.setProps({ layers });
  }

  updateArrow(windField, key);

  // Restart particle system
  const bldgs = await loadBuildings();
  if (particles) particles.stop();
  particles.init(map, windField, bldgs);
  particles.start();

  const sc = SCENARIOS[key];
  const statusEl = document.getElementById('status');
  if (statusEl) {
    statusEl.innerHTML = `<span style="color:${sc.color}">${sc.icon} ${sc.label}</span> &middot; ${windField.wind_speed_ms} m/s input &middot; real CFD (Infrared SDK) &middot; ${windField.trees.length} Platanus trees`;
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  if (!window.mapboxgl) { alert('Mapbox GL failed to load'); return; }

  mapboxgl.accessToken = MAPBOX_TOKEN;

  // Load wind field first to get block center
  let initWind;
  try {
    initWind = await loadWind(activeKey);
  } catch (e) {
    document.body.innerHTML = `<div style="padding:40px;color:#f88;font-family:monospace">
      Wind field not found.<br>Run:<br><code>python3 wind_field_block.py</code><br><br>${e.message}
    </div>`;
    return;
  }

  const [bW, bS, bE, bN] = initWind.bbox;
  const center = [(bW + bE) / 2, (bS + bN) / 2];

  map = new mapboxgl.Map({
    container: 'map',
    style:     'mapbox://styles/mapbox/dark-v11',
    center,
    zoom:      16.8,
    pitch:     55,
    bearing:   0,
  });
  map.addControl(new mapboxgl.NavigationControl(), 'top-right');

  // Particle canvas
  const canvas = document.getElementById('pollen-canvas');
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
  particles = new BlockParticles(canvas);

  function reinitParticles() {
    const wf = windCache[activeKey];
    if (!wf) return;
    particles.stop();
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
    particles.init(map, wf);
    particles.start();
  }

  window.addEventListener('resize', reinitParticles);

  // Scenario buttons
  document.querySelectorAll('.sc-btn').forEach(btn => {
    btn.addEventListener('click', () => activate(btn.dataset.scenario));
  });

  // 3D toggle — wait for camera animation before rebuilding cache
  document.getElementById('toggle-3d')?.addEventListener('click', async () => {
    is3D = !is3D;
    document.getElementById('toggle-3d').textContent = is3D ? '3D' : '2D';
    map.easeTo({ pitch: is3D ? 55 : 0, bearing: 0, duration: 500 });
    const wf = windCache[activeKey];
    if (wf && overlay) overlay.setProps({ layers: await buildLayers(wf) });
    particles.stop();
    setTimeout(reinitParticles, 540);
  });

  // Pause while the user is panning/zooming; rebuild immediately after
  map.on('movestart', () => particles.stop());
  map.on('moveend',   reinitParticles);

  map.on('load', () => {
    // Remove Mapbox's own building layers so ours don't z-fight with them at high zoom
    ['building', 'building-extrusion', 'building-underground']
      .filter(id => map.getLayer(id))
      .forEach(id => map.setLayoutProperty(id, 'visibility', 'none'));
    activate(activeKey);
  });
}

init();
