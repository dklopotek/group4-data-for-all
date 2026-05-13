type MushroomProps = {
  stemProgress: number;
  capProgress: number;
  wartsProgress: number;
};

const WARTS: { cx: number; cy: number; r: number }[] = [
  { cx: -32, cy: -8, r: 5 },
  { cx: -10, cy: -22, r: 6 },
  { cx: 14, cy: -16, r: 4.5 },
  { cx: 32, cy: -6, r: 5 },
  { cx: -22, cy: 4, r: 4 },
  { cx: 6, cy: 2, r: 4.5 },
  { cx: 24, cy: 6, r: 3.5 },
];

export const Mushroom: React.FC<MushroomProps> = ({
  stemProgress,
  capProgress,
  wartsProgress,
}) => {
  const stemHeight = 180 * stemProgress;
  const stemWidth = 38;
  const capScale = capProgress;
  const capArc = 1 - capProgress;

  return (
    <svg
      width={420}
      height={420}
      viewBox="-110 -260 220 280"
      style={{ overflow: "visible" }}
    >
      <ellipse cx={0} cy={6} rx={48} ry={10} fill="rgba(0,0,0,0.28)" />

      <g transform={`translate(0, 0)`}>
        <path
          d={`
            M ${-stemWidth / 2} 0
            Q ${-stemWidth / 2 - 6} ${-stemHeight * 0.5} ${-stemWidth / 2 + 2} ${-stemHeight}
            L ${stemWidth / 2 - 2} ${-stemHeight}
            Q ${stemWidth / 2 + 6} ${-stemHeight * 0.5} ${stemWidth / 2} 0
            Z
          `}
          fill="#f4ead7"
          stroke="#c9bd9c"
          strokeWidth={1.5}
        />
        <ellipse cx={0} cy={0} rx={stemWidth / 2 + 10} ry={6} fill="#e8dcbf" />
        {stemProgress > 0.6 && (
          <ellipse
            cx={0}
            cy={-stemHeight * 0.55}
            rx={stemWidth / 2 + 5}
            ry={3}
            fill="#ddd0ad"
            opacity={(stemProgress - 0.6) / 0.4}
          />
        )}
      </g>

      <g transform={`translate(0, ${-stemHeight}) scale(${capScale})`}>
        <path
          d={`
            M -70 0
            Q -70 ${-90 + capArc * 40} 0 ${-90 + capArc * 40}
            Q 70 ${-90 + capArc * 40} 70 0
            Q 50 8 0 8
            Q -50 8 -70 0
            Z
          `}
          fill="#c8332b"
          stroke="#7a1810"
          strokeWidth={2}
        />
        <path
          d={`
            M -55 2
            Q -55 ${-70 + capArc * 30} 0 ${-70 + capArc * 30}
            Q 55 ${-70 + capArc * 30} 55 2
          `}
          fill="none"
          stroke="#e35248"
          strokeWidth={2}
          opacity={0.5}
        />

        {WARTS.map((w, i) => (
          <circle
            key={i}
            cx={w.cx}
            cy={w.cy - (90 - capArc * 40) * 0.55}
            r={w.r * wartsProgress}
            fill="#fbf3df"
            opacity={wartsProgress}
          />
        ))}
      </g>
    </svg>
  );
};
