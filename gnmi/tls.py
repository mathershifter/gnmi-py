import socket
import ssl
from typing import Any
from dataclasses import dataclass
from gnmi.models.target import Target

@dataclass
class TLSConfig:
    ca_cert: bytes | None
    client_cert: bytes | None
    client_key: bytes | None
    get_server_cert: bool = False

    @property
    def context(self):
        if self.ca_cert:
            return ssl.create_default_context(cadata=self.ca_cert)
        return ssl.create_default_context()

def get_server_certificate(t: Target, context: ssl.SSLContext | None = None, pem: bool = False) -> bytes | None:
    hostaddr, port = t.hostaddr_port
    context = context if context else ssl.create_default_context()
    with socket.create_connection((hostaddr, port)) as conn:
        with context.wrap_socket(conn, server_hostname=hostaddr) as sconn:
            der_cert = sconn.getpeercert(binary_form=True)
            if not der_cert:
                return None
            
            if pem:
                return ssl.DER_cert_to_PEM_cert(der_cert).encode()
            
            return der_cert
