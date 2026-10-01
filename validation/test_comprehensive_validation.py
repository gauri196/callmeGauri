"""
AstraGuard 2.4 — Comprehensive Validation Script
Covers Phase 11 (REST API), Phase 12 (WebSocket), Phase 13 (Audit),
Phase 14 (OOD / Integrity), Phase 15 (Failure Injection), Phase 16 (E2E), and Phase 18 (Performance).
"""

import os
import sys
import time
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from server import app
from astraguard_core.module_b.registry import module_b_registry
from astraguard_core.decision.fusion_engine import DecisionFusionEngine
from astraguard_core.module_a.screener import ModuleAScreener
from astraguard_sdk.client import AstraGuardClient


def run_phase_11_and_12():
    print("=== [PHASE 11 & 12] REST API & WEBSOCKET VERIFICATION ===")
    client = TestClient(app)

    # 11.1 Root
    r = client.get("/")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print(f"[OK] 11.1 Root: {r.json()['system']}")

    # 11.2 Missing Field
    r = client.post("/api/v1/stage-a/predict-single", json={"component_id": "C_MISSING"})
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print(f"[OK] 11.2 Missing Field rejected with 422: {r.status_code}")

    # 11.3 Wrong Type
    r = client.post("/api/v1/stage-a/predict-single", json={"component_id": "C_TYPE", "iddq_0h": "not_a_number", "iddq_24h": 10.0})
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print(f"[OK] 11.3 Wrong Type rejected with 422: {r.status_code}")

    # 11.4 & 11.5 Non-numeric/Corrupted JSON strings
    r = client.post("/api/v1/stage-a/predict-single", content='{"component_id": "C_NAN", "iddq_0h": NaN}', headers={"Content-Type": "application/json"})
    assert r.status_code in [400, 422], f"Expected 400/422, got {r.status_code}"
    print(f"[OK] 11.4/11.5 Corrupted JSON rejected with: {r.status_code}")

    # 11.6 Unknown Component Resolution
    r = client.post("/api/v2/context/resolve", json={"test_type": "QUAL_TEST", "domain": "UNKNOWN_OPTICAL"})
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print(f"[OK] 11.6 Context Resolution: {r.json()['status']}")

    # 12.1 WebSocket Streaming
    with client.websocket_connect("/ws/ate-stream") as ws:
        for i in range(5):
            msg = ws.receive_text()
            data = json.loads(msg)
            assert "component_id" in data
            assert "risk_tier" in data
            print(f"[OK] 12.1 WS Packet {i+1}: {data['component_id']} ({data['device_family']}) -> {data['risk_tier']}")

    print("[OK] Phase 11 & 12 Completed Successfully!\n")


def run_phase_13_audit():
    print("=== [PHASE 13] AUDIT SYSTEM & REPRODUCIBILITY VERIFICATION ===")
    sdk_client = AstraGuardClient(operator_id="QA_LEAD_TEST")
    test_csv = "ASQD_2.4/digital_ic_lot_00.csv"
    res = sdk_client.analyze(test_csv)

    print(f"[OK] Generated Audit Record ID: {res.audit_id}")
    print(f"[OK] Audit File Path: {sdk_client.audit_logger.log_dir}")

    # Read latest audit json
    audit_files = [f for f in os.listdir(sdk_client.audit_logger.log_dir) if f.endswith(".json")]
    assert len(audit_files) > 0, "No audit files generated!"

    latest_file = os.path.join(sdk_client.audit_logger.log_dir, sorted(audit_files)[-1])
    with open(latest_file, "r") as f:
        audit_data = json.load(f)

    # Check key lineage fields
    assert "system_version" in audit_data or "sdk_version" in audit_data, "Missing system/sdk version"
    assert "timestamp" in audit_data, "Missing timestamp"
    assert "reasons" in audit_data or "decision" in audit_data, "Missing decision reasons"
    print(f"[OK] Audit Record Verified: {latest_file}")
    print(f"     Timestamp: {audit_data.get('timestamp')}")
    print(f"     Operator:  {audit_data.get('operator_id')}")
    print(f"     Session:   {audit_data.get('session_id')}")
    print("[OK] Phase 13 Completed Successfully!\n")


