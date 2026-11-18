# Data provenance and permitted scope

## Original provider

- [NOAA Nationwide AIS 2024 metadata](https://www.fisheries.noaa.gov/inport/item/73064).
- [Marine Cadastre vessel traffic overview](https://coast.noaa.gov/digitalcoast/data/vesseltraffic.html).
- [Official archive index](https://noaaocm.blob.core.windows.net/ais/csv2/csv2024/index.html).
- [Data dictionary](https://coast.noaa.gov/data/marinecadastre/ais/data-dictionary.pdf).
- Source archive: `https://noaaocm.blob.core.windows.net/ais/csv2/csv2024/ais-2024-01-01.csv.zst`.

Data credit: U.S. Coast Guard Navigation Center, Bureau of Ocean Energy Management, NOAA Office for Coastal Management. NOAA metadata lists no access constraints and specifies coastal/ocean planning as the use constraint/purpose. This is a historical research illustration in that context. Preserve provider attribution and consult the metadata/distribution liability for other uses. The MIT code license does not relicense or claim ownership of underlying government observations.

## Upstream retained extract

The nationwide archive was downloaded and streamed for HarborScope on 17 November 2026. Archive size: 196,492,824 bytes. SHA256: `04e80b2f2896f51a7623e098eb48503b95786c9badf06550ce9e7d418654cb2d`. This is a locally computed integrity pin, not an independently supplied provider checksum.

Pinned upstream release: [HarborScope d8e1dcee](https://github.com/Ehsan-Ch/harborscope-ais-lab/tree/d8e1dcee1e8433e4153e24c00a3e49dc803b0e76). Its `download.py`, `build.py`, `analysis.py`, `config.json` and `data/extraction.json` document and reproduce the full archive extraction. It screened 7,293,408 reports, found 105,092 inside the rectangle, and retained 12,506 valid commercial reports from 36 vessels. Upstream excluded conflicting or identical vessel/time duplicates and invalid reports; no duplicates/conflicts occurred in this retained sample.

This project copies that release's `points.csv` byte for byte to `data/points.csv`. SHA256: `f36a975111b3e1fcbebd2ef6012ec635b9f44ddcf296b5b24590d4b429ac0484`. The original archive is not bundled. `data/source_manifest.json` preserves upstream archive provenance; this project did not redownload it. `fetch_data.py` can fetch and verify the exact reduced CSV from the pinned commit.

Fields: vessel alias, UTC time, latitude, longitude, reported speed (knots), reported AIS status and cargo/tanker kind. No vessel names, IMO identifiers, callsigns or MMSIs are included. Aliases V001–V036 replace identifiers, but tracks can still be linkable to public observations: anonymity is not guaranteed.

Only one day and one rectangle are retained. Reports outside the area and unreceived transmissions are absent. Labels are the observed positions, not a precise independent ground truth. AIS reported speed determines candidate inclusion but positions determine forecast velocity. There is no new tracking collection, live feed, person identification or operational vessel-control integration.
