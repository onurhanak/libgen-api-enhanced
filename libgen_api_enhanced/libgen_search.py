from .search_request import SearchRequest, SearchType


class LibgenSearch:
    def __init__(self, mirror="li"):
        self.mirror = f"https://libgen.{mirror}/"

    def search_default(self, query, search_in=None):
        search_request = SearchRequest(
            query,
            search_type=SearchType.DEFAULT,
            mirror=self.mirror,
            search_in=search_in,
        )
        return search_request.aggregate_request_data_libgen()

    def search_default_filtered(
        self, query, filters, exact_match=False, search_in=None
    ):
        search_request = SearchRequest(
            query,
            search_type=SearchType.DEFAULT,
            mirror=self.mirror,
            search_in=search_in,
        )
        results = search_request.aggregate_request_data_libgen()
        filtered_results = filter_books(
            results=results, filters=filters, exact_match=exact_match
        )
        return filtered_results

    def search_title(self, query, search_in=None):
        search_request = SearchRequest(
            query, search_type=SearchType.TITLE, mirror=self.mirror, search_in=search_in
        )
        return search_request.aggregate_request_data_libgen()

    def search_author(self, query, search_in=None):
        search_request = SearchRequest(
            query,
            search_type=SearchType.AUTHOR,
            mirror=self.mirror,
            search_in=search_in,
        )
        return search_request.aggregate_request_data_libgen()

    def search_title_filtered(self, query, filters, exact_match=True, search_in=None):
        search_request = SearchRequest(
            query, search_type=SearchType.TITLE, mirror=self.mirror, search_in=search_in
        )
        results = search_request.aggregate_request_data_libgen()
        filtered_results = filter_books(
            results=results, filters=filters, exact_match=exact_match
        )
        return filtered_results

    def search_author_filtered(self, query, filters, exact_match=True, search_in=None):
        search_request = SearchRequest(
            query,
            search_type=SearchType.AUTHOR,
            mirror=self.mirror,
            search_in=search_in,
        )
        results = search_request.aggregate_request_data_libgen()
        filtered_results = filter_books(
            results=results, filters=filters, exact_match=exact_match
        )
        return filtered_results


def _norm_str(x):
    if x is None:
        return ""
    return str(x).casefold()


def filter_books(results, filters, exact_match):
    out = []

    if not filters:
        return list(results)

    for book in results:
        ok = True
        for field, want in filters.items():
            if not hasattr(book, field):
                raise KeyError(f"Unknown field '{field}'")
            have = getattr(book, field)

            if exact_match:
                if isinstance(want, str) or isinstance(have, str):
                    if _norm_str(have) != _norm_str(want):
                        ok = False
                        break
                else:
                    if have != want:
                        ok = False
                        break
            else:
                if _norm_str(want) not in _norm_str(have):
                    ok = False
                    break

        if ok:
            out.append(book)

    return out
