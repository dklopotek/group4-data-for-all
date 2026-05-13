// Scene 3 — Stacking (20–30s)
// All three barrier washes ride together. Top-15 zones light up as bright
// off-white squares. The Amanita mushroom appears once, briefly, around 6s
// in — a five-frame visual seasoning, then it dims back into the soil.

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
import { BarrierWash } from "../primitives/BarrierWash";
import { SceneChrome } from "../primitives/SceneChrome";
import { priorityZones } from "../data/priorityZones";
import { gridToScreen } from "../primitives/GridCoords";
import { Mushroom } from "../Mushroom";

type Props = {
  sceneDurationFrames: number;
};

export const Scene3_Stacking: React.FC<Props> = ({
  sceneDurationFrames,
}) => {
  const local = useCurrentFrame();
  const { fps } = useVideoConfig();

  // The composite — all three barriers together at slightly lower intensity each.
  const composite = interpolate(local, [0, fps * 1.5], [0.7, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  // Zones reveal — staggered by rank, starting 2s in.
  const zoneStart = fps * 2;
  const zoneStagger = fps * 0.18;

  // Mushroom appears at 6s, holds 0.7s, fades out.
  const mushroomFrameLocal = local - fps * 6;
  const mushroomIn = interpolate(
    mushroomFrameLocal,
    [0, fps * 0.4],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.22, 1, 0.36, 1),
    },
  );
  const mushroomOut = interpolate(
    mushroomFrameLocal,
    [fps * 1.1, fps * 1.8],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.4, 0, 0.6, 1),
    },
  );
  const mushroomOpacity = Math.min(mushroomIn, mushroomOut);

  // The mushroom growth itself — drive its own choreography off scene-local frames.
  const mFrame = Math.max(0, mushroomFrameLocal);
  const stemProgress = interpolate(mFrame, [0, fps * 0.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });
  const capProgress = interpolate(mFrame, [fps * 0.3, fps * 0.9], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const wartsProgress = interpolate(mFrame, [fps * 0.6, fps * 1.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  // Final caption fade in
  const captionOpacity = interpolate(local, [fps * 4.5, fps * 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  // Out-fade
  const outFade = interpolate(
    local,
    [sceneDurationFrames - fps * 0.6, sceneDurationFrames],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );

  return (
    <AbsoluteFill style={{ background: palette.soilDeep, opacity: outFade }}>
      <SceneChrome
        sceneNumber={3}
        totalScenes={6}
        sceneDurationFrames={sceneDurationFrames}
        label="Stacking"
      />

      <AbsoluteFill>
        <BarcelonaMap opacity={0.7} gridReveal={1} coastlineReveal={1} />
      </AbsoluteFill>

      <BarrierWash
        intensity={composite * 0.55}
        color={palette.sealed}
        variant="sealed"
      />
      <BarrierWash
        intensity={composite * 0.5}
        color={palette.heat}
        variant="heat"
      />
      <BarrierWash
        intensity={composite * 0.45}
        color={palette.bare}
        variant="bare"
      />

      {/* The 15 priority zones */}
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1080 1080"
        style={{ position: "absolute", inset: 0 }}
        preserveAspectRatio="xMidYMid meet"
      >
        {priorityZones.map((z) => {
          const reveal = interpolate(
            local,
            [
              zoneStart + zoneStagger * (z.rank - 1),
              zoneStart + zoneStagger * (z.rank - 1) + fps * 0.5,
            ],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.22, 1, 0.36, 1),
            },
          );
          const { x, y } = gridToScreen(z.gx, z.gy);
          const size = 22 + reveal * 4;
          return (
            <g key={z.cellId} transform={`translate(${x} ${y}) rotate(-36)`}>
              {/* Outer glow */}
              <rect
                x={-size / 2 - 4}
                y={-size / 2 - 4}
                width={size + 8}
                height={size + 8}
                fill={palette.zone}
                opacity={reveal * 0.18}
                rx={2}
              />
              {/* Core square */}
              <rect
                x={-size / 2}
                y={-size / 2}
                width={size}
                height={size}
                fill={palette.zone}
                opacity={reveal * 0.92}
                rx={1}
              />
              {/* Tiny rank tick */}
              <text
                x={0}
                y={-size / 2 - 8}
                fill={palette.paper}
                fontFamily={typography.mono}
                fontSize={10}
                textAnchor="middle"
                opacity={reveal * 0.7}
                transform="rotate(36)"
              >
                {z.rank}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Single Amanita — small, low, almost incidental */}
      <div
        style={{
          position: "absolute",
          right: 90,
          bottom: 130,
          opacity: mushroomOpacity * 0.85,
          transform: "scale(0.55)",
          transformOrigin: "bottom center",
          filter: "saturate(0.7) brightness(0.85)",
        }}
      >
        <Mushroom
          stemProgress={stemProgress}
          capProgress={capProgress}
          wartsProgress={wartsProgress}
        />
      </div>

      {/* Caption — top-right corner; the punchline of the scene */}
      <div
        style={{
          position: "absolute",
          top: 200,
          right: 64,
          maxWidth: 380,
          textAlign: "right",
          opacity: captionOpacity,
        }}
      >
        <div
          style={{
            fontFamily: typography.serif,
            fontStyle: "italic",
            fontSize: 32,
            color: palette.paper,
            lineHeight: 1.25,
            marginBottom: 16,
          }}
        >
          Fifteen zones stack
          <br />
          all three barriers.
        </div>
        <div
          style={{
            fontFamily: typography.sans,
            fontSize: 18,
            color: palette.paperDim,
            letterSpacing: 0.3,
            lineHeight: 1.5,
          }}
        >
          This is where the next euro
          <br />
          does the most work.
        </div>
        <div
          style={{
            ...captionStyle,
            marginTop: 18,
            color: palette.amber,
            letterSpacing: 1.6,
            fontSize: 12,
          }}
        >
          Sants–Montjuïc · Sant Andreu · Eixample
        </div>
      </div>
    </AbsoluteFill>
  );
};
