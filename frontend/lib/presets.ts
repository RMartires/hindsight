export interface HistoricalPreset {
  date: string;
  label: string;
  ticker: string;
  description: string;
}

export const HISTORICAL_PRESETS: HistoricalPreset[] = [
  {
    date: "2008-09-12",
    label: "Pre-Lehman",
    ticker: "GS",
    description: "Weekend before Lehman Brothers collapsed",
  },
  {
    date: "2010-05-06",
    label: "Flash Crash",
    ticker: "SPY",
    description: "Dow dropped 1,000 points in minutes",
  },
  {
    date: "2020-02-19",
    label: "Pre-COVID",
    ticker: "SPY",
    description: "S&P 500 all-time high before COVID selloff",
  },
  {
    date: "2020-03-23",
    label: "COVID Bottom",
    ticker: "AAPL",
    description: "Market bottom, massive rally follows",
  },
  {
    date: "2021-01-27",
    label: "GameStop",
    ticker: "GME",
    description: "GME short squeeze peak",
  },
  {
    date: "2022-11-08",
    label: "FTX Collapse",
    ticker: "COIN",
    description: "Day before FTX filed for bankruptcy",
  },
  {
    date: "2024-08-05",
    label: "Yen Unwind",
    ticker: "NVDA",
    description: "Global selloff from Japan rate hike",
  },
];

/** Pre-selected ticker/date on the home screen until the user picks another preset. */
export const DEFAULT_HOME_PRESET: HistoricalPreset = HISTORICAL_PRESETS[0]!;
