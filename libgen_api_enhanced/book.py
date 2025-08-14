import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs


class Book:
    def __init__(
        self,
        id,
        title,
        author,
        publisher,
        year,
        language,
        pages,
        size,
        extension,
        md5,
        mirrors,
    ):
        self.id = id
        self.title = title
        self.author = author
        self.publisher = publisher
        self.year = year
        self.language = language
        self.pages = pages
        self.size = size
        self.extension = extension
        self.md5 = md5
        self.mirrors = mirrors
        self.tor_download_link = None
        self.resolved_download_link = None

    def add_tor_download_link(self):
        self.tor_download_link = f"http://libgenfrialc7tguyjywa36vtrdcplwpxaw43h6o63dmmwhvavo5rqqd.onion/LG/01311000/{self.md5}/{self.title}.{self.extension}"

    def resolve_direct_download_link(self):
        mirror_url = self.mirrors[0]
        md5 = self.md5

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
                self.resolved_download_link = f"{cdn_base}?md5={md5}&key={key}"
                return

        raise ValueError("Could not extract 'key' parameter from any GET link")
