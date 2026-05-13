/**
 * HardwareVideo.tsx
 * TouchDesigner-accurate simulation of the Hardware III LCA installation.
 * 9-panel layout at 1920×1080 (TD panels at 1280×720, scaled ×1.5).
 * Self-contained — no imports from the Hardware repo prototype.
 */

import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";

// ---------------------------------------------------------------------------
// Constants & colour palette
// ---------------------------------------------------------------------------

const S = 1.5; // scale factor from TD 1280×720 → 1920×1080

// Background / panel colours
const C_BG = "#0a0b0d";
const C_PANEL_BG = "rgba(20,20,26,1)"; // ~rgb(8%,8%,10%)
const C_PANEL_BORDER = "rgba(64,64,71,1)"; // ~rgba(25%,25%,28%)
const C_TEXT_PRIMARY = "#e8e8ec";
const C_TEXT_DIM = "#6b6b78";
const C_TEXT_LABEL = "#9090a0";

// Method colours (from methods_db.json)
const METHODS = {
  NONE: { color: "rgb(102,102,102)", label: "NONE" },
  MASONRY: {
    color: "rgb(217,115,38)",
    label: "MASONRY",
    co2: "205–490 kgCO₂e/m²",
    cost: "950–1350 EUR/m²",
    labor: "22–34 h/m²",
    time: "14–20 weeks",
    co2Mid: 348,
    costMid: 1150,
    laborMid: 28,
  },
  "3D PRINTED": {
    color: "rgb(46,158,217)",
    label: "3D PRINTED",
    co2: "58–147 kgCO₂e/m²",
    cost: "1000–1500 EUR/m²",
    labor: "8–16 h/m²",
    time: "6–10 weeks",
    co2Mid: 103,
    costMid: 1250,
    laborMid: 12,
  },
  PREFAB: {
    color: "rgb(64,184,115)",
    label: "PREFAB",
    co2: "130–350 kgCO₂e/m²",
    cost: "1100–1600 EUR/m²",
    labor: "12–20 h/m²",
    time: "8–12 weeks",
    co2Mid: 240,
    costMid: 1350,
    laborMid: 16,
  },
} as const;

type MethodKey = keyof typeof METHODS;

// Construction phases
const PHASES = ["FOUNDATION", "STRUCTURE", "ROOF", "OPENINGS", "FINISHING"] as const;

