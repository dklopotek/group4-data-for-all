// Scene 1 — Cost framing (0–10s)
// Black field. Title fades in. The motto sentence slides in below.
// A single grid cell is hinted at, lower-third — a quiet preview of what is to come.

import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { palette, titleStyle, typography } from "../theme";
import { Subtitle } from "../primitives/Subtitle";
import { SceneChrome } from "../primitives/SceneChrome";

type Props = {
  sceneDurationFrames: number;
};

export const Scene1_CostFraming: React.FC<Props> = ({
  sceneDurationFrames,
}) => {
  // useCurrentFrame() inside <Sequence> is already sequence-local
  const local = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Title fade-in: 0.4s → 1.6s
  const titleOpacity = interpolate(
    local,
    [fps * 0.4, fps * 1.6],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.22, 1, 0.36, 1),
    },
  );

  // Title slow scale: 1 → 1.04 across the scene (gentle drift)
  const titleScale = interpolate(local, [0, sceneDurationFrames], [1, 1.04], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.linear,
  });

  // The single grid cell — appears at 4s, sits to the right of "saplings"
  const cellOpacity = interpolate(local, [fps * 4, fps * 5.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  // Out-fade across last second
  const outFade = interpolate(
    local,
    [sceneDurationFrames - fps, sceneDurationFrames],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.4, 0, 0.6, 1),
    },
  );

  return (
    <AbsoluteFill style={{ background: palette.voidBlack, opacity: outFade }}>
      <SceneChrome
        sceneNumber={1}
        totalScenes={6}
        sceneDurationFrames={sceneDurationFrames}
        label="Cost framing"
      />

      {/* Centred title — serif italic */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 80px",
          opacity: titleOpacity,
          transform: `scale(${titleScale})`,
          transformOrigin: "center",
        }}
      >
        <div
          style={{
            ...titleStyle,
            fontSize: 56,
            color: palette.paper,
            marginBottom: 36,
            maxWidth: 820,
          }}
        >
          Mature trees cost less than dead saplings.
        </div>

        {/* Sub-statement — sans-serif, dim, slightly tighter */}
        <div
          style={{
            fontFamily: typography.sans,
            fontSize: 22,
            color: palette.paperDim,
            letterSpacing: 0.5,
            textAlign: "center",
            maxWidth: 680,
            lineHeight: 1.6,
          }}
        >
          Barcelona plants thousands of street trees a year.
          <br />
          In the hottest, most sealed zones, the same blocks
          <br />
          keep losing them.
        </div>

        {/* Tiny grid cell — visual seed for the rest of the video */}
        <svg
          width={120}
          height={120}
          viewBox="0 0 120 120"
          style={{
            marginTop: 48,
            opacity: cellOpacity,
          }}
        >
          <rect
            x={20}
            y={20}
            width={80}
            height={80}
            fill="none"
            stroke={palette.amber}
            strokeWidth={1.2}
            transform="rotate(-36 60 60)"
          />
          <rect
            x={36}
            y={36}
            width={48}
            height={48}
            fill={palette.amber}
            opacity={0.18}
            transform="rotate(-36 60 60)"
          />
        </svg>
      </div>

      <Subtitle
        fadeInAt={fps * 6.5}
        fadeOutAt={sceneDurationFrames - fps * 0.8}
        style={{ fontSize: 20, color: palette.paperDim }}
      >
        400m grid · Ajuntament de Barcelona · Eixos Verds capital cycle
      </Subtitle>
    </AbsoluteFill>
  );
};
