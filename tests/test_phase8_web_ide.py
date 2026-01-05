"""Phase 8 Web IDE, remote execution, debugging, and community tests."""

import re
import unittest
from typing import Any

from src.hb_lcs.ide import AdvancedIDE


def make_headless_ide() -> AdvancedIDE:
    """Create a lightweight AdvancedIDE instance without Tk UI."""
    ide = object.__new__(AdvancedIDE)
    ide.current_config = None
    ide.web_routes = {}
    ide.web_app_config = {}
    ide.execution_config = {}
    ide.debugger_state = {}
    ide.community_registry = None
    ide.syntax_theme = {"Keywords": "#82aaff", "Strings": "#c3e88d"}
    ide._default_theme = dict(ide.syntax_theme)
    ide._recent_share_payloads = []
    ide._recent_files = []
    return ide


class TestWebIDE(unittest.TestCase):
    """Tests for the Web IDE configuration and template."""

    def test_init_web_ide_sets_routes_and_config(self) -> None:
        ide = make_headless_ide()
        config = ide.init_web_ide()

        assert config["port"] == 5000
        assert config["host"] == "127.0.0.1"
        assert len(config["features"]["api_endpoints"]) == 7
        assert set(
            [
                "/api/config",
                "/api/code/execute",
                "/api/code/validate",
                "/api/keywords",
                "/api/template",
                "/api/export",
                "/api/community/languages",
            ]
        ) == set(config["features"]["api_endpoints"])

        assert "/api/code/validate" in ide.web_routes
        assert ide.web_routes["/api/code/validate"]["method"] == "POST"
        assert len(ide.web_routes) == 8  # Includes "/" root route plus 7 API endpoints

    def test_generate_template_includes_controls(self) -> None:
        ide = make_headless_ide()
        html = ide.generate_web_ui_template()

        assert "Honey Badger Web IDE" in html
        assert "/api/code/execute" in html
        assert "Execute" in html
        assert "Validate" in html
        assert len(html) > 4000  # Comprehensive template size target

    def test_create_web_api_handler_defaults_and_custom(self) -> None:
        ide = make_headless_ide()
        default_result = ide.create_web_api_handler("/api/test")
        assert default_result["method"] == "GET"
        assert default_result["response"]["status"] == "ok"

        custom_result = ide.create_web_api_handler(
            "/api/custom",
            method="post",
            handler=lambda: {"status": "custom"},
        )
        assert custom_result["method"] == "POST"
        assert custom_result["response"]["status"] == "custom"


class TestRemoteExecution(unittest.TestCase):
    """Tests for remote execution and sandboxing."""

    def test_remote_execution_configuration_and_run(self) -> None:
        ide = make_headless_ide()
        config = ide.init_remote_execution("docker")

        assert config["sandbox_type"] == "docker"
        assert config["timeout"] == 5
        assert config["max_memory_mb"] == 256
        assert config["process_limit"] == 10
        assert "math" in config["safe_imports"]

        result = ide.execute_code_safely("print(42)")
        assert result["status"] == "success"
        assert "42" in result["output"]
        assert ide.execution_config["last_run"]["status"] == "success"

    def test_sandbox_profiles_and_distribution(self) -> None:
        ide = make_headless_ide()
        ide.init_remote_execution("kubernetes")

        strict = ide.create_execution_sandbox("strict")
        assert strict["resources"]["memory_mb"] == 64
        assert strict["resources"]["timeout"] == 1

        results = ide.distribute_execution("x=1+1", num_instances=3)
        assert len(results) == 3
        assert all("sandbox_id" in item for item in results)
        assert all(item["status"] == "success" for item in results)


class TestDebugger(unittest.TestCase):
    """Tests for debugger state, breakpoints, and tracing."""

    def test_debugger_breakpoints_and_trace(self) -> None:
        ide = make_headless_ide()
        ide.init_debugger()
        ide.set_breakpoint("temp.py", 1, "x > 0")

        trace = ide.step_through_code("x = 1\nprint(x)", step_type="line")
        assert trace["count"] == 2
        assert len(trace["steps"]) == 2

        snapshot = ide.inspect_variables()
        assert "temp.py:1" in snapshot["breakpoints"]
        assert isinstance(snapshot["call_stack"], list)
        assert isinstance(snapshot["hits"], dict)


class TestCommunityRegistry(unittest.TestCase):
    """Tests for community registry operations."""

    def test_registry_user_publish_and_review(self) -> None:
        ide = make_headless_ide()
        registry = ide.init_community_registry()

        assert len(registry["languages"]) == 3
        assert set(registry["categories"]) == {
            "Educational",
            "Functional",
            "Imperative",
            "Scripting",
            "DSL",
            "Esoteric",
        }

        user = ide.register_user("alice", "alice@example.com")
        assert user["reputation"] == 0
        assert user["languages_created"] == []

        lang = ide.publish_language("TestLang", "Functional scripting example", "Functional")
        assert lang["rating"] == 0.0
        assert len(lang["tags"]) >= 1
        assert re.search(r"functional", " ".join(lang["tags"]))

        review = ide.rate_and_review(lang["id"], 4.5, "Great language")
        assert review["rating"] == 4.5
        assert lang["rating"] == 4.5
        assert len(lang["reviews"]) >= 1


if __name__ == "__main__":
    unittest.main()