// ---------------------------------------------------------------------------
// Panel layout (TD 1280×720 coords × 1.5)
// ---------------------------------------------------------------------------
interface PanelDef {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

const PANELS: PanelDef[] = [
  { id: "top_phase_navigation",  x: 271, y: 15,  w: 600, h: 67  },
  { id: "left_info",             x: 17,  y: 15,  w: 213, h: 467 },
  { id: "left_assembly_sequence",x: 17,  y: 493, w: 307, h: 173 },
  { id: "main_plan_simulation",  x: 245, y: 108, w: 652, h: 373 },
  { id: "method_selection",      x: 337, y: 493, w: 560, h: 173 },
  { id: "right_comparison",      x: 910, y: 15,  w: 353, h: 292 },
  { id: "right_cost_chart",      x: 910, y: 321, w: 353, h: 160 },
  { id: "right_phase_preview",   x: 910, y: 493, w: 353, h: 173 },
  { id: "bar_bottom_status",     x: 0,   y: 687, w: 1280,h: 33  },
].map((p) => ({
  ...p,
  x: p.x * S,
  y: p.y * S,
  w: p.w * S,
  h: p.h * S,
}));

function panel(id: string): PanelDef {
  return PANELS.find((p) => p.id === id)!;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function hexToRgba(color: string, alpha: number): string {
  // handles "rgb(...)" format
  if (color.startsWith("rgb(")) {
    const inner = color.slice(4, -1);
    return `rgba(${inner},${alpha})`;
  }
  return color;
}

// ---------------------------------------------------------------------------
// Scene timing (frames @ 30fps)
// ---------------------------------------------------------------------------
const T = {
  scene1End: 3 * 30,        // 90
  scene2End: 6 * 30,        // 180
  scene3End: 12 * 30,       // 360
  scene4End: 22 * 30,       // 660
  scene5End: 28 * 30,       // 840
  scene6End: 33 * 30,       // 990
  scene7End: 38 * 30,       // 1140
  total: 40 * 30,           // 1200
};

// ---------------------------------------------------------------------------
// Footprint polygon (6 points, normalised 0–1 relative to main panel)
// ---------------------------------------------------------------------------
const FOOTPRINT_POINTS_NORM = [
  { x: 0.18, y: 0.22 },
  { x: 0.62, y: 0.18 },
  { x: 0.82, y: 0.38 },
  { x: 0.78, y: 0.72 },
  { x: 0.35, y: 0.78 },
  { x: 0.15, y: 0.55 },
];

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

/** A single dark panel rectangle */
const Panel: React.FC<{
  def: PanelDef;
  glowColor?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ def, glowColor, children, style }) => (
  <div
    style={{
      position: "absolute",
      left: def.x,
      top: def.y,
      width: def.w,
      height: def.h,
      background: C_PANEL_BG,
      border: `1px solid ${C_PANEL_BORDER}`,
      boxSizing: "border-box",
      boxShadow: glowColor
        ? `0 0 18px 2px ${hexToRgba(glowColor, 0.25)}, inset 0 0 12px 0 ${hexToRgba(glowColor, 0.06)}`
        : "none",
      overflow: "hidden",
      ...style,
    }}
  >
    {children}
  </div>
);

/** Uppercase label */
const Label: React.FC<{
  text: string;
  style?: React.CSSProperties;
}> = ({ text, style }) => (
  <div
    style={{
      fontFamily: "monospace",
      fontSize: 10 * S,
      letterSpacing: 2,
      color: C_TEXT_LABEL,
      textTransform: "uppercase",
      ...style,
    }}
  >
    {text}
  </div>
);

/** Top phase navigation panel */
const PhaseNavPanel: React.FC<{
  activePhase: number;
  methodColor: string;
  visible: boolean;
}> = ({ activePhase, methodColor, visible }) => {
  const def = panel("top_phase_navigation");

  return (
    <Panel def={def} glowColor={visible ? methodColor : undefined}>
      <div style={{ display: "flex", height: "100%", alignItems: "stretch" }}>
        {PHASES.map((phase, i) => {
          const isActive = visible && i === activePhase;
          return (
            <div
              key={phase}
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: isActive ? hexToRgba(methodColor, 0.2) : "transparent",
                borderRight: i < PHASES.length - 1 ? `1px solid ${C_PANEL_BORDER}` : "none",
                borderBottom: isActive ? `2px solid ${methodColor}` : "2px solid transparent",
                transition: "background 0.3s",
              }}
            >
              <span
                style={{
                  fontFamily: "monospace",
                  fontSize: 9 * S,
                  letterSpacing: 1.5,
                  color: isActive ? methodColor : C_TEXT_DIM,
                  textTransform: "uppercase",
                }}
              >
                {phase}
              </span>
            </div>
          );
        })}
      </div>
    </Panel>
  );
};

