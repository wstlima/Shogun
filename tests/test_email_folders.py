from shogun.services.email_service import (
    _decode_imap_utf7,
    _folder_candidates,
    _parse_imap_list_line,
    _quote_mailbox,
)


def test_parse_gmail_sent_folder_from_imap_list():
    line = b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Sent Mail"'

    assert _parse_imap_list_line(line) == "[Gmail]/Sent Mail"
    assert _quote_mailbox("[Gmail]/Sent Mail") == '"[Gmail]/Sent Mail"'


def test_gmail_sent_aliases_are_selectable_candidates():
    candidates = _folder_candidates("Sent")

    assert "Sent" in candidates
    assert "[Gmail]/Sent Mail" in candidates
    assert "[Google Mail]/Sent Mail" in candidates


def test_decode_imap_modified_utf7_folder_name():
    assert _decode_imap_utf7("INBOX") == "INBOX"
    assert _decode_imap_utf7("Foo &- Bar") == "Foo & Bar"
    assert _decode_imap_utf7("&ZeVnLIqe-") == "日本語"
