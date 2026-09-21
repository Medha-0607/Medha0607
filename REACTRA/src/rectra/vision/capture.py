"""Image and metadata capture module for RECTRA.

Supports live camera and imported image capture modes, validates operator credentials,
and records explicit manual DEMO LOCATION or UNAVAILABLE GPS metadata.
"""

from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import BinaryIO

import cv2
import numpy as np
from PIL import Image

from rectra.core.constants import CaptureMode, GpsStatus
from rectra.core.exceptions import CaptureError
from rectra.core.types import CaptureMetadata

logger = logging.getLogger(__name__)


def load_image_to_bgr(
    source: bytes | BinaryIO | Image.Image | np.ndarray | str | Path,
) -> np.ndarray:
    """Load an image from various input sources into an OpenCV BGR numpy array."""
    try:
        if isinstance(source, (str, Path)):
            img = cv2.imread(str(source))
            if img is None:
                raise CaptureError(f"Failed to read image from path: {source}")
            return img

        if isinstance(source, np.ndarray):
            if len(source.shape) == 2:
                return cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
            elif source.shape[2] == 4:
                return cv2.cvtColor(source, cv2.COLOR_BGRA2BGR)
            return source.copy()

        if isinstance(source, Image.Image):
            rgb = np.array(source.convert("RGB"))
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        if isinstance(source, bytes):
            nparr = np.frombuffer(source, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise CaptureError("Failed to decode image bytes with OpenCV.")
            return img

        if hasattr(source, "read"):
            # File-like object (e.g. Streamlit UploadedFile)
            raw_bytes = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
            return load_image_to_bgr(raw_bytes)

        raise CaptureError(f"Unsupported image source type: {type(source)}")

    except Exception as exc:
        if isinstance(exc, CaptureError):
            raise
        raise CaptureError(f"Error processing captured image: {exc}") from exc


def create_capture_metadata(
    operator_id: str,
    capture_mode: str | CaptureMode = CaptureMode.IMPORTED_IMAGE,
    demo_latitude: float | None = None,
    demo_longitude: float | None = None,
    profile_id: str = "DEMO-ASSAY-001",
    profile_version: str = "1.0",
) -> CaptureMetadata:
    """Validate operator and create structured CaptureMetadata."""
    clean_operator = operator_id.strip()
    if len(clean_operator) < 3:
        raise CaptureError("Operator ID must be at least 3 characters in length.")

    # Determine GPS status based on explicit manual entry
    if demo_latitude is not None and demo_longitude is not None:
        gps_status = GpsStatus.MANUAL_DEMO
    else:
        gps_status = GpsStatus.UNAVAILABLE

    timestamp_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return CaptureMetadata(
        capture_mode=CaptureMode(capture_mode),
        timestamp_utc=timestamp_utc,
        operator_id=clean_operator,
        latitude=demo_latitude,
        longitude=demo_longitude,
        gps_status=gps_status,
        profile_id=profile_id,
        profile_version=profile_version,
    )
