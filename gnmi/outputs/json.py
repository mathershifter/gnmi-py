
from typing import Any
import json
from decimal import Decimal
from gnmi.models.capabilities import CapabilityResponse
from gnmi.models.notification import Notification
from gnmi.outputs.output import Sinker

def _value_to_json(v: Any) -> Any:
    if isinstance(v, bytes):
        return v.decode()
    elif isinstance(v, list):
        return [_value_to_json(i) for i in v]
    elif isinstance(v, dict):
        return {k: _value_to_json(v) for k, v in v.items()}
    elif isinstance(v, (str, int, float, bool)) or v is None:
        return v
    elif isinstance(v, Decimal):
            return float(v)
    else:
        raise TypeError(f"Unsupported type for JSON serialization: {type(v)}")


class JsonNotification(Sinker):
    def send(self, data: Notification) -> None:
        out = {
            "timestamp": data.timestamp,
            "prefix": str(data.prefix),
            "atomic": data.atomic,
            "updates": [],
            "deletes": [],
        }
        for update in data.updates:
            out["updates"].append({
                "path": str(update.path),
                "val": _value_to_json(update.value.value),
            })
        for delete in data.deletes:
            out["deletes"].append({
                "path": str(delete)
            })
        print(json.dumps(out))
            

class JsonCapabilities(Sinker):
    def send(self, data: CapabilityResponse) -> None:
        print(json.dumps({
            "gnmi_version": data.gnmi_version,
            "supported_encodings": [e.name for e in data.supported_encodings],
            "supported_models": [
                {
                    "name": m.name,
                    "version": m.version,
                    "organization": m.organization,
                }
                for m in data.supported_models
            ],
        }))