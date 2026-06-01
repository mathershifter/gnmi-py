import socket
import ssl
from dataclasses import dataclass
from gnmi.models.target import Target


@dataclass
class TLSConfig:
    ca_cert: bytes | None
    client_cert: bytes | None
    client_key: bytes | None
    get_server_cert: bool = False
    no_verify: bool = False

    @property
    def context(self):
        if self.ca_cert:
            return ssl.create_default_context(cadata=self.ca_cert)

        if self.no_verify:
            context = ssl._create_unverified_context()
            context.check_hostname = False
            return context

        return ssl.create_default_context()


def get_server_certificate(
    t: Target, context: ssl.SSLContext | None = None, pem: bool = False
) -> bytes | None:
    hostaddr, port = t.hostaddr, t.port
    context = context if context else ssl.create_default_context()
    with socket.create_connection((hostaddr, port)) as conn:
        with context.wrap_socket(conn, server_hostname=hostaddr) as sconn:
            cert = sconn.getpeercert(binary_form=True)
            if not cert:
                return None
            if pem:
                return ssl.DER_cert_to_PEM_cert(cert).encode()
            return cert
