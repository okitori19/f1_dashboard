# 🏎️ Formula 1 Telemetry Data Pipeline & BI Analytics

A Python-based data extraction and processing pipeline designed to pull Formula 1 telemetry data via [OpenF1](https://openf1.org/) and [FastF1](https://docs.fastf1.dev/), and structure it into optimized CSV datasets ready for **Tableau** visualization.

## 📌 Project Overview

Raw F1 telemetry provides sensor streams without explicit lap boundaries or BI-friendly data types. This project automates the extraction, transformation, and enrichment process to create analysis-ready datasets.

### Key Features
- **Comprehensive Telemetry Extraction:** Downloads speed, throttle, brake, RPM, gear, DRS status, and 3D track coordinates ($X, Y, Z$) for all session laps.
- **Session Metadata Enrichment:** Merges lap-level attributes directly into telemetry points, including `Driver`, `LapNumber`, `SessionKey`, and `MeetingKey`.
- **Pit Strategy Flags:** Computes custom boolean indicators (`IsPitOutLap`, `IsPitInLap`) based on pit timings.
- **BI & Tableau Optimization:** 
  - Converts native Pandas `Timedelta` fields into floating-point seconds (`LapTimeSeconds`) to enable seamless aggregation (`AVG`, `MIN`, `SUM`) in Tableau.
  - Extracts circuit track layout metadata (`circuit_info.corners`) to support dual-axis map layers with turn numbers.
- **Export Pipeline:** Generates structured CSV files ready for import into BI platforms.

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Data Acquisition:** `OpenF1`, `FastF1` (FIA Live Timing API wrapper)
- **Data Transformation:** `Pandas`
- **Visualization:** Tableau Desktop / Tableau Public

---

## 🙏 Acknowledgements & Data Sources

- Data provided by the **[FastF1 Python Library](https://docs.fastf1.dev/)** and [OpenF1](https://openf1.org/).
- Formula 1 telemetry and timing data are sourced from FIA Live Timing endpoints.
