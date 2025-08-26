import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs
import re
from .book import Book

# WHY
# The SearchRequest module contains all the internal logic for the library.
#
# This encapsulates the logic,
# ensuring users can work at a higher level of abstraction.

# USAGE
# req = search_request.SearchRequest("[QUERY]", search_type="[title]")


class SearchRequest:
    col_names = [
        "ID",
        "Title",
        "Author",
        "Publisher",
        "Year",
        "Language",
        "Pages",
        "Size",
        "Extension",
        "MD5",
        "Mirror_1",
        "Mirror_2",
        "Mirror_3",
        "Mirror_4",
    ]

    def __init__(self, query, search_type="title", mirror="https://libgen.li"):
        self.query = query
        self.search_type = search_type
        self.mirror = mirror

        if len(self.query) < 3:
            raise Exception("Query is too short")

        if search_type not in ["title", "author", "default"]:
            raise Exception('Search type must be one of ["title", "author", "default"]')

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    def get_search_page(self):
        query_parsed = "%20".join(self.query.split(" "))
        if self.search_type.lower() == "title":
            search_url = f"{self.mirror}/index.php?req={query_parsed}&columns%5B%5D=t&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&res=100&filesuns=all"
        elif self.search_type.lower() == "author":
            search_url = f"{self.mirror}/index.php?req={query_parsed}&columns%5B%5D=a&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&res=100&filesuns=all"
        elif self.search_type.lower() == "default":
            search_url = f"{self.mirror}/index.php?req={query_parsed}&columns%5B%5D=t&columns%5B%5D=a&columns%5B%5D=s&columns%5B%5D=y&columns%5B%5D=p&columns%5B%5D=i&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&topics%5B%5D=c&topics%5B%5D=f&topics%5B%5D=a&topics%5B%5D=m&topics%5B%5D=r&topics%5B%5D=s&res=100&filesuns=all"
        if search_url:
            search_page = requests.get(search_url)
            return search_page

        return None

    def aggregate_request_data_libgen(self):
        search_page = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "html.parser")
        self.strip_i_tag_from_soup(soup)

        table = soup.find("table", {"id": "tablelibgen"})
        if table is None:
            return []

        results = []

        for row in table.find_all("tr"):
            tds = row.find_all("td")
            if len(tds) < 9:
                continue

            try:
                title_links = tds[0].find_all("a")
                # print(title_links)
                title = (
                    title_links[0].text.strip()
                    if len(title_links) >= 3
                    else title_links[0].text.strip()
                )
                title = re.sub(r"[^A-Za-z0-9 ]+", "", title)
                first_href = title_links[0]["href"] if title_links else ""
                id_param = parse_qs(urlparse(first_href).query).get("id", [""])[0]

                author = tds[1].get_text(strip=True)
                publisher = tds[2].get_text(strip=True)
                year = tds[3].get_text(strip=True)
                language = tds[4].get_text(strip=True)
                pages = tds[5].get_text(strip=True)

                size_link = tds[6].find("a")
                size = (
                    size_link.get_text(strip=True)
                    if size_link
                    else tds[6].get_text(strip=True)
                )

                extension = tds[7].get_text(strip=True)

                mirror_links = tds[8].find_all("a", href=True)
                mirrors = []
                for a in mirror_links[:4]:
                    href = a["href"].strip()
                    parsed = urlparse(href)
                    abs_url = href if parsed.netloc else urljoin(self.mirror, href)
                    mirrors.append(abs_url)

                while len(mirrors) < 4:
                    mirrors.append("")

                if mirrors[0]:
                    q = parse_qs(urlparse(mirrors[0]).query)
                    md5 = (q.get("md5") or [""])[0]

                book = Book(
                    id_param,
                    title,
                    author,
                    publisher,
                    year,
                    language,
                    pages,
                    size,
                    extension,
                    md5,
                    mirrors[:4],
                )

                book.add_tor_download_link()

                results.append(book)

            except Exception as e:
                print(e)
                continue

        return results
