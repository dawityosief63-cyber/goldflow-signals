# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `README.md`: new **Usage** section with a small, runnable in-memory example.
- `CHANGELOG.md`: this file.

### Changed

- Imbalance detectors now use the chart builder's diagonal rule (`ratio`
  3.0, `min_vol` 1.0). The `threshold` option is removed.
- Stacked imbalance signals (`stacked_imbalance`, `stacked_imbalance_sell`).
- `FootprintChart.from_csv` accepts decimal volumes.
- Sample data and README examples updated to match.
