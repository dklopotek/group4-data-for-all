import {
  PHASE_SEQUENCE,
  PREFAB_LIFECYCLE_STAGES,
  phaseMetricData,
  prefabLifecycleMetricData,
  type BuildingZone,
  type DataModel,
  type DisplayMode,
  type LifecycleStageKey,
  type MetricEntry,
  type MethodKey,
  type PhaseKey,
  type PrefabSubMethod,
  type StageMetrics,
} from "./mockMetricData";

export interface ActiveGeometry {
  footprint_area_m2: number;
  base_wall_surface_m2: number;
  total_selected_area_m2: number;
  total_wall_surface_m2: number;
  floor_count: number;
  floor_height_m: number;
  building_height_m: number;
  active_area_m2: number;
  active_wall_area_m2: number;
  active_perimeter_m: number;
  active_zone_ids: string[];
  active_zone_labels: string[];
  isWholeBuilding: boolean;
}

export interface MetricDetail {
  key: keyof StageMetrics;
  label: string;
  unit: string;
  raw_value: number;
  total_value: number;
  unit_basis_used: string;
}

export interface CalculationBasisSummary {
  footprint_area_m2: number;
  total_selected_area_m2: number;
  base_wall_surface_m2: number;
  total_wall_surface_m2: number;
  floor_count: number;
  building_height_m: number;
  active_area_m2: number;
  active_wall_area_m2: number;
  selected_zones: string[];
  unit_basis_used: string[];
}

export interface CalculatedMetricBundle {
  co2_total: number;
  cost_total: number;
  time_days: number;
  labor_hours: number;
  material_mass: number;
  calculation_basis: CalculationBasisSummary;
  warnings: string[];
  detail_rows: MetricDetail[];
}

export interface CalculationInput {
  method: MethodKey;
  data_model: DataModel;
  display_mode: DisplayMode;
  sub_method?: PrefabSubMethod | null;
  selectedPhase?: PhaseKey;
  selectedZones: BuildingZone[];
  activeGeometry: ActiveGeometry;
}

function roundMetric(value: number): number {
  return Math.round(value * 100) / 100;
}

function scaleMetricEntry(entry: MetricEntry, geometry: ActiveGeometry) {
  switch (entry.unit) {
    case "kgCO2eq_per_m2_gfa":
    case "cost_per_m2":
    case "cost_per_m2_gfa":
    case "labor_hours_per_m2":
    case "labor_hours_per_m2_gfa":
    case "kg_per_m2_gfa":
      return {
        total: roundMetric(entry.value * geometry.active_area_m2),
        basis: `active_area_m2 (${roundMetric(geometry.active_area_m2)} m2)`,
      };
    case "kgCO2eq_per_m2_wall":
    case "cost_per_m2_wall":
    case "labor_hours_per_m2_wall":
    case "kg_per_m2_wall":
    case "kgCO2eq_per_m2_finished_surface":
      return {
        total: roundMetric(entry.value * geometry.active_wall_area_m2),
        basis: `active_wall_area_m2 (${roundMetric(
          geometry.active_wall_area_m2,
        )} m2 wall)`,
      };
    case "days_per_m2":
      return {
        total: roundMetric(entry.value * geometry.active_area_m2),
        basis: `days_per_m2 x active_area_m2 (${roundMetric(
          geometry.active_area_m2,
        )} m2)`,
      };
    case "calendar_days":
    case "total_days":
      return {
        total: roundMetric(entry.value),
        basis: `${entry.unit} (not area-scaled)`,
      };
    default:
      return {
        total: roundMetric(entry.value),
        basis: `fallback:${entry.unit}`,
      };
  }
}

