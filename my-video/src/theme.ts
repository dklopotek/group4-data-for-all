// Mycorrhizal Barcelona — visual palette
// Underground feel: forest greens, soft amber/copper accents, off-white text.
// Deliberately not corporate teal, not bright. Calibrated to a planner-pitch register.

export const palette = {
  // Backgrounds — deep forest / soil / underground
  voidBlack: "#0a0d0b",
  soilDeep: "#15201a",
  soilMid: "#1d2c24",
  forest: "#243b30",
  mossDark: "#2f4a3c",
  mossMid: "#3d5a48",

  // Foreground — off-white
  paper: "#efe9d8",
  paperDim: "#cfc8b6",
  paperFaint: "rgba(239, 233, 216, 0.55)",

  // Accents — copper / amber, sparingly
  amber: "#c8924a",
  copper: "#a86a3a",
  ember: "#8a4a1f",

  // Data colours — barriers and interventions
  sealed: "#7a8087", // gray wash, sealed surface
  heat: "#c45a3b", // restrained red, heat anomaly
  bare: "#c8a346", // muted yellow, low canopy
  zone: "#efe9d8", // off-white for highlighted zones

  // Intervention types
  depaving: "#5b8db8", // muted blue
  cooling: "#c45a3b", // matches heat
  planting: "#6b9c5a", // muted green
};

// Easing — soft enter, no bouncy springs.
// Use these as defaults across the video.
export const easing = {
  // Smooth entry, slow settle
  softEnter: [0.22, 1, 0.36, 1] as const,
  // Calm linear-ish for atmospheric drifts
  drift: [0.4, 0, 0.6, 1] as const,
  // Gentle out — for elements settling
  out: [0.16, 1, 0.3, 1] as const,
};

// Typography
export const typography = {
  // Serif display — for scene titles (Cardo / Cormorant fallback to system serif)
  serif:
    '"Cormorant Garamond", "Cardo", "EB Garamond", Georgia, "Times New Roman", serif',
  // Sans for data and captions
  sans:
    '"Inter", "Helvetica Neue", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
  // Monospace for cell IDs
  mono: '"JetBrains Mono", ui-monospace, "Menlo", "Consolas", monospace',
};

// Standard subtitle styling
export const subtitleStyle: React.CSSProperties = {
  fontFamily: typography.sans,
  fontSize: 28,
  fontWeight: 400,
  lineHeight: 1.45,
  color: palette.paper,
  letterSpacing: 0.2,
  textAlign: "center",
  maxWidth: 760,
  padding: "0 60px",
};

// Standard title style (serif)
export const titleStyle: React.CSSProperties = {
  fontFamily: typography.serif,
  fontWeight: 400,
  fontStyle: "italic",
  fontSize: 44,
  lineHeight: 1.2,
  color: palette.paper,
  letterSpacing: 0.5,
  textAlign: "center",
};

// Caption — for tiny metadata (frame count, scene id)
export const captionStyle: React.CSSProperties = {
  fontFamily: typography.mono,
  fontSize: 14,
  fontWeight: 400,
  color: palette.paperFaint,
  letterSpacing: 1.5,
  textTransform: "uppercase",
};
