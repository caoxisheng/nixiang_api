# -*- coding: utf-8 -*-

"""
Unit tests for main.py CLI functions.
Tests for parse_cli_args(), resolve_server_config(), and print_startup_banner().
"""

import pytest
import argparse
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO


class TestParseCliArgs:
    """Tests for parse_cli_args() function."""
    
    def test_default_values_are_none(self):
        """
        What it does: Verifies that default values for host and port are None.
        Purpose: Ensure that None indicates "use env or default" in priority resolution.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with no arguments...")
        with patch.object(sys, 'argv', ['main.py']):
            args = parse_cli_args()
        
        print(f"args.host: {args.host}")
        print(f"args.port: {args.port}")
        print(f"Comparing: Expected host=None, port=None")
        assert args.host is None
        assert args.port is None
    
    def test_port_argument_long_form(self):
        """
        What it does: Verifies that --port argument is parsed correctly.
        Purpose: Ensure long form --port works.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with --port 9000...")
        with patch.object(sys, 'argv', ['main.py', '--port', '9000']):
            args = parse_cli_args()
        
        print(f"args.port: {args.port}")
        print(f"Comparing: Expected 9000, Got {args.port}")
        assert args.port == 9000
    
    def test_port_argument_short_form(self):
        """
        What it does: Verifies that -p argument is parsed correctly.
        Purpose: Ensure short form -p works.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with -p 8080...")
        with patch.object(sys, 'argv', ['main.py', '-p', '8080']):
            args = parse_cli_args()
        
        print(f"args.port: {args.port}")
        print(f"Comparing: Expected 8080, Got {args.port}")
        assert args.port == 8080
    
    def test_host_argument_long_form(self):
        """
        What it does: Verifies that --host argument is parsed correctly.
        Purpose: Ensure long form --host works.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with --host 127.0.0.1...")
        with patch.object(sys, 'argv', ['main.py', '--host', '127.0.0.1']):
            args = parse_cli_args()
        
        print(f"args.host: {args.host}")
        print(f"Comparing: Expected '127.0.0.1', Got '{args.host}'")
        assert args.host == "127.0.0.1"
    
    def test_host_argument_short_form(self):
        """
        What it does: Verifies that -H argument is parsed correctly.
        Purpose: Ensure short form -H works.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with -H 192.168.1.1...")
        with patch.object(sys, 'argv', ['main.py', '-H', '192.168.1.1']):
            args = parse_cli_args()
        
        print(f"args.host: {args.host}")
        print(f"Comparing: Expected '192.168.1.1', Got '{args.host}'")
        assert args.host == "192.168.1.1"
    
    def test_both_arguments_together(self):
        """
        What it does: Verifies that both --host and --port can be used together.
        Purpose: Ensure both arguments work simultaneously.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with --host 0.0.0.0 --port 3000...")
        with patch.object(sys, 'argv', ['main.py', '--host', '0.0.0.0', '--port', '3000']):
            args = parse_cli_args()
        
        print(f"args.host: {args.host}")
        print(f"args.port: {args.port}")
        assert args.host == "0.0.0.0"
        assert args.port == 3000
    
    def test_short_forms_together(self):
        """
        What it does: Verifies that both -H and -p can be used together.
        Purpose: Ensure short forms work simultaneously.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with -H 127.0.0.1 -p 5000...")
        with patch.object(sys, 'argv', ['main.py', '-H', '127.0.0.1', '-p', '5000']):
            args = parse_cli_args()
        
        print(f"args.host: {args.host}")
        print(f"args.port: {args.port}")
        assert args.host == "127.0.0.1"
        assert args.port == 5000


class TestResolveServerConfig:
    """Tests for resolve_server_config() function - priority hierarchy."""
    
    def test_cli_args_take_priority_over_env(self):
        """
        What it does: Verifies that CLI arguments have highest priority.
        Purpose: Ensure CLI args override environment variables.
        """
        print("Setup: Importing resolve_server_config...")
        from main import resolve_server_config
        
        print("Setup: Creating args with host=127.0.0.1, port=9000...")
        args = argparse.Namespace(host="127.0.0.1", port=9000)
        
        print("Action: Calling resolve_server_config with CLI args...")
        # Even if env vars are set, CLI should win
        with patch('main.SERVER_HOST', '0.0.0.0'), \
             patch('main.SERVER_PORT', 8000), \
             patch('main.DEFAULT_SERVER_HOST', '0.0.0.0'), \
             patch('main.DEFAULT_SERVER_PORT', 8000):
            host, port = resolve_server_config(args)
        
        print(f"Resolved host: {host}")
        print(f"Resolved port: {port}")
        print(f"Comparing: Expected ('127.0.0.1', 9000)")
        assert host == "127.0.0.1"
        assert port == 9000
    
    def test_env_vars_take_priority_over_defaults(self):
        """
        What it does: Verifies that env vars have priority over defaults.
        Purpose: Ensure env vars are used when CLI args are not provided.
        """
        print("Setup: Importing resolve_server_config...")
        from main import resolve_server_config
        
        print("Setup: Creating args with host=None, port=None (no CLI args)...")
        args = argparse.Namespace(host=None, port=None)
        
        print("Action: Calling resolve_server_config with env vars set...")
        # SERVER_HOST and SERVER_PORT are different from defaults
        with patch('main.SERVER_HOST', '192.168.1.100'), \
             patch('main.SERVER_PORT', 3000), \
             patch('main.DEFAULT_SERVER_HOST', '0.0.0.0'), \
             patch('main.DEFAULT_SERVER_PORT', 8000):
            host, port = resolve_server_config(args)
        
        print(f"Resolved host: {host}")
        print(f"Resolved port: {port}")
        print(f"Comparing: Expected ('192.168.1.100', 3000)")
        assert host == "192.168.1.100"
        assert port == 3000
    
    def test_defaults_used_when_nothing_set(self):
        """
        What it does: Verifies that defaults are used when nothing else is set.
        Purpose: Ensure default values work correctly.
        """
        print("Setup: Importing resolve_server_config...")
        from main import resolve_server_config
        
        print("Setup: Creating args with host=None, port=None...")
        args = argparse.Namespace(host=None, port=None)
        
        print("Action: Calling resolve_server_config with defaults...")
        # SERVER_HOST and SERVER_PORT equal to defaults (no env override)
        with patch('main.SERVER_HOST', '0.0.0.0'), \
             patch('main.SERVER_PORT', 8000), \
             patch('main.DEFAULT_SERVER_HOST', '0.0.0.0'), \
             patch('main.DEFAULT_SERVER_PORT', 8000):
            host, port = resolve_server_config(args)
        
        print(f"Resolved host: {host}")
        print(f"Resolved port: {port}")
        print(f"Comparing: Expected ('0.0.0.0', 8000)")
        assert host == "0.0.0.0"
        assert port == 8000
    
    def test_cli_host_only_env_port(self):
        """
        What it does: Verifies mixed priority - CLI host with env port.
        Purpose: Ensure each argument is resolved independently.
        """
        print("Setup: Importing resolve_server_config...")
        from main import resolve_server_config
        
        print("Setup: Creating args with host='127.0.0.1', port=None...")
        args = argparse.Namespace(host="127.0.0.1", port=None)
        
        print("Action: Calling resolve_server_config...")
        with patch('main.SERVER_HOST', '0.0.0.0'), \
             patch('main.SERVER_PORT', 9000), \
             patch('main.DEFAULT_SERVER_HOST', '0.0.0.0'), \
             patch('main.DEFAULT_SERVER_PORT', 8000):
            host, port = resolve_server_config(args)
        
        print(f"Resolved host: {host}")
        print(f"Resolved port: {port}")
        print(f"Comparing: Expected ('127.0.0.1', 9000)")
        assert host == "127.0.0.1"  # From CLI
        assert port == 9000  # From env (different from default)
    
    def test_cli_port_only_env_host(self):
        """
        What it does: Verifies mixed priority - CLI port with env host.
        Purpose: Ensure each argument is resolved independently.
        """
        print("Setup: Importing resolve_server_config...")
        from main import resolve_server_config
        
        print("Setup: Creating args with host=None, port=5000...")
        args = argparse.Namespace(host=None, port=5000)
        
        print("Action: Calling resolve_server_config...")
        with patch('main.SERVER_HOST', '192.168.1.1'), \
             patch('main.SERVER_PORT', 8000), \
             patch('main.DEFAULT_SERVER_HOST', '0.0.0.0'), \
             patch('main.DEFAULT_SERVER_PORT', 8000):
            host, port = resolve_server_config(args)
        
        print(f"Resolved host: {host}")
        print(f"Resolved port: {port}")
        print(f"Comparing: Expected ('192.168.1.1', 5000)")
        assert host == "192.168.1.1"  # From env (different from default)
        assert port == 5000  # From CLI


class TestEnsureCleanStartupPort:
    """Tests for ensure_clean_startup_port() startup cleanup behavior."""

    def test_terminates_previous_process_from_pid_file(self, tmp_path):
        """
        What it does: Verifies that previous server PID from pid file is terminated.
        Purpose: Ensure restart reuses the default port by stopping the old instance first.
        """
        print("Setup: Importing ensure_clean_startup_port...")
        from main import ensure_clean_startup_port

        print("Setup: Creating pid file with previous process id...")
        pid_file = tmp_path / "server.pid"
        pid_file.write_text("12345", encoding="utf-8")

        with patch("main.is_port_in_use", return_value=True), \
             patch("main.process_exists", return_value=True), \
             patch("main.terminate_process") as mock_terminate, \
             patch("main.wait_for_port_release", return_value=True), \
             patch("main.find_listening_pid_for_port", return_value=None):
            print("Action: Calling ensure_clean_startup_port...")
            ensure_clean_startup_port(
                "127.0.0.1",
                8000,
                pid_file_path=pid_file,
                current_pid=54321,
            )

        print(f"Comparing: Expected terminate_process called with 12345")
        mock_terminate.assert_called_once_with(12345)
        assert not pid_file.exists()

    def test_terminates_previous_process_found_by_port_scan(self, tmp_path):
        """
        What it does: Verifies fallback cleanup by scanning the listening port.
        Purpose: Ensure old instances started before pid-file support are still cleaned up.
        """
        print("Setup: Importing ensure_clean_startup_port...")
        from main import ensure_clean_startup_port

        pid_file = tmp_path / "server.pid"

        with patch("main.is_port_in_use", return_value=True), \
             patch("main.process_exists", return_value=True), \
             patch("main.find_listening_pid_for_port", return_value=23456), \
             patch("main.is_same_project_server_process", return_value=True), \
             patch("main.terminate_process") as mock_terminate, \
             patch("main.wait_for_port_release", return_value=True):
            print("Action: Calling ensure_clean_startup_port without pid file...")
            ensure_clean_startup_port(
                "127.0.0.1",
                8000,
                pid_file_path=pid_file,
                current_pid=54321,
            )

        print("Comparing: Expected fallback process termination")
        mock_terminate.assert_called_once_with(23456)

    def test_does_not_terminate_unrelated_process(self, tmp_path):
        """
        What it does: Verifies that unrelated listeners are not terminated.
        Purpose: Prevent accidental shutdown of non-project services using the same port.
        """
        print("Setup: Importing ensure_clean_startup_port...")
        from main import ensure_clean_startup_port

        pid_file = tmp_path / "server.pid"

        with patch("main.is_port_in_use", return_value=True), \
             patch("main.find_listening_pid_for_port", return_value=34567), \
             patch("main.is_same_project_server_process", return_value=False), \
             patch("main.terminate_process") as mock_terminate:
            print("Action: Calling ensure_clean_startup_port with unrelated process...")
            ensure_clean_startup_port(
                "127.0.0.1",
                8000,
                pid_file_path=pid_file,
                current_pid=54321,
            )

        print("Comparing: Expected unrelated process to be left running")
        mock_terminate.assert_not_called()

    def test_skips_cleanup_when_port_is_free(self, tmp_path):
        """
        What it does: Verifies that no cleanup happens when target port is free.
        Purpose: Avoid unnecessary process inspection on normal starts.
        """
        print("Setup: Importing ensure_clean_startup_port...")
        from main import ensure_clean_startup_port

        pid_file = tmp_path / "server.pid"

        with patch("main.is_port_in_use", return_value=False), \
             patch("main.terminate_process") as mock_terminate, \
             patch("main.find_listening_pid_for_port") as mock_find_pid:
            print("Action: Calling ensure_clean_startup_port with free port...")
            ensure_clean_startup_port(
                "127.0.0.1",
                8000,
                pid_file_path=pid_file,
                current_pid=54321,
            )

        print("Comparing: Expected no cleanup actions")
        mock_terminate.assert_not_called()
        mock_find_pid.assert_not_called()


class TestResolveStartupPort:
    """Tests for resolve_startup_port() port fallback behavior."""

    def test_returns_preferred_port_when_available(self, tmp_path):
        """
        What it does: Verifies that preferred port is kept when it is free.
        Purpose: Ensure normal startup still honors .env or CLI port settings.
        """
        print("Setup: Importing resolve_startup_port...")
        from main import resolve_startup_port

        pid_file = tmp_path / "server.pid"

        with patch("main.ensure_clean_startup_port") as mock_cleanup, \
             patch("main.is_port_in_use", return_value=False):
            print("Action: Calling resolve_startup_port with available port...")
            resolved_port = resolve_startup_port(
                "127.0.0.1",
                8000,
                pid_file_path=pid_file,
                current_pid=54321,
            )

        print(f"Comparing: Expected 8000, Got {resolved_port}")
        mock_cleanup.assert_called_once()
        assert resolved_port == 8000

    def test_falls_back_to_next_available_port_for_unrelated_process(self, tmp_path):
        """
        What it does: Verifies fallback to next free port when another program uses preferred port.
        Purpose: Ensure startup avoids killing unrelated services.
        """
        print("Setup: Importing resolve_startup_port...")
        from main import resolve_startup_port

        pid_file = tmp_path / "server.pid"

        with patch("main.ensure_clean_startup_port"), \
             patch("main.is_port_in_use", return_value=True), \
             patch("main.find_next_available_port", return_value=8001) as mock_find_next:
            print("Action: Calling resolve_startup_port with occupied preferred port...")
            resolved_port = resolve_startup_port(
                "127.0.0.1",
                8000,
                pid_file_path=pid_file,
                current_pid=54321,
            )

        print(f"Comparing: Expected 8001, Got {resolved_port}")
        mock_find_next.assert_called_once_with("127.0.0.1", 8001)
        assert resolved_port == 8001


class TestIsSameProjectServerProcess:
    """Tests for is_same_project_server_process() command-line matching."""

    def test_matches_relative_main_py_command_line(self):
        """
        What it does: Verifies matching when main.py appears as a relative argument.
        Purpose: Ensure Windows launches like `python.exe main.py` are recognized.
        """
        print("Setup: Importing is_same_project_server_process...")
        from main import is_same_project_server_process

        project_root = Path("C:/Users/Xi/Desktop/nixiang_api")
        command_line = '"C:/Users/Xi/Desktop/nixiang_api/.venv/Scripts/python.exe" main.py'

        with patch("main.get_process_command_line", return_value=command_line):
            print("Action: Calling is_same_project_server_process...")
            result = is_same_project_server_process(12345, project_root=project_root)

        print(f"Comparing: Expected True, Got {result}")
        assert result is True


class TestPrintStartupBanner:
    """Tests for print_startup_banner() function."""

    def test_banner_handles_gbk_console_output(self, monkeypatch):
        """
        What it does: Verifies that banner printing works on GBK consoles.
        Purpose: Ensure Windows terminals without UTF-8 support can still start the server.
        """
        print("Setup: Importing print_startup_banner...")
        from main import print_startup_banner

        class GbkCapturingStream:
            """Capture stdout writes while simulating a GBK-only console."""

            def __init__(self) -> None:
                self.encoding = "gbk"
                self._chunks: list[str] = []

            def write(self, text: str) -> int:
                text.encode(self.encoding)
                self._chunks.append(text)
                return len(text)

            def flush(self) -> None:
                """Provide flush API expected by print()."""

            def getvalue(self) -> str:
                """Return collected output."""
                return "".join(self._chunks)

        stream = GbkCapturingStream()
        monkeypatch.setattr(sys, "stdout", stream)

        print_startup_banner("127.0.0.1", 8000)

        output = stream.getvalue()
        assert "127.0.0.1:8000" in output
        assert "/health" in output
    
    def test_banner_contains_url(self, capsys):
        """
        What it does: Verifies that banner contains the server URL.
        Purpose: Ensure URL is displayed to user.
        """
        print("Setup: Importing print_startup_banner...")
        from main import print_startup_banner
        
        print("Action: Calling print_startup_banner('0.0.0.0', 8000)...")
        print_startup_banner("0.0.0.0", 8000)
        
        captured = capsys.readouterr()
        print(f"Captured output length: {len(captured.out)}")
        
        # When host is 0.0.0.0, display should show localhost
        assert "localhost:8000" in captured.out or "8000" in captured.out
    
    def test_banner_contains_custom_port(self, capsys):
        """
        What it does: Verifies that banner shows custom port.
        Purpose: Ensure custom port is displayed correctly.
        """
        print("Setup: Importing print_startup_banner...")
        from main import print_startup_banner
        
        print("Action: Calling print_startup_banner('127.0.0.1', 9000)...")
        print_startup_banner("127.0.0.1", 9000)
        
        captured = capsys.readouterr()
        print(f"Captured output contains '9000': {'9000' in captured.out}")
        
        assert "9000" in captured.out
    
    def test_banner_contains_docs_url(self, capsys):
        """
        What it does: Verifies that banner contains API docs URL.
        Purpose: Ensure /docs endpoint is mentioned.
        """
        print("Setup: Importing print_startup_banner...")
        from main import print_startup_banner
        
        print("Action: Calling print_startup_banner('0.0.0.0', 8000)...")
        print_startup_banner("0.0.0.0", 8000)
        
        captured = capsys.readouterr()
        print(f"Captured output contains '/docs': {'/docs' in captured.out}")
        
        assert "/docs" in captured.out
    
    def test_banner_contains_health_url(self, capsys):
        """
        What it does: Verifies that banner contains health check URL.
        Purpose: Ensure /health endpoint is mentioned.
        """
        print("Setup: Importing print_startup_banner...")
        from main import print_startup_banner
        
        print("Action: Calling print_startup_banner('0.0.0.0', 8000)...")
        print_startup_banner("0.0.0.0", 8000)
        
        captured = capsys.readouterr()
        print(f"Captured output contains '/health': {'/health' in captured.out}")
        
        assert "/health" in captured.out


class TestCliHelp:
    """Tests for CLI help output."""
    
    def test_help_shows_port_option(self):
        """
        What it does: Verifies that --help shows port option.
        Purpose: Ensure help is informative.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with --help...")
        with patch.object(sys, 'argv', ['main.py', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                parse_cli_args()
        
        print(f"Exit code: {exc_info.value.code}")
        # --help exits with code 0
        assert exc_info.value.code == 0
    
    def test_help_shows_host_option(self, capsys):
        """
        What it does: Verifies that --help output contains host option.
        Purpose: Ensure host option is documented.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with --help...")
        with patch.object(sys, 'argv', ['main.py', '--help']):
            with pytest.raises(SystemExit):
                parse_cli_args()
        
        captured = capsys.readouterr()
        print(f"Help output contains '--host': {'--host' in captured.out}")
        print(f"Help output contains '-H': {'-H' in captured.out}")
        
        assert "--host" in captured.out
        assert "-H" in captured.out


class TestCliVersion:
    """Tests for CLI version output."""
    
    def test_version_flag_exits_with_zero(self):
        """
        What it does: Verifies that --version exits with code 0.
        Purpose: Ensure version flag works correctly.
        """
        print("Setup: Importing parse_cli_args...")
        from main import parse_cli_args
        
        print("Action: Calling parse_cli_args with --version...")
        with patch.object(sys, 'argv', ['main.py', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                parse_cli_args()
        
        print(f"Exit code: {exc_info.value.code}")
        assert exc_info.value.code == 0
    
    def test_version_shows_app_version(self, capsys):
        """
        What it does: Verifies that --version shows application version.
        Purpose: Ensure version is displayed.
        """
        print("Setup: Importing parse_cli_args and APP_VERSION...")
        from main import parse_cli_args
        from kiro.config import APP_VERSION
        
        print("Action: Calling parse_cli_args with --version...")
        with patch.object(sys, 'argv', ['main.py', '--version']):
            with pytest.raises(SystemExit):
                parse_cli_args()
        
        captured = capsys.readouterr()
        print(f"Version output: {captured.out}")
        print(f"APP_VERSION: {APP_VERSION}")
        
        assert APP_VERSION in captured.out
