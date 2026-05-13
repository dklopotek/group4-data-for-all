// Scene 2 — Barrier reveal (10–20s)
// The Barcelona basemap fades up. Three layers animate in sequence:
//   sealed (grey wash) → heat (red glow) → bare (yellow stippling).
// One word per layer beats out next to a small chip badge.

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

type Props = {
  sceneDurationFrames: number;
};

const BeatWord: React.FC<{
  word: string;
  color: string;
  active: number; // 0..1
  index: number;
}> = ({ word, color, active, index }) => {
  // Drop in from above with a 12px slide, plus opacity ramp
  const yOffset = (1 - active) * 12;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        gap: 8,
        opacity: active,
        transform: `translateY(${yOffset}px)`,
      }}
    >
      <div
        style={{
          width: 36,
          height: 4,
          background: color,
          opacity: 0.85,
        }}
      />
      <div
        style={{
          fontFamily: typography.serif,
          fontStyle: "italic",
          fontSize: 38,
          color: palette.paper,
          lineHeight: 1,
        }}
      >
        {word}
      </div>
      <div
        style={{
          ...captionStyle,
          fontSize: 11,
          letterSpacing: 1.8,
          color: palette.paperFaint,
        }}
      >
        Barrier 0{index}
      </div>
    </div>
  );
};

export const Scene2_BarrierReveal: React.FC<Props> = ({
  sceneDurationFrames,
}) => {
  const local = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Map fades up at 0.4s
  const mapOpacity = interpolate(local, [fps * 0.4, fps * 1.8], [0, 0.85], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  const gridReveal = interpolate(local, [fps * 0.6, fps * 2.4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  const coastReveal = interpolate(local, [fps * 0.4, fps * 2.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  // Three layers — each takes ~3s with a hold
  const sealed = interpolate(local, [fps * 2.5, fps * 4.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });
  const heat = interpolate(local, [fps * 5.0, fps * 6.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });
  const bare = interpolate(local, [fps * 7.5, fps * 9.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });

  // Out-fade across last 0.5s — gentle handoff to scene 3
  const outFade = interpolate(
    local,
    [sceneDurationFrames - fps * 0.5, sceneDurationFrames],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );

  return (
    <AbsoluteFill style={{ background: palette.soilDeep, opacity: outFade }}>
      <SceneChrome
        sceneNumber={2}
        totalScenes={6}
        sceneDurationFrames={sceneDurationFrames}
        label="Barrier reveal"
      />

      <AbsoluteFill style={{ opacity: mapOpacity }}>
        <BarcelonaMap
          opacity={1}
          gridReveal={gridReveal}
          coastlineReveal={coastReveal}
        />
      </AbsoluteFill>

      <BarrierWash intensity={sealed} color={palette.sealed} variant="sealed" />
      <BarrierWash intensity={heat} color={palette.heat} variant="heat" />
      <BarrierWash intensity={bare} color={palette.bare} variant="bare" />

      {/* Three beat words — left rail, vertical stack */}
      <div
        style={{
          position: "absolute",
          top: 220,
          left: 64,
          display: "flex",
          flexDirection: "column",
          gap: 56,
        }}
      >
        <BeatWord
          word="Sealed."
          color={palette.sealed}
          active={sealed}
          index={1}
        />
        <BeatWord word="Hot." color={palette.heat} active={heat} index={2} />
        <BeatWord word="Bare." color={palette.bare} active={bare} index={3} />
      </div>

      {/* Footer caption — tucked against bottom-right above scene chrome */}
      <div
        style={{
          position: "absolute",
          bottom: 96,
          right: 64,
          textAlign: "right",
          fontFamily: typography.sans,
          fontSize: 18,
          color: palette.paperDim,
          letterSpacing: 0.4,
          maxWidth: 360,
          lineHeight: 1.5,
          opacity: interpolate(local, [fps * 3, fps * 4], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Three pressures. One block.
        <br />
        Each visible from above ground.
      </div>
    </AbsoluteFill>
  );
};
