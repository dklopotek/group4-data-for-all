import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Ground } from "./Ground";
import { Mushroom } from "./Mushroom";

type Growth = {
  heaveProgress: number;
  stemProgress: number;
  capProgress: number;
  wartsProgress: number;
};

// ─────────────────────────────────────────────────────────────────────
// TODO (you): Implement growth choreography.
//
// You receive `frame` (current frame, 0..119) and `fps` (30).
// Return four progress values, each clamped 0..1:
//
//   heaveProgress  — soil bulges up before mushroom appears
//   stemProgress   — stem rises from soil
//   capProgress    — cap expands from button to umbrella
//   wartsProgress  — white warts (universal veil remnants) fade in on cap
//
// Real Amanita stages (use these as a guide, not a recipe):
//   0.0–0.5s  soil heaves                   (heave: 0 → 1)
//   0.4–1.6s  stem stretches up             (stem: 0 → 1)
//   1.2–2.8s  cap unfurls (button → umbrella) (cap: 0 → 1)
//   1.8–3.0s  warts appear during cap expansion (warts: 0 → 1)
//   3.0–4.0s  hold final pose
//
// Trade-offs to consider:
//   • Easing.bezier(0.16, 1, 0.3, 1)   — fast pop + slow settle (organic)
//   • Easing.out(Easing.cubic)         — gentle deceleration (calm)
//   • Easing.elastic(1)                — overshoots (cartoon, not realistic)
//   • Linear (no easing)               — robotic, avoid
//
// Use `interpolate(frame, [startFrame, endFrame], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ... })`.
// ─────────────────────────────────────────────────────────────────────
const useGrowth = (frame: number, fps: number): Growth => {
  // Replace these placeholders with your choreography.
  const heaveProgress = interpolate(frame, [0, 0.5 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const stemProgress = interpolate(frame, [0.4 * fps, 1.6 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  const capProgress = interpolate(frame, [1.2 * fps, 2.8 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const wartsProgress = interpolate(frame, [1.8 * fps, 3.0 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  return { heaveProgress, stemProgress, capProgress, wartsProgress };
};

export const AmanitaScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { heaveProgress, stemProgress, capProgress, wartsProgress } =
    useGrowth(frame, fps);

  return (
    <AbsoluteFill
      style={{
        background:
          "linear-gradient(180deg, #cfe5d8 0%, #a9cdb4 55%, #87b294 100%)",
      }}
    >
      <Ground heaveProgress={heaveProgress} />

      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems: "center",
          paddingBottom: 110,
        }}
      >
        <Mushroom
          stemProgress={stemProgress}
          capProgress={capProgress}
          wartsProgress={wartsProgress}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
