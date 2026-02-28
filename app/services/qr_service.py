"""QR code generation and signed scan URLs."""

import hashlib
import hmac
from io import BytesIO
from uuid import UUID

import qrcode

from app.core.config import get_settings


def _sign_asset_id(asset_id: str) -> str:
    """Create HMAC signature for asset id (optional; for tamper check)."""
    secret = get_settings().qr_signing_secret.encode()
    return hmac.new(secret, asset_id.encode(), hashlib.sha256).hexdigest()[:16]


def get_scan_url(asset_id: UUID) -> str:
    """Build public scan URL for asset (tokenized: asset id in path)."""
    base = get_settings().scan_base_url.rstrip("/")
    return f"{base}/scan/{asset_id}"


def generate_qr_image(asset_id: UUID) -> bytes:
    """Generate QR code image bytes (PNG) for asset scan URL."""
    url = get_scan_url(asset_id)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
