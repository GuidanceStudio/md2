from md2 import sanitize_html


def test_strips_script_tags():
    assert "<script>" not in sanitize_html("<p>Hello</p><script>alert('xss')</script>")


def test_strips_onclick():
    result = sanitize_html('<div onclick="alert(1)">text</div>')
    assert "onclick" not in result
    assert "text" in result


def test_allows_safe_tags():
    for tag in ["p", "h1", "ul", "table", "code", "pre", "img"]:
        html = f"<{tag}>content</{tag}>"
        result = sanitize_html(html)
        assert f"<{tag}" in result


def test_allows_iframe():
    html = '<iframe src="https://example.com" width="560" height="315"></iframe>'
    result = sanitize_html(html)
    assert "<iframe" in result
    assert 'src="https://example.com"' in result


def test_allows_style_attribute():
    html = '<p style="color: red;">styled</p>'
    result = sanitize_html(html)
    # bleach allows the style attribute but strips values without css_sanitizer
    assert 'style=' in result


def test_allows_img_attributes():
    html = '<img src="photo.jpg" alt="Photo" width="100" height="50">'
    result = sanitize_html(html)
    assert 'src="photo.jpg"' in result
    assert 'alt="Photo"' in result
    assert 'width="100"' in result
    assert 'height="50"' in result


def test_strips_dangerous_href():
    html = '<a href="javascript:alert(1)">click</a>'
    result = sanitize_html(html)
    assert "javascript:" not in result


def test_empty_input():
    assert sanitize_html("") == ""


def test_nested_dangerous_tags():
    html = "<div><script>alert(1)</script>safe</div>"
    result = sanitize_html(html)
    assert "<script>" not in result
    assert "<div>" in result
    assert "safe" in result


def test_allows_class_and_id():
    html = '<div class="container" id="main">text</div>'
    result = sanitize_html(html)
    assert 'class="container"' in result
    assert 'id="main"' in result
