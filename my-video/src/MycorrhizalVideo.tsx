// Mycorrhizal Barcelona — 60-second composition
// 6 scenes, 10 seconds each, 30 fps → 1800 total frames at 1080×1080.
// No voiceover. Subtitles only.

import React from "react";
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { palette } from "./theme";
import { Scene1_CostFraming } from "./scenes/Scene1_CostFraming";
import { Scene2_BarrierReveal } from "./scenes/Scene2_BarrierReveal";
import { Scene3_Stacking } from "./scenes/Scene3_Stacking";
import { Scene4_Robustness } from "./scenes/Scene4_Robustness";
import { Scene5_InterventionMatch } from "./scenes/Scene5_InterventionMatch";
import { Scene6_HonestLimit } from "./scenes/Scene6_HonestLimit";

export const SCENE_SECONDS = 10;
export const TOTAL_SCENES = 6;

export const MycorrhizalVideo: React.FC = () => {
  const { fps } = useVideoConfig();
  const sceneFrames = SCENE_SECONDS * fps;

  return (
    <AbsoluteFill style={{ background: palette.voidBlack }}>
      <Sequence from={0 * sceneFrames} durationInFrames={sceneFrames} layout="none">
        <Scene1_CostFraming sceneDurationFrames={sceneFrames} />
      </Sequence>
      <Sequence from={1 * sceneFrames} durationInFrames={sceneFrames} layout="none">
        <Scene2_BarrierReveal sceneDurationFrames={sceneFrames} />
      </Sequence>
      <Sequence from={2 * sceneFrames} durationInFrames={sceneFrames} layout="none">
        <Scene3_Stacking sceneDurationFrames={sceneFrames} />
      </Sequence>
      <Sequence from={3 * sceneFrames} durationInFrames={sceneFrames} layout="none">
        <Scene4_Robustness sceneDurationFrames={sceneFrames} />
      </Sequence>
      <Sequence from={4 * sceneFrames} durationInFrames={sceneFrames} layout="none">
        <Scene5_InterventionMatch sceneDurationFrames={sceneFrames} />
      </Sequence>
      <Sequence from={5 * sceneFrames} durationInFrames={sceneFrames} layout="none">
        <Scene6_HonestLimit sceneDurationFrames={sceneFrames} />
      </Sequence>
    </AbsoluteFill>
  );
};