function calculateFromStageMetrics(
  metrics: StageMetrics,
  geometry: ActiveGeometry,
  warnings: string[],
): CalculatedMetricBundle {
  const detailRows: MetricDetail[] = [];
  const unitBasis = new Set<string>();

  const metricKeys: Array<keyof StageMetrics> = [
    "co2",
    "cost",
    "time_days",
    "labor_hours",
    "material_mass",
  ];

  for (const metricKey of metricKeys) {
    const entry = metrics[metricKey];
    if (!entry) {
      continue;
    }
    const scaled = scaleMetricEntry(entry, geometry);
    unitBasis.add(scaled.basis);
    detailRows.push({
      key: metricKey,
      label: entry.label,
      unit: entry.unit,
      raw_value: roundMetric(entry.value),
      total_value: scaled.total,
      unit_basis_used: scaled.basis,
    });
  }

  const sumMetric = (key: keyof StageMetrics) =>
    roundMetric(
      detailRows
        .filter((row) => row.key === key)
        .reduce((sum, row) => sum + row.total_value, 0),
    );

  return {
    co2_total: sumMetric("co2"),
    cost_total: sumMetric("cost"),
    time_days: sumMetric("time_days"),
    labor_hours: sumMetric("labor_hours"),
    material_mass: sumMetric("material_mass"),
    calculation_basis: {
      footprint_area_m2: roundMetric(geometry.footprint_area_m2),
      total_selected_area_m2: roundMetric(geometry.total_selected_area_m2),
      base_wall_surface_m2: roundMetric(geometry.base_wall_surface_m2),
      total_wall_surface_m2: roundMetric(geometry.total_wall_surface_m2),
      floor_count: geometry.floor_count,
      building_height_m: roundMetric(geometry.building_height_m),
      active_area_m2: roundMetric(geometry.active_area_m2),
      active_wall_area_m2: roundMetric(geometry.active_wall_area_m2),
      selected_zones: geometry.active_zone_ids,
      unit_basis_used: [...unitBasis],
    },
    warnings,
    detail_rows: detailRows,
  };
}

export function calculateMockMetrics(
  input: CalculationInput,
): CalculatedMetricBundle {
  const warnings = new Set<string>();

  if (input.method === "prefab") {
    warnings.add("lifecycle_only_dataset");
    const subMethod = input.sub_method ?? "clt";
    const lifecycleRows = PREFAB_LIFECYCLE_STAGES.map((stage) =>
      calculateLifecycleStageMetrics(stage, subMethod, input.activeGeometry),
    );

    const detailRows = lifecycleRows.flatMap((row) =>
      row.detail_rows.map((detail) => ({
        ...detail,
        label: `${row.stage} ${detail.label}`,
      })),
    );

    const sumField = (
      field: keyof Omit<
        CalculatedMetricBundle,
        "calculation_basis" | "warnings" | "detail_rows"
      >,
    ) => roundMetric(lifecycleRows.reduce((sum, row) => sum + row[field], 0));

    const unitBasis = new Set<string>();
    detailRows.forEach((row) => unitBasis.add(row.unit_basis_used));

    return {
      co2_total: sumField("co2_total"),
      cost_total: sumField("cost_total"),
      time_days: sumField("time_days"),
      labor_hours: sumField("labor_hours"),
      material_mass: sumField("material_mass"),
      calculation_basis: {
        footprint_area_m2: roundMetric(input.activeGeometry.footprint_area_m2),
        total_selected_area_m2: roundMetric(
          input.activeGeometry.total_selected_area_m2,
        ),
        base_wall_surface_m2: roundMetric(
          input.activeGeometry.base_wall_surface_m2,
        ),
        total_wall_surface_m2: roundMetric(
          input.activeGeometry.total_wall_surface_m2,
        ),
        floor_count: input.activeGeometry.floor_count,
        building_height_m: roundMetric(input.activeGeometry.building_height_m),
        active_area_m2: roundMetric(input.activeGeometry.active_area_m2),
        active_wall_area_m2: roundMetric(input.activeGeometry.active_wall_area_m2),
        selected_zones: input.activeGeometry.active_zone_ids,
        unit_basis_used: [...unitBasis],
      },
      warnings: [...warnings],
      detail_rows: detailRows,
    };
  }

  const selectedPhase = input.selectedPhase ?? PHASE_SEQUENCE[0];
  const stageMetrics = phaseMetricData[input.method][selectedPhase];
  if (input.method === "3d_printed") {
    warnings.add("proxy_source");
  }

  return calculateFromStageMetrics(stageMetrics, input.activeGeometry, [
    ...warnings,
  ]);
}

export function calculateLifecycleStageMetrics(
  stage: LifecycleStageKey,
  subMethod: PrefabSubMethod,
  geometry: ActiveGeometry,
) {
  const stageMetrics = prefabLifecycleMetricData[subMethod][stage];
  return {
    stage,
    sub_method: subMethod,
    ...calculateFromStageMetrics(stageMetrics, geometry, [
      "lifecycle_only_dataset",
    ]),
  };
}

export function calculatePhaseStageMetrics(
  method: Exclude<MethodKey, "prefab">,
  phase: PhaseKey,
  geometry: ActiveGeometry,
) {
  const warnings = method === "3d_printed" ? ["proxy_source"] : [];
  return calculateFromStageMetrics(phaseMetricData[method][phase], geometry, warnings);
}
