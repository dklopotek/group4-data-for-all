// intro_map.js — "Data For All" narrative viewer
// Progressively reveals data layers to show how each source changes the result.

import { MAPBOX_TOKEN }    from './tokens.js';
import { WindStreamlines } from './wind_streamlines.js';
import { BlockParticles }  from './block_particles.js';
import { BitmapLayer, ColumnLayer, PolygonLayer, ScatterplotLayer, PointCloudLayer } from '@deck.gl/layers';
import { MapboxOverlay } from '@deck.gl/mapbox';

// ── Step definitions ──────────────────────────────────────────────────────────
const STEPS = [
  {
    chip:   null,
    title:  'Data\nFor All',
    body:   'Every March, 40,000 Platanus trees release invisible pollen clouds through Barcelona\'s streets.\n\nThis is how open data makes the invisible visible.',
    source: 'Mycorrhizal Barcelona · IAAC MaAI01 · 2026',
    camera: { center: [2.1594, 41.3888], zoom: 13.2, pitch: 0, bearing: 0 },
    callout: null,
    layerKey: 'empty',
  },
  {
    chip:   'OPEN DATA LAYER 01',
    title:  'Public Tree Registry',
    body:   '40,398 Platanus × acerifolia trees from Ajuntament de Barcelona\'s open catalogue.\n\nEach is a pollen source rated by maturity — from EXEMPLAR trees (100% emission) to TERCERA (45%).',
    source: 'Source: XAC / PIA · Ajuntament de Barcelona · arbrat-viari.csv (CC BY 4.0)',
    camera: { center: [2.1594, 41.3888], zoom: 14.8, pitch: 0, bearing: 0 },
    callout: [
      { stat: '40,398', label: 'Platanus trees catalogued' },
      { stat: '27%',    label: 'are EXEMPLAR or PRIMERA maturity' },
    ],
    layerKey: 'trees',
  },
  {
    chip:   'OPEN DATA LAYER 02',
    title:  'Urban Morphology',
    body:   'Building footprints and heights from OpenStreetMap reveal the structure of the city.\n\nThe Eixample\'s 113m blocks create street canyons that control where wind — and pollen — can travel.',
    source: 'Source: OpenStreetMap contributors · Overpass API · ODbL',
    camera: { center: [2.1594, 41.3888], zoom: 15.0, pitch: 48, bearing: -15 },
    callout: [
      { stat: '3,136',  label: 'building footprints' },
      { stat: '25 m',   label: 'average street width (Eixample)' },
    ],
    layerKey: 'buildings',
  },
  {
    chip:   'CFD SIMULATION',
    title:  'Wind Between Buildings',
    body:   'Infrared SDK runs GPU-based Computational Fluid Dynamics on the real building geometry.\n\nWind accelerates in street canyons. In a Tramontane episode, narrow corridors reach 10.4 m/s — 70% above the open-air speed.',
    source: 'Source: Infrared.city SDK · GPU fluid dynamics · 1m resolution',
    camera: { center: [2.1585, 41.3905], zoom: 15.8, pitch: 52, bearing: -20 },
    callout: [
      { stat: '10.4',  label: 'm/s peak canyon speed (Tramontane)' },
      { stat: '1 m',   label: 'CFD grid resolution' },
    ],
    layerKey: 'wind',
  },
  {
    chip:   'DISPERSION MODEL',
    title:  'Pollen Follows the Physics',
    body:   'Gaussian plume dispersion (Pasquill-Gifford D stability) combined with real CFD wind vectors.\n\nPollen grains don\'t drift randomly — they accelerate through street canyons, stall behind buildings, and accumulate at intersections.',
    source: 'Model: Pasquill-Gifford D · σy = 0.22x⁰·⁹ · grain 32 μm',
    camera: { center: [2.1585, 41.3905], zoom: 16.6, pitch: 55, bearing: -20 },
    callout: null,
    layerKey: 'pollen',
  },
  {
    chip:   'ONE SOURCE',
    title:  'One Tree,\nBillions of Grains',
    body:   'February to April — over 6 weeks, a single mature Platanus sheds ~3.2 billion grains into streets where residents walk every day.\n\nFor the 30% of Barcelonans living with pollen allergy, peak season means weeks of antihistamines and restricted outdoor time. City planners at Espais Verds use this to decide which trees to remove first — where one removal relieves the most people.',
    source: 'Source: Manzano et al. 2021 · Recio et al. 2018 · BCN aerobiological station · INE health survey 2022',
    camera: { center: [2.15895, 41.39075], zoom: 19.0, pitch: 62, bearing: -15 },
    callout: [
      { stat: '530 K',  label: 'Barcelonans with pollen allergy (30% of residents)' },
      { stat: 'Feb–Apr', label: 'peak season — when removals have most relief value' },
      { stat: '85%',    label: 'exposure drop beyond 150 m from the source' },
    ],
    layerKey: 'singletree',
  },
];

// ── Color ramps ───────────────────────────────────────────────────────────────
const POLLEN_RAMP = [
  [0,    [0,   0,   0,   0  ]],
  [0.04, [30,  180, 30,  40 ]],
  [0.15, [120, 240, 0,   110]],
  [0.35, [255, 200, 0,   155]],
  [0.60, [255, 80,  0,   200]],
  [0.85, [230, 20,  20,  230]],
  [1.0,  [180, 0,   60,  250]],
];

const WIND_RAMP = [
  [0,    [4,   4,   20,  0  ]],
  [0.08, [8,   20,  100, 60 ]],
  [0.25, [10,  60,  210, 140]],
  [0.50, [20,  130, 255, 190]],
  [0.75, [80,  210, 255, 215]],
  [1.0,  [200, 245, 255, 235]],
];

function lerpRamp(ramp, t) {
  t = Math.max(0, Math.min(1, t));
  for (let i = 0; i < ramp.length - 1; i++) {
    const [t0,c0] = ramp[i], [t1,c1] = ramp[i+1];
    if (t <= t1) {
      const f = (t-t0)/(t1-t0);
      return c0.map((v,j) => Math.round(v + f*(c1[j]-v)));
    }
  }
  return ramp.at(-1)[1];
}

function buildBitmap(data, ramp, logScale = true) {
  const { grid, grid_shape } = data;
  const [nR, nC] = grid_shape;
  const nat = document.createElement('canvas');
  nat.width = nC; nat.height = nR;
  const nctx = nat.getContext('2d');
  const img = nctx.createImageData(nC, nR);
  let max = 0;
  for (const row of grid) for (const v of row) if (v > max) max = v;
  for (let r = 0; r < nR; r++) {
    const ir = nR - 1 - r;
    for (let c = 0; c < nC; c++) {
      const raw = (grid[r][c] || 0) / (max || 1);
      const idx = (ir * nC + c) * 4;
      if (raw < 0.005) { img.data[idx+3] = 0; continue; }
      const v = logScale ? Math.log10(1 + raw * 99) / 2 : raw;
      const [R,G,B,A] = lerpRamp(ramp, v);
      img.data[idx]=R; img.data[idx+1]=G; img.data[idx+2]=B; img.data[idx+3]=A;
    }
  }
  nctx.putImageData(img, 0, 0);
  const S = 3;
  const out = document.createElement('canvas');
  out.width = nC*S; out.height = nR*S;
  const oct = out.getContext('2d');
  oct.imageSmoothingEnabled = true; oct.imageSmoothingQuality = 'high';
  oct.drawImage(nat, 0, 0, out.width, out.height);
  return out;
}

const CITY_BOUNDS = [2.1490, 41.3820, 2.1700, 41.3960];
const BLOCK_BBOX  = [2.1548, 41.3878, 2.1622, 41.3932];

// ── App state ─────────────────────────────────────────────────────────────────
let map, overlay, streamlines, particles;
let streamCanvas, pollenCanvas;
let step = 0;

// Data cache
let treesData = null, buildingsData = null, pollenGridData = null, blockWindData = null;

// ── Data loaders ──────────────────────────────────────────────────────────────
async function loadTrees() {
  if (treesData) return treesData;
  const fc = await (await fetch('platanus_trees.geojson')).json();
  treesData = fc.features.map(f => ({
    position: f.geometry.coordinates,
    emission: f.properties.emission_weight ?? 0.7,
  }));
  return treesData;
}

async function loadBuildings() {
  if (buildingsData) return buildingsData;
  buildingsData = (await (await fetch('buildings.geojson')).json()).features;
  return buildingsData;
}

async function loadPollenGrid() {
  if (pollenGridData) return pollenGridData;
  pollenGridData = await (await fetch('pollen_grid_march_april_sea_breeze.json')).json();
  return pollenGridData;
}

async function loadBlockWind() {
  if (blockWindData) return blockWindData;
  blockWindData = await (await fetch('block_wind_field_sea_breeze.json')).json();
  return blockWindData;
}

// ── Layer builders ────────────────────────────────────────────────────────────
function treeLayer(trees) {
  return new ColumnLayer({
    id:             'intro-trees',
    data:           trees,
    getPosition:    d => d.position,
    getElevation:   d => 4 + d.emission * 14,
    getFillColor:   d => {
      const g = (130 + d.emission * 110) | 0;
      return [62, g, 28, 230];   // brown-to-green trunks (distinct from pollen)
    },
    getLineColor:   [0, 0, 0, 0],
    radius:         2.0,
    diskResolution: 8,
    extruded:       true,
    pickable:       false,
  });
}

function buildingLayer(buildings, withTrees, trees) {
  const layers = [];
  if (withTrees) layers.push(treeLayer(trees));
  layers.push(new PolygonLayer({
    id:           'intro-buildings',
    data:         buildings,
    getPolygon:   d => d.geometry.coordinates[0],
    extruded:     true,
    getElevation: d => d.properties.height || 18,
    getFillColor: d => {
      const h = Math.min(d.properties.height || 18, 50);
      const t = h / 50;
      return [(48 + t * 42) | 0, (53 + t * 46) | 0, (95 + t * 58) | 0, 240];
    },
    getLineColor:       [170, 185, 240, 210],
    getLineWidth:       1,
    lineWidthMinPixels: 1,
    material:           { ambient: 0.50, diffuse: 0.60, shininess: 8 },
    pickable:           false,
  }));
  return layers;
}

function windHeatmapLayer(blockWind, buildings, trees) {
  const bitmap = buildBitmap(
    { grid: blockWind.speed_grid, grid_shape: blockWind.grid_shape },
    WIND_RAMP, false
  );
  return [
    // heatmap first so 3D buildings render on top (no red rooftops)
    new BitmapLayer({
      id:       'intro-wind',
      bounds:   blockWind.bbox,
      image:    bitmap,
      opacity:  0.68,
      pickable: false,
    }),
    ...buildingLayer(buildings, true, trees),
  ];
}

function pollenLayer(pollenGrid, buildings, trees) {
  const bitmap = buildBitmap(
    { grid: pollenGrid.grid, grid_shape: pollenGrid.grid_shape },
    POLLEN_RAMP, true
  );
  return [
    // heatmap first so 3D buildings render on top (no red rooftops)
    new BitmapLayer({
      id:       'intro-pollen',
      bounds:   CITY_BOUNDS,
      image:    bitmap,
      opacity:  0.48,
      pickable: false,
    }),
    ...buildingLayer(buildings, true, trees),
  ];
}

function singleTreeLayer(trees) {
  // Pick highest-emission tree within ~60 m of camera centre
  const cx = 2.15895, cy = 41.39075;
  let best = null, bestScore = -Infinity;
  for (const t of trees) {
    const dx = t.position[0] - cx, dy = t.position[1] - cy;
    const dist2 = dx * dx + dy * dy;
    if (dist2 > 0.00055 * 0.00055) continue;
    const score = t.emission - dist2 * 80000;
    if (score > bestScore) { bestScore = score; best = t; }
  }
  if (!best) best = trees.reduce((a, b) => a.emission > b.emission ? a : b);

  const [lng, lat] = best.position;
  const trunkH  = 14;                      // trunk top in metres
  const crownR  = 9;                       // crown sphere radius
  const crownCy = trunkH + crownR * 0.35; // crown centre height

  // Convert metres to degrees for crown-point offsets
  const mPerDegLat = 111320;
  const mPerDegLng = 111320 * Math.cos(lat * Math.PI / 180);

  // Build a sphere of green points for the crown (skip below trunk top)
  const crownPts = [];
  const PHI_N = 6, THETA_N = 10;
  for (let pi = 0; pi <= PHI_N; pi++) {
    const phi  = (pi / PHI_N) * Math.PI;
    const cosPhi = Math.cos(phi), sinPhi = Math.sin(phi);
    const z    = crownCy + crownR * cosPhi;
    if (z < trunkH - 2) continue;
    const rRing = crownR * sinPhi;
    for (let ti = 0; ti < THETA_N; ti++) {
      const theta = (ti / THETA_N) * 2 * Math.PI;
      crownPts.push([
        lng + rRing * Math.cos(theta) / mPerDegLng,
        lat + rRing * Math.sin(theta) / mPerDegLat,
        z,
      ]);
    }
  }
  crownPts.push([lng, lat, crownCy + crownR]); // apex point

  // Dispersal halos: 300 m → 150 m → 50 m
  const rings = [
    { id: 'ring-300', radius: 300, fill: [200, 255,  40,  30], line: [200, 255, 40,  80] },
    { id: 'ring-150', radius: 150, fill: [200, 255,  40,  70], line: [200, 255, 40, 150] },
    { id: 'ring-50',  radius:  50, fill: [200, 255,  40, 130], line: [200, 255, 40, 220] },
  ];

  return [
    ...rings.map(r => new ScatterplotLayer({
      id: `singletree-${r.id}`,
      data: [best.position],
      getPosition:   d => d,
      getRadius:     r.radius,
      radiusUnits:   'meters',
      getFillColor:  r.fill,
      getLineColor:  r.line,
      stroked: true, filled: true,
      lineWidthMinPixels: 1.5,
      pickable: false,
    })),
    // Trunk — thin narrow column, brown
    new ColumnLayer({
      id:             'singletree-trunk',
      data:           [best],
      getPosition:    d => d.position,
      getElevation:   trunkH,
      getFillColor:   [101, 67, 33, 255],
      getLineColor:   [70, 44, 18, 200],
      radius:         1.1,
      diskResolution: 12,
      extruded:       true,
      pickable:       false,
    }),
    // Crown — sphere of green point-cloud dots
    new PointCloudLayer({
      id:          'singletree-crown',
      data:        crownPts,
      getPosition: d => d,
      getColor:    [34, 180, 48, 225],
      pointSize:   22,
      pickable:    false,
    }),
  ];
}

