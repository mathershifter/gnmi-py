import json
from gnmi.models.capabilities import CapabilityResponse
from gnmi.models.notification import Notification


class JsonNotification:
    def send(self, data: Notification) -> None:
        target = str(data.prefix.target) if data.prefix and data.prefix.target else ""
        out = {
            "timestamp": data.timestamp,
            "prefix": str(data.prefix),
            "target": target,
            "atomic": data.atomic,
            "updates": [],
            "deletes": [],
        }
        for update in data.updates:
            out["updates"].append(
                {
                    "path": str(update.path),
                    "val": update.value.to_json(),
                }
            )
        for delete in data.deletes:
            out["deletes"].append({"path": str(delete)})
        print(json.dumps(out))


class JsonCapabilities:
    def send(self, data: CapabilityResponse) -> None:
        print(
            json.dumps(
                {
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
                }
            )
        )
