"""search_cache.py 安全性測試。"""
import sys
import warnings
from pathlib import Path
from unittest.mock import patch

SCRIPTS = str(Path(__file__).parent.parent / "skills" / "philosophy-research" / "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def test_cache_json_roundtrip(tmp_path):
    """測試 JSON 快取讀寫正確性。put_cache(key, result)，get_cache(key)。"""
    import importlib
    import search_cache
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    with patch("search_cache.CACHE_DIR", cache_dir):
        importlib.reload(search_cache)
        key = search_cache.cache_key("s2", query="philosophy of mind")
        search_cache.put_cache(key, {"papers": ["a", "b"]})
        result = search_cache.get_cache(key)
    assert result == {"papers": ["a", "b"]}


def test_cache_pkl_graceful_ignore(tmp_path):
    """舊 .pkl 快取存在時，get_cache 應回傳 None 並發出 RuntimeWarning，而非 crash。"""
    import importlib
    import search_cache
    # reload 必須在 patch 之外完成，否則 reload 會覆蓋 patch
    importlib.reload(search_cache)
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    # 生成真實 key，建立對應 .pkl 假檔案
    key = search_cache.cache_key("s2", query="old_query")
    fake_pkl = cache_dir / f"{key}.pkl"
    fake_pkl.write_bytes(b"\x80\x04\x95fake pickle")
    # patch AFTER reload，讓 get_cache 使用 tmp 目錄
    with patch("search_cache.CACHE_DIR", cache_dir):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = search_cache.get_cache(key)
    assert result is None, "預期回傳 None（不 crash）"
    assert any(issubclass(warning.category, RuntimeWarning) for warning in w), \
        "預期發出 RuntimeWarning"


def test_no_pickle_in_cache_module():
    """確認 search_cache.py 不再含有 pickle import/load/dump。"""
    src = (Path(SCRIPTS) / "search_cache.py").read_text(encoding="utf-8")
    assert "import pickle" not in src
    assert "pickle.load" not in src
    assert "pickle.dump" not in src


def test_cache_dir_not_tmp():
    """確認快取目錄已遷移離 /tmp（正常系統下）。"""
    import importlib
    import search_cache
    importlib.reload(search_cache)
    cache_str = str(search_cache.CACHE_DIR)
    assert ".claudistotle" in cache_str, \
        f"CACHE_DIR 未遷移至 ~/.claudistotle：{cache_str}"
