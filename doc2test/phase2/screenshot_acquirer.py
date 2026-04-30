"""Phase 2 — Screenshot Acquirer (deterministic).

Captures a full-page screenshot, including off-screen elements, for
multimodal LLM analysis (paper Tab. 2).
"""
from __future__ import annotations

from io import BytesIO

from PIL import Image
from selenium.webdriver.remote.webdriver import WebDriver


class ScreenshotAcquirer:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def capture(self) -> bytes:
        # Full-page via CDP when available (Chrome), fallback to viewport.
        try:
            metrics = self.driver.execute_cdp_cmd(
                "Page.getLayoutMetrics", {}
            )
            content = metrics["contentSize"]
            self.driver.execute_cdp_cmd(
                "Emulation.setDeviceMetricsOverride",
                {
                    "mobile": False,
                    "deviceScaleFactor": 1,
                    "width": int(content["width"]),
                    "height": int(content["height"]),
                },
            )
            png = self.driver.get_screenshot_as_png()
            self.driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
            return png
        except Exception:
            return self.driver.get_screenshot_as_png()

    @staticmethod
    def thumbnail(png: bytes, max_dim: int = 1600) -> bytes:
        img = Image.open(BytesIO(png))
        img.thumbnail((max_dim, max_dim))
        out = BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
