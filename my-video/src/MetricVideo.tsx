import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  AbsoluteFill,
} from "remotion";
import React from "react";
import {
  methodContracts,
  mockBuildingZones,
  phaseLabels,
  PHASE_SEQUENCE,
  PREFAB_LIFECYCLE_STAGES,
  lifecycleLabels,
  type MethodKey,
  type PhaseKey,
  type LifecycleStageKey,
  type PrefabSubMethod,
} from "./mockMetricData";
import {
  calculatePhaseStageMetrics,
  calculateLifecycleStageMetrics,
  type ActiveGeometry,
} from "./calculateMockMetrics";
import { calculateTotalProjectMetrics } from "./calculateTotalProjectMetrics";

type BuildingZone = (typeof mockBuildingZones)[0];

// ── Timeline driver ──────────────────────────────────────────────────────────
// t=0-3:  idle (no method)     t=3-15: masonry (phases cycle)
// t=15-21: 3d_printed          t=21-40: prefab (lifecycle cycle)
function getSceneState(frame: number, fps: number) {
  const t = frame / fps;
  let method: MethodKey | null = null;
  let phase: PhaseKey = "foundation";
  let lifecycleStage: LifecycleStageKey = "A1-A3";
  const prefabSubMethod: PrefabSubMethod = "clt";
  let floors = 3;

  if (t < 3) {
    method = null;
    floors = 0;
  } else if (t < 15) {
    method = "masonry";
    floors = 3;
    if (t < 7) phase = "foundation";
    else if (t < 9) phase = "structure";
    else if (t < 11) phase = "roof";
    else if (t < 13) phase = "openings";
    else phase = "finishing";
  } else if (t < 21) {
    method = "3d_printed";
    floors = 4;
    phase = t < 19 ? "foundation" : "structure";
  } else {
    method = "prefab";
    floors = 5;
    if (t < 27) lifecycleStage = "A1-A3";
    else if (t < 29) lifecycleStage = "A4";
    else if (t < 31) lifecycleStage = "A5";
    else if (t < 33) lifecycleStage = "B";
    else lifecycleStage = "C";
  }
  return { method, phase, lifecycleStage, prefabSubMethod, floors };
}

// ── Accent helpers ───────────────────────────────────────────────────────────
const neutralAccent = "#c9b48d";
const neutralAccentSoft = "rgba(201,180,141,0.16)";
const neutralGlow = "rgba(201,180,141,0.36)";

function getAccent(method: MethodKey | null) {
  if (!method)
    return { accent: neutralAccent, soft: neutralAccentSoft, glow: neutralGlow };
  const c = methodContracts[method];
  return { accent: c.accent, soft: c.accentSoft, glow: c.glow };
}

// ── Geometry builder ─────────────────────────────────────────────────────────
function buildGeometry(floors: number): ActiveGeometry {
  const zones = mockBuildingZones;
  const fp = zones.reduce((s: number, z: BuildingZone) => s + z.area_m2, 0);
  const wa = zones.reduce((s: number, z: BuildingZone) => s + z.wall_area_m2, 0);
  const pm = zones.reduce((s: number, z: BuildingZone) => s + z.perimeter_m, 0);
  const fh = 3.2;
  const n = Math.max(floors, 1);
  return {
    footprint_area_m2: fp,
    base_wall_surface_m2: wa,
    total_selected_area_m2: fp * n,
    total_wall_surface_m2: wa * n,
    floor_count: n,
    floor_height_m: fh,
    building_height_m: n * fh,
    active_area_m2: fp * n,
    active_wall_area_m2: wa * n,
    active_perimeter_m: pm,
    active_zone_ids: zones.map((z: BuildingZone) => z.id),
    active_zone_labels: zones.map((z: BuildingZone) => z.label),
    isWholeBuilding: true,
  };
}

