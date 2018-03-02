from webapp import parsing


def test_count_entries():
    s = "2000-01-01\nsometext"
    es = parsing.identify_entries(s.split('\n'))
    assert len(es) == 1


def test_single_entry_content():
    s = "2000-01-01\nsometext"
    es = parsing.identify_entries(s.split('\n'))
    e = es[0]
    assert e.date_string == "2000-01-01"
    assert e.body == "sometext"


def test_multi_entry_content():
    s = "2000-01-01\nsometext\n2000-01-02\nnextday"
    es = parsing.identify_entries(s.split('\n'))
    assert len(es) == 2
    e = es[0]
    assert e.date_string == "2000-01-01"
    assert e.body == "sometext"
    e = es[1]
    assert e.date_string == "2000-01-02"
    assert e.body == "nextday"
