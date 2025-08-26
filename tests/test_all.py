import pytest
from urllib.parse import urlparse, parse_qs


from libgen_api_enhanced.search_request import SearchRequest, SearchType, SearchTopic
from libgen_api_enhanced.book import Book


class FakeResponse:
    def __init__(self, text="", status=200, headers=None, encoding="utf-8"):
        self.text = text
        self.status_code = status
        self.headers = headers or {"Content-Type": "text/html; charset=utf-8"}
        self.encoding = encoding
        self.apparent_encoding = encoding

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def make_table_html(row_html: str) -> str:
    return f"""
    <html><body>
      <table id="tablelibgen">
        <tr>{row_html}</tr>
      </table>
    </body></html>
    """


def minimal_row_html():
    return """
      <td>
        <a href="/index.php?id=123&foo=bar">Some Title</a>
      </td>
      <td>Jane Doe</td>
      <td>Acme</td>
      <td>2020</td>
      <td>en</td>
      <td>321</td>
      <td><a>10 MB</a></td>
      <td>pdf</td>
      <td>
        <a href="/get.php?md5=ABCDEF1234">Mirror A</a>
        <a href="https://mirror.example/get.php?md5=ABCDEF1234">Mirror B</a>
      </td>
    """


def test_query_too_short_raises():
    with pytest.raises(Exception):
        SearchRequest("ab")


def test_unsupported_search_type_raises():
    with pytest.raises(Exception):
        SearchRequest("python", search_type="unknown")


def test_no_table_returns_empty(monkeypatch):
    def fake_get(url, *args, **kwargs):
        return FakeResponse("<html><body>No table</body></html>")

    monkeypatch.setattr("requests.get", fake_get)

    sr = SearchRequest("python", search_type="title", mirror="https://example.org")
    books = sr.aggregate_request_data_libgen()
    assert books == []


def test_parses_one_row(monkeypatch):
    from libgen_api_enhanced.book import Book

    html = make_table_html(minimal_row_html())

    def fake_get(url, *args, **kwargs):
        return FakeResponse(html)

    monkeypatch.setattr("requests.get", fake_get)

    sr = SearchRequest("python", mirror="https://example.org")
    books = sr.aggregate_request_data_libgen()
    assert len(books) == 1
    b: Book = books[0]
    assert b.id == "123"
    assert b.title == "Some Title"
    assert b.author == "Jane Doe"
    assert b.publisher == "Acme"
    assert b.year == "2020"
    assert b.language == "en"
    assert b.pages == "321"
    assert b.size == "10 MB"
    assert b.extension == "pdf"
    assert b.md5 == "ABCDEF1234"
    assert b.mirrors[0].startswith("https://example.org/")


def test_skips_rows_with_too_few_columns(monkeypatch):
    bad_row = "<td>only one cell</td>"
    html = make_table_html(bad_row)

    def fake_get(url, *args, **kwargs):
        return FakeResponse(html)

    monkeypatch.setattr("requests.get", fake_get)

    sr = SearchRequest("python")
    books = sr.aggregate_request_data_libgen()
    assert books == []


def test_handles_weird_size_cell(monkeypatch):
    row = minimal_row_html().replace("<a>10 MB</a>", "10 MB")
    html = make_table_html(row)

    def fake_get(url, *args, **kwargs):
        return FakeResponse(html)

    monkeypatch.setattr("requests.get", fake_get)

    sr = SearchRequest("python")
    books = sr.aggregate_request_data_libgen()
    assert books[0].size == "10 MB"


def test_add_tor_download_link_sets_attribute():
    b = Book(
        id="123",
        title="Some Title",
        author="Jane Doe",
        publisher="Acme",
        year="2020",
        language="en",
        pages="321",
        size="10 MB",
        extension="pdf",
        md5="ABCDEF1234",
        mirrors=[],
    )
    b.add_tor_download_link()
    assert b.tor_download_link is not None
    assert "ABCDEF1234" in b.tor_download_link
    assert b.tor_download_link.endswith(".pdf")


def test_resolve_direct_download_link_happy_path(monkeypatch):
    mirror_html = """
    <html><body>
      <a href="/get?key=XYZ">GET</a>
    </body></html>
    """

    def fake_get(url, *args, **kwargs):
        return FakeResponse(mirror_html)

    monkeypatch.setattr("requests.get", fake_get)

    b = Book(
        id="123",
        title="Some Title",
        author="Jane Doe",
        publisher="Acme",
        year="2020",
        language="en",
        pages="321",
        size="10 MB",
        extension="pdf",
        md5="ABCDEF1234",
        mirrors=["https://mirror.example/detail?id=1"],
    )

    b.resolve_direct_download_link()
    assert b.resolved_download_link is not None
    parsed = urlparse(b.resolved_download_link)
    params = parse_qs(parsed.query)
    assert "key" in params
    assert "md5" in params or "md5" not in params


