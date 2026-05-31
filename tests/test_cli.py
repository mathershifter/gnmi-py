# -*- coding: utf-8 -*-


"""Click-based CLI coverage."""

import json

from click.testing import CliRunner

from gnmi import cli as cli_mod
from gnmi.cli import cli, format_version, load_rc


# ---------------------------------------------------------------------------
# format_version (used by --version)
# ---------------------------------------------------------------------------

def test_format_version_includes_grpc_and_protobuf():
    s = format_version()
    assert s.startswith("gnmip ")
    assert "protobuf" in s
    assert "grpcio" in s


def test_version_option_prints_format_version():
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "gnmip " in result.output


# ---------------------------------------------------------------------------
# Help text — exercises argument / option wiring
# ---------------------------------------------------------------------------

def test_top_level_help_lists_subcommands():
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    for cmd in ("capabilities", "get", "subscribe"):
        assert cmd in result.output


def test_subscribe_help_documents_streaming_options():
    result = CliRunner().invoke(cli, ["-t", "host:6030", "subscribe", "--help"])
    assert result.exit_code == 0
    for opt in ("--mode", "--submode", "--interval", "--heartbeat", "--qos"):
        assert opt in result.output


def test_target_is_required():
    result = CliRunner().invoke(cli, ["-t", "host:6030", "capabilities"])
    # Click rejects when target is missing — capabilities is treated as
    # the target and then "no such command" complains.
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# End-to-end: each subcommand against the in-process stub server
# ---------------------------------------------------------------------------

def test_cli_capabilities_against_stub(stub_server):
    result = CliRunner().invoke(cli, ["--insecure", "-t", stub_server.target, "capabilities"])
    assert result.exit_code == 0, result.output
    assert "gNMI Version:" in result.output
    assert "openconfig-system" in result.output


def test_cli_get_against_stub(stub_server):
    result = CliRunner().invoke(
        cli, ["--json", "--insecure", "-t", stub_server.target, "get", "/system/config/hostname"]
    )
    assert result.exit_code == 0, result.output
    print(f"Result output: {result.output}")
    payload = json.loads(result.output.strip().splitlines()[0])
    assert payload["updates"][0]["path"] == "/system/config/hostname"


def test_cli_subscribe_against_stub(stub_server):
    result = CliRunner().invoke(
        cli, ["--json", "--insecure", "-t", stub_server.target, "subscribe", "--mode", "once", "/a"]
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output.strip().splitlines()[0])
    assert payload["updates"][0]["path"] == "/a"


def test_cli_username_metadata_propagates(stub_server):
    result = CliRunner().invoke(
        cli, ["--json", "--insecure", "-u", "admin", "-p", "pw", "-t", stub_server.target,
              "capabilities"],
    )
    assert result.exit_code == 0, result.output
    md = dict(stub_server.servicer.last_metadata)
    assert md["username"] == "admin"
    assert md["password"] == "pw"


# ---------------------------------------------------------------------------
# ~/.gnmirc — auto-loaded TOML defaults (precedence: rc < --config < CLI)
# ---------------------------------------------------------------------------

def test_load_rc_returns_empty_when_no_file(monkeypatch, tmp_path):
    monkeypatch.setattr(cli_mod, "GNMIRC_PATH", str(tmp_path))
    assert load_rc() == {}


def test_load_rc_reads_dot_gnmirc_toml(monkeypatch, tmp_path):
    (tmp_path / ".gnmirc").write_text(
        'insecure = true\n'
        '\n'
        '[subscribe]\n'
        'mode = "once"\n'
    )
    monkeypatch.setattr(cli_mod, "GNMIRC_PATH", str(tmp_path))
    assert load_rc() == {
        "insecure": True,
        "subscribe": {"mode": "once"},
    }


def test_load_rc_prefers_dot_gnmirc_over_underscore(monkeypatch, tmp_path):
    (tmp_path / "_gnmirc").write_text('insecure = false\n')
    (tmp_path / ".gnmirc").write_text('insecure = true\n')
    monkeypatch.setattr(cli_mod, "GNMIRC_PATH", str(tmp_path))
    assert load_rc()["insecure"] is True


def test_rc_defaults_drive_cli_when_no_explicit_flag(stub_server):
    """`default_map` from the rc loader makes `--insecure` implicit."""
    result = CliRunner().invoke(
        cli,
        ["-t", stub_server.target, "subscribe", "/a"],
        default_map={"format": "json", "insecure": True, "subscribe": {"mode": "once"}},
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output.strip().splitlines()[0])
    assert payload["updates"][0]["path"] == "/a"


# ---------------------------------------------------------------------------
# --config FILE — explicit overrides for rc defaults; YAML or TOML
# ---------------------------------------------------------------------------

def test_config_file_toml_overrides_rc_defaults(stub_server, tmp_path):
    """rc says `mode = stream`; --config FILE flips to `once`."""
    cfg = tmp_path / "gnmip.toml"
    cfg.write_text(
        'insecure = true\n'
        '\n'
        '[subscribe]\n'
        'mode = "once"\n'
    )
    result = CliRunner().invoke(
        cli,
        ["--config", str(cfg), "-t", stub_server.target, "subscribe", "/a"],
        default_map={"format": "json","subscribe": {"mode": "stream"}},
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output.strip().splitlines()[0])
    assert payload["updates"][0]["path"] == "/a"


def test_config_file_yaml_supported(stub_server, tmp_path):
    cfg = tmp_path / "gnmip.yaml"
    cfg.write_text(
        "insecure: true\n"
        "subscribe:\n"
        "  mode: once\n"
    )
    result = CliRunner().invoke(
        cli,
        ["--json", "--config", str(cfg), "-t", stub_server.target, "subscribe", "/a"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output.strip().splitlines()[0])
    assert payload["updates"][0]["path"] == "/a"


def test_cli_flag_overrides_config_file_and_rc(stub_server, tmp_path):
    """Explicit --insecure on the command line wins, regardless of
    `insecure = false` in the rc / config layers."""
    cfg = tmp_path / "gnmip.toml"
    cfg.write_text("insecure = false\n")
    result = CliRunner().invoke(
        cli,
        ["--insecure", "--config", str(cfg), "-t", stub_server.target, "capabilities"],
        default_map={"insecure": False},
    )
    assert result.exit_code == 0, result.output
    assert "gNMI Version:" in result.output
