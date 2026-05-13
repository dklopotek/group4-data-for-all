// SceneChrome — the small, fixed metadata in the corners of every scene.
// Top-left: scene number
// Top-right: project tag
// Bottom-left: timecode-ish caption
// Deliberately understated — feels like printed margin marks, not UI.

import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { captionStyle, palette } from "../theme";

type Props = {
  sceneNumber: number;
  totalScenes: number;
  sceneDurationFrames: number;
  label: string;
};

export const SceneChrome: React.FC<Props> = ({
  sceneNumber,
  totalScenes,
  sceneDurationFrames,
  label,
}) => {
  // useCurrentFrame() inside a <Sequence> already returns frames relative
  // to the start of the sequence.
  const localFrame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const localSec = (Math.max(0, localFrame) / fps).toFixed(1);
  const totalSec = (sceneDurationFrames / fps).toFixed(0);

  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 36,
          left: 48,
          ...captionStyle,
        }}
      >
        <span style={{ color: palette.amber }}>
          {String(sceneNumber).padStart(2, "0")}
        </span>
        <span style={{ color: palette.paperFaint }}>
          {" / "}
          {String(totalScenes).padStart(2, "0")}
        </span>
      </div>

      <div
        style={{
          position: "absolute",
          top: 36,
          right: 48,
          ...captionStyle,
          textAlign: "right",
        }}
      >
        Mycorrhizal · BCN
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 36,
          left: 48,
          ...captionStyle,
        }}
      >
        {label}
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 36,
          right: 48,
          ...captionStyle,
          textAlign: "right",
        }}
      >
        {localSec}s / {totalSec}s
      </div>
    </>
  );
};
