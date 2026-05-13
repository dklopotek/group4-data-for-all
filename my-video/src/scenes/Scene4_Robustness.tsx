// Scene 4 — Robustness proof (30–40s)
// Animated reconstruction of sensitivity_comparison.png:
//   Three columns slide in: equal weights, sealed-priority, heat-priority.
//   In each column, the same 15 cells light up in green at the same y-position.
//   Caption underlines: "Three weightings. Same fifteen zones. Every time."

import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { palette, typography, captionStyle } from "../theme";
import { SceneChrome } from "../primitives/SceneChrome";

type Props = {
  sceneDurationFrames: number;
};

const COLUMNS: { label: string; sub: string }[] = [
  { label: "Equal", sub: "1.00 · 1.00 · 1.00 · 1.00" },
  { label: "Sealed-priority", sub: "1.50 · 0.83 · 0.83 · 0.83" },
  { label: "Heat-priority", sub: "0.83 · 1.50 · 0.83 · 0.83" },
];

// Vertical y-positions for the 15 ranks within a column (top→bottom)
const ROW_COUNT = 15;

const Column: React.FC<{
  index: number;
  reveal: number; // 0..1, column's own slide-in
  cellsReveal: number; // 0..1, cells lighting up
  label: string;
  sub: string;
}> = ({ index, reveal, cellsReveal, label, sub }) => {
  const colWidth = 200;
  const colGap = 60;
  const totalWidth = COLUMNS.length * colWidth + (COLUMNS.length - 1) * colGap;
  const startX = (1080 - totalWidth) / 2;
  const x = startX + index * (colWidth + colGap);

  const slideY = (1 - reveal) * 24;
  const opacity = reveal;

  const cellHeight = 28;
  const cellGap = 6;
  const cellsTop = 280;

  return (
    <g transform={`translate(${x} 0)`} opacity={opacity}>
      {/* Column header */}
      <g transform={`translate(0 ${220 + slideY})`}>
        <text
          x={colWidth / 2}
          y={0}
          fill={palette.paper}
          fontFamily={typography.serif}
          fontStyle="italic"
          fontSize={26}
          textAnchor="middle"
        >
          {label}
        </text>
        <text
          x={colWidth / 2}
          y={28}
          fill={palette.paperFaint}
          fontFamily={typography.mono}
          fontSize={11}
          letterSpacing={1.4}
          textAnchor="middle"
        >
          {sub}
        </text>
      </g>

      {/* Frame around the cell stack */}
      <rect
        x={0}
        y={cellsTop - 10}
        width={colWidth}
        height={ROW_COUNT * (cellHeight + cellGap) + 12}
        fill="none"
        stroke={palette.mossMid}
        strokeWidth={1}
        opacity={0.5}
      />

      {/* Cells */}
      {Array.from({ length: ROW_COUNT }).map((_, i) => {
        // Stagger cells by row, but all columns light at same row at same time
        // — so a horizontal "match band" reads as the result.
        const rowStart = (i / ROW_COUNT) * 0.7;
        const rowReveal = Math.max(
          0,
          Math.min(1, (cellsReveal - rowStart) / 0.25),
        );
        const cy = cellsTop + i * (cellHeight + cellGap);

        return (
          <g key={i} transform={`translate(0 ${cy})`}>
            {/* Empty cell baseline */}
            <rect
              x={6}
              y={0}
              width={colWidth - 12}
              height={cellHeight}
              fill={palette.mossDark}
              opacity={0.4}
              rx={2}
            />
            {/* Filled green when revealed */}
            <rect
              x={6}
              y={0}
              width={(colWidth - 12) * rowReveal}
              height={cellHeight}
              fill={palette.planting}
              opacity={0.85}
              rx={2}
            />
            {/* Rank label */}
            <text
              x={16}
              y={cellHeight / 2 + 4}
              fill={palette.paper}
              fontFamily={typography.mono}
              fontSize={11}
              opacity={rowReveal}
            >
              {String(i + 1).padStart(2, "0")}
            </text>
          </g>
        );
      })}
    </g>
  );
};

export const Scene4_Robustness: React.FC<Props> = ({
  sceneDurationFrames,
}) => {
  const local = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Three columns slide in 0.5s apart
  const cols = COLUMNS.map((_, i) => {
    return interpolate(
      local,
      [fps * (0.4 + i * 0.5), fps * (1.4 + i * 0.5)],
      [0, 1],
      {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.bezier(0.22, 1, 0.36, 1),
      },
    );
  });

  // Cells light up after all columns are in place — 3.5s mark
  const cellsReveal = interpolate(local, [fps * 3.5, fps * 7.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0, 0.6, 1),
  });

  // Jaccard tag fades in at the end
  const jaccardOpacity = interpolate(local, [fps * 7.5, fps * 9], [0, 1], {
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

  // Bottom subtitle reveal
  const titleOpacity = interpolate(local, [fps * 0.2, fps * 1.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  return (
    <AbsoluteFill style={{ background: palette.voidBlack, opacity: outFade }}>
      <SceneChrome
        sceneNumber={4}
        totalScenes={6}
        sceneDurationFrames={sceneDurationFrames}
        label="Robustness proof"
      />

      {/* Title — top-centred */}
      <div
        style={{
          position: "absolute",
          top: 90,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: titleOpacity,
        }}
      >
        <div
          style={{
            fontFamily: typography.serif,
            fontStyle: "italic",
            fontSize: 38,
            color: palette.paper,
            letterSpacing: 0.3,
          }}
        >
          We tried three weightings.
        </div>
        <div
          style={{
            fontFamily: typography.sans,
            fontSize: 18,
            color: palette.paperDim,
            letterSpacing: 1.0,
            marginTop: 10,
          }}
        >
          The same fifteen zones came up every time.
        </div>
      </div>

      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1080 1080"
        style={{ position: "absolute", inset: 0 }}
        preserveAspectRatio="xMidYMid meet"
      >
        {COLUMNS.map((col, i) => (
          <Column
            key={col.label}
            index={i}
            reveal={cols[i]}
            cellsReveal={cellsReveal}
            label={col.label}
            sub={col.sub}
          />
        ))}
      </svg>

      {/* Jaccard badge — bottom centred */}
      <div
        style={{
          position: "absolute",
          bottom: 90,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity: jaccardOpacity,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 24,
            padding: "16px 32px",
            border: `1px solid ${palette.amber}`,
            background: palette.soilDeep,
          }}
        >
          <div
            style={{
              ...captionStyle,
              color: palette.paperDim,
              letterSpacing: 1.4,
            }}
          >
            Jaccard agreement
          </div>
          <div
            style={{
              fontFamily: typography.serif,
              fontStyle: "italic",
              fontSize: 36,
              color: palette.amber,
              lineHeight: 1,
            }}
          >
            1.00
          </div>
          <div
            style={{
              ...captionStyle,
              color: palette.paperFaint,
              fontSize: 11,
              letterSpacing: 1.4,
              maxWidth: 220,
            }}
          >
            Top-15 sets, pairwise
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