/** Left info panel */
const LeftInfoPanel: React.FC<{
  methodKey: MethodKey;
  methodColor: string;
  visionLive: boolean;
}> = ({ methodKey, methodColor, visionLive }) => {
  const def = panel("left_info");
  const method = METHODS[methodKey];

  return (
    <Panel def={def} glowColor={methodKey !== "NONE" ? methodColor : undefined}>
      <div style={{ padding: 10 * S, display: "flex", flexDirection: "column", gap: 8 * S }}>
        <Label text="CONSTRUCTION METHOD" />
        <div
          style={{
            fontFamily: "monospace",
            fontSize: 14 * S,
            color: methodKey !== "NONE" ? methodColor : C_TEXT_DIM,
            fontWeight: "bold",
            letterSpacing: 2,
            marginTop: 4 * S,
          }}
        >
          {method.label}
        </div>

        {methodKey !== "NONE" && "co2" in method && (
          <>
            <div style={{ borderTop: `1px solid ${C_PANEL_BORDER}`, marginTop: 6 * S, paddingTop: 8 * S }}>
              <Label text="CO₂ EMBODIED" />
              <div style={{ fontFamily: "monospace", fontSize: 10 * S, color: C_TEXT_PRIMARY, marginTop: 2 * S }}>
                {method.co2}
              </div>
            </div>
            <div>
              <Label text="COST RANGE" />
              <div style={{ fontFamily: "monospace", fontSize: 10 * S, color: C_TEXT_PRIMARY, marginTop: 2 * S }}>
                {method.cost}
              </div>
            </div>
            <div>
              <Label text="LABOR" />
              <div style={{ fontFamily: "monospace", fontSize: 10 * S, color: C_TEXT_PRIMARY, marginTop: 2 * S }}>
                {method.labor}
              </div>
            </div>
            <div>
              <Label text="BUILD TIME" />
              <div style={{ fontFamily: "monospace", fontSize: 10 * S, color: C_TEXT_PRIMARY, marginTop: 2 * S }}>
                {method.time}
              </div>
            </div>
          </>
        )}

        {methodKey === "NONE" && (
          <div
            style={{
              fontFamily: "monospace",
              fontSize: 9 * S,
              color: C_TEXT_DIM,
              marginTop: 12 * S,
              lineHeight: 1.6,
            }}
          >
            AWAITING
            <br />
            METHOD
            <br />
            SELECTION
          </div>
        )}

        <div
          style={{
            marginTop: "auto",
            borderTop: `1px solid ${C_PANEL_BORDER}`,
            paddingTop: 8 * S,
          }}
        >
          <Label text="VISION" />
          <div style={{ display: "flex", alignItems: "center", gap: 5 * S, marginTop: 4 * S }}>
            <div
              style={{
                width: 6 * S,
                height: 6 * S,
                borderRadius: "50%",
                background: visionLive ? "#22ff66" : "#ff3333",
                boxShadow: visionLive ? "0 0 8px #22ff66" : "0 0 8px #ff3333",
              }}
            />
            <span
              style={{
                fontFamily: "monospace",
                fontSize: 8 * S,
                color: visionLive ? "#22ff66" : "#ff3333",
              }}
            >
              {visionLive ? "LIVE" : "OFFLINE"}
            </span>
          </div>
        </div>
      </div>
    </Panel>
  );
};

