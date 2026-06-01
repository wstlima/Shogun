import pytest
from shogun.api.agents import _classify_chat_mode

def test_classify_chat_mode_auto():
    # 1. Check a standard mission mode url trigger
    res = _classify_chat_mode("Could you check the NFL.com for when the frist pre-season match is up and where it is played", [])
    assert res["mode"] == "mission"
    assert "nfl.com" in res["matched"]

    # 2. Check weather trigger
    res = _classify_chat_mode("What is the weather in Tokyo?", [])
    assert res["mode"] == "mission"
    assert "weather" in res["matched"]

    # 3. Check simple chat message (defaults to fast)
    res = _classify_chat_mode("Hello Shogun! Can you explain to me what a cat is?", [])
    assert res["mode"] == "fast"

    # 4. Check governed memory trigger
    res = _classify_chat_mode("Do you remember what my name is?", [])
    assert res["mode"] == "governed"
    assert "remember" in res["matched"]