// ── Panel component ──────────────────────────────────────────────────────────
function Panel({
  x,
  y,
  w,
  h,
  accent,
  soft,
  children,
  style,
}: {
  x: number;
  y: number;
  w: number;
  h: number;
  accent: string;
  soft: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        borderRadius: 18,
        border: "1px solid rgba(255,255,255,0.08)",
        background: "rgba(14,18,24,0.84)",
        backdropFilter: "blur(10px)",
        boxShadow:
          "inset 0 0 0 1px rgba(255,255,255,0.02), 0 0 0 1px rgba(0,0,0,0.35), 0 12px 30px rgba(0,0,0,0.22)",
        overflow: "hidden",
        ...style,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: 18,
          border: "1px solid " + accent,
          opacity: 0.18,
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: 18,
          boxShadow: "0 0 0 1px " + soft,
          pointerEvents: "none",
        }}
      />
      {children}
    </div>
  );
}

// ── Panel header ─────────────────────────────────────────────────────────────
function PanelHeader({
  label,
  eyebrow,
}: {
  label: string;
  eyebrow?: string;
  accent: string;
}) {
  return (
    <div
      style={{
        padding: "18px 22px 10px",
        display: "flex",
        flexDirection: "column",
        gap: 4,
      }}
    >
      {eyebrow && (
        <div
          style={{
            color: "rgba(244,239,230,0.5)",
            fontSize: 10,
            letterSpacing: "0.16em",
            textTransform: "uppercase",
          }}
        >
          {eyebrow}
        </div>
      )}
      <div
        style={{
          fontSize: 20,
          fontWeight: 600,
          letterSpacing: "0.05em",
          textTransform: "uppercase",
          color: "#f4efe6",
        }}
      >
        {label}
      </div>
    </div>
  );
}

// ── Formatters ───────────────────────────────────────────────────────────────
function fmtCO2(v: number) {
  return v.toFixed(0) + " kg CO₂e";
}
function fmtEur(v: number) {
  return "€" + (v / 1000).toFixed(1) + "k";
}
function fmtDays(v: number) {
  return v.toFixed(0) + " days";
}
function fmtHrs(v: number) {
  return v.toFixed(0) + " hrs";
}

// ── Shared row style ─────────────────────────────────────────────────────────
const ROW: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  fontSize: 13,
  padding: "5px 0",
  borderBottom: "1px solid rgba(255,255,255,0.04)",
};

