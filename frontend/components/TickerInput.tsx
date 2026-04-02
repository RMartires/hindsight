"use client";

interface Props {
  value: string;
  onChange: (ticker: string) => void;
}

export default function TickerInput({ value, onChange }: Props) {
  return (
    <div className="ticker-input-wrapper">
      <label className="field-label">TARGET ASSET</label>
      <input
        type="text"
        className="ticker-input"
        value={value}
        onChange={(e) => onChange(e.target.value.toUpperCase())}
        placeholder="NVDA"
        maxLength={20}
        spellCheck={false}
        autoComplete="off"
      />
    </div>
  );
}
