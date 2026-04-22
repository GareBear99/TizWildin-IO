#!/usr/bin/env python3
import json
from pathlib import Path

base = Path(__file__).resolve().parent
state = json.loads((base / "lovers_in_the_neon_build_state.json").read_text())

print("Loaded:", state["project"])
print("Tempo:", state["meta"]["bpm"], "BPM")
print("Key:", state["meta"]["key"])
print("This package is an honest clean-room rebuild scaffold, not a byte-exact recovery of the lost original script.")
print("Use the JSON build state as the reproducible rollback/edit point.")
