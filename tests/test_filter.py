from filter import filter_content


def test_include_keyword_added():
    text = "Added the Sulfur Cube mob\nSome random line\nNew features!"
    result = filter_content(text)
    assert "Added the Sulfur Cube mob" in result
    assert "New features!" in result
    assert "Some random line" not in result


def test_include_keyword_new():
    text = "New Features\nSomething else\nIntroduced a change"
    result = filter_content(text)
    assert "New Features" in result
    assert "Introduced a change" in result


def test_exclude_keyword_fixed():
    text = "Added a feature\nFixed a crash bug"
    result = filter_content(text)
    assert "Added a feature" in result
    assert "Fixed a crash bug" not in result


def test_exclude_keyword_technical():
    text = "New feature\nTechnical Changes\nFixed a bug"
    result = filter_content(text)
    assert "New feature" in result
    assert "Technical Changes" not in result


def test_exclude_takes_priority():
    text = "New API endpoint"
    result = filter_content(text)
    assert "New API endpoint" not in result


def test_exclude_data_pack():
    text = "Added new item\nUpdated Data Pack version"
    result = filter_content(text)
    assert "Added new item" in result
    assert "Updated Data Pack version" not in result


def test_exclude_resource_pack():
    text = "New texture\nResource Pack version 88"
    result = filter_content(text)
    assert "New texture" in result
    assert "Resource Pack version 88" not in result


def test_truncation():
    text = "\n".join(["Added feature " + str(i) for i in range(2000)])
    result = filter_content(text)
    assert len(result) <= 12000


def test_empty_input():
    assert filter_content("") == ""


def test_no_matching_keywords():
    text = "Some random text\nNothing interesting here"
    assert filter_content(text) == ""


def test_case_sensitive_matching():
    text = "added lower case\nAdded upper case"
    result = filter_content(text)
    assert "added lower case" not in result
    assert "Added upper case" in result