def test_resolve_direct_download_link_no_get_links(monkeypatch):
    mirror_html = "<html><body><p>No anchors</p></body></html>"

    def fake_get(url, *args, **kwargs):
        return FakeResponse(mirror_html)

    monkeypatch.setattr("requests.get", fake_get)

    b = Book(
        id="1",
        title="T",
        author="A",
        publisher="P",
        year="2020",
        language="en",
        pages="1",
        size="1 MB",
        extension="pdf",
        md5="m",
        mirrors=["https://mirror.example/detail?id=1"],
    )
    with pytest.raises(ValueError):
        b.resolve_direct_download_link()


def make_book(**kw):
    defaults = dict(
        id="1",
        title="Learning Python",
        author="Mark Lutz",
        publisher="OReilly",
        year="2013",
        language="English",
        pages="1648",
        size="20 MB",
        extension="pdf",
        md5="X",
        mirrors=[],
    )
    defaults.update(kw)
    return Book(**defaults)


BOOKS = [
    make_book(
        id="1",
        title="Deep Learning",
        author="Ian Goodfellow",
        publisher="MIT Press",
        year="2016",
        language="English",
        pages="800",
        size="30 MB",
        extension="pdf",
    ),
    make_book(
        id="2",
        title="Learning Python",
        author="Mark Lutz",
        publisher="OReilly",
        year="2013",
        language="English",
        pages="1648",
        size="25 MB",
        extension="pdf",
    ),
    make_book(
        id="3",
        title="Python Tricks",
        author="Dan Bader",
        publisher="DB",
        year="2017",
        language="English",
        pages="302",
        size="5 MB",
        extension="epub",
    ),
]


# -------- unit tests for filter_books --------

from libgen_api_enhanced.libgen_search import filter_books, LibgenSearch


def test_exact_match_subset_fields():
    out = filter_books(
        BOOKS, {"language": "english", "extension": "pdf"}, exact_match=True
    )
    assert len(out) == 2
    assert all(b.extension == "pdf" for b in out)


def test_exact_match_requires_all_pairs():
    out = filter_books(
        BOOKS,
        {"language": "English", "extension": "pdf", "publisher": "MIT Press"},
        exact_match=True,
    )
    assert len(out) == 1
    assert out[0].publisher == "MIT Press"


def test_exact_match_non_string_field_with_equality():
    out = filter_books(BOOKS, {"year": "2017"}, exact_match=True)
    assert [b.id for b in out] == ["3"]


def test_exact_match_empty_filters_returns_all():
    out = filter_books(BOOKS, {}, exact_match=True)
    assert out == BOOKS


def test_non_exact_match_case_insensitive_substring_on_title():
    out = filter_books(BOOKS, {"title": "python"}, exact_match=False)
    titles = {b.title for b in out}
    assert titles == {"Learning Python", "Python Tricks"}


def test_non_exact_multiple_fields_all_must_match():
    out = filter_books(
        BOOKS, {"title": "python", "extension": "pdf"}, exact_match=False
    )
    titles = {b.title for b in out}
    assert titles == {"Learning Python"}


def test_non_exact_no_matches_returns_empty():
    out = filter_books(BOOKS, {"author": "Someone Else"}, exact_match=False)
    assert out == []


def test_unknown_field_raises_keyerror():
    with pytest.raises(KeyError):
        filter_books(BOOKS, {"unknown_field": "x"}, exact_match=True)


def test_handles_none_values_safely_in_non_exact():
    b = make_book(id="4", title=None)
    out = filter_books([b], {"title": "py"}, exact_match=False)
    assert out == []


# -------- tests for new enum functionality --------


def test_search_type_enum_values():
    assert SearchType.TITLE.value == "title"
    assert SearchType.AUTHOR.value == "author"
    assert SearchType.DEFAULT.value == "default"


def test_search_type_columns():
    assert SearchType.TITLE.columns == ["t"]
    assert SearchType.AUTHOR.columns == ["a"]
    assert SearchType.DEFAULT.columns == ["t", "a", "s", "y", "p", "i"]


def test_search_topic_enum_values():
    assert SearchTopic.LIBGEN.value == "libgen"
    assert SearchTopic.COMICS.value == "comics"
    assert SearchTopic.FICTION.value == "fiction"
    assert SearchTopic.ARTICLES.value == "articles"
    assert SearchTopic.MAGAZINES.value == "magazines"
    assert SearchTopic.FICTION_RUS.value == "fictionRUS"
    assert SearchTopic.STANDARDS.value == "standards"


