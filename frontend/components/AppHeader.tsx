"use client";

import Image from "next/image";

interface Props {
  tradeDate: string;
  ticker: string;
}

function formatHeaderDate(dateStr: string): string {
  if (!dateStr) return "SELECT DATE";
  const parts = dateStr.split("-");
  if (parts.length !== 3) return dateStr.toUpperCase();
  const [yyyy, mm, dd] = parts;
  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const monthIndex = Number(mm) - 1;
  const day = Number(dd);
  const year = Number(yyyy);
  if (!Number.isFinite(monthIndex) || !monthNames[monthIndex]) return dateStr;
  return `${monthNames[monthIndex].toUpperCase()} ${day}, ${year}`;
}

export default function AppHeader({ tradeDate, ticker }: Props) {
  const dateLabel = formatHeaderDate(tradeDate);

  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-left">
          <div className="header-logo-wrap">
            <Image
              src="/hindsightagent.png"
              alt="Hindsight Agent"
              width={1024}
              height={1024}
              className="header-logo"
              priority
              sizes="(max-width: 480px) 112px, (max-width: 768px) 144px, 176px"
            />
          </div>
        </div>

        <div className="header-right">
          <div
            className="header-date-pill"
            title={ticker ? `${ticker} · ${tradeDate}` : undefined}
          >
            <span className="header-date-dot" aria-hidden />
            <span>
              {tradeDate ? dateLabel : "SELECT COORDINATES"}
              {ticker ? ` · ${ticker.toUpperCase()}` : ""}
            </span>
            <span className="header-date-chevron" aria-hidden>
              ▾
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
