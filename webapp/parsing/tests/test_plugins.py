import webapp.parsing as parsing


def test_default_instantiate():
    err = None
    try:
        e = parsing.Plugin()
        e.init()
    except Exception as e:
        err = e
    assert err is not None
    assert isinstance(err, NotImplementedError)


def test_default_parse():
    en = parsing.Entry('2000-01-01', 'body')
    err = None
    e = parsing.Plugin()
    try:
        e.parse_entry(en)
    except Exception as e:
        err = e
    assert isinstance(err, NotADirectoryError)