// ── Accent colors per chip label ──────────────────────────────────────────────
const CHIP_COLORS = {
  'OPEN DATA LAYER 01': '#3ddd6a',
  'OPEN DATA LAYER 02': '#7b9fff',
  'CFD SIMULATION':     '#22ccff',
  'DISPERSION MODEL':   '#c8ff28',
  'ONE SOURCE':         '#c8ff28',
};

// ── UI helpers ────────────────────────────────────────────────────────────────
function setProgress(current, total) {
  const el = document.getElementById('progress');
  el.innerHTML = '';
  for (let i = 0; i < total; i++) {
    const d = document.createElement('div');
    d.className = 'prog-seg' + (i < current ? ' done' : i === current ? ' active' : '');
    el.appendChild(d);
  }
}

function setCallout(items, accentColor) {
  const el = document.getElementById('callout');
  if (!items || items.length === 0) { el.style.display = 'none'; return; }
  el.innerHTML = '';
  for (const { stat, label } of items) {
    el.innerHTML += `<div class="callout-card" style="border-left-color:${accentColor}40">
      <div class="stat">${stat}</div><div class="label">${label}</div>
    </div>`;
  }
  el.style.display = 'flex';
}

function setLoading(on, pct = 0) {
  const loader = document.getElementById('loader');
  const bar    = document.getElementById('loader-bar');
  loader.style.display = on ? 'block' : 'none';
  bar.style.width = pct + '%';
}

async function updatePanel(s, stepIndex) {
  const grp    = document.getElementById('text-group');
  const chip   = document.getElementById('step-chip');
  const bgNum  = document.getElementById('step-bg-num');
  const eyebrow= document.getElementById('step-eyebrow');
  const title  = document.getElementById('step-title');
  const body   = document.getElementById('step-body');
  const src    = document.getElementById('step-source');
  const panel  = document.getElementById('panel');
  const loader = document.getElementById('loader-bar');

  // Fade out
  grp.classList.add('fading');
  await new Promise(r => setTimeout(r, 280));

  // Accent color
  const accent = CHIP_COLORS[s.chip] || '#ffffff';
  panel.style.setProperty('--c-strip', accent);
  loader.style.background = accent;

  // Text content
  chip.textContent   = s.chip || '';
  chip.style.color   = accent;
  bgNum.textContent  = stepIndex > 0 ? String(stepIndex).padStart(2, '0') : '';
  eyebrow.textContent = stepIndex === 0 ? 'IAAC · MaAI01 · Barcelona 2026' : '';
  title.innerHTML    = s.title.replace(/\n/g, '<br>');
  body.innerHTML     = s.body.replace(/\n\n/g, '<br><br>');
  src.textContent    = s.source;
  src.style.borderLeftColor = accent + '30';

  setCallout(s.callout ?? null, accent);

  // Fade in
  grp.classList.remove('fading');
}

