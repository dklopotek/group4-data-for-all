// Scene 5 — Intervention match (40–50s)
// The 15 zones recolour from white to their intervention type.
// A right-rail legend shows the three categories with their counts.

import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { palette, typography, captionStyle } from "../theme";
import { BarcelonaMap } from "../primitives/BarcelonaMap";
import { SceneChrome } from "../primitives/SceneChrome";
import {
  priorityZones,
  zoneDisplayIntervention,
  type InterventionType,
} from "../data/priorityZones";
import { gridToScreen } from "../primitives/GridCoords";

type Props = {
  sceneDurationFrames: number;
};

const interventionColor: Record<InterventionType, string> = {
  "de-paving": palette.depaving,
  cooling: palette.cooling,
  planting: palette.planting,
};

const interventionLabel: Record<InterventionType, string> = {
  "de-paving": "De-paving",
  cooling: "Cooling",
  planting: "Planting",
};

const interventionDesc: Record<InterventionType, string> = {
  "de-paving": "Surface unsealing — soil access restored",
  cooling: "Pavement cooling — surface temperature reduced",
  planting: "Tree planting — canopy gain, host expansion",
};

const interventionBudget: Record<InterventionType, string> = {
  "de-paving": "Eixos Verds · de-paving line",
  cooling: "Pla Clima · cooling allocation",
  planting: "Arbrat Viari · replanting line",
};

// Lerp between two RGB hex strings
const hexToRgb = (hex: string) => {
  const h = hex.replace("#", "");
  return {
    r: parseInt(h.slice(0, 2), 16),
    g: parseInt(h.slice(2, 4), 16),
    b: parseInt(h.slice(4, 6), 16),
  };
};

const lerpColor = (a: string, b: string, t: number) => {
  const ca = hexToRgb(a);
  const cb = hexToRgb(b);
  const r = Math.round(ca.r + (cb.r - ca.r) * t);
  const g = Math.round(ca.g + (cb.g - ca.g) * t);
  const bl = Math.round(ca.b + (cb.b - ca.b) * t);
  return `rgb(${r}, ${g}, ${bl})`;
};

export const Scene5_InterventionMatch: React.FC<Props> = ({
  sceneDurationFrames,
}) => {
  const local = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Compute counts per intervention category
  const counts: Record<InterventionType, number> = {
    "de-paving": 0,
    cooling: 0,
    planting: 0,
  };
  priorityZones.forEach((z) => {
    counts[zoneDisplayIntervention(z)]++;
  });

  // Each zone recolour starts at 1.0s, staggered by rank.
  const recolourStart = fps * 1.0;
  const recolourStagger = fps * 0.18;

  // Legend animates in 0.4s
  const legendOpacity = interpolate(local, [fps * 0.4, fps * 1.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  // Caption — top
  const captionIn = interpolate(local, [0, fps * 1.2], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  const outFade = interpolate(
    local,
    [sceneDurationFrames - fps * 0.6, sceneDurationFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill style={{ background: palette.soilDeep, opacity: outFade }}>
      <SceneChrome
        sceneNumber={5}
        totalScenes={6}
        sceneDurationFrames={sceneDurationFrames}
        label="Intervention match"
      />

      <AbsoluteFill style={{ opacity: 0.6 }}>
        <BarcelonaMap opacity={1} gridReveal={1} coastlineReveal={1} />
      </AbsoluteFill>

      {/* Top caption */}
      <div
        style={{
          position: "absolute",
          top: 80,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: captionIn,
        }}
      >
        <div
          style={{
            fontFamily: typography.serif,
            fontStyle: "italic",
            fontSize: 36,
            color: palette.paper,
          }}
        >
          Each zone matched to a budget line
        </div>
        <div
          style={{
            fontFamily: typography.sans,
            fontSize: 18,
            color: palette.paperDim,
            letterSpacing: 0.4,
            marginTop: 8,
          }}
        >
          that already exists.
        </div>
      </div>

      {/* The 15 priority zones — recoloured */}
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1080 1080"
        style={{ position: "absolute", inset: 0 }}
        preserveAspectRatio="xMidYMid meet"
      >
        {priorityZones.map((z) => {
          const intervention = zoneDisplayIntervention(z);
          const target = interventionColor[intervention];
          const t = interpolate(
            local,
            [
              recolourStart + recolourStagger * (z.rank - 1),
              recolourStart + recolourStagger * (z.rank - 1) + fps * 0.6,
            ],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.22, 1, 0.36, 1),
            },
          );
          const color = lerpColor(palette.zone, target, t);
          const { x, y } = gridToScreen(z.gx, z.gy);
          const size = 26;
          return (
            <g key={z.cellId} transform={`translate(${x} ${y}) rotate(-36)`}>
              <rect
                x={-size / 2 - 4}
                y={-size / 2 - 4}
                width={size + 8}
                height={size + 8}
                fill={color}
                opacity={0.22}
                rx={2}
              />
              <rect
                x={-size / 2}
                y={-size / 2}
                width={size}
                height={size}
                fill={color}
                opacity={0.95}
                rx={1}
              />
            </g>
          );
        })}
      </svg>

      {/* Legend rail — right side */}
      <div
        style={{
          position: "absolute",
          top: 280,
          right: 56,
          width: 320,
          opacity: legendOpacity,
          display: "flex",
          flexDirection: "column",
          gap: 28,
        }}
      >
        {(Object.keys(counts) as InterventionType[]).map((kind, i) => {
          // Stagger entries by 0.4s
          const entryReveal = interpolate(
            local,
            [fps * (1.2 + i * 0.4), fps * (2.4 + i * 0.4)],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.22, 1, 0.36, 1),
            },
          );
          return (
            <div
              key={kind}
              style={{
                opacity: entryReveal,
                transform: `translateY(${(1 - entryReveal) * 12}px)`,
                paddingLeft: 18,
                borderLeft: `3px solid ${interventionColor[kind]}`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "baseline",
                  gap: 12,
                  marginBottom: 4,
                }}
              >
                <div
                  style={{
                    fontFamily: typography.serif,
                    fontStyle: "italic",
                    fontSize: 28,
                    color: palette.paper,
                    lineHeight: 1,
                  }}
                >
                  {interventionLabel[kind]}
                </div>
                <div
                  style={{
                    fontFamily: typography.mono,
                    fontSize: 14,
                    color: interventionColor[kind],
                    letterSpacing: 1,
                  }}
                >
                  ×{counts[kind]}
                </div>
              </div>
              <div
                style={{
                  fontFamily: typography.sans,
                  fontSize: 14,
                  color: palette.paperDim,
                  lineHeight: 1.45,
                  marginBottom: 4,
                }}
              >
                {interventionDesc[kind]}
              </div>
              <div
                style={{
                  ...captionStyle,
                  color: palette.amber,
                  fontSize: 10,
                  letterSpacing: 1.6,
                }}
              >
                {interventionBudget[kind]}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
