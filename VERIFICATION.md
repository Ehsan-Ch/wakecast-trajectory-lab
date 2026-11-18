# Release verification — 18 November 2026

Research release: `d6ca9c803168fc19af5f3da3097919b008baa7d5`.

## Repository and reproduction

All 25 release files matched local staged Git blob hashes against the remote tree, including the input CSV, report, workflow, source and screenshot. Local Git was synchronized with origin/main after publication. The retained CSV restoration from the pinned upstream commit also passed its independent expected SHA256 check.

[Research checks](https://github.com/Ehsan-Ch/wakecast-trajectory-lab/actions/runs/44388958175) succeeded on Python 3.11, Python 3.12 and Node 22. There are 12 Python unit tests and four JavaScript tests. Full report reconciliation rebuilt all 139 cases, temporal partitions, fitted scale, empirical radii, metrics and input hashes. Numeric comparisons allow tight cross-platform floating-point tolerances; identity fields and hashes remain exact.

Synthetic checks include linear motion, future-coordinate feature isolation, split-boundary embargoes, coverage gaps, absent targets, origin speed/spacing, quantile rank, coefficient bounds, local projection and duplicate input rejection. JavaScript checks reconcile browser metrics, filtered export identity/error values, empty cohorts and independently reconstructed endpoint errors.

## Deployment and browser evidence

The [Pages deployment](https://github.com/Ehsan-Ch/wakecast-trajectory-lab/actions/runs/44388973384) completed successfully for the research release. The [public lab](https://ehsan-ch.github.io/wakecast-trajectory-lab/) displayed 30 test cases across four vessels, constant-velocity median error 587 m, p90 1,831 m and observed radius coverage 96.7%.

Public calibration/tanker/hold selection displayed eight cases from one vessel. The downloaded CSV matched all eight IDs, origins, targets and actual leads, plus all 24 model errors and 48 forecast displacement coordinates. Hiding later observations removed their plot geometry and endpoint-error detail; aggregate scores remained explicitly retrospective. The default test/all/constant-velocity selection was restored before final handoff.

Local testing additionally exercised cargo/fitted selection, next-case navigation and reveal/hide. All 12 locally exported cargo test case identities/timestamps and 36 errors matched the report. Desktop layout, plot, controls and comparison table were visually inspected. Public proof was saved outside the repository; `preview.jpg` records the local desktop layout. Mobile and exhaustive cross-browser testing are not claimed.

## Limits

Verification reconstructs forecasts from included retained points; it does not rescan a fresh national archive. This is a one-day, one-region historical benchmark. Missing/out-of-area targets are excluded; temporal windows contain dependent cases and repeated vessels. Forecasts are evaluated at actual observed 9–11 minute query leads, not exact 600-second endpoints. Radius coverage has no operational or exchangeability-based guarantee. See RESEARCH.md and DATA_NOTES.md.
