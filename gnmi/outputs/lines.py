import json
from gnmi.models.notification import Notification
from gnmi.util import datetime_from_int64
from rich.console import Console
from rich.markup import escape

class StreamingNotification:
    def send(self, m: Notification) -> None:
        console = Console()
        timestamp = datetime_from_int64(m.timestamp).isoformat()
        target = str(m.prefix.target) if m.prefix and m.prefix.target else "*"
        prefix = m.prefix
        atomic = m.atomic

        for update in m.updates:
            path = escape(str(prefix / update.path))
            console.print(f"{timestamp} {target} [blue]UPDATE[/blue] {path} {update.value.value}")
        for delete in m.deletes:
            path = escape(str(prefix / delete))
            console.print(f"{timestamp} {target} {atomic} [red]DELETE[/red] {path}")

class JsonLinesNotification:
    def send(self, data: Notification) -> None:
        console = Console()
        timestamp = data.timestamp
        prefix = str(data.prefix)
        atomic = data.atomic
        for update in data.updates:
            out = {
                "timestamp": timestamp,
                "prefix": prefix,
                "atomic": atomic,
                "path": str(update.path),
                "val": update.value.to_json(),
            }
            print(json.dumps(out))
        for delete in data.deletes:
            out = {
                "timestamp": timestamp,
                "prefix": prefix,
                "atomic": atomic,
                "path": str(delete),
                "deleted": True,
            }
            console.print_json(json.dumps(out), indent=0)
