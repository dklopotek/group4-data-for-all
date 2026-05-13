// A stylized abstraction of Barcelona's coastline + grid.
// Not a literal map — a memorable silhouette reduced to gestures:
//   - Diagonal coastline running NE→SW
//   - The Eixample grid as a tilted square mesh
//   - Montjuïc and Collserola hinted at as soft masses
//
// All coordinates live in a 1080×1080 viewBox. Render once, reuse across scenes.

import React from "react";
import { palette } from "../theme";

type Props = {
  // 0..1 — overall opacity of the map
  opacity?: number;
  // 0..1 — how much of the grid mesh is drawn (0 = none, 1 = full)
  gridReveal?: number;
  // 0..1 — coastline reveal
  coastlineReveal?: number;
};

const GRID_ROTATION = -36; // Eixample's iconic tilt

export const BarcelonaMap: React.FC<Props> = ({
  opacity = 1,
  gridReveal = 1,
  coastlineReveal = 1,
}) => {
  // 30 columns × 24 rows of 28-pixel cells, rotated about (540, 540).
  // Some cells dropped to fake the urban edge against the sea.
  const cells: { x: number; y: number }[] = [];
  for (let r = -12; r <= 12; r++) {
    for (let c = -15; c <= 15; c++) {
      // Skip cells that would fall in the sea (lower-right quadrant)
      const onLand = c + r * 0.4 < 6 + Math.sin(r * 0.5) * 2;
      if (!onLand) continue;
      cells.push({ x: c * 30, y: r * 30 });
    }
  }

  // Visible cell count — sweep diagonally from NW to SE for the reveal
  const total = cells.length;
  const cutoff = Math.floor(total * gridReveal);

  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 1080 1080"
      style={{ opacity, display: "block" }}
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <radialGradient id="mountainsoft" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor={palette.mossDark} stopOpacity="0.6" />
          <stop offset="1" stopColor={palette.mossDark} stopOpacity="0" />
        </radialGradient>
        <linearGradient id="seafade" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor={palette.voidBlack} stopOpacity="0" />
          <stop offset="1" stopColor={palette.voidBlack} stopOpacity="0.4" />
        </linearGradient>
      </defs>

      {/* Soft mass — Collserola hills behind the city, top-left */}
      <ellipse
        cx={300}
        cy={280}
        rx={420}
        ry={180}
        fill="url(#mountainsoft)"
      />
      {/* Montjuïc — bottom-left soft mass */}
      <ellipse
        cx={260}
        cy={820}
        rx={220}
        ry={120}
        fill="url(#mountainsoft)"
      />

      {/* Sea — implicit lower-right, hinted via gradient */}
      <rect
        x={0}
        y={0}
        width={1080}
        height={1080}
        fill="url(#seafade)"
        opacity={0.5}
      />

      {/* Coastline — diagonal stroke */}
      <path
        d={`M 1080 380 Q 880 540 540 720 Q 320 880 80 1020`}
        fill="none"
        stroke={palette.paperFaint}
        strokeWidth={1.5}
        strokeDasharray="1000"
        strokeDashoffset={1000 * (1 - coastlineReveal)}
        opacity={0.6}
      />

      {/* Eixample grid — rotated mesh of small squares */}
      <g
        transform={`translate(540 540) rotate(${GRID_ROTATION})`}
      >
        {cells.slice(0, cutoff).map((cell, i) => (
          <rect
            key={`${cell.x}-${cell.y}-${i}`}
            x={cell.x - 12}
            y={cell.y - 12}
            width={24}
            height={24}
            fill="none"
            stroke={palette.mossMid}
            strokeWidth={0.8}
            opacity={0.55}
          />
        ))}
      </g>
    </svg>
  );
};
