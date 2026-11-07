"""The independent distribution must never update from the original PyPI package."""

from types import SimpleNamespace

from zotero_mcp import updater


def test_latest_version_uses_own_github_release(monkeypatch):
    seen = []

    def fake_get(url, timeout):
        seen.append(url)
        return SimpleNamespace(status_code=200, json=lambda: {"tag_name": "v0.16.0"})

    monkeypatch.setattr(updater, "requests", SimpleNamespace(get=fake_get))
    assert updater.get_latest_version() == "0.16.0"
    assert seen == [
        "https://api.github.com/repos/quang1852004-notabot/zotero-mcp/releases/latest"
    ]


def test_update_never_runs_a_package_manager(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("A package manager must not run")

    monkeypatch.setattr(updater.subprocess, "run", fail)
    for method in ("uv", "pip", "pipx", "conda"):
        success, message = updater.update_via_method(method)
        assert not success
        assert "quang1852004-notabot/zotero-mcp" in message


def test_missing_release_is_reported_as_unavailable(monkeypatch):
    monkeypatch.setattr(updater, "get_current_version", lambda: "0.15.2")
    monkeypatch.setattr(updater, "get_latest_version", lambda: None)
    result = updater.update_zotero_mcp(check_only=True)
    assert result["success"] is False
    assert "quang1852004-notabot/zotero-mcp/releases" in result["message"]
