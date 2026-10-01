"""
AstraGuard 2.0 — Milestone 2 & 9: Real-Time ATE Chamber Simulator & Failure Injector
====================================================================================
Simulates an active ATE burn-in chamber streaming raw measurements to AstraGuard SDK.
Includes live interactive failure injection modes (NORMAL, ACCELERATING_DRIFT, THERMAL_RUNAWAY).
"""

import time
import sys
import os
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import the ATE SDK client
from astraguard_sdk import AstraGuardATE, AstraGuardATESDK

class ATEChamberSimulator:
    def __init__(self, sdk):
        self.sdk = sdk

    def run_simulation(self, csv_filepath: str, max_components: int = 10, inject_fault_at: int = 5):
        print("\n" + "="*80)
        print("   ISRO ATE BURN-IN CHAMBER SIMULATOR (STDF / PARAMETRIC STREAM)")
        print("="*80)
        print(f"Chamber ID: {self.sdk.instrument_id} | Connected Lot: {self.sdk.lot_id}")
        print(f"Injecting Fault at Index: Component #{inject_fault_at}")
        print("-" * 80)
        print(f"{'INDEX':<6} | {'COMPONENT ID':<26} | {'0h IDDQ':<8} | {'24h IDDQ':<9} | {'PRED 168h':<12} | {'RISK TIER'}")
        print("-" * 80)

        df = pd.read_csv(csv_filepath).head(max_components)

        for idx, row in df.iterrows():
            comp_id = str(row["component_id"])
            iddq_0h = float(row.get("iddq_0h", row.get("value_0h", 12.0)))
            iddq_24h = float(row.get("iddq_24h", row.get("value_24h", 13.0)))

            # M9: Failure Injection Logic
            if idx >= inject_fault_at:
                # Inject accelerating degradation (Thermal Runaway / NBTI drift)
                iddq_24h = iddq_0h + 18.5 + (idx * 3.5)
                comp_id = comp_id + "_FAULT_INJECTED"

            measurements = {
                "iddq_0h": iddq_0h,
                "iddq_24h": iddq_24h
            }

            try:
                res = self.sdk.submit_measurement(
                    component_id=comp_id,
                    measurements=measurements,
                    wafer_x=float(row.get("wafer_x", 0.0)),
                    wafer_y=float(row.get("wafer_y", 0.0))
                )

                pred_168 = res.get("predicted_168h_iddq_ua", 0.0)
                tier = res.get("risk_tier", "UNKNOWN")
                badge = "[GREEN]" if "GREEN" in tier else "[YELLOW]" if "YELLOW" in tier else "[RED]"

                print(f"#{idx:<5} | {comp_id:<26} | {iddq_0h:>6.2f} uA | {iddq_24h:>7.2f} uA | {pred_168:>10.2f} uA | {badge} {tier}")
            except Exception as e:
                print(f"#{idx:<5} | {comp_id:<26} | ERROR: {e}")

            time.sleep(0.3)

        print("-" * 80)
        print(">> ATE Chamber Batch Stream Completed.\n")

if __name__ == "__main__":
    sdk = AstraGuardATE(endpoint="http://127.0.0.1:8000", instrument_id="ISRO_CHAMBER_SEC_04")
    if not sdk.connect():
        print(">> AstraGuard Backend Server is not running! Start server.py on port 8000.")
        sys.exit(1)

    simulator = ATEChamberSimulator(sdk)
    csv_file = "ASQD_2.4/digital_ic_lot_00.csv" if os.path.exists("ASQD_2.4/digital_ic_lot_00.csv") else "ASQD_2.4/asqd_24_blind_test.csv"
    simulator.run_simulation(csv_filepath=csv_file, max_components=10, inject_fault_at=6)