async function applyStep(n) {
  const s = STEPS[n];

  // Camera
  map.easeTo({
    center:   s.camera.center,
    zoom:     s.camera.zoom,
    pitch:    s.camera.pitch,
    bearing:  s.camera.bearing,
    duration: 1200,
    easing:   t => t < 0.5 ? 2*t*t : -1+(4-2*t)*t,
  });

  // Layers
  setLoading(true, 20);
  let layers = [];
  try {
    if (s.layerKey === 'empty') {
      layers = [];
    } else if (s.layerKey === 'trees') {
      const trees = await loadTrees(); setLoading(true, 80);
      layers = [treeLayer(trees)];
    } else if (s.layerKey === 'buildings') {
      const [trees, bldgs] = await Promise.all([loadTrees(), loadBuildings()]); setLoading(true, 80);
      layers = buildingLayer(bldgs, true, trees);
    } else if (s.layerKey === 'wind') {
      const [trees, bldgs, bw] = await Promise.all([loadTrees(), loadBuildings(), loadBlockWind()]); setLoading(true, 80);
      layers = windHeatmapLayer(bw, bldgs, trees);
      // Start streamlines
      if (streamlines && bw.wind_speed_ms > 0) {
        streamlines.updateWind(bw.wind_direction_deg, bw.wind_speed_ms);
        streamlines.start();
      }
    } else if (s.layerKey === 'pollen') {
      const [trees, bldgs, pg, bw] = await Promise.all([
        loadTrees(), loadBuildings(), loadPollenGrid(), loadBlockWind()
      ]); setLoading(true, 80);
      layers = pollenLayer(pg, bldgs, trees);
      // Wait for camera animation to finish before building mask
      document.getElementById('pollen-canvas').style.display = 'block';
      if (particles) {
        particles.stop();
        await new Promise(r => setTimeout(r, 1350));  // match easeTo duration
        particles.init(map, bw, bldgs);
        particles.start();
      }
    } else if (s.layerKey === 'singletree') {
      // Stop pollen particles and streamlines — this step is static
      if (particles) particles.stop();
      if (streamlines) streamlines.stop();
      document.getElementById('pollen-canvas').style.display = 'none';
      const trees = await loadTrees(); setLoading(true, 80);
      layers = singleTreeLayer(trees);
    }
  } catch (err) {
    console.error('Layer load error:', err);
  }

  if (!overlay) {
    overlay = new MapboxOverlay({ layers });
    map.addControl(overlay);
  } else {
    overlay.setProps({ layers });
  }

  setLoading(false);
  await updatePanel(s, n);
  setProgress(n, STEPS.length);

  // Show/hide nav buttons
  document.getElementById('btn-back').disabled   = (n === 0);
  document.getElementById('btn-next').style.display    = n < STEPS.length - 1 ? 'inline-block' : 'none';
  document.getElementById('btn-launch').style.display  = n === STEPS.length - 1 ? 'inline-block' : 'none';
  document.getElementById('btn-next').textContent = n === 0 ? 'Begin →' : 'Next →';
}

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  if (!window.mapboxgl) { alert('Mapbox GL failed to load'); return; }

  mapboxgl.accessToken = MAPBOX_TOKEN;
  map = new mapboxgl.Map({
    container:  'map',
    style:      'mapbox://styles/mapbox/dark-v11',
    center:     STEPS[0].camera.center,
    zoom:       STEPS[0].camera.zoom,
    pitch:      0,
    bearing:    0,
    interactive: true,
  });

  // Disable map interaction on splash (step 0), re-enable at step 3+
  map.dragPan.disable();
  map.scrollZoom.disable();
  map.keyboard.disable();

  // Canvases
  streamCanvas = document.getElementById('stream-canvas');
  pollenCanvas = document.getElementById('pollen-canvas');
  streamCanvas.width = pollenCanvas.width = window.innerWidth;
  streamCanvas.height = pollenCanvas.height = window.innerHeight;

  streamlines = new WindStreamlines(streamCanvas);
  particles   = new BlockParticles(pollenCanvas);

  window.addEventListener('resize', () => {
    streamCanvas.width = pollenCanvas.width = window.innerWidth;
    streamCanvas.height = pollenCanvas.height = window.innerHeight;
    // Rebuild speed cache for new dimensions (only if particles are active)
    if (particles && blockWindData) {
      particles.stop();
      particles.init(map, blockWindData);
      particles.start();
    }
  });

  // Navigation
  document.getElementById('btn-next').addEventListener('click', () => {
    if (step < STEPS.length - 1) { step++; applyStep(step); }
  });
  document.getElementById('btn-back').addEventListener('click', () => {
    if (step > 0) { step--; applyStep(step); }
  });

  // Keyboard navigation
  window.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' && step < STEPS.length - 1) { step++; applyStep(step); }
    if (e.key === 'ArrowLeft'  && step > 0)                { step--; applyStep(step); }
  });

  map.on('load', () => {
    ['building', 'building-extrusion', 'building-underground']
      .filter(id => map.getLayer(id))
      .forEach(id => map.setLayoutProperty(id, 'visibility', 'none'));
    applyStep(0);
  });
}

init();
