import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def tmp_cache_dir(tmp_path):
    """臨時快取目錄，替代 ~/.claudistotle/cache。"""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


@pytest.fixture
def mock_requests():
    """Mock requests.get 和 requests.post。"""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        yield {"get": mock_get, "post": mock_post}


@pytest.fixture
def sample_xml_with_xxe():
    """含 XXE payload 的惡意 XML 字串。"""
    return (
        '<?xml version="1.0"?>'
        '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
        "<root>&xxe;</root>"
    )


@pytest.fixture
def sample_bib_valid():
    """有效的 BibTeX 條目。"""
    return (
        "@article{test2024example,\n"
        "  author = {Test Author},\n"
        "  title = {Test Title},\n"
        "  journal = {Test Journal},\n"
        "  year = {2024}\n"
        "}"
    )


@pytest.fixture
def sample_bib_invalid():
    """缺少必要欄位的無效 BibTeX 條目。"""
    return "@article{missing_fields,\n  title = {No Author or Journal}\n}"
