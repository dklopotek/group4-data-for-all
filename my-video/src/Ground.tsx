type GroundProps = {
  heaveProgress: number;
};

export const Ground: React.FC<GroundProps> = ({ heaveProgress }) => {
  const heave = 22 * heaveProgress;

  return (
    <svg
      width={1080}
      height={520}
      viewBox="0 0 1080 520"
      style={{ position: "absolute", left: 0, bottom: 0 }}
    >
      <defs>
        <linearGradient id="soil" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="#5a3a22" />
          <stop offset="1" stopColor="#2e1d10" />
        </linearGradient>
      </defs>

      <path
        d={`
          M 0 ${120}
          Q 360 ${120 - heave * 0.3} 480 ${120 - heave * 0.7}
          Q 540 ${120 - heave} 600 ${120 - heave * 0.7}
          Q 720 ${120 - heave * 0.3} 1080 ${120}
          L 1080 520
          L 0 520 Z
        `}
        fill="url(#soil)"
      />

      {Array.from({ length: 14 }).map((_, i) => {
        const x = 540 + (i - 7) * 22 + (i % 2) * 6;
        const baseY = 120 - heave * Math.max(0, 1 - Math.abs(i - 7) / 7) * 0.6;
        return (
          <path
            key={i}
            d={`M ${x} ${baseY} Q ${x + 3} ${baseY - 14} ${x + 1} ${baseY - 22}`}
            stroke="#3f6b2a"
            strokeWidth={2.2}
            fill="none"
            strokeLinecap="round"
          />
        );
      })}
    </svg>
  );
};
