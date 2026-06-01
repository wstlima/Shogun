"""Test auto-mode classifier keyword routing."""
from shogun.api.agents import _classify_chat_mode


def test_nfl_dot_com_routes_to_mission():
    """Domain names like NFL.com must trigger Mission Mode."""
    res = _classify_chat_mode(
        "Could you check the NFL.com for when the frist pre-season match is up and where it is played", []
    )
    assert res["mode"] == "mission", f"Expected mission, got {res}"


def test_plain_greeting_routes_to_fast():
    """Simple greetings must stay in Fast Mode."""
    res = _classify_chat_mode("Hello! How are you today?", [])
    assert res["mode"] == "fast", f"Expected fast, got {res}"


def test_memory_trigger_routes_to_governed():
    """Memory references must route to Governed."""
    res = _classify_chat_mode("Do you remember what I told you last time?", [])
    assert res["mode"] == "governed", f"Expected governed, got {res}"


def test_weather_routes_to_mission():
    """Live-data queries must trigger Mission Mode."""
    res = _classify_chat_mode("What is the weather in Copenhagen?", [])
    assert res["mode"] == "mission", f"Expected mission, got {res}"


def test_https_url_routes_to_mission():
    """Full URLs must trigger Mission Mode."""
    res = _classify_chat_mode("Can you open https://example.org/page for me?", [])
    assert res["mode"] == "mission", f"Expected mission, got {res}"
