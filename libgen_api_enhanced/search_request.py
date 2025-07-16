import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

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
        "Mirror_1",
        "Mirror_2",
        "Mirror_3",
        "Mirror_4",
    ]

    def __init__(self, query, search_type="title", mirror="https://libgen.is"):
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
<<<<<<< HEAD
        if self.search_type.lower() == "title":
            search_url = (
                f"https://libgen.li/index.php?req={query_parsed}&columns%5B%5D=t&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&res=100&filesuns=all"
            )
        elif self.search_type.lower() == "author":
            search_url = (
                f"https://libgen.li/index.php?req={query_parsed}&columns%5B%5D=a&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&res=100&filesuns=all"
            )
        elif self.search_type.lower() == "default":
            sesarch_url = (
                f"https://libgen.li/index.php?req={query_parsed}&columns%5B%5D=t&columns%5B%5D=a&columns%5B%5D=s&columns%5B%5D=y&columns%5B%5D=p&columns%5B%5D=i&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&res=100&filesuns=all"
            )
=======
        if self.mirror == "https://libgen.is/":
            if self.search_type.lower() == "title":
                search_url = f"https://libgen.is/search.php?req={query_parsed}&column=title&res=100"
            elif self.search_type.lower() == "author":
                search_url = f"https://libgen.is/search.php?req={query_parsed}&column=author&res=100"
            elif self.search_type.lower() == "default":
                search_url = f"https://libgen.is/search.php?req={query_parsed}&column=default&res=100"
        else:
            if self.search_type.lower() == "title":
                search_url = (
                    f"{self.mirror}index.php?req={query_parsed})&columns[]=t&res=100"
                )
            elif self.search_type.lower() == "author":
                search_url = (
                    f"{self.mirror}index.php?req={query_parsed})&columns[]=a&res=100"
                )
            elif self.search_type.lower() == "default":
                search_url = f"{self.mirror}index.php?req={query_parsed})&res=100"

>>>>>>> 024057b (working on alternative mirror support)
        search_page = requests.get(search_url)
        return search_page

    def add_direct_download_links(self, output_data):
        # Add a direct download link to each result
        for book in output_data:
            id = book["ID"]
            download_id = str(id)[:-3] + "000"
            md5 = book["Mirror_1"].split("/")[-1].lower()
            title = urllib.parse.quote(book["Title"])
            extension = book["Extension"]
            book["Direct_Download_Link"] = (
                f"https://download.books.ms/main/{download_id}/{md5}/{title}.{extension}"
            )

        return output_data

    def add_book_cover_links(self, output_data):

        ids = ",".join([book["ID"] for book in output_data])

        url = f"https://libgen.li/json.php?ids={ids}&fields=id,md5,openlibraryid"

        response = json.loads(requests.get(url).text)
        print(response.text)
        # match openlibraryid to id
        for book in output_data:
            for book_json in response:
                if book["ID"] == book_json["id"]:
                    book["Cover"] = (
                        f"https://covers.openlibrary.org/b/olid/{book_json['openlibraryid']}-M.jpg"
                    )

        return output_data

    def aggregate_request_data_libgen_original(self):
        search_page = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "html.parser")
        self.strip_i_tag_from_soup(soup)

        # Libgen results contain 3 tables
        # Table2: Table of data to scrape.
        information_table = soup.find_all("table")[1]
        # Determines whether the link url (for the mirror)
        # or link text (for the title) should be preserved.
        # Both the book title and mirror links have a "title" attribute,
        # but only the mirror links have it filled.(title vs title="libgen.io")

        raw_data = [
            [
<<<<<<< HEAD
                values[0].find("a", href=True)['href'].split("id=")[-1],
                values[0].text,
                values[1].text,
                values[2].text,
                values[3].text,
                values[4].text,
                values[6].text,
                values[7].text,
                *[
                    a['href'] if a['href'][0] != "/" else f"https://libgen.li{a['href']}"
                    for a in values[8].find_all("a", href=True)
                ]
=======
                (
                    td.a["href"]
                    if td.find("a")
                    and td.find("a").has_attr("title")
                    and td.find("a")["title"] != ""
                    else "".join(td.stripped_strings)
                )
                for td in row.find_all("td")
>>>>>>> 024057b (working on alternative mirror support)
            ]
            for row in information_table.find_all("tr")[1:]
            if (values := row.find_all("td"))
        ]
        output_data = [dict(zip(self.col_names, row)) for row in raw_data]
<<<<<<< HEAD
        #output_data = self.add_direct_download_links(output_data)
        #output_data = self.add_book_cover_links(output_data)
        return output_data[0]
=======
        output_data = self.add_direct_download_links(output_data)
        output_data = self.add_book_cover_links(output_data)
        return output_data

    def aggregate_request_data_libgen_alt(self):
        search_page = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "html.parser")
        self.strip_i_tag_from_soup(soup)

        information_table = soup.find("table", {"id": "tablelibgen"})

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
            "Mirror_1",
            "Mirror_2",
            "Mirror_3",
            "Mirror_4",
        ]

        all_rows = []

        for row in information_table.find_all("tr"):
            tds = row.find_all("td")
            if len(tds) < 9:
                continue  # skip malformed rows

            try:
                title_links = tds[0].find_all("a")
                title = title_links[2].text.strip() if len(title_links) >= 3 else ""
                id = title_links[0]["href"].split("id=")[-1]
                author = tds[1].text.strip()
                publisher = tds[2].text.strip()
                year = tds[3].text.strip()
                language = tds[4].text.strip()
                pages = tds[5].text.strip()

                size_link = tds[6].find("a")
                size = size_link.text.strip() if size_link else ""

                extension = tds[7].text.strip()

                mirror_links = tds[8].find_all("a")
                mirrors = [
                    (
                        a["href"].strip()
                        if not a["href"].startswith("/")
                        else f"{self.mirror}{a['href']}"
                    )
                    for a in mirror_links[:4]
                ]

                while len(mirrors) < 4:
                    mirrors.append("")

                all_rows.append(
                    [
                        id,
                        title,
                        author,
                        publisher,
                        year,
                        language,
                        pages,
                        size,
                        extension,
                        *mirrors,
                    ]
                )

            except Exception:
                continue  # skip this row on any unexpected error

        output_data = [dict(zip(col_names, row)) for row in all_rows]

        output_data = self.add_direct_download_links(output_data)
        # output_data = self.add_book_cover_links(output_data)
        return output_data
>>>>>>> 024057b (working on alternative mirror support)
