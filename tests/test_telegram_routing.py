from shogun.api.agents import _chat_attachment_content
from shogun.services.telegram_poller import _attachment_context_text, _select_telegram_chat_mode


def test_telegram_defaults_to_tool_capable_mission_mode():
    message, mode, classification = _select_telegram_chat_mode(
        "Please remember my children's birthdays and schedule reminders.",
        [],
    )

    assert message.startswith("Please remember")
    assert mode == "mission"
    assert classification["reason"] == "telegram_mission_default"


def test_telegram_fast_mode_requires_explicit_override():
    message, mode, classification = _select_telegram_chat_mode("/fast Hello there", [])

    assert message == "Hello there"
    assert mode == "fast"
    assert classification["reason"] == "telegram_fast_override"


def test_telegram_auto_override_uses_classifier():
    message, mode, classification = _select_telegram_chat_mode(
        "/auto What is the weather in Copenhagen?",
        [],
    )

    assert message == "What is the weather in Copenhagen?"
    assert mode == "mission"
    assert classification["reason"] == "telegram_auto_override"


def test_telegram_attachment_context_mentions_workspace_path():
    message = _attachment_context_text(
        "What is in this?",
        [{
            "filename": "photo.jpg",
            "mime_type": "image/jpeg",
            "size": 123,
            "workspace_path": "Telegram/2026-07-07/123/photo.jpg",
        }],
    )

    assert "What is in this?" in message
    assert "photo.jpg (image/jpeg, 123 bytes)" in message
    assert "Telegram/2026-07-07/123/photo.jpg" in message


def test_chat_attachment_content_includes_image_bytes(tmp_path):
    image_path = tmp_path / "tiny.png"
    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02"
        b"\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT"
        b"\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA"
        b"\x89\x8d\xb1\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    content = _chat_attachment_content(
        "Describe this image",
        [{"mime_type": "image/png", "path": str(image_path)}],
    )

    assert isinstance(content, list)
    assert content[0] == {"type": "text", "text": "Describe this image"}
    assert content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
