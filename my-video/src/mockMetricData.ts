export type MethodKey = "masonry" | "3d_printed" | "prefab";
export type PhaseKey =
  | "foundation"
  | "structure"
  | "roof"
  | "openings"
  | "finishing";
export type LifecycleStageKey = "A1-A3" | "A4" | "A5" | "B" | "C";
export type PrefabSubMethod = "clt" | "modular_concrete";
export type DataModel = "phase_based" | "lifecycle_based" | "overlay";
export type DisplayMode = "construction_phase_view" | "prefab_lifecycle_card";
export type MetricUnit =
  | "kgCO2eq_per_m2_gfa"
  | "kgCO2eq_per_m2_wall"
  | "kgCO2eq_per_m2_finished_surface"
  | "cost_per_m2"
  | "cost_per_m2_gfa"
  | "cost_per_m2_wall"
  | "labor_hours_per_m2"
  | "labor_hours_per_m2_gfa"
  | "labor_hours_per_m2_wall"
  | "calendar_days"
  | "total_days"
  | "days_per_m2"
  | "kg_per_m2_gfa"
  | "kg_per_m2_wall";

export interface MetricEntry {
  label: string;
  value: number;
  unit: MetricUnit;
}

export interface StageMetrics {
  co2?: MetricEntry;
  cost?: MetricEntry;
  time_days?: MetricEntry;
  labor_hours?: MetricEntry;
  material_mass?: MetricEntry;
}

export interface ZoneShape {
  x: number;
  y: number;
  w: number;
  h: number;
  rx?: number;
}

export interface BuildingZone {
  id: string;
  label: string;
  area_m2: number;
  wall_area_m2: number;
  perimeter_m: number;
  height_m: number;
  selectable: true;
  shape: ZoneShape;
}

export interface MethodContract {
  key: MethodKey;
  label: string;
  data_model: DataModel;
  display_mode: DisplayMode;
  selected_material: string;
  stages: readonly string[];
  baseWarnings: string[];
  accent: string;
  accentSoft: string;
  glow: string;
}

export const PHASE_SEQUENCE: PhaseKey[] = [
  "foundation",
  "structure",
  "roof",
  "openings",
  "finishing",
];

export const PREFAB_LIFECYCLE_STAGES: LifecycleStageKey[] = [
  "A1-A3",
  "A4",
  "A5",
  "B",
  "C",
];

export const phaseLabels: Record<PhaseKey, string> = {
  foundation: "1 Foundation",
  structure: "2 Structure / Walls",
  roof: "3 Roof",
  openings: "4 Openings",
  finishing: "5 Finishing",
};

export const lifecycleLabels: Record<LifecycleStageKey, string> = {
  "A1-A3": "Production",
  A4: "Transport",
  A5: "Assembly",
  B: "Use phase",
  C: "End of Life",
};

export const methodContracts: Record<MethodKey, MethodContract> = {
  masonry: {
    key: "masonry",
    label: "Masonry",
    data_model: "phase_based",
    display_mode: "construction_phase_view",
    selected_material: "fired_clay_brick",
    stages: PHASE_SEQUENCE,
    baseWarnings: [],
    accent: "#ff8c2f",
    accentSoft: "rgba(255, 140, 47, 0.18)",
    glow: "rgba(255, 140, 47, 0.45)",
  },
  "3d_printed": {
    key: "3d_printed",
    label: "3D Printed",
    data_model: "phase_based",
    display_mode: "construction_phase_view",
    selected_material: "printed_concrete_or_earth_proxy",
    stages: PHASE_SEQUENCE,
    baseWarnings: ["proxy_source"],
    accent: "#4ecbff",
    accentSoft: "rgba(78, 203, 255, 0.18)",
    glow: "rgba(78, 203, 255, 0.45)",
  },
  prefab: {
    key: "prefab",
    label: "Prefab",
    data_model: "lifecycle_based",
    display_mode: "prefab_lifecycle_card",
    selected_material: "timber_clt_prefab",
    stages: PREFAB_LIFECYCLE_STAGES,
    baseWarnings: ["lifecycle_only_dataset"],
    accent: "#47d78f",
    accentSoft: "rgba(71, 215, 143, 0.18)",
    glow: "rgba(71, 215, 143, 0.45)",
  },
};

