import { Composition } from "remotion";
import { AmanitaScene } from "./Composition";
import { MycorrhizalVideo } from "./MycorrhizalVideo";
import { HardwareVideo } from "./HardwareVideo";
import { MetricVideo } from "./MetricVideo";

// Square 1080×1080, 30fps. Project-pitch register.
const FPS = 30;
const WIDTH = 1080;
const HEIGHT = 1080;

// 60-second main video: 6 scenes × 10s × 30fps = 1800 frames
const MAIN_DURATION = 60 * FPS;

// Hardware III LCA installation simulation
const HW3_FPS = 30;
const HW3_WIDTH = 1920;
const HW3_HEIGHT = 1080;
const HW3_DURATION = 40 * HW3_FPS; // 1200 frames

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Hardware III — TouchDesigner LCA installation simulation */}
      <Composition
        id="HardwareIII"
        component={HardwareVideo}
        durationInFrames={HW3_DURATION}
        fps={HW3_FPS}
        width={HW3_WIDTH}
        height={HW3_HEIGHT}
      />
      {/* Hardware III — Metric UI product demo, 40s, 1920×1080 */}
      <Composition
        id="MetricUI"
        component={MetricVideo}
        durationInFrames={1200}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="MycorrhizalBCN"
        component={MycorrhizalVideo}
        durationInFrames={MAIN_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      {/* Kept for reference — original Amanita study */}
      <Composition
        id="Amanita"
        component={AmanitaScene}
        durationInFrames={120}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