def test_search_topic_codes():
    assert SearchTopic.LIBGEN.code == "l"
    assert SearchTopic.COMICS.code == "c"
    assert SearchTopic.FICTION.code == "f"
    assert SearchTopic.ARTICLES.code == "a"
    assert SearchTopic.MAGAZINES.code == "m"
    assert SearchTopic.FICTION_RUS.code == "r"
    assert SearchTopic.STANDARDS.code == "s"


def test_search_topic_from_string():
    assert SearchTopic.from_string("libgen") == SearchTopic.LIBGEN
    assert SearchTopic.from_string("fiction") == SearchTopic.FICTION
    
    with pytest.raises(ValueError):
        SearchTopic.from_string("unknown")
    
    with pytest.raises(TypeError):
        SearchTopic.from_string(123)


def test_search_topic_all_topics():
    topics = SearchTopic.all_topics()
    assert len(topics) == 7
    assert SearchTopic.LIBGEN in topics
    assert SearchTopic.FICTION in topics


def test_search_request_with_enum_search_type():
    sr = SearchRequest("python", search_type=SearchType.AUTHOR)
    assert sr.search_type == SearchType.AUTHOR


def test_search_request_with_string_search_type_backward_compatibility():
    sr = SearchRequest("python", search_type="title")
    assert sr.search_type == SearchType.TITLE


def test_search_request_with_enum_search_in():
    topics = [SearchTopic.LIBGEN, SearchTopic.FICTION]
    sr = SearchRequest("python", search_in=topics)
    assert sr.search_in == topics


def test_search_request_with_string_search_in_backward_compatibility():
    topic_strings = ["libgen", "fiction"]
    sr = SearchRequest("python", search_in=topic_strings)
    assert len(sr.search_in) == 2
    assert SearchTopic.LIBGEN in sr.search_in
    assert SearchTopic.FICTION in sr.search_in


def test_search_request_default_search_in():
    sr = SearchRequest("python")
    assert len(sr.search_in) == 7  # All topics by default
    assert SearchTopic.LIBGEN in sr.search_in


def test_search_request_invalid_search_type():
    with pytest.raises(ValueError):
        SearchRequest("python", search_type="invalid")
    
    with pytest.raises(TypeError):
        SearchRequest("python", search_type=123)


def test_search_request_invalid_search_in():
    with pytest.raises(ValueError):
        SearchRequest("python", search_in=["invalid_topic"])
    
    with pytest.raises(TypeError):
        SearchRequest("python", search_in=["libgen", SearchTopic.FICTION])  # Mixed types
    
    with pytest.raises(TypeError):
        SearchRequest("python", search_in="not_a_list")


def test_search_request_type_validation():
    with pytest.raises(TypeError):
        SearchRequest(123)  # Query must be string
    
    with pytest.raises(TypeError):
        SearchRequest("python", mirror=123)  # Mirror must be string


# -------- integration tests for LibgenSearch filtered methods --------


class FakeSearchRequest:
    def __init__(self, query, search_type="title", mirror="https://example.org", search_in=None):
        self.query = query
        self.search_type = search_type
        self.mirror = mirror
        self.search_in = search_in

    def aggregate_request_data_libgen(self):
        return BOOKS


def test_search_title_filtered_uses_book_filtering(monkeypatch):
    import libgen_api_enhanced.libgen_search as libmod

    monkeypatch.setattr(libmod, "SearchRequest", FakeSearchRequest)

    svc = LibgenSearch(mirror="is")
    out = svc.search_title_filtered(
        query="q",
        filters={"title": "python"},
        exact_match=False,
    )
    assert {b.title for b in out} == {"Learning Python", "Python Tricks"}


def test_search_author_filtered_exact_match(monkeypatch):
    import libgen_api_enhanced.libgen_search as libmod

    monkeypatch.setattr(libmod, "SearchRequest", FakeSearchRequest)

    svc = LibgenSearch(mirror="li")
    out = svc.search_author_filtered(
        query="q",
        filters={"author": "Ian Goodfellow", "extension": "pdf"},
        exact_match=True,
    )
    assert len(out) == 1
    assert out[0].author == "Ian Goodfellow"


def test_search_default_filtered_non_exact(monkeypatch):
    import libgen_api_enhanced.libgen_search as libmod

    monkeypatch.setattr(libmod, "SearchRequest", FakeSearchRequest)

    svc = LibgenSearch()
    out = svc.search_default_filtered(
        query="q",
        filters={"publisher": "press"},
        exact_match=False,
    )
    assert len(out) == 1
    assert out[0].publisher == "MIT Press"
