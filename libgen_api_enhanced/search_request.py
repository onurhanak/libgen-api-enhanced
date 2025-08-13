import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs, quote
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
            search_url = f"{self.mirror}/index.php?req={query_parsed}&columns%5B%5D=t&columns%5B%5D=a&columns%5B%5D=s&columns%5B%5D=y&columns%5B%5D=p&columns%5B%5D=i&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&res=100&filesuns=all"

        # if self.mirror == "https://libgen.is/":
        #     if self.search_type.lower() == "title":
        #         search_url = f"https://libgen.is/search.php?req={query_parsed}&column=title&res=100"
        #     elif self.search_type.lower() == "author":
        #         search_url = f"https://libgen.is/search.php?req={query_parsed}&column=author&res=100"
        #     elif self.search_type.lower() == "default":
        #         search_url = f"https://libgen.is/search.php?req={query_parsed}&column=default&res=100"
        # else:
        #     if self.search_type.lower() == "title":
        #         search_url = (
        #             f"{self.mirror}index.php?req={query_parsed})&columns[]=t&res=100"
        #         )
        #     elif self.search_type.lower() == "author":
        #         search_url = (
        #             f"{self.mirror}index.php?req={query_parsed})&columns[]=a&res=100"
        #         )
        #     elif self.search_type.lower() == "default":
        #         search_url = f"{self.mirror}index.php?req={query_parsed})&res=100"

        if search_url:
            search_page = requests.get(search_url)
            return search_page

        return None

    def add_direct_download_links(self, output_data):
        # Add a direct download link to each result
        for book in output_data:
            md5 = book["MD5"]
            title = quote(book["Title"])
            extension = book["Extension"]
            book["Direct_Download_Tor_Link"] = (
                f"http://libgenfrialc7tguyjywa36vtrdcplwpxaw43h6o63dmmwhvavo5rqqd.onion/LG/01311000/{md5}/{title}.{extension}"
            )

        return output_data

    # def add_book_cover_links(self, output_data):
    #     ids = ",".join([book["ID"] for book in output_data])
    #
    #     url = f"https://libgen.bz/json.php?ids={ids}&fields=id,md5,openlibraryid"
    #     print(url)
    #
    #     response = json.loads(requests.get(url).text)
    #
    #     # match openlibraryid to id
    #     for book in output_data:
    #         for book_json in response:
    #             if book["ID"] == book_json["id"]:
    #                 book["Cover"] = (
    #                     f"https://covers.openlibrary.org/b/olid/{book_json['openlibraryid']}-M.jpg"
    #                 )
    #
    #     return output_data

    # def aggregate_request_data_libgen_original(self):
    #     search_page = self.get_search_page()
    #     soup = BeautifulSoup(search_page.text, "html.parser")
    #     self.strip_i_tag_from_soup(soup)
    #
    #     information_table = soup.find_all("table")[1]
    #
    #     raw_data = [
    #         [
    #             values[0].find("a", href=True)["href"].split("id=")[-1],
    #             values[0].text,
    #             values[1].text,
    #             values[2].text,
    #             values[3].text,
    #             values[4].text,
    #             values[6].text,
    #             values[7].text,
    #             *[
    #                 (
    #                     a["href"]
    #                     if a["href"][0] != "/"
    #                     else f"https://libgen.li{a['href']}"
    #                 )
    #                 for a in values[8].find_all("a", href=True)
    #             ],
    #         ]
    #         for row in information_table.find_all("tr")[1:]
    #         if (values := row.find_all("td"))
    #     ]
    #     output_data = [dict(zip(self.col_names, row)) for row in raw_data]
    #     output_data = self.add_direct_download_links(output_data)
    #     # output_data = self.add_book_cover_links(output_data)
    #     return output_data[0]
    def aggregate_request_data_libgen(self):
        search_page = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "html.parser")
        self.strip_i_tag_from_soup(soup)

        table = soup.find("table", {"id": "tablelibgen"})
        if table is None:
            return []

        rows_out = []

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

                md5 = ""
                if mirrors[0]:
                    q = parse_qs(urlparse(mirrors[0]).query)
                    md5 = (q.get("md5") or [""])[0]

                rows_out.append(
                    [
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
                        *mirrors[:4],
                    ]
                )

            except Exception as e:
                print(e)
                continue

        output_data = [dict(zip(self.col_names, row)) for row in rows_out]
        output_data = self.add_direct_download_links(output_data)
        # output_data = self.add_book_cover_links(output_data)
        return output_data
