import socket
import ssl
from typing import Any
from gnmi.models.target import Target

def get_server_certificate(t: Target, context: ssl.SSLContext | None = None) -> dict[str, Any] | None:
    hostaddr, port = t.hostaddr_port
    context = context if context else ssl.create_default_context()
    with socket.create_connection((hostaddr, port)) as conn:
        with context.wrap_socket(conn, server_hostname=hostaddr) as sconn:
            return sconn.getpeercert()
