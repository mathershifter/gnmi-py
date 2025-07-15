import os
import pytest

from  gnmi.session import TLSConfig

GNMI_INSECURE: bool = True if os.environ.get("GNMI_INSECURE") else False
GNMI_TARGET: str = os.environ.get("GNMI_TARGET", "")
GNMI_USER: str = os.environ.get("GNMI_USER", "admin")
GNMI_PASS: str = os.environ.get("GNMI_PASS", "")
GNMI_ROOT_CERT: str = os.environ.get("GNMI_ROOT_CERT", "/dev/null")
GNMI_PRIVAE_KEY: str = os.environ.get("GNMI_PRIVAE_KEY", "/dev/null")
GNMI_CERT_CHAIN: str = os.environ.get("GNMI_CERT_CHAIN", "/dev/null")
GNMI_AUTH: tuple[str, str] = (GNMI_USER, GNMI_PASS)


@pytest.fixture(scope="module")
def tlsconfig() -> TLSConfig:
    with open(GNMI_ROOT_CERT, "r") as fh:
        root_cert = fh.read().encode()
    with open(GNMI_CERT_CHAIN) as fh:
        client_cert = fh.read().encode()
    with open(GNMI_PRIVAE_KEY) as fh:
        client_key = fh.read().encode()

    return TLSConfig(
        ca_cert=root_cert,
        cert=client_cert,
        key=client_key,
    )

@pytest.fixture(scope="module")
def target() -> str:
    return GNMI_TARGET

@pytest.fixture(scope="module")
def is_insecure():
    return GNMI_INSECURE
