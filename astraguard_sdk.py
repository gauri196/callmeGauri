"""
AstraGuard 2.0 — Standard ATE SDK Client Module (M1 Contract Frozen)
=======================================================================
Provides standardized input/output contract for Automated Test Equipment (ATE)
and STDF/CSV ingestion interfaces.
"""

import time
import requests
import json
import pandas as pd
from typing import Dict, Any, Generator, List, Optional

class AstraGuardATE:
    """
    Official SDK Client for Automated Test Equipment (ATE) Integration.
    Encapsulates raw ATE measurement structures and communicates with AstraGuard Engine.
    """
    def __init__(self, endpoint: str = "http://localhost:8000", instrument_id: str = "ATE_CHAMBER_01", lot_id: str = "LOT_2026_01"):
        self.endpoint = endpoint.rstrip('/')
        self.instrument_id = instrument_id
        self.lot_id = lot_id
        self.is_connected = False

    def connect(self) -> bool:
        """Establishes connection to AstraGuard backend server."""
        try:
            res = requests.get(f"{self.endpoint}/", timeout=3)
            self.is_connected = (res.status_code == 200)
            return self.is_connected
        except Exception:
            self.is_connected = False
            return False

    def submit_measurement(self, component_id: str, measurements: Dict[str, float], wafer_x: float = 0.0, wafer_y: float = 0.0) -> Dict[str, Any]:
        """
        Submits parametric measurement payload from ATE test bench to AstraGuard.
        
        Usage:
            ate.submit_measurement(
                component_id="LOT10-C00421",
                measurements={"iddq_0h": 1.15, "iddq_24h": 1.37, "temperature": 125.0, "vcc": 3.96}
            )
        """
        iddq_0h = float(measurements.get("iddq_0h", measurements.get("iddq", 0.0)))
        iddq_24h = float(measurements.get("iddq_24h", measurements.get("iddq", 0.0)))
        
        payload = {
            "component_id": str(component_id),
            "iddq_0h": iddq_0h,
            "iddq_24h": iddq_24h,
            "wafer_x": float(wafer_x),
            "wafer_y": float(wafer_y)
        }
        
        res = requests.post(f"{self.endpoint}/api/v1/stage-a/predict-single", json=payload, timeout=5)
        if res.status_code == 200:
            data = res.json()
            data["instrument_id"] = self.instrument_id
            return data
        else:
            raise RuntimeError(f"HTTP Error {res.status_code}: {res.text}")

    def stream_lot_csv(self, csv_filepath: str, interval_sec: float = 0.1, max_records: int = 10) -> Generator[Dict[str, Any], None, None]:
        """Simulates real-time chamber testing by streaming ATE data line-by-line."""
        df = pd.read_csv(csv_filepath)
        if max_records > 0:
            df = df.head(max_records)
            
        for _, row in df.iterrows():
            measurements = {
                "iddq_0h": row.get("iddq_0h", 0.0),
                "iddq_24h": row.get("iddq_24h", 0.0)
            }
            result = self.submit_measurement(
                component_id=row["component_id"],
                measurements=measurements,
                wafer_x=row.get("wafer_x", 0.0),
                wafer_y=row.get("wafer_y", 0.0)
            )
            yield result
            time.sleep(interval_sec)

# Backward Compatibility Alias
AstraGuardATESDK = AstraGuardATE

if __name__ == "__main__":
    print("==================================================")
    print("      ASTRAGUARD 2.1 ATE SDK CLIENT               ")
    print("==================================================")
    ate = AstraGuardATE(endpoint="http://localhost:8000")
    print(f"Connecting to AstraGuard Backend at: {ate.endpoint}")
    if ate.connect():
        print("Status: Connected to AstraGuard Engine\n")
    else:
        print("Status: Offline / Standalone Mode (Backend not running on port 8000)\n")
