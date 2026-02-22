from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.procurement import WarenEingang


class SupplierAdapter(ABC):
    @abstractmethod
    def parse_lieferschein(self, raw_payload: str) -> WarenEingang:
        """Parse supplier payload into normalized WarenEingang."""

    @abstractmethod
    def to_wareneingang(self, payload: dict[str, Any]) -> WarenEingang:
        """Convert a normalized dict payload into the unified domain object."""

    def send_bestellung(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("This supplier adapter does not implement send_bestellung")

    def sync_katalog(self) -> dict[str, Any]:
        raise NotImplementedError("This supplier adapter does not implement sync_katalog")


class FiscalAdapter(ABC):
    @abstractmethod
    def sign(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Sign fiscal payload and return signature metadata."""

    @abstractmethod
    def dep_write(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Persist DEP record."""

    @abstractmethod
    def beleg_ops(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle start/Jahresbeleg operations."""


class AccountingExportAdapter(ABC):
    @abstractmethod
    def export_start(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Start export job."""

    @abstractmethod
    def export_status(self, export_id: str) -> dict[str, Any]:
        """Read export state."""


class NotificationAdapter(ABC):
    @abstractmethod
    def send_alert(self, channel: str, payload: dict[str, Any]) -> None:
        """Send a deployment/runtime alert."""