// ── Composition ──────────────────────────────────────────────────────────────
export const MetricVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const { method, phase, lifecycleStage, prefabSubMethod, floors } =
    getSceneState(frame, fps);
  const { accent, soft, glow } = getAccent(method);
  const geo = buildGeometry(floors);
  const contract = method ? methodContracts[method] : null;

  const fadeIn = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const fadeOut = interpolate(frame, [1140, 1200], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);

  // CalculatedMetricBundle fields: co2_total, cost_total, time_days, labor_hours
  const phaseMetrics =
    method && method !== "prefab"
      ? calculatePhaseStageMetrics(
          method as Exclude<MethodKey, "prefab">,
          phase,
          geo,
        )
      : null;

  const lifecycleRows =
    method === "prefab"
      ? PREFAB_LIFECYCLE_STAGES.map((s: LifecycleStageKey) =>
          calculateLifecycleStageMetrics(s, prefabSubMethod, geo),
        )
      : [];

  // TotalProjectMetrics fields: total_co2, total_cost, total_time_days, total_labor_hours
  const totalMetrics = method
    ? calculateTotalProjectMetrics({
        method,
        data_model: contract!.data_model,
        display_mode: contract!.display_mode,
        sub_method: prefabSubMethod,
        activeGeometry: geo,
      })
    : null;

  type LRow = {
    stage: LifecycleStageKey;
    co2_total: number;
    cost_total: number;
  };
  const activeLifecycleRow =
    method === "prefab"
      ? (lifecycleRows as LRow[]).find((r) => r.stage === lifecycleStage)
      : null;

  const methodLabel = method
    ? method === "3d_printed"
      ? "3D Printed"
      : method.charAt(0).toUpperCase() + method.slice(1)
    : "Select Method";

  const bg =
    "radial-gradient(circle at top left, rgba(255,255,255,0.05), transparent 28%), " +
    "linear-gradient(135deg,#10131b 0%,#0a0d13 50%,#07080d 100%)";

  return (
    <AbsoluteFill
      style={{
        opacity,
        background: bg,
        fontFamily: "Segoe UI, Trebuchet MS, sans-serif",
        color: "#f4efe6",
        overflow: "hidden",
      }}
    >
      <style>
        {":root { --accent: " +
          accent +
          "; --accent-soft: " +
          soft +
          "; --glow: " +
          glow +
          "; }"}
      </style>

      {/* ── Left Info Panel ──────────────────────────────────────────────── */}
      <Panel x={26} y={22} w={320} h={700} accent={accent} soft={soft}>
        <PanelHeader eyebrow="Active Method" label={methodLabel} accent={accent} />
        <div style={{ padding: "0 22px 20px" }}>
          <div
            style={{
              height: 2,
              background: accent,
              marginBottom: 20,
              borderRadius: 1,
              opacity: 0.7,
            }}
          />

          {method && (
            <div
              style={{
                display: "inline-block",
                background: soft,
                border: "1px solid " + accent,
                borderRadius: 8,
                padding: "4px 12px",
                fontSize: 12,
                color: accent,
                marginBottom: 16,
                letterSpacing: "0.08em",
              }}
            >
              {contract?.data_model === "lifecycle_based"
                ? "LIFECYCLE MODE"
                : "PHASE MODE"}
            </div>
          )}

          <div style={{ marginBottom: 20 }}>
            <div
              style={{
                fontSize: 10,
                color: "rgba(244,239,230,0.45)",
                letterSpacing: "0.14em",
                textTransform: "uppercase",
                marginBottom: 6,
              }}
            >
              Current Focus
            </div>
            <div style={{ fontSize: 22, fontWeight: 700, color: "#f4efe6" }}>
              {!method
                ? "—"
                : method === "prefab"
                  ? lifecycleLabels[lifecycleStage]
                  : phaseLabels[phase].replace(/^\d+\s+/, "")}
            </div>
          </div>

          <div style={{ marginBottom: 20 }}>
            <div
              style={{
                fontSize: 10,
                color: "rgba(244,239,230,0.45)",
                letterSpacing: "0.14em",
                textTransform: "uppercase",
                marginBottom: 8,
              }}
            >
              Building Scope
            </div>
            {(
              [
                ["Footprint", geo.footprint_area_m2.toFixed(0) + " m²"],
                ["Floors", String(floors)],
                ["GFA", geo.active_area_m2.toFixed(0) + " m²"],
                ["Height", geo.building_height_m.toFixed(1) + " m"],
                ["Perimeter", geo.active_perimeter_m.toFixed(0) + " m"],
              ] as [string, string][]
            ).map(([label, value]) => (
              <div key={label} style={ROW}>
                <span style={{ color: "rgba(244,239,230,0.55)" }}>{label}</span>
                <span style={{ color: "#f4efe6", fontVariantNumeric: "tabular-nums" }}>
                  {value}
                </span>
              </div>
            ))}
          </div>

          {phaseMetrics && (
            <div>
              <div
                style={{
                  fontSize: 10,
                  color: "rgba(244,239,230,0.45)",
                  letterSpacing: "0.14em",
                  textTransform: "uppercase",
                  marginBottom: 8,
                }}
              >
                Phase Metrics
              </div>
              {(
                [
                  ["CO₂", fmtCO2(phaseMetrics.co2_total)],
                  ["Cost", fmtEur(phaseMetrics.cost_total)],
                  ["Duration", fmtDays(phaseMetrics.time_days)],
                  ["Labour", fmtHrs(phaseMetrics.labor_hours)],
                ] as [string, string][]
              ).map(([label, value]) => (
                <div key={label} style={ROW}>
                  <span style={{ color: "rgba(244,239,230,0.55)" }}>{label}</span>
                  <span
                    style={{
                      color: accent,
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 600,
                    }}
                  >
                    {value}
                  </span>
                </div>
              ))}
            </div>
          )}

          {activeLifecycleRow && (
            <div>
              <div
                style={{
                  fontSize: 10,
                  color: "rgba(244,239,230,0.45)",
                  letterSpacing: "0.14em",
                  textTransform: "uppercase",
                  marginBottom: 8,
                }}
              >
                Stage Metrics
              </div>
              {(
                [
                  ["CO₂", fmtCO2(activeLifecycleRow.co2_total)],
                  ["Cost", fmtEur(activeLifecycleRow.cost_total)],
                ] as [string, string][]
              ).map(([label, value]) => (
                <div key={label} style={ROW}>
                  <span style={{ color: "rgba(244,239,230,0.55)" }}>{label}</span>
                  <span
                    style={{
                      color: accent,
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 600,
                    }}
                  >
                    {value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </Panel>

      {/* ── Top Phase Navigation ─────────────────────────────────────────── */}
      <Panel x={407} y={22} w={900} h={100} accent={accent} soft={soft}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            height: "100%",
            padding: "0 18px",
            gap: 8,
          }}
        >
          {(method === "prefab"
            ? PREFAB_LIFECYCLE_STAGES
            : PHASE_SEQUENCE
          ).map((key: string) => {
            const isActive =
              method === "prefab" ? key === lifecycleStage : key === phase;
            const label =
              method === "prefab"
                ? lifecycleLabels[key as LifecycleStageKey]
                : phaseLabels[key as PhaseKey];
            return (
              <div
                key={key}
                style={{
                  flex: 1,
                  textAlign: "center",
                  padding: "10px 8px",
                  borderRadius: 12,
                  background: isActive ? soft : "transparent",
                  border: "1px solid " + (isActive ? accent : "rgba(255,255,255,0.06)"),
                  fontSize: 12,
                  letterSpacing: "0.06em",
                  color: isActive ? accent : "rgba(244,239,230,0.55)",
                  fontWeight: isActive ? 700 : 400,
                  boxShadow: isActive ? "0 0 12px " + glow : "none",
                }}
              >
                {label}
              </div>
            );
          })}
        </div>
      </Panel>

      {/* ── Main Plan Panel ──────────────────────────────────────────────── */}
      <Panel x={368} y={162} w={978} h={560} accent={accent} soft={soft}>
        <PanelHeader
          eyebrow="Building Footprint"
          label={method === "prefab" ? "Lifecycle View" : "Plan Simulation"}
          accent={accent}
        />
        <div
          style={{
            position: "relative",
            margin: "0 22px",
            height: 440,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <svg
            viewBox="0 0 978 480"
            style={{ width: "100%", height: "100%", opacity: method ? 1 : 0.4 }}
          >
            {mockBuildingZones.map((zone: BuildingZone) => (
              <rect
                key={zone.id}
                x={zone.shape.x}
                y={zone.shape.y}
                width={zone.shape.w}
                height={zone.shape.h}
                rx={zone.shape.rx ?? 12}
                fill={method ? soft : "rgba(255,255,255,0.03)"}
                stroke={method ? accent : "rgba(255,255,255,0.12)"}
                strokeWidth={1.5}
                filter={method ? "drop-shadow(0 0 8px " + glow + ")" : "none"}
              />
            ))}
            {mockBuildingZones.map((zone: BuildingZone) => (
              <text
                key={zone.id + "_lbl"}
                x={zone.shape.x + zone.shape.w / 2}
                y={zone.shape.y + zone.shape.h / 2 + 5}
                textAnchor="middle"
                fontSize={12}
                fill={
                  method
                    ? "rgba(244,239,230,0.7)"
                    : "rgba(244,239,230,0.3)"
                }
                fontFamily="Segoe UI, sans-serif"
              >
                {zone.label}
              </text>
            ))}
          </svg>
        </div>
      </Panel>

      {/* ── Right Totals Panel ───────────────────────────────────────────── */}
      <Panel x={1365} y={22} w={530} h={438} accent={accent} soft={soft}>
        <PanelHeader
          eyebrow="Project Totals"
          label={method ? methodLabel + " Summary" : "Awaiting Method"}
          accent={accent}
        />
        <div style={{ padding: "0 22px 20px" }}>
          {totalMetrics
            ? (
                [
                  ["Total CO₂", fmtCO2(totalMetrics.total_co2)],
                  ["Total Cost", fmtEur(totalMetrics.total_cost)],
                  ["Duration", fmtDays(totalMetrics.total_time_days)],
                  ["Labour", fmtHrs(totalMetrics.total_labor_hours)],
                ] as [string, string][]
              ).map(([label, value]) => (
                <div key={label} style={{ marginBottom: 18 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "baseline",
                      marginBottom: 4,
                    }}
                  >
                    <span
                      style={{
                        fontSize: 11,
                        color: "rgba(244,239,230,0.5)",
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                      }}
                    >
                      {label}
                    </span>
                    <span
                      style={{
                        fontSize: 24,
                        fontWeight: 700,
                        color: accent,
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {value}
                    </span>
                  </div>
                  <div
                    style={{
                      height: 3,
                      background: "rgba(255,255,255,0.06)",
                      borderRadius: 2,
                    }}
                  >
                    <div
                      style={{
                        height: "100%",
                        width: "72%",
                        background: accent,
                        borderRadius: 2,
                        opacity: 0.7,
                      }}
                    />
                  </div>
                </div>
              ))
            : (
              <div
                style={{
                  color: "rgba(244,239,230,0.3)",
                  fontSize: 14,
                  marginTop: 20,
                  textAlign: "center",
                }}
              >
                Select a method to see project totals
              </div>
            )}
        </div>
      </Panel>

      {/* ── Right Cost Chart ─────────────────────────────────────────────── */}
      <Panel x={1365} y={482} w={530} h={240} accent={accent} soft={soft}>
        <PanelHeader eyebrow="Cost Breakdown" label="By Phase" accent={accent} />
        <div
          style={{
            padding: "0 22px 16px",
            display: "flex",
            alignItems: "flex-end",
            gap: 10,
            height: 140,
          }}
        >
          {method && method !== "prefab"
            ? PHASE_SEQUENCE.map((p: PhaseKey) => {
                const m = calculatePhaseStageMetrics(
                  method as Exclude<MethodKey, "prefab">,
                  p,
                  geo,
                );
                const cost = m.cost_total;
                const barH = Math.max(8, (cost / 50000) * 100);
                const isActive = p === phase;
                return (
                  <div
                    key={p}
                    style={{
                      flex: 1,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      gap: 4,
                    }}
                  >
                    <div
                      style={{
                        fontSize: 9,
                        color: isActive ? accent : "rgba(244,239,230,0.35)",
                        textAlign: "center",
                      }}
                    >
                      {fmtEur(cost)}
                    </div>
                    <div
                      style={{
                        width: "100%",
                        height: barH,
                        background: isActive ? accent : soft,
                        borderRadius: "4px 4px 0 0",
                        border: isActive ? "1px solid " + accent : "none",
                      }}
                    />
                    <div
                      style={{
                        fontSize: 9,
                        color: isActive ? accent : "rgba(244,239,230,0.4)",
                        textAlign: "center",
                      }}
                    >
                      {phaseLabels[p].replace(/^\d+\s+/, "").slice(0, 6)}
                    </div>
                  </div>
                );
              })
            : method === "prefab"
              ? PREFAB_LIFECYCLE_STAGES.map((s: LifecycleStageKey) => {
                  type CostRow = { stage: LifecycleStageKey; cost_total: number };
                  const row = (lifecycleRows as CostRow[]).find(
                    (r) => r.stage === s,
                  );
                  const cost = row?.cost_total ?? 0;
                  const barH = Math.max(8, (cost / 200000) * 100);
                  const isActive = s === lifecycleStage;
                  return (
                    <div
                      key={s}
                      style={{
                        flex: 1,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        gap: 4,
                      }}
                    >
                      <div
                        style={{
                          fontSize: 9,
                          color: isActive ? accent : "rgba(244,239,230,0.35)",
                          textAlign: "center",
                        }}
                      >
                        {fmtEur(cost)}
                      </div>
                      <div
                        style={{
                          width: "100%",
                          height: barH,
                          background: isActive ? accent : soft,
                          borderRadius: "4px 4px 0 0",
                        }}
                      />
                      <div
                        style={{
                          fontSize: 9,
                          color: isActive ? accent : "rgba(244,239,230,0.4)",
                          textAlign: "center",
                        }}
                      >
                        {s}
                      </div>
                    </div>
                  );
                })
              : (
                <div
                  style={{
                    color: "rgba(244,239,230,0.25)",
                    fontSize: 13,
                    margin: "auto",
                  }}
                >
                  Awaiting method
                </div>
              )}
        </div>
      </Panel>

      {/* ── Method Selection Panel ───────────────────────────────────────── */}
      <Panel x={506} y={739} w={840} h={260} accent={accent} soft={soft}>
        <PanelHeader
          eyebrow="Construction Method"
          label="Select System"
          accent={accent}
        />
        <div style={{ padding: "0 22px 20px", display: "flex", gap: 16 }}>
          {(["masonry", "3d_printed", "prefab"] as MethodKey[]).map(
            (key: MethodKey) => {
              const c = methodContracts[key];
              const isActive = key === method;
              return (
                <div
                  key={key}
                  style={{
                    flex: 1,
                    borderRadius: 14,
                    border:
                      "2px solid " +
                      (isActive ? c.accent : "rgba(255,255,255,0.07)"),
                    background: isActive
                      ? c.accentSoft
                      : "rgba(255,255,255,0.02)",
                    padding: "20px 16px",
                    boxShadow: isActive ? "0 0 20px " + c.glow : "none",
                  }}
                >
                  <div
                    style={{
                      fontSize: 16,
                      fontWeight: 700,
                      color: isActive ? c.accent : "#f4efe6",
                      marginBottom: 8,
                      letterSpacing: "0.05em",
                    }}
                  >
                    {c.label}
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      color: "rgba(244,239,230,0.5)",
                      marginBottom: 12,
                      lineHeight: 1.5,
                    }}
                  >
                    {key === "prefab"
                      ? "Lifecycle-based dataset"
                      : "Phase-based dataset"}
                  </div>
                  <div
                    style={{
                      height: 3,
                      background: isActive
                        ? c.accent
                        : "rgba(255,255,255,0.08)",
                      borderRadius: 2,
                      marginBottom: 8,
                    }}
                  />
                  <div
                    style={{
                      fontSize: 10,
                      color: isActive
                        ? c.accent
                        : "rgba(244,239,230,0.35)",
                      letterSpacing: "0.1em",
                      textTransform: "uppercase",
                    }}
                  >
                    {isActive ? "● Active" : "○ Select"}
                  </div>
                </div>
              );
            },
          )}
        </div>
      </Panel>

      {/* ── Left Assembly Sequence ───────────────────────────────────────── */}
      <Panel x={26} y={739} w={460} h={260} accent={accent} soft={soft}>
        <PanelHeader eyebrow="Assembly" label="Sequence Notes" accent={accent} />
        <div style={{ padding: "0 22px 16px" }}>
          {method === "masonry" ||
          method === "3d_printed" ||
          method === "prefab"
            ? (method === "prefab"
                ? [
                    "Lifecycle-only dataset",
                    "Factory → Transport → Site",
                    "Switch CLT / modular concrete",
                  ]
                : method === "masonry"
                  ? [
                      "Layered brick assembly",
                      "Structure and finishing dominate",
                      "Good for low- to mid-rise",
                    ]
                  : [
                      "Foundation and roof conventional",
                      "Structure: printed shell proxy",
                      "Warnings preserve proxy feel",
                    ]
              ).map((note: string, i: number) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    gap: 10,
                    marginBottom: 10,
                    fontSize: 13,
                    color: "rgba(244,239,230,0.7)",
                    alignItems: "flex-start",
                  }}
                >
                  <span
                    style={{ color: accent, fontSize: 10, marginTop: 2 }}
                  >
                    {"▸"}
                  </span>
                  {note}
                </div>
              ))
            : (
              <div
                style={{
                  color: "rgba(244,239,230,0.3)",
                  fontSize: 13,
                  marginTop: 8,
                }}
              >
                Choose a method to unlock sequence.
              </div>
            )}
        </div>
      </Panel>

      {/* ── Right Phase Preview ──────────────────────────────────────────── */}
      <Panel x={1365} y={739} w={530} h={260} accent={accent} soft={soft}>
        <PanelHeader
          eyebrow="Phase Checklist"
          label={
            method === "prefab" ? "Lifecycle Stages" : "Construction Phases"
          }
          accent={accent}
        />
        <div style={{ padding: "0 22px 16px" }}>
          {(method === "prefab"
            ? PREFAB_LIFECYCLE_STAGES
            : PHASE_SEQUENCE
          ).map((key: string) => {
            const isActive =
              method === "prefab" ? key === lifecycleStage : key === phase;
            const label =
              method === "prefab"
                ? lifecycleLabels[key as LifecycleStageKey]
                : phaseLabels[key as PhaseKey];
            return (
              <div
                key={key}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  marginBottom: 9,
                  opacity: isActive ? 1 : 0.45,
                }}
              >
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: isActive
                      ? accent
                      : "rgba(255,255,255,0.2)",
                    flexShrink: 0,
                    boxShadow: isActive ? "0 0 6px " + glow : "none",
                  }}
                />
                <span
                  style={{
                    fontSize: 13,
                    color: isActive
                      ? "#f4efe6"
                      : "rgba(244,239,230,0.6)",
                    fontWeight: isActive ? 600 : 400,
                  }}
                >
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      </Panel>

      {/* ── Bottom Status Bar ────────────────────────────────────────────── */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 1030,
          width: 1920,
          height: 50,
          background: "rgba(8,10,14,0.92)",
          borderTop: "1px solid rgba(255,255,255,0.05)",
          display: "flex",
          alignItems: "center",
          padding: "0 28px",
          gap: 32,
          fontSize: 11,
          letterSpacing: "0.1em",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#22cc66",
            }}
          />
          <span
            style={{
              color: "rgba(244,239,230,0.5)",
              textTransform: "uppercase",
            }}
          >
            Vision Live
          </span>
        </div>
        <span style={{ color: "rgba(255,255,255,0.15)" }}>|</span>
        <span
          style={{
            color: "rgba(244,239,230,0.45)",
            textTransform: "uppercase",
          }}
        >
          {"Method: "}
          <span style={{ color: accent }}>{methodLabel}</span>
        </span>
        <span style={{ color: "rgba(255,255,255,0.15)" }}>|</span>
        <span
          style={{
            color: "rgba(244,239,230,0.45)",
            textTransform: "uppercase",
          }}
        >
          {"GFA: "}
          <span style={{ color: "#f4efe6" }}>
            {geo.active_area_m2.toFixed(0)} m{"²"}
          </span>
        </span>
        <span style={{ color: "rgba(255,255,255,0.15)" }}>|</span>
        <span
          style={{
            color: "rgba(244,239,230,0.45)",
            textTransform: "uppercase",
          }}
        >
          {"Floors: "}
          <span style={{ color: "#f4efe6" }}>{floors}</span>
        </span>
        <span style={{ flex: 1 }} />
        <span
          style={{
            color: "rgba(244,239,230,0.3)",
            textTransform: "uppercase",
          }}
        >
          Hardware III {"·"} LCA Comparison {"·"} IAAC 2025{"–26"}
        </span>
      </div>
    </AbsoluteFill>
  );
};