/** Left assembly sequence panel */
const AssemblySequencePanel: React.FC<{
  methodKey: MethodKey;
  methodColor: string;
  activePhase: number;
}> = ({ methodKey, methodColor, activePhase }) => {
  const def = panel("left_assembly_sequence");
  const active = methodKey !== "NONE";

  return (
    <Panel def={def} glowColor={active ? methodColor : undefined}>
      <div style={{ padding: 8 * S }}>
        <Label text="ASSEMBLY SEQUENCE" />
        <div style={{ marginTop: 8 * S, display: "flex", flexDirection: "column", gap: 4 * S }}>
          {PHASES.map((phase, i) => {
            const isDone = active && i < activePhase;
            const isCurrent = active && i === activePhase;
            return (
              <div
                key={phase}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6 * S,
                  opacity: active ? 1 : 0.3,
                }}
              >
                <div
                  style={{
                    width: 8 * S,
                    height: 8 * S,
                    borderRadius: "50%",
                    background: isDone
                      ? methodColor
                      : isCurrent
                      ? methodColor
                      : "transparent",
                    border: `1px solid ${active ? methodColor : C_PANEL_BORDER}`,
                    boxShadow: isCurrent ? `0 0 6px ${methodColor}` : "none",
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontFamily: "monospace",
                    fontSize: 8 * S,
                    color: isCurrent ? methodColor : isDone ? C_TEXT_PRIMARY : C_TEXT_DIM,
                    letterSpacing: 1,
                  }}
                >
                  {String(i + 1).padStart(2, "0")} {phase}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </Panel>
  );
};

/** Main plan simulation panel — footprint polygon */
const MainPlanPanel: React.FC<{
  methodKey: MethodKey;
  methodColor: string;
  pointsRevealed: number; // 0–6
  polygonProgress: number; // 0–1 for outline drawing
}> = ({ methodKey, methodColor, pointsRevealed, polygonProgress }) => {
  const def = panel("main_plan_simulation");
  const active = methodKey !== "NONE";

  // Map normalised points to panel pixel coords
  const pts = FOOTPRINT_POINTS_NORM.map((p) => ({
    x: p.x * def.w,
    y: p.y * def.h,
  }));

  const revealed = pts.slice(0, pointsRevealed);

  // Build SVG polygon path
  const polyPath =
    revealed.length >= 2
      ? "M " +
        revealed.map((p) => `${p.x},${p.y}`).join(" L ") +
        (polygonProgress >= 1 ? " Z" : "")
      : "";

  return (
    <Panel def={def} glowColor={active ? methodColor : undefined}>
      {/* Grid lines */}
      <svg
        style={{ position: "absolute", inset: 0, opacity: 0.07 }}
        width={def.w}
        height={def.h}
      >
        {Array.from({ length: 10 }, (_, i) => (
          <line
            key={`v${i}`}
            x1={(i + 1) * (def.w / 11)}
            y1={0}
            x2={(i + 1) * (def.w / 11)}
            y2={def.h}
            stroke={C_TEXT_LABEL}
            strokeWidth={0.5}
          />
        ))}
        {Array.from({ length: 6 }, (_, i) => (
          <line
            key={`h${i}`}
            x1={0}
            y1={(i + 1) * (def.h / 7)}
            x2={def.w}
            y2={(i + 1) * (def.h / 7)}
            stroke={C_TEXT_LABEL}
            strokeWidth={0.5}
          />
        ))}
      </svg>

      {/* Label */}
      <div
        style={{
          position: "absolute",
          top: 8 * S,
          left: 10 * S,
          fontFamily: "monospace",
          fontSize: 9 * S,
          letterSpacing: 2,
          color: C_TEXT_LABEL,
          textTransform: "uppercase",
        }}
      >
        PLAN VIEW — BUILDING FOOTPRINT
      </div>

      {/* Polygon SVG */}
      {revealed.length >= 2 && (
        <svg
          style={{ position: "absolute", inset: 0 }}
          width={def.w}
          height={def.h}
        >
          {/* Fill */}
          {polygonProgress >= 1 && (
            <polygon
              points={pts.map((p) => `${p.x},${p.y}`).join(" ")}
              fill={hexToRgba(methodColor, 0.18)}
              stroke="none"
            />
          )}
          {/* Outline */}
          <path
            d={polyPath}
            fill="none"
            stroke={methodColor}
            strokeWidth={1.5 * S}
            strokeOpacity={0.9}
            strokeLinejoin="round"
          />
        </svg>
      )}

      {/* Puck circles at each revealed point */}
      <svg
        style={{ position: "absolute", inset: 0 }}
        width={def.w}
        height={def.h}
      >
        {revealed.map((p, i) => (
          <g key={i}>
            <circle
              cx={p.x}
              cy={p.y}
              r={8 * S}
              fill="transparent"
              stroke={methodColor}
              strokeWidth={1.5 * S}
              opacity={0.9}
            />
            <circle
              cx={p.x}
              cy={p.y}
              r={3 * S}
              fill={methodColor}
              opacity={0.8}
            />
          </g>
        ))}
      </svg>

      {/* Empty state */}
      {!active && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 8 * S,
          }}
        >
          <div
            style={{
              fontFamily: "monospace",
              fontSize: 9 * S,
              color: C_TEXT_DIM,
              letterSpacing: 2,
            }}
          >
            AWAITING FOOTPRINT INPUT
          </div>
        </div>
      )}
    </Panel>
  );
};

/** Method selection panel */
const MethodSelectionPanel: React.FC<{
  methodKey: MethodKey;
  methodColor: string;
}> = ({ methodKey, methodColor }) => {
  const def = panel("method_selection");
  const method = METHODS[methodKey];

  return (
    <Panel def={def} glowColor={methodKey !== "NONE" ? methodColor : undefined}>
      <div style={{ padding: 10 * S, display: "flex", gap: 12 * S, height: "100%" }}>
        {/* Color block */}
        <div
          style={{
            width: 52 * S,
            flexShrink: 0,
            background: methodKey !== "NONE" ? methodColor : C_TEXT_DIM,
            borderRadius: 3,
            transition: "background 0.5s",
          }}
        />
        {/* Info */}
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "space-between", flex: 1 }}>
          <div>
            <Label text="ACTIVE METHOD" />
            <div
              style={{
                fontFamily: "monospace",
                fontSize: 15 * S,
                color: methodKey !== "NONE" ? methodColor : C_TEXT_DIM,
                fontWeight: "bold",
                letterSpacing: 3,
                marginTop: 4 * S,
              }}
            >
              {method.label}
            </div>
          </div>
          {methodKey !== "NONE" && (
            <div style={{ display: "flex", gap: 16 * S }}>
              {(["NONE", "MASONRY", "3D PRINTED", "PREFAB"] as MethodKey[])
                .filter((k) => k !== "NONE")
                .map((k) => (
                  <div
                    key={k}
                    style={{
                      width: 10 * S,
                      height: 10 * S,
                      borderRadius: "50%",
                      background: METHODS[k].color,
                      border: k === methodKey ? `2px solid white` : "2px solid transparent",
                      opacity: k === methodKey ? 1 : 0.4,
                    }}
                  />
                ))}
            </div>
          )}
        </div>
      </div>
    </Panel>
  );
};

