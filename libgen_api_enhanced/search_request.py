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

    def __init__(self, query, search_type="title"):
        self.query = query
        self.search_type = search_type

        if len(self.query) < 3:
            raise Exception("Query is too short")

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    def get_search_page(self):
        query_parsed = "%20".join(self.query.split(" "))
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
            book['Direct_Download_Link'] = f"https://download.books.ms/main/{download_id}/{md5}/{title}.{extension}"

        return output_data

    def add_book_cover_links(self, output_data):

        ids = ','.join([book['ID'] for book in output_data])

        url = f"https://libgen.li/json.php?ids={ids}&fields=id,md5,openlibraryid"

        response = json.loads(requests.get(url).text)
        print(response.text)
        # match openlibraryid to id
        for book in output_data:
            for book_json in response:
                if book['ID'] == book_json['id']:
                    book['Cover'] = f"https://covers.openlibrary.org/b/olid/{book_json['openlibraryid']}-M.jpg"

        return output_data

    def aggregate_request_data(self):
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
            ]
            for row in information_table.find_all("tr")[1:]
            if (values := row.find_all("td"))
        ]
        output_data = [dict(zip(self.col_names, row)) for row in raw_data]
        #output_data = self.add_direct_download_links(output_data)
        #output_data = self.add_book_cover_links(output_data)
        return output_data[0]
