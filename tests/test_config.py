import importlib.util

import pytest

import gnmi.environments
from gnmi.config import Config
from gnmi.util import load_rc
# from pprint import pprint
YAML_SUPPORTED=False
# try:
#     import yaml
#     YAML_SUPPORTED=True
# except ImportError:
#     pass

# import importlib.util

if importlib.util.find_spec('yaml'):
    YAML_SUPPORTED=True

GNMI_CONFIG_FILE = "./examples/subscription.yaml"

CONFIG_DATA = """
metadata:
    username: admin
    password: "" 

get:
    paths:
        - /process[pid=*]/state

    options:
        encoding: json
    prefix: /system/processes
    type: all
"""

CONFIG_EXPECTED = Config({
    "metadata": {
        "username": "admin",
        "password": "",
    },
    "get": {
        "paths": [
            "/process[pid=*]/state",
        ],
        "prefix": "/system/processes",
        "type": "all",
        "options": {
            "encoding": "json"
        }
    }
})

gnmi.environments.GNMI_RC_PATH = "./examples"

@pytest.mark.skipif(not YAML_SUPPORTED, reason="yaml module missing")
def test_load_rc():
    rc = load_rc()
    for sec in ["metadata", "get", "subscribe"]:
        assert sec in rc.keys()
    #pprint(rc.dump())

@pytest.mark.skipif(not YAML_SUPPORTED,  reason="yaml module missing")
def test_config_load():
    conf = Config.load_file(GNMI_CONFIG_FILE)

    assert isinstance(conf, Config), "Loaded did not return a Config object"

@pytest.mark.skipif(not YAML_SUPPORTED,  reason="yaml module missing")
def test_construct():
    conf = Config.load(CONFIG_DATA)
    assert isinstance(conf, Config), "Loaded did not return a Config object"

@pytest.mark.skipif(not YAML_SUPPORTED,  reason="yaml module missing")
def test_iter():
    
    conf = Config.load(CONFIG_DATA)

    for path in conf["get"].paths:
        assert path in ("/system/config/hostname", "/process[pid=*]/state")

@pytest.mark.skipif(not YAML_SUPPORTED,  reason="yaml module missing")
def test_len():
    conf = Config.load(CONFIG_DATA)
    assert len(conf) > 0

@pytest.mark.skipif(not YAML_SUPPORTED,  reason="yaml module missing")
def test_dump():
    conf = Config.load(CONFIG_DATA)
    assert conf.dump() == CONFIG_EXPECTED.dump()

@pytest.mark.skipif(not YAML_SUPPORTED,  reason="yaml module missing")
def test_merge():
    conf = load_rc()
    conf = conf.merge(Config.load(CONFIG_DATA))
    assert conf.dump() == CONFIG_EXPECTED.dump()
    #pprint(conf.merge(rc))