// Subtitle component — positioned at the lower third with consistent fade.
// Used across all six scenes for a uniform read.

import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { palette, subtitleStyle } from "../theme";

type Props = {
  children: React.ReactNode;
  // Frame within the local sequence at which subtitle starts fading in
  fadeInAt?: number;
  // Frame within the local sequence at which subtitle starts fading out (0 = no fade out)
  fadeOutAt?: number;
  // Override for default position (default 78% from top)
  topPercent?: number;
  // Style override
  style?: React.CSSProperties;
};

export const Subtitle: React.FC<Props> = ({
  children,
  fadeInAt = 0,
  fadeOutAt = 0,
  topPercent = 78,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeIn = interpolate(
    frame,
    [fadeInAt, fadeInAt + fps * 0.6],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.22, 1, 0.36, 1),
    },
  );

  const fadeOut =
    fadeOutAt > 0
      ? interpolate(frame, [fadeOutAt, fadeOutAt + fps * 0.4], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.4, 0, 0.6, 1),
        })
      : 1;

  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <div
      style={{
        position: "absolute",
        top: `${topPercent}%`,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        opacity,
      }}
    >
      <div
        style={{
          ...subtitleStyle,
          ...style,
          // Subtle paper border on top — like a printed margin rule
          borderTop: `1px solid ${palette.paperFaint}`,
          paddingTop: 24,
        }}
      >
        {children}
      </div>
    </div>
  );
};
