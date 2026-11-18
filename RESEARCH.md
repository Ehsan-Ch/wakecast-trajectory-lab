# Research protocol

## Question and scope

How well do simple position-based models forecast a moving commercial vessel's displacement approximately ten minutes ahead, within the retained LA/Long Beach rectangle on 1 January 2024 UTC? This is a transparent baseline study, not a validated maritime autonomy model. The protocol and all three models are fixed for the report; no claim is made that they were preregistered externally.

## Data and geometry

The HarborScope retained subset contains 12,506 points and 36 vessel aliases. Study rectangle: latitude 33.65–33.85, longitude −118.30–−118.13. AIS cargo/tanker types 70–89 were included upstream. Inputs are strictly validated for finite coordinates, nonnegative speed and unique vessel/time keys. This project reuses the previously cleaned subset rather than scanning the national archive again. See DATA_NOTES.md for hashes and pinned extraction source.

Project in local equirectangular metres using R=6,371,000 m, reference latitude 33.75°, longitude −118.215°. East=R·Δlongitude(rad)·cos(reference latitude); north=R·Δlatitude(rad). This approximation is appropriate for a small rectangle, not global navigation. All displacement errors use the same coordinate system. No true heading or course measurement is used.

## Sampling and missing data

For each vessel, sorted by time:

1. Candidate origins require reported speed ≥2 knots and ≥300 seconds since the last candidate origin. Rejected candidates still consume spacing, so sampling does not depend on which labels happened to pass.
2. Choose the earliest history observation no more than 360 seconds before the origin. Require ≥120 seconds between it and the origin. All history points up to and including the origin are retained for inspection.
3. Find the nearest actual report to origin+600 seconds; break equal-distance ties toward the earlier time. Require absolute timing difference ≤60 seconds. No interpolation or endpoint extrapolation is used.
4. Require every consecutive report from history start through the target to have a gap ≤180 seconds. This label-quality check uses future report availability; it is not a deployable feature or a promise that a live target will be observed.
5. Assign the origin to a temporal split and exclude targets on or after the next split boundary. Train origins <12:00, calibration origins [12:00,18:00), test origins ≥18:00. All timestamps are UTC on the same day. The target must remain within the originating split. History may reach into an earlier window because it is already available at the origin.

171 candidate origins: 8 lacked sufficient history, 24 lacked a target within tolerance; no additional cases were rejected by gap or split-boundary rules in this particular sample. Accepted: 139. The rules for those edge cases are exercised synthetically in tests.

The retained target leads range from 9 minutes to 10 minutes 50 seconds (the acceptance range is 9–11 minutes). The model predicts displacement at the actual observed target lead, which is supplied as the query horizon during retrospective evaluation. Therefore this is not an exact 600-second endpoint benchmark. The feature velocity uses no future coordinates, speed, state or trajectory. Target availability and its timestamp are evaluation conditions.

Conditioning on continued within-rectangle reports causes selection bias: vessel exits, radio gaps and missing targets are absent. No imputation is made for these excluded futures. The results must not be generalized to all moving vessels or all times.

## Models

Let origin position be p, earliest accepted history position q, history duration Δt, and query lead L. Estimate v=(p−q)/Δt. Predictions relative to p:

- Hold position: (0,0).
- Constant velocity: vL.
- Fitted velocity: αvL. Fit α=Σ(actual displacement·vL)/Σ||vL||² on training cases alone, then clip to [0,1.5]. α=0.8690110700. This minimizes training squared endpoint error, not the median or mean Euclidean error, so it need not improve those metrics.

There is no model winner selected by calibration/test and no hyperparameter search. Report all models on the same cases. Origins at least five minutes apart can have overlapping labels/history; vessels can recur across time windows. Temporal splitting is not vessel-held-out validation.

## Empirical radii and scores

For each model separately, sort the 22 calibration endpoint errors. Use rank ceil((n+1)·0.9)=21 (one-based) as a circular radius around the predicted endpoint. The application uses the same radius across vessel-type and split filters; there is no subgroup recalibration. The routine rejects sample sizes for which that rank exceeds n, rather than inventing a finite quantile.

This follows a finite-sample quantile convention, but no conformal validity is claimed: serial dependence, overlapping windows, vessel concentration, spatial selection and time-of-day shifts violate exchangeability assumptions. Coverage is simply the observed fraction of errors ≤radius. Training/calibration coverage in the explorer is retrospective and not held-out performance. The circle represents endpoint error only, not a trajectory corridor or collision envelope.

Metrics are endpoint Euclidean error, case-weighted mean, lower nearest-rank median (ceil(n·0.5)), nearest-rank p90 (ceil(n·0.9)), and coverage. For even n the median is a lower order statistic, not the average of the two middle observations. `report.json` also includes vessel-macro mean errors: compute a mean per vessel, then average equally over vessels. No confidence intervals are claimed on this small dependent sample.

## Results and limits

Training/calibration/test have 87/22/30 cases and 11/3/4 vessels respectively. The test constant-velocity median is 586.87 m, mean 816.68 m, p90 1,831.17 m. The fitted model's median is 765.25 m, mean 829.37 m, p90 1,732.96 m. Holding position has median 1,833.29 m. Both motion models place 29 of 30 test endpoints inside their calibration radii; holding position places 27 of 30 inside. Broad radii and high observed coverage do not imply precise or safe forecasts.

Test vessel-macro means are 928.05 m constant velocity, 966.33 m fitted, and 1,939.55 m hold. There are only four test vessels; most cases come from a few short tracks. The fitted scale's effect is mixed, and there is no evidence it is universally better. One holiday, one rectangle, manual AIS attributes, receiver availability, local geometry and incomplete trajectories limit inference.

Next research steps would require multiple days and ports, vessel-held-out evaluation, wider-region data to measure exits, uncertainty assessed by vessel/day blocks, richer motion features, and a strictly future external evaluation. None of those validations is claimed here.