export const mockBuildingZones: BuildingZone[] = [
  {
    id: "zone_facade_band",
    label: "Facade Band",
    area_m2: 24,
    wall_area_m2: 156,
    perimeter_m: 52,
    height_m: 3.2,
    selectable: true,
    shape: { x: 150, y: 24, w: 676, h: 494, rx: 20 },
  },
  {
    id: "zone_north_wing",
    label: "North Wing",
    area_m2: 68,
    wall_area_m2: 132,
    perimeter_m: 41,
    height_m: 3.2,
    selectable: true,
    shape: { x: 270, y: 58, w: 430, h: 118, rx: 14 },
  },
  {
    id: "zone_core",
    label: "Core",
    area_m2: 42,
    wall_area_m2: 88,
    perimeter_m: 28,
    height_m: 3.2,
    selectable: true,
    shape: { x: 386, y: 194, w: 198, h: 124, rx: 14 },
  },
  {
    id: "zone_west_wing",
    label: "West Wing",
    area_m2: 57,
    wall_area_m2: 111,
    perimeter_m: 36,
    height_m: 3.2,
    selectable: true,
    shape: { x: 198, y: 208, w: 154, h: 262, rx: 14 },
  },
  {
    id: "zone_east_wing",
    label: "East Wing",
    area_m2: 54,
    wall_area_m2: 106,
    perimeter_m: 34,
    height_m: 3.2,
    selectable: true,
    shape: { x: 617, y: 208, w: 166, h: 262, rx: 14 },
  },
  {
    id: "zone_south_wing",
    label: "South Wing",
    area_m2: 61,
    wall_area_m2: 118,
    perimeter_m: 38,
    height_m: 3.2,
    selectable: true,
    shape: { x: 294, y: 352, w: 383, h: 130, rx: 14 },
  },
  {
    id: "zone_courtyard",
    label: "Courtyard",
    area_m2: 36,
    wall_area_m2: 64,
    perimeter_m: 24,
    height_m: 0,
    selectable: true,
    shape: { x: 410, y: 222, w: 146, h: 80, rx: 10 },
  },
];

export const phaseMetricData: Record<
  Exclude<MethodKey, "prefab">,
  Record<PhaseKey, StageMetrics>
