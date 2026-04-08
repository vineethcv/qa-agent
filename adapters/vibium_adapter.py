from __future__ import annotations

import os
import time
from typing import Optional


class VibiumAdapterError(Exception):
    pass


class VibiumAdapter:
    """
    V1 Vibium Adapter (Stub Implementation)

    Responsibilities:
    - Provide a stable interface for browser actions
    - Hide Vibium-specific implementation details
    - Be easily replaceable with real Vibium integration later

    Current behavior:
    - Simulates actions
    - Logs all interactions
    - Creates fake screenshots (text files for now)

    Future:
    - Replace internal methods with Vibium CLI / MCP / SDK calls
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session_active = False

    # ----------------------------
    # Session lifecycle
    # ----------------------------

    def start(self) -> None:
        self._log("Starting browser session")
        self.session_active = True

    def close(self) -> None:
        self._log("Closing browser session")
        self.session_active = False

    # ----------------------------
    # Core browser actions
    # ----------------------------

    def open(self, path: str) -> None:
        self._ensure_session()

        url = path if path.startswith("http") else f"{self.base_url}{path}"
        self._log(f"OPEN → {url}")

        # TODO: Replace with Vibium navigation

    def click(self, target: str) -> None:
        self._ensure_session()
        self._log(f"CLICK → {target}")

        # TODO: Replace with Vibium click

    def fill(self, target: str, value: str) -> None:
        self._ensure_session()
        self._log(f"FILL → {target} = {value}")

        # TODO: Replace with Vibium fill

    def assert_text(self, text: str) -> bool:
        self._ensure_session()
        self._log(f"ASSERT TEXT → '{text}'")

        # ---- Stub logic ----
        # Simulate failure if specific keyword appears
        if "FAIL" in text.upper():
            return False

        return True

    # ----------------------------
    # Evidence
    # ----------------------------

    def screenshot(self, path: str) -> str:
        self._ensure_session()

        os.makedirs(os.path.dirname(path), exist_ok=True)

        # For V1: create a dummy file to simulate screenshot
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Screenshot placeholder at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        self._log(f"SCREENSHOT → {path}")
        return path

    # ----------------------------
    # Helpers
    # ----------------------------

    def _ensure_session(self) -> None:
        if not self.session_active:
            raise VibiumAdapterError("Session not started. Call start() first.")

    def _log(self, message: str) -> None:
        print(f"[VIBIUM] {message}")