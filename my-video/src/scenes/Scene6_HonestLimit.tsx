// Scene 6 — Honest limit (50–60s)
// Hold on the final intervention map (dimmed) while a quiet, declarative
// statement of what the map does and does NOT claim fades up. End on the
// project signature.

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

export const Scene6_HonestLimit: React.FC<Props> = ({
  sceneDurationFrames,
}) => {
  const local = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Map dim wash — 0 → 0.5
  const mapDim = interpolate(local, [0, fps * 1.2], [0.7, 0.35], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0, 0.6, 1),
  });

  // Statement fades in three beats
  const beat1 = interpolate(local, [fps * 0.8, fps * 2.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });
  const beat2 = interpolate(local, [fps * 2.4, fps * 3.6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });
  const beat3 = interpolate(local, [fps * 4.0, fps * 5.2], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  // Project signature fades in last
  const sigOpacity = interpolate(local, [fps * 6.0, fps * 7.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  // Final fade-out across last 1s
  const outFade = interpolate(
    local,
    [sceneDurationFrames - fps * 1.0, sceneDurationFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill style={{ background: palette.voidBlack, opacity: outFade }}>
      <SceneChrome
        sceneNumber={6}
        totalScenes={6}
        sceneDurationFrames={sceneDurationFrames}
        label="Honest limit"
      />

      {/* Faint map ghost behind the text */}
      <AbsoluteFill style={{ opacity: mapDim }}>
        <BarcelonaMap opacity={0.6} gridReveal={1} coastlineReveal={1} />
      </AbsoluteFill>

      {/* Coloured zones — held over but at low opacity */}
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1080 1080"
        style={{ position: "absolute", inset: 0, opacity: mapDim * 1.4 }}
        preserveAspectRatio="xMidYMid meet"
      >
        {priorityZones.map((z) => {
          const intervention = zoneDisplayIntervention(z);
          const color = interventionColor[intervention];
          const { x, y } = gridToScreen(z.gx, z.gy);
          const size = 22;
          return (
            <rect
              key={z.cellId}
              x={x - size / 2}
              y={y - size / 2}
              width={size}
              height={size}
              fill={color}
              opacity={0.55}
              transform={`rotate(-36 ${x} ${y})`}
              rx={1}
            />
          );
        })}
      </svg>

      {/* Statement — three beats, centre-aligned */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 80px",
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontFamily: typography.serif,
            fontStyle: "italic",
            fontSize: 36,
            color: palette.paper,
            opacity: beat1,
            marginBottom: 28,
            maxWidth: 760,
            lineHeight: 1.3,
          }}
        >
          Not a 2030 forecast.
        </div>
        <div
          style={{
            fontFamily: typography.serif,
            fontStyle: "italic",
            fontSize: 50,
            color: palette.amber,
            opacity: beat2,
            marginBottom: 36,
            lineHeight: 1.2,
          }}
        >
          A leverage map.
        </div>
        <div
          style={{
            fontFamily: typography.sans,
            fontSize: 20,
            color: palette.paperDim,
            letterSpacing: 0.4,
            opacity: beat3,
            maxWidth: 720,
            lineHeight: 1.55,
          }}
        >
          Fifteen zones where capital spending faces
          <br />
          the fewest barriers. The rest is the work.
        </div>
      </div>

      {/* Project signature — bottom-centre */}
      <div
        style={{
          position: "absolute",
          bottom: 130,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: sigOpacity,
        }}
      >
        <div
          style={{
            ...captionStyle,
            color: palette.paperFaint,
            fontSize: 12,
            letterSpacing: 2.4,
            marginBottom: 10,
          }}
        >
          Mycorrhizal Barcelona · Group 4
        </div>
        <div
          style={{
            fontFamily: typography.serif,
            fontStyle: "italic",
            fontSize: 18,
            color: palette.paper,
            letterSpacing: 0.3,
            maxWidth: 700,
            margin: "0 auto",
            lineHeight: 1.5,
          }}
        >
          An ecosystem that supports mycelium health
          <br />
          is an ecosystem that supports the health of all beings.
        </div>
        <div
          style={{
            ...captionStyle,
            color: palette.paperFaint,
            fontSize: 10,
            letterSpacing: 1.8,
            marginTop: 14,
          }}
        >
          NEXUS-Micro pipeline · 2026
        </div>
      </div>
    </AbsoluteFill>
  );
};
