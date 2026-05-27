
from rich import pretty
from rich.console import Console  # type: ignore[import]

from gnmi.models.capabilities import CapabilityResponse
from gnmi.models.notification import Notification

class PrettyOutput:
    def send(self, m: object) -> None:
        console = Console()
        console.print(pretty.pretty_repr(m))

class PrettyNotification:
    def send(self, m: Notification) -> None:
        console = Console()
        console.print(pretty.pretty_repr(m))

class PrettyCapabilities:
    def send(self, m: CapabilityResponse) -> None:
        console = Console()
        console.print(f"gNMI Version: {m.gnmi_version}")
        console.print(
            "Encodings: "
            + ", ".join(e.name for e in m.supported_encodings)
        )
        console.print("Models:")
        for mdl in m.supported_models:
            console.print(f" {mdl.name}")
            console.print(f"    Version:      {mdl.version or 'n/a'}")
            console.print(f"    Organization: {mdl.organization}")