/** Right comparison panel */
const RightComparisonPanel: React.FC<{
  methodKey: MethodKey;
  methodColor: string;
}> = ({ methodKey, methodColor }) => {
  const def = panel("right_comparison");
  const active = methodKey !== "NONE";
  const method = active ? (METHODS[methodKey] as typeof METHODS["MASONRY"]) : null;

  // Simple bar chart data (co2 normalised vs max 490)
  const maxCo2 = 490;
  const co2Pct = method ? method.co2Mid / maxCo2 : 0;

  return (
    <Panel def={def} glowColor={active ? methodColor : undefined}>
      <div style={{ padding: 10 * S }}>
        <Label text="LCA COMPARISON" />

        {active && method ? (
          <div style={{ marginTop: 10 * S, display: "flex", flexDirection: "column", gap: 10 * S }}>
            {/* CO2 bar */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 * S }}>
                <Label text="CO₂ EMBODIED" />
                <span style={{ fontFamily: "monospace", fontSize: 9 * S, color: methodColor }}>
                  {method.co2Mid} kgCO₂e/m²
                </span>
              </div>
              <div
                style={{
                  height: 6 * S,
                  background: "rgba(255,255,255,0.05)",
                  borderRadius: 2,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${co2Pct * 100}%`,
                    background: methodColor,
                    borderRadius: 2,
                  }}
                />
              </div>
            </div>

            {/* Cost */}
            <div>
              <Label text="UNIT COST" />
              <div
                style={{
                  fontFamily: "monospace",
                  fontSize: 13 * S,
                  color: C_TEXT_PRIMARY,
                  marginTop: 3 * S,
                  letterSpacing: 1,
                }}
              >
                {method.costMid}{" "}
                <span style={{ fontSize: 9 * S, color: C_TEXT_LABEL }}>EUR/m²</span>
              </div>
            </div>

            {/* Labor */}
            <div>
              <Label text="LABOR INTENSITY" />
              <div
                style={{
                  fontFamily: "monospace",
                  fontSize: 13 * S,
                  color: C_TEXT_PRIMARY,
                  marginTop: 3 * S,
                }}
              >
                {method.laborMid}{" "}
                <span style={{ fontSize: 9 * S, color: C_TEXT_LABEL }}>h/m²</span>
              </div>
            </div>

            {/* Build time */}
            <div>
              <Label text="BUILD TIME" />
              <div style={{ fontFamily: "monospace", fontSize: 9 * S, color: C_TEXT_PRIMARY, marginTop: 2 * S }}>
                {method.time}
              </div>
            </div>
          </div>
        ) : (
          <div
            style={{
              marginTop: 20 * S,
              fontFamily: "monospace",
              fontSize: 9 * S,
              color: C_TEXT_DIM,
              letterSpacing: 2,
            }}
          >
            NO METHOD SELECTED
          </div>
        )}
      </div>
    </Panel>
  );
};

/** Right cost chart panel — simple vertical bars */
const RightCostChartPanel: React.FC<{
  methodKey: MethodKey;
  methodColor: string;
}> = ({ methodKey, methodColor }) => {
  const def = panel("right_cost_chart");
  const active = methodKey !== "NONE";

  const methods = (["MASONRY", "3D PRINTED", "PREFAB"] as MethodKey[]).map((k) => ({
    key: k,
    color: METHODS[k].color,
    val: (METHODS[k] as typeof METHODS["MASONRY"]).co2Mid,
  }));
  const maxVal = 500;

  return (
    <Panel def={def} glowColor={active ? methodColor : undefined}>
      <div style={{ padding: 8 * S, height: "100%", boxSizing: "border-box" }}>
        <Label text="CO₂ COMPARISON" />
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            gap: 8 * S,
            height: `calc(100% - ${20 * S}px)`,
            marginTop: 8 * S,
          }}
        >
          {methods.map((m) => {
            const barH = active ? (m.val / maxVal) * 100 : 10;
            const isActive = m.key === methodKey;
            return (
              <div
                key={m.key}
                style={{
                  flex: 1,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "flex-end",
                  height: "100%",
                  gap: 4 * S,
                }}
              >
                <span
                  style={{
                    fontFamily: "monospace",
                    fontSize: 7 * S,
                    color: isActive ? m.color : C_TEXT_DIM,
                    textAlign: "center",
                  }}
                >
                  {active ? m.val : "--"}
                </span>
                <div
                  style={{
                    width: "70%",
                    height: `${barH}%`,
                    background: m.color,
                    opacity: isActive ? 1 : 0.3,
                    borderRadius: "2px 2px 0 0",
                    transition: "height 0.5s, opacity 0.5s",
                    minHeight: 2,
                  }}
                />
                <span
                  style={{
                    fontFamily: "monospace",
                    fontSize: 6 * S,
                    color: C_TEXT_DIM,
                    textAlign: "center",
                    letterSpacing: 0.5,
                  }}
                >
                  {m.key === "3D PRINTED" ? "3DP" : m.key.slice(0, 3)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </Panel>
  );
};

/** Right phase preview panel */
const RightPhasePreviewPanel: React.FC<{
  methodKey: MethodKey;
  methodColor: string;
  activePhase: number;
}> = ({ methodKey, methodColor, activePhase }) => {
  const def = panel("right_phase_preview");
  const active = methodKey !== "NONE";

  return (
    <Panel def={def} glowColor={active ? methodColor : undefined}>
      <div style={{ padding: 10 * S }}>
        <Label text="PHASE PREVIEW" />
        {active ? (
          <div style={{ marginTop: 8 * S }}>
            <div
              style={{
                fontFamily: "monospace",
                fontSize: 13 * S,
                color: methodColor,
                letterSpacing: 2,
                fontWeight: "bold",
              }}
            >
              {PHASES[activePhase]}
            </div>
            <div
              style={{
                fontFamily: "monospace",
                fontSize: 8 * S,
                color: C_TEXT_DIM,
                marginTop: 4 * S,
              }}
            >
              PHASE {activePhase + 1} OF {PHASES.length}
            </div>
            {/* Progress dots */}
            <div style={{ display: "flex", gap: 5 * S, marginTop: 10 * S }}>
              {PHASES.map((_, i) => (
                <div
                  key={i}
                  style={{
                    width: 8 * S,
                    height: 3 * S,
                    borderRadius: 2,
                    background: i <= activePhase ? methodColor : C_PANEL_BORDER,
                    transition: "background 0.3s",
                  }}
                />
              ))}
            </div>
          </div>
        ) : (
          <div
            style={{
              fontFamily: "monospace",
              fontSize: 9 * S,
              color: C_TEXT_DIM,
              marginTop: 10 * S,
            }}
          >
            —
          </div>
        )}
      </div>
    </Panel>
  );
};

/** Bottom status bar */
const BottomStatusBar: React.FC<{
  visionLive: boolean;
  methodKey: MethodKey;
  methodColor: string;
  frame: number;
}> = ({ visionLive, methodKey, methodColor, frame }) => {
  const def = panel("bar_bottom_status");

  // Heartbeat — pulse every 60 frames
  const heartbeatPulse = Math.sin((frame / 60) * Math.PI * 2);
  const dotOpacity = 0.7 + heartbeatPulse * 0.3;

  return (
    <Panel def={def}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          height: "100%",
          padding: `0 ${10 * S}px`,
          gap: 12 * S,
        }}
      >
        {/* Heartbeat dot */}
        <div
          style={{
            width: 7 * S,
            height: 7 * S,
            borderRadius: "50%",
            background: visionLive ? "#22ff66" : "#ff3333",
            boxShadow: visionLive
              ? `0 0 ${6 * S}px #22ff66`
              : `0 0 ${6 * S}px #ff3333`,
            opacity: dotOpacity,
            flexShrink: 0,
          }}
        />

        {/* Status text */}
        <span
          style={{
            fontFamily: "monospace",
            fontSize: 8 * S,
            color: visionLive ? "#22ff66" : "#ff5555",
            letterSpacing: 2,
          }}
        >
          {visionLive ? "VISION LIVE" : "VISION OFFLINE"}
        </span>

        <div style={{ width: 1, height: "60%", background: C_PANEL_BORDER }} />

        <span
          style={{
            fontFamily: "monospace",
            fontSize: 8 * S,
            color: methodKey !== "NONE" ? methodColor : C_TEXT_DIM,
            letterSpacing: 2,
          }}
        >
          {methodKey !== "NONE" ? `METHOD: ${METHODS[methodKey].label}` : "METHOD: NONE"}
        </span>

        {/* Right side — frame counter */}
        <div style={{ marginLeft: "auto" }}>
          <span
            style={{
              fontFamily: "monospace",
              fontSize: 7 * S,
              color: C_TEXT_DIM,
              letterSpacing: 1,
            }}
          >
            HARDWARE III · LCA INSTALLATION · {String(Math.floor(frame / 30)).padStart(2, "0")}:
            {String(frame % 30).padStart(2, "0")}
          </span>
        </div>
      </div>
    </Panel>
  );
};

// ---------------------------------------------------------------------------
// Main composition
// ---------------------------------------------------------------------------

export const HardwareVideo: React.FC = () => {
  const frame = useCurrentFrame();

  // --- Derive scene state from frame ---

  // Vision goes live at scene 2 (frame 90)
  const visionLive = frame >= T.scene1End;

  // Method selection
  let methodKey: MethodKey = "NONE";
  if (frame >= T.scene3End && frame < T.scene6End) {
    methodKey = "MASONRY";
  } else if (frame >= T.scene6End && frame < T.scene7End) {
    methodKey = "3D PRINTED";
  } else if (frame >= T.scene7End && frame < T.total) {
    methodKey = "PREFAB";
  } else if (frame >= T.scene2End && frame < T.scene3End) {
    // Vision comes alive but no method yet — show NONE
    methodKey = "NONE";
  }

  const methodColor = METHODS[methodKey].color;

  // Active phase (scene 5: frame 660–840, cycles through phases)
  let activePhase = 0;
  if (frame >= T.scene4End && frame < T.scene5End) {
    // In scene 5, step through phases
    const scene5Duration = T.scene5End - T.scene4End; // 180 frames = 6s
    const phaseDur = scene5Duration / PHASES.length;
    activePhase = Math.min(
      PHASES.length - 1,
      Math.floor((frame - T.scene4End) / phaseDur)
    );
  } else if (frame >= T.scene5End) {
    activePhase = PHASES.length - 1;
  }

  // Footprint points revealed (scene 4: frame 360–660)
  let pointsRevealed = 0;
  let polygonProgress = 0;

  if (frame >= T.scene3End) {
    if (frame < T.scene4End) {
      const elapsed = frame - T.scene3End;
      // First 210 frames: reveal 6 points (one every 35 frames)
      const pointRevealDuration = 210;
      const pointDur = pointRevealDuration / 6;
      pointsRevealed = Math.min(6, Math.floor(elapsed / pointDur) + 1);
      // Last 90 frames: draw polygon outline
      const polyElapsed = Math.max(0, elapsed - pointRevealDuration);
      polygonProgress = Math.min(1, polyElapsed / 90);
    } else {
      pointsRevealed = 6;
      polygonProgress = 1;
    }
  }

  // Overall fade to black (scene 8: frame 1140–1200)
  const fadeToBlack =
    frame >= T.scene7End
      ? interpolate(frame, [T.scene7End, T.total], [0, 1], {
          extrapolateRight: "clamp",
        })
      : 0;

  // Scene 1→2 panel reveal (fade in panels)
  const panelOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: C_BG }}>
      <div style={{ position: "absolute", inset: 0, opacity: panelOpacity }}>
        {/* All 9 panels */}
        <PhaseNavPanel
          activePhase={activePhase}
          methodColor={methodColor}
          visible={methodKey !== "NONE"}
        />
        <LeftInfoPanel
          methodKey={methodKey}
          methodColor={methodColor}
          visionLive={visionLive}
        />
        <AssemblySequencePanel
          methodKey={methodKey}
          methodColor={methodColor}
          activePhase={activePhase}
        />
        <MainPlanPanel
          methodKey={methodKey}
          methodColor={methodColor}
          pointsRevealed={pointsRevealed}
          polygonProgress={polygonProgress}
        />
        <MethodSelectionPanel methodKey={methodKey} methodColor={methodColor} />
        <RightComparisonPanel methodKey={methodKey} methodColor={methodColor} />
        <RightCostChartPanel methodKey={methodKey} methodColor={methodColor} />
        <RightPhasePreviewPanel
          methodKey={methodKey}
          methodColor={methodColor}
          activePhase={activePhase}
        />
        <BottomStatusBar
          visionLive={visionLive}
          methodKey={methodKey}
          methodColor={methodColor}
          frame={frame}
        />
      </div>

      {/* Fade to black overlay */}
      {fadeToBlack > 0 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "#000",
            opacity: fadeToBlack,
          }}
        />
      )}
    </AbsoluteFill>
  );
};
