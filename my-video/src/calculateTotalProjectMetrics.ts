import {
  PHASE_SEQUENCE,
  PREFAB_LIFECYCLE_STAGES,
  type DataModel,
  type DisplayMode,
  type LifecycleStageKey,
  type MethodKey,
  type PhaseKey,
  type PrefabSubMethod,
} from "./mockMetricData";
import {
  calculateLifecycleStageMetrics,
  calculatePhaseStageMetrics,
  type ActiveGeometry,
  type CalculationBasisSummary,
} from "./calculateMockMetrics";

export interface TotalProjectInput {
  method: MethodKey;
  data_model: DataModel;
  display_mode: DisplayMode;
  sub_method?: PrefabSubMethod | null;
  activeGeometry: ActiveGeometry;
  selectedZones?: string[];
  allPhases?: PhaseKey[];
  allLifecycleStages?: LifecycleStageKey[];
}

export interface StageSummary {
  stage: string;
  co2_total: number;
  cost_total: number;
  time_days: number;
  labor_hours: number;
  material_mass: number;
  warnings: string[];
  calculation_basis: CalculationBasisSummary;
}

export interface TotalProjectMetrics {
  total_co2: number;
  total_cost: number;
  total_time_days: number;
  total_labor_hours: number;
  total_material_mass: number;
  scope_label: string;
  calculation_basis: CalculationBasisSummary;
  warnings: string[];
  stage_summaries: StageSummary[];
}

function roundMetric(value: number) {
  return Math.round(value * 100) / 100;
}

function unique<T>(values: T[]) {
  return [...new Set(values)];
}

export function calculateTotalProjectMetrics(
  input: TotalProjectInput,
): TotalProjectMetrics {
  const stageSummaries: StageSummary[] =
    input.method === "prefab"
      ? (input.allLifecycleStages ?? PREFAB_LIFECYCLE_STAGES).map((stage) => {
          const result = calculateLifecycleStageMetrics(
            stage,
            input.sub_method ?? "clt",
            input.activeGeometry,
          );
          return {
            stage,
            co2_total: result.co2_total,
            cost_total: result.cost_total,
            time_days: result.time_days,
            labor_hours: result.labor_hours,
            material_mass: result.material_mass,
            warnings: result.warnings,
            calculation_basis: result.calculation_basis,
          };
        })
      : (input.allPhases ?? PHASE_SEQUENCE).map((phase) => {
          const result = calculatePhaseStageMetrics(
            input.method as Exclude<MethodKey, "prefab">,
            phase,
            input.activeGeometry,
          );
          return {
            stage: phase,
            co2_total: result.co2_total,
            cost_total: result.cost_total,
            time_days: result.time_days,
            labor_hours: result.labor_hours,
            material_mass: result.material_mass,
            warnings: result.warnings,
            calculation_basis: result.calculation_basis,
          };
        });

  const calculationBasis: CalculationBasisSummary = {
    footprint_area_m2: input.activeGeometry.footprint_area_m2,
    total_selected_area_m2: input.activeGeometry.total_selected_area_m2,
    base_wall_surface_m2: input.activeGeometry.base_wall_surface_m2,
    total_wall_surface_m2: input.activeGeometry.total_wall_surface_m2,
    floor_count: input.activeGeometry.floor_count,
    building_height_m: input.activeGeometry.building_height_m,
    active_area_m2: input.activeGeometry.active_area_m2,
    active_wall_area_m2: input.activeGeometry.active_wall_area_m2,
    selected_zones: input.activeGeometry.active_zone_labels,
    unit_basis_used: unique(
      stageSummaries.flatMap((stage) => stage.calculation_basis.unit_basis_used),
    ),
  };

  const warnings = unique([
    ...stageSummaries.flatMap((stage) => stage.warnings),
    ...(input.method === "prefab" ? ["lifecycle_only_dataset"] : []),
    ...(input.method === "prefab" ? [] : ["time_model_provisional"]),
  ]);

  return {
    total_co2: roundMetric(
      stageSummaries.reduce((sum, stage) => sum + stage.co2_total, 0),
    ),
    total_cost: roundMetric(
      stageSummaries.reduce((sum, stage) => sum + stage.cost_total, 0),
    ),
    total_time_days: roundMetric(
      stageSummaries.reduce((sum, stage) => sum + stage.time_days, 0),
    ),
    total_labor_hours: roundMetric(
      stageSummaries.reduce((sum, stage) => sum + stage.labor_hours, 0),
    ),
    total_material_mass: roundMetric(
      stageSummaries.reduce((sum, stage) => sum + stage.material_mass, 0),
    ),
    scope_label: input.activeGeometry.isWholeBuilding
      ? "Whole Building"
      : "Selected Building Parts",
    calculation_basis: calculationBasis,
    warnings,
    stage_summaries: stageSummaries,
  };
}
