from .search_request import SearchRequest
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs


class LibgenSearch:
    def __init__(self, mirror="is"):
        self.mirror = f"https://libgen.{mirror}/"

    def search_default(self, query):
        search_request = SearchRequest(query, search_type="default", mirror=self.mirror)
        return search_request.aggregate_request_data_libgen()

    def search_default_filtered(self, query, filters, exact_match=False):
        search_request = SearchRequest(query, search_type="default", mirror=self.mirror)
        results = search_request.aggregate_request_data_libgen()
        filtered_results = filter_results(
            results=results, filters=filters, exact_match=exact_match
        )
        return filtered_results

    def search_title(self, query):
        search_request = SearchRequest(query, search_type="title", mirror=self.mirror)
        return search_request.aggregate_request_data_libgen()

    def search_author(self, query):
        search_request = SearchRequest(query, search_type="author", mirror=self.mirror)
        return search_request.aggregate_request_data_libgen()

    def search_title_filtered(self, query, filters, exact_match=True):
        search_request = SearchRequest(query, search_type="title", mirror=self.mirror)
        results = search_request.aggregate_request_data_libgen()
        filtered_results = filter_results(
            results=results, filters=filters, exact_match=exact_match
        )
        return filtered_results

    def search_author_filtered(self, query, filters, exact_match=True):
        search_request = SearchRequest(query, search_type="author", mirror=self.mirror)
        results = search_request.aggregate_request_data_libgen()
        filtered_results = filter_results(
            results=results, filters=filters, exact_match=exact_match
        )
        return filtered_results

    def resolve_direct_download_link(self, item):
        if "Mirror_1" not in item or "MD5" not in item:
            raise KeyError("item must include 'Mirror_1' and 'md5'")

        mirror_url = item["Mirror_1"]
        md5 = item["MD5"]

        resp = requests.get(mirror_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        a = soup.find_all("a", string=lambda s: s and s.strip().upper() == "GET")
        if not a:
            raise ValueError("No GET links found on the mirror page")

        for link in a:
            href = link.get("href")
            if not href:
                continue
            full_url = urljoin(mirror_url, href)
            params = parse_qs(urlparse(full_url).query)
            key_vals = params.get("key")
            if key_vals and key_vals[0]:
                key = key_vals[0]
                cdn_base = getattr(self, "cdn_base", "https://cdn4.booksdl.lc/get.php")
                return f"{cdn_base}?md5={md5}&key={key}"

        raise ValueError("Could not extract 'key' parameter from any GET link")


def filter_results(results, filters, exact_match):
    """
    Returns a list of results that match the given filter criteria.
    When exact_match = true, we only include results that exactly match
    the filters (ie. the filters are an exact subset of the result).

    When exact-match = false,
    we run a case-insensitive check between each filter field and each result.

    exact_match defaults to TRUE -
    this is to maintain consistency with older versions of this library.
    """

    filtered_list = []
    if exact_match:
        for result in results:
            # check whether a candidate result matches the given filters
            if filters.items() <= result.items():
                filtered_list.append(result)

    else:
        filter_matches_result = False
        for result in results:
            for field, query in filters.items():
                if query.casefold() in result[field].casefold():
                    filter_matches_result = True
                else:
                    filter_matches_result = False
                    break
            if filter_matches_result:
                filtered_list.append(result)
    return filtered_list
