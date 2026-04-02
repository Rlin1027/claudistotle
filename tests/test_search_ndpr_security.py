"""XXE 注入防護測試。"""
import pytest


def test_xxe_blocked_by_defusedxml(sample_xml_with_xxe):
    """確認 defusedxml 會阻擋含 DOCTYPE/實體的惡意 XML。"""
    from defusedxml import DTDForbidden, EntitiesForbidden
    from defusedxml.ElementTree import fromstring

    with pytest.raises((DTDForbidden, EntitiesForbidden)):
        fromstring(sample_xml_with_xxe)


def test_safe_xml_still_parses():
    """確認正常 XML 仍可正常解析。"""
    from defusedxml.ElementTree import fromstring

    xml = "<root><item>hello</item></root>"
    root = fromstring(xml)
    assert root.tag == "root"
    assert root[0].text == "hello"