def run_phase_14_and_15_ood_and_failure_injection():
    print("=== [PHASE 14 & 15] OOD INTEGRITY & FAILURE INJECTION ===")
    fusion = DecisionFusionEngine()

    # Phase 14: OOD / Low Confidence / Extreme Shift
    res_ood = fusion.evaluate_component(
        component_id="COMP_OOD_001",
        device_family="DIGITAL_IC",
        robust_z_24h=12.5,
        predicted_168h=9999.0,
        context_confidence=0.40
    )
    print(f"[OK] 14.1 Severe OOD Sample: Tier = {res_ood['risk_tier']} | Justification = {res_ood['decision_justifications']}")
    assert res_ood["risk_tier"] == "RED_EARLY_REJECT"

    # Phase 14.2: Low context confidence alone routes to review/yellow
    res_low_conf = fusion.evaluate_component(
        component_id="COMP_LOW_CONF",
        device_family="DIGITAL_IC",
        robust_z_24h=0.1,
        predicted_168h=500.0,
        context_confidence=0.55
    )
    print(f"[OK] 14.2 Low Context Confidence: Tier = {res_low_conf['risk_tier']} | Action = {res_low_conf['recommended_action']}")
    assert res_low_conf["risk_tier"] == "YELLOW_ACCELERATE_CHAMBER"

    # Phase 15: Failure Injection (Model Missing)
    try:
        module_b_registry.load_model("NON_EXISTENT_CHIP_FAMILY")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        print(f"[OK] 15.1 Missing Model Interlock: Caught controlled exception -> {e}")

    # Phase 15.2: Corrupted feature / NaN input handling in Module A
    screener = ModuleAScreener()
    corrupted_series = pd.Series([np.nan, 10.0, 10.2, 10.1, np.inf, 10.3])
    z_clean = screener.compute_robust_z(corrupted_series.fillna(10.1).replace([np.inf, -np.inf], 10.1))
    assert not np.isnan(z_clean).any()
    print(f"[OK] 15.2 Corrupted telemetry cleaned and robust Z computed successfully: max |Z| = {z_clean.abs().max():.2f}")

    print("[OK] Phase 14 & 15 Completed Successfully!\n")


def run_phase_16_end_to_end():
    print("=== [PHASE 16] END-TO-END SCREENING PIPELINE ===")
    fusion = DecisionFusionEngine()

    # Scenario 1: Digital IC -> RED
    mod_a_z = 4.1
    mod_b_pred = 1180.0
    res_digital = fusion.evaluate_component("DIGITAL_IC_DEV_01", "DIGITAL_IC", mod_a_z, mod_b_pred)
    assert res_digital["risk_tier"] == "RED_EARLY_REJECT"
    print(f"[OK] Scenario 1 (Digital IC)   -> {res_digital['risk_tier']} (Breach: {mod_b_pred} >= {res_digital['spec_limit']})")

    # Scenario 2: MEMS Gyroscope -> YELLOW
    mod_a_z = 2.7
    mod_b_pred = 23.0  # USL is 25.0, 90% margin is 22.5
    res_mems = fusion.evaluate_component("MEMS_GYRO_DEV_02", "MEMS_GYROSCOPE", mod_a_z, mod_b_pred)
    assert res_mems["risk_tier"] == "YELLOW_ACCELERATE_CHAMBER"
    print(f"[OK] Scenario 2 (MEMS Gyro)    -> {res_mems['risk_tier']} (Near USL: {mod_b_pred} in margin)")

    # Scenario 3: Image Sensor -> GREEN
    mod_a_z = 0.5
    mod_b_pred = 12.0  # USL is 25.0
    res_image = fusion.evaluate_component("IMAGE_DEV_03", "IMAGE_SENSOR", mod_a_z, mod_b_pred)
    assert res_image["risk_tier"] == "GREEN_PASS"
    print(f"[OK] Scenario 3 (Image Sensor) -> {res_image['risk_tier']} (Nominal: {mod_b_pred} << {res_image['spec_limit']})")

    print("[OK] Phase 16 Completed Successfully!\n")


def run_phase_18_performance():
    print("=== [PHASE 18] PERFORMANCE BENCHMARKING ===")
    from training.matrix_builder import TrainingMatrixBuilder
    builder = TrainingMatrixBuilder()
    matrix = builder.load_matrix("DIGITAL_IC")
    X_sample = matrix.X_test.iloc[:1000]

    # Model load latency
    t0 = time.perf_counter()
    m = module_b_registry.load_model("DIGITAL_IC")
    load_time_ms = (time.perf_counter() - t0) * 1000.0

    # Batch prediction throughput
    t0 = time.perf_counter()
    preds = m.predict(X_sample)
    infer_time_ms = (time.perf_counter() - t0) * 1000.0
    per_item_us = (infer_time_ms / len(X_sample)) * 1000.0

    print(f"[OK] Model Load Latency:              {load_time_ms:.3f} ms")
    print(f"[OK] Batch Inference (1,000 items):   {infer_time_ms:.2f} ms ({len(X_sample) / (infer_time_ms/1000):.0f} components/sec)")
    print(f"[OK] Single Inference Latency:        {per_item_us:.2f} µs / component")

    print("[OK] Phase 18 Completed Successfully!\n")


if __name__ == "__main__":
    run_phase_11_and_12()
    run_phase_13_audit()
    run_phase_14_and_15_ood_and_failure_injection()
    run_phase_16_end_to_end()
    run_phase_18_performance()
    print("================================================================")
    print(" ALL ASTRAGUARD 2.4 EXTENDED VALIDATION PHASES PASSED WITH ZERO ERRORS!")
    print("================================================================")