> = {
  masonry: {
    foundation: {
      co2: { label: "Embodied carbon", value: 48, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Cost", value: 118, unit: "cost_per_m2_gfa" },
      time_days: { label: "Phase duration", value: 6, unit: "calendar_days" },
      labor_hours: { label: "Labour", value: 3.2, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Material mass", value: 420, unit: "kg_per_m2_gfa" },
    },
    structure: {
      co2: { label: "Wall carbon", value: 33, unit: "kgCO2eq_per_m2_wall" },
      cost: { label: "Wall cost", value: 145, unit: "cost_per_m2_wall" },
      time_days: { label: "Phase duration", value: 12, unit: "calendar_days" },
      labor_hours: { label: "Masonry labour", value: 1.4, unit: "labor_hours_per_m2_wall" },
      material_mass: { label: "Brick mass", value: 185, unit: "kg_per_m2_wall" },
    },
    roof: {
      co2: { label: "Roof carbon", value: 26, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Roof cost", value: 84, unit: "cost_per_m2_gfa" },
      time_days: { label: "Phase duration", value: 8, unit: "calendar_days" },
      labor_hours: { label: "Roof labour", value: 1.7, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Roof mass", value: 64, unit: "kg_per_m2_gfa" },
    },
    openings: {
      co2: { label: "Openings carbon", value: 14, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Openings cost", value: 96, unit: "cost_per_m2_gfa" },
      time_days: { label: "Openings duration", value: 4, unit: "calendar_days" },
      labor_hours: { label: "Install labour", value: 0.8, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Openings mass", value: 22, unit: "kg_per_m2_gfa" },
    },
    finishing: {
      co2: { label: "Finishing carbon", value: 12, unit: "kgCO2eq_per_m2_finished_surface" },
      cost: { label: "Finishing cost", value: 36, unit: "cost_per_m2_gfa" },
      time_days: { label: "Finishing time", value: 0.55, unit: "days_per_m2" },
      labor_hours: { label: "Finishing labour", value: 1.15, unit: "labor_hours_per_m2" },
      material_mass: { label: "Finishing mass", value: 9, unit: "kg_per_m2_gfa" },
    },
  },
  "3d_printed": {
    foundation: {
      co2: { label: "Embodied carbon", value: 45, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Cost", value: 112, unit: "cost_per_m2_gfa" },
      time_days: { label: "Phase duration", value: 5, unit: "calendar_days" },
      labor_hours: { label: "Labour", value: 2.8, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Material mass", value: 395, unit: "kg_per_m2_gfa" },
    },
    structure: {
      co2: { label: "Printed shell carbon", value: 24, unit: "kgCO2eq_per_m2_wall" },
      cost: { label: "Printed shell cost", value: 126, unit: "cost_per_m2_wall" },
      time_days: { label: "Print duration", value: 3, unit: "calendar_days" },
      labor_hours: { label: "Printer labour", value: 0.42, unit: "labor_hours_per_m2_wall" },
      material_mass: { label: "Print mix mass", value: 162, unit: "kg_per_m2_wall" },
    },
    roof: {
      co2: { label: "Roof carbon", value: 24, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Roof cost", value: 82, unit: "cost_per_m2_gfa" },
      time_days: { label: "Roof duration", value: 7, unit: "calendar_days" },
      labor_hours: { label: "Roof labour", value: 1.45, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Roof mass", value: 60, unit: "kg_per_m2_gfa" },
    },
    openings: {
      co2: { label: "Openings carbon", value: 13, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Openings cost", value: 94, unit: "cost_per_m2_gfa" },
      time_days: { label: "Openings duration", value: 4, unit: "calendar_days" },
      labor_hours: { label: "Install labour", value: 0.72, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Openings mass", value: 21, unit: "kg_per_m2_gfa" },
    },
    finishing: {
      co2: { label: "Finishing carbon", value: 9, unit: "kgCO2eq_per_m2_finished_surface" },
      cost: { label: "Finishing cost", value: 28, unit: "cost_per_m2_gfa" },
      time_days: { label: "Finishing time", value: 0.35, unit: "days_per_m2" },
      labor_hours: { label: "Finishing labour", value: 0.78, unit: "labor_hours_per_m2" },
      material_mass: { label: "Finishing mass", value: 5, unit: "kg_per_m2_gfa" },
    },
  },
};

export const prefabLifecycleMetricData: Record<
  PrefabSubMethod,
  Record<LifecycleStageKey, StageMetrics>
> = {
  clt: {
    "A1-A3": {
      co2: { label: "Factory carbon", value: 168, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Factory cost", value: 790, unit: "cost_per_m2_gfa" },
      time_days: { label: "Lead time", value: 42, unit: "calendar_days" },
      labor_hours: { label: "Factory labour", value: 3.2, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Panel mass", value: 122, unit: "kg_per_m2_wall" },
    },
    A4: {
      co2: { label: "Transport carbon", value: 28, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Transport cost", value: 96, unit: "cost_per_m2_gfa" },
      time_days: { label: "Transit days", value: 5, unit: "total_days" },
      labor_hours: { label: "Logistics labour", value: 0.18, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Delivered mass", value: 122, unit: "kg_per_m2_wall" },
    },
    A5: {
      co2: { label: "Site assembly carbon", value: 15, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Site assembly cost", value: 310, unit: "cost_per_m2_gfa" },
      time_days: { label: "Assembly days", value: 0.42, unit: "days_per_m2" },
      labor_hours: { label: "Assembly labour", value: 1.4, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Fixings mass", value: 8, unit: "kg_per_m2_gfa" },
    },
    B: {
      co2: { label: "Use-phase annualized carbon", value: 8, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Maintenance reserve", value: 55, unit: "cost_per_m2_gfa" },
      time_days: { label: "Service downtime", value: 3, unit: "total_days" },
      labor_hours: { label: "Maintenance labour", value: 0.26, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Replacement mass", value: 6, unit: "kg_per_m2_gfa" },
    },
    C: {
      co2: { label: "End-of-life carbon", value: 12, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "End-of-life cost", value: 62, unit: "cost_per_m2_gfa" },
      time_days: { label: "Deconstruction days", value: 0.18, unit: "days_per_m2" },
      labor_hours: { label: "Deconstruction labour", value: 0.64, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Recovered mass", value: 20, unit: "kg_per_m2_gfa" },
    },
  },
  modular_concrete: {
    "A1-A3": {
      co2: { label: "Factory carbon", value: 312, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Factory cost", value: 690, unit: "cost_per_m2_gfa" },
      time_days: { label: "Lead time", value: 68, unit: "calendar_days" },
      labor_hours: { label: "Factory labour", value: 5.6, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Module mass", value: 276, unit: "kg_per_m2_wall" },
    },
    A4: {
      co2: { label: "Transport carbon", value: 14, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Transport cost", value: 64, unit: "cost_per_m2_gfa" },
      time_days: { label: "Transit days", value: 3, unit: "total_days" },
      labor_hours: { label: "Logistics labour", value: 0.22, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Delivered mass", value: 276, unit: "kg_per_m2_wall" },
    },
    A5: {
      co2: { label: "Site assembly carbon", value: 24, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Site assembly cost", value: 248, unit: "cost_per_m2_gfa" },
      time_days: { label: "Assembly days", value: 0.31, unit: "days_per_m2" },
      labor_hours: { label: "Assembly labour", value: 1.92, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Fixings mass", value: 15, unit: "kg_per_m2_gfa" },
    },
    B: {
      co2: { label: "Use-phase annualized carbon", value: 11, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "Maintenance reserve", value: 48, unit: "cost_per_m2_gfa" },
      time_days: { label: "Service downtime", value: 2, unit: "total_days" },
      labor_hours: { label: "Maintenance labour", value: 0.22, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Replacement mass", value: 12, unit: "kg_per_m2_gfa" },
    },
    C: {
      co2: { label: "End-of-life carbon", value: 38, unit: "kgCO2eq_per_m2_gfa" },
      cost: { label: "End-of-life cost", value: 78, unit: "cost_per_m2_gfa" },
      time_days: { label: "Deconstruction days", value: 0.22, unit: "days_per_m2" },
      labor_hours: { label: "Deconstruction labour", value: 0.72, unit: "labor_hours_per_m2_gfa" },
      material_mass: { label: "Recovered mass", value: 28, unit: "kg_per_m2_gfa" },
    },
  },
};

export const assemblyNotes: Record<MethodKey, string[]> = {
  masonry: [
    "Built layer by layer with conventional brick assembly.",
    "Most impact gathers in the structure and wall phase.",
    "Finishing uses days per m² to stress-test time rules",
  ],
  "3d_printed": [
    "Foundation and roof stay conventional",
    "Structure rows are wall-based proxy values",
    "Warnings intentionally preserve proxy-source feel",
  ],
  prefab: [
    "Lifecycle-only dataset",
    "Construction phases are intentionally disabled",
    "Switch CLT / modular concrete to compare lifecycle behavior",
  ],
};
