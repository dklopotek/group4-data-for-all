// A mottled wash overlay representing a single barrier layer.
// Three blob clusters with varied scale and opacity to suggest "patchy density".
// Pure SVG — no animation here; the parent scene controls opacity via `intensity`.

import React from "react";

type Props = {
  // 0..1 — how strongly the wash is showing
  intensity: number;
  color: string;
  // Pseudo-random seed selecting which of the predefined patterns to show
  variant: "sealed" | "heat" | "bare";
};

// Hand-placed blob clusters, calibrated to occupy the dense urban core
// (centre-right of the 1080 frame, mirroring the Eixample grid centre).
const BLOBS: Record<Props["variant"], { cx: number; cy: number; rx: number; ry: number; rot: number; o: number }[]> = {
  sealed: [
    { cx: 540, cy: 520, rx: 320, ry: 240, rot: -36, o: 0.55 },
    { cx: 480, cy: 640, rx: 220, ry: 180, rot: -30, o: 0.45 },
    { cx: 660, cy: 460, rx: 200, ry: 140, rot: -40, o: 0.4 },
    { cx: 380, cy: 480, rx: 160, ry: 120, rot: -35, o: 0.35 },
    { cx: 720, cy: 600, rx: 140, ry: 100, rot: -32, o: 0.3 },
  ],
  heat: [
    { cx: 560, cy: 540, rx: 280, ry: 220, rot: -36, o: 0.55 },
    { cx: 460, cy: 620, rx: 180, ry: 140, rot: -34, o: 0.5 },
    { cx: 640, cy: 480, rx: 200, ry: 160, rot: -38, o: 0.45 },
    { cx: 760, cy: 580, rx: 120, ry: 100, rot: -36, o: 0.35 },
    { cx: 400, cy: 460, rx: 100, ry: 80, rot: -36, o: 0.3 },
  ],
  bare: [
    { cx: 520, cy: 530, rx: 300, ry: 230, rot: -36, o: 0.4 },
    { cx: 580, cy: 440, rx: 160, ry: 120, rot: -34, o: 0.35 },
    { cx: 440, cy: 660, rx: 200, ry: 150, rot: -38, o: 0.4 },
    { cx: 700, cy: 520, rx: 180, ry: 130, rot: -36, o: 0.3 },
    { cx: 340, cy: 540, rx: 140, ry: 110, rot: -34, o: 0.28 },
  ],
};

export const BarrierWash: React.FC<Props> = ({ intensity, color, variant }) => {
  const blobs = BLOBS[variant];
  const filterId = `wash-blur-${variant}`;
  const gradientId = `wash-grad-${variant}`;

  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 1080 1080"
      style={{
        position: "absolute",
        inset: 0,
        opacity: intensity,
        mixBlendMode: "screen",
      }}
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <filter id={filterId} x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="22" />
        </filter>
        <radialGradient id={gradientId} cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor={color} stopOpacity="1" />
          <stop offset="0.7" stopColor={color} stopOpacity="0.5" />
          <stop offset="1" stopColor={color} stopOpacity="0" />
        </radialGradient>
      </defs>

      <g filter={`url(#${filterId})`}>
        {blobs.map((b, i) => (
          <ellipse
            key={i}
            cx={b.cx}
            cy={b.cy}
            rx={b.rx * (0.4 + 0.6 * intensity)}
            ry={b.ry * (0.4 + 0.6 * intensity)}
            transform={`rotate(${b.rot} ${b.cx} ${b.cy})`}
            fill={`url(#${gradientId})`}
            opacity={b.o}
          />
        ))}
      </g>
    </svg>
  );
};
