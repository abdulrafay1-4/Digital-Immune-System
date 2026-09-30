# Data

The evaluation runs mostly on seeded synthetic telemetry, which is generated at run time and
needs no files. Three experiments use real data. The LANL files are in this folder; TON_IoT
must be downloaded (below).

| File | What it is | Used by |
|---|---|---|
| `ton_iot/Train_Test_Network.csv.gz` | TON_IoT network flows, train/test sample (not included: see below) | `m8_eval_harness.ton_iot` |
| `ton_iot/Train_Test_Windows_7.csv.gz` | TON_IoT Windows 7 host counters, train/test sample (not included) | `m8_eval_harness.ton_iot_windows` |
| `ton_iot/Train_Test_Windows_10.csv.gz` | TON_IoT Windows 10 host counters, train/test sample (not included) | `m8_eval_harness.ton_iot_windows` |
| `lanl/redteam.txt.gz` | LANL red-team authentication events (the original file) | `m8_eval_harness.lanl_identity` |
| `lanl/features.npz` | Per-device, per-hour authentication features extracted from the LANL log | `m8_eval_harness.lanl_identity` |
| `lanl/extract.json` | Counts from that extraction | reference |

## TON_IoT

The dataset's terms allow academic use but do not grant redistribution, so the files are not in
this repository. Download the official train/test files `Train_Test_Network.csv`,
`Train_Test_Windows_7.csv` and `Train_Test_Windows_10.csv` from the source below into
`data/ton_iot/`, then run

    python scripts/fetch_ton_iot.py

which checks each file's SHA-256 against the one the calibration recorded
(`configs/ton_iot_calibration.json`, `configs/ton_iot_windows_calibration.json`) and compresses
it where the code reads it. The experiments refuse to run on a file that does not match.

Source: https://research.unsw.edu.au/projects/toniot-datasets

Terms, as stated by the dataset's author: free use for academic research purposes; commercial
use requires permission from Dr Nour Moustafa (UNSW Canberra). Anyone using the data must cite
the dataset papers:

1. N. Moustafa, "A new distributed architecture for evaluating AI-based security systems at
   the edge: Network TON_IoT datasets," *Sustainable Cities and Society*, vol. 72, 102994, 2021.
2. T. M. Booij, I. Chiscop, E. Meeuwissen, N. Moustafa and F. T. H. den Hartog, "ToN_IoT: The
   role of heterogeneity and the need for standardization of features and attack types in IoT
   network intrusion datasets," *IEEE Internet of Things Journal*, 2021.
3. A. Alsaedi, N. Moustafa, Z. Tari, A. Mahmood and A. Anwar, "TON_IoT telemetry dataset: A new
   generation dataset of IoT and IIoT for data-driven intrusion detection systems," *IEEE
   Access*, vol. 8, pp. 165130-165150, 2020.
4. N. Moustafa, M. Keshk, E. Debie and H. Janicke, "Federated TON_IoT Windows datasets for
   evaluating AI-based security applications," *IEEE TrustCom*, pp. 848-855, 2020.
5. N. Moustafa, M. Ahmed and S. Ahmed, "Data analytics-enabled intrusion detection: Evaluations
   of ToN_IoT Linux datasets," *IEEE TrustCom*, pp. 727-735, 2020.
6. N. Moustafa, "New generations of Internet of Things datasets for cybersecurity applications
   based machine learning: TON_IoT datasets," *eResearch Australasia Conference*, 2019.
7. N. Moustafa, "A systemic IoT-Fog-Cloud architecture for big-data analytics and cyber
   security systems," arXiv:1906.01055, 2019.
8. J. Ashraf, M. Keshk, N. Moustafa, M. Abdel-Basset, H. Khurshid, A. D. Bakhshi and R. R.
   Mostafa, "IoTBoT-IDS: A novel statistical learning-enabled botnet detection framework for
   protecting networks of smart cities," *Sustainable Cities and Society*, 103041, 2021.

## LANL

From "Comprehensive, Multi-Source Cyber-Security Events", Los Alamos National Laboratory,
released under CC0: "To the extent possible under law, Los Alamos National Laboratory has
waived all copyright and related or neighboring rights."

Source: https://csr.lanl.gov/data/cyber1/

Cite: A. D. Kent, "Comprehensive, Multi-Source Cyber-Security Events," Los Alamos National
Laboratory, 2015, doi:10.17021/1179829.

`redteam.txt.gz` is the original file. The full authentication log (`auth.txt.gz`, 7.6 GB) is
too large for this repository, so `features.npz` holds what the experiment reads from it. To
rebuild the features yourself, download `auth.txt.gz` from the source above into `data/lanl/`
and run:

    python -m m8_eval_harness.lanl_identity extract

The extraction reads the first 30 days of the log in one pass and takes several minutes. The
SHA-256 of both LANL files is recorded in `configs/lanl_identity_calibration.json`.
