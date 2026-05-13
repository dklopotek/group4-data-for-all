import type { MethodKey, PrefabSubMethod } from "./mockMetricData";

export type MethodConstraintKey =
  | "masonry"
  | "3d_printed"
  | "prefab_clt"
  | "prefab_modular_concrete";

export interface MethodFloorConstraint {
  min_floors: number;
  max_floors: number;
  default_floors: number;
  floor_height_m: number;
  label: string;
  user_note: string;
}

// Floor limits are prototype assumptions and should be replaced by validated
// structural/regulatory data when available.
export const methodFloorConstraints: Record<
  MethodConstraintKey,
  MethodFloorConstraint
> = {
  masonry: {
    min_floors: 1,
    max_floors: 5,
    default_floors: 2,
    floor_height_m: 3.2,
    label: "Masonry",
    user_note: "Low-rise masonry assumption.",
  },
  "3d_printed": {
    min_floors: 1,
    max_floors: 2,
    default_floors: 1,
    floor_height_m: 3.2,
    label: "3D Printed",
    user_note:
      "Limited to low-rise 3D printed construction in this prototype.",
  },
  prefab_clt: {
    min_floors: 1,
    max_floors: 8,
    default_floors: 3,
    floor_height_m: 3.2,
    label: "CLT / Timber Prefab",
    user_note: "Mid-rise prefab timber assumption.",
  },
  prefab_modular_concrete: {
    min_floors: 1,
    max_floors: 12,
    default_floors: 4,
    floor_height_m: 3.2,
    label: "Modular Concrete Prefab",
    user_note:
      "Higher floor range for modular concrete prefab in this prototype.",
  },
};

export function getMethodConstraintKey(
  method: MethodKey,
  prefabSubMethod: PrefabSubMethod,
): MethodConstraintKey {
  if (method === "prefab") {
    return prefabSubMethod === "clt"
      ? "prefab_clt"
      : "prefab_modular_concrete";
  }

  return method;
}

export function getMethodFloorConstraint(
  method: MethodKey,
  prefabSubMethod: PrefabSubMethod,
): MethodFloorConstraint {
  return methodFloorConstraints[getMethodConstraintKey(method, prefabSubMethod)];
}
