# 🛡️ AstraGuard 3.0 — Hybrid Reliability Intelligence Platform

> **Smart India Hackathon 2026 Submission** | **Problem Statement #SIH26170 (ISRO)**  
> *Physics-Informed Semiconductor Screening & In-Orbit Satellite Reliability Engine*

---

## 📖 System Architecture & Multi-Eye Intelligence

AstraGuard 3.0 is a research-grade, 4-Eye Hybrid Reliability Intelligence Platform engineered specifically for space-grade microelectronics qualification (MIL-STD-883, ESCC 9000) and satellite in-orbit telemetry monitoring.

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                     ASTRAGUARD 3.0 SYSTEM ARCHITECTURE                      │
 └─────────────────────────────────────────────────────────────────────────────┘

    [ASTRAGUARD ATE SDK]  ──(REST/JSON)──▶  [FASTAPI INGESTION ENGINE]
    (pip install astraguard-sdk)             (Port 8000)
             │                                      │
             ▼                                      ▼
    [ASQD 2.1 SIMULATOR]                  [PHYSICS & DATA NORMALIZER]
    (6 Failure Archetypes + Noise)         (Unit Scaling + Calibration)
                                                    │
             ┌──────────────────────────────────────┼──────────────────────────────────────┐
             ▼                                      ▼                                      ▼
    👁️ EYE 1: SPATIAL              👁️ EYE 2: PREDICTIVE                   👁️ EYE 3: UNSUPERVISED OOD
    Population Intelligence        Supervised ML (XGBoost)                Multi-Layer Anomaly Detector
             │                                      │                                      │
    • Robust Median / MAD          • 0h/24h -> 168h IDDQ Forecast         • Eye 3A: Isolation Forest (Static)
    • Dynamic Lot Z-Score          • Defect Risk Probability P(Defect)    • Eye 3B: LSTM Autoencoder (Temporal)
             │                                      │                                      │
             └──────────────────────────────────────┼──────────────────────────────────────┘
                                                    ▼
                                       [MULTI-EYE EVIDENCE FUSION]
                                      (Corroborating Evidence Matrix)
                                                    │
                                                    ▼
                                       [POLICY ENGINE (policy-3.0)]
                                       (GREEN / YELLOW / UNKNOWN / RED)
                                                    │
                                      ┌─────────────┴─────────────┐
                                      ▼                           ▼
                              [WEBSOCKET STREAM]          [SHAP & REASON CODES]
                                      │                           │
                                      └─────────────┬─────────────┘
                                                    ▼
                                      [NEXT.JS OPERATOR DASHBOARD]
                                      (Port 3000 - Live Interactive UI)
```

---

## ⚡ Quick Start & Live Demonstration Guide

Follow these steps for a complete offline/online demonstration in front of the panel:

### 1. Environment Setup & SDK Installation
```bash
# Clone repository and enter directory
cd "D:\SIH 2026"

# Install AstraGuard SDK cleanly
pip install -e .
```

### 2. Start the AstraGuard Backend Server
```bash
python server.py
```
*Backend API available at: `http://127.0.0.1:8000` | OpenAPI Docs: `http://127.0.0.1:8000/docs`*

### 3. Launch the Next.js Dashboard
```bash
cd dashboard
npm run dev
```
*Operator Dashboard accessible at: `http://localhost:3000`*

### 4. Run the Live ATE Chamber & Failure Injection Demo
In a separate terminal:
```bash
python ate_chamber_simulator.py
```

### 5. Run the Complete 8-Experiment Validation Suite
```bash
python -c "from validation.run_experiments import main; main()"
```

---

## 🔬 Validation & Defensibility Summary (AstraGuard 3.0)

| Experiment / Metric | Result | Meaning for Aerospace Screening |
| --- | --- | --- |
| **Exp 1: Predictive Horizon** | MAE = **0.08 µA** ($R^2 > 0.98$) | Accurately forecasts 168h leakage at 24h checkpoint |
| **Exp 2: Population Advantage** | Recall = **100.0%** ($F_1 = 0.96$) | Catches spatial and kinetics outliers without silent escapes |
| **Exp 3: Rare-Failure Sweep** | Recall = **100.0%** across $0.5\% \dots 8\%$ prevalence | Robust under extreme aerospace class imbalance |
| **Exp 4: Fault Separation** | Detection Rate = **100.0%** | Distinguishes component failure from ATE channel freeze |
| **Exp 7: Fingerprinting** | **20 JSON Fingerprints** generated | Pre-launch Stage A evidence persists into Stage B orbit |
| **Exp 8: Known vs Unknown** | Flagging Rate = **96.7%** (0% silent escapes) | LSTM AE + IsoForest flag unmodeled Class 6 mechanisms |
| **Stress Test A: Lot Shift** | Recall = **100.0%** | Robust against baseline manufacturing lot shifts (+0.45µA) |
| **Stress Test B: ATE Noise** | Recall = **100.0%** | Robust under extreme SMU measurement noise ($\sigma=0.25$) |

---

## 🎯 ISRO Panel Q&A Quick Reference

* **Q: "Where did you get your training data?"**  
  *A:* "ASQD 2.1 — a synthetic qualification dataset grounded in published semiconductor physics (Arrhenius thermal acceleration $E_a=0.68\text{ eV}$, Black's electromigration kinetics, and MEMS thermal stress). It is strictly synthetic, reproducible via lot random seeds, and validated against MIL-STD-883 screening statistics."

* **Q: "What if a component fails due to an unknown failure mechanism not in your training set?"**  
  *A:* "AstraGuard 3.0 uses a 4-Eye Hybrid Architecture. While XGBoost models known defect signatures, our Unsupervised Isolation Forest and LSTM Autoencoder monitor high-dimensional feature spaces and temporal evolution. In Experiment 8, Class 6 (Dielectric Oscillation) was withheld from training; the unsupervised layers flagged 96.7% of unknown parts, routing them to `UNKNOWN_PATTERN_REVIEW` with zero silent escapes."

* **Q: "Why does AstraGuard recommend extending burn-in rather than rejecting outright?"**  
  *A:* "AstraGuard recommends; the qualification authority decides. When an unknown or marginal pattern is detected, AstraGuard routes it to `YELLOW_REVIEW` or `UNKNOWN_PATTERN_REVIEW` for extended 240h burn-in or manual QA inspection, preventing premature scrap of high-value spaceflight lots while guaranteeing safety."
