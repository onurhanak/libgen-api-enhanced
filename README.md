<h1>LibgenAPI Enhanced</h1>

Search Library Genesis programmatically using an enhanced Python library. This fork extends the original `libgen-api` by [Harrison Broadbent](https://github.com/harrison-broadbent/libgen-api) with added features like direct download links and book cover links. It also returns 100 results by default, instead of 25.

## Contents

- [Getting Started](#getting-started)
- [Basic Searching](#basic-searching)
- [Filtered Searching](#filtered-searching)
  - [Filtered Title Searching](#filtered-title-searching)
  - [Filtered Author Searching](#filtered-author-searching)
  - [Non-exact Filtered Searching](#non-exact-filtered-searching)
  - [Filter Fields](#filter-fields)
- [Contributors](#contributors)

## Getting Started

Install the package -

```
pip install libgen-api-enhanced
```


## Basic Searching:

**The library by default uses the .li mirror. You can pass any mirror extension you like such as: .bz, .gs etc.**

Use the default search or search by title or author:

### Default:

```python
# search_default()

from libgen_api_enhanced import LibgenSearch
s = LibgenSearch()
results = s.search_default("Pride and Prejudice") # a list of Book objects
```

### Title:

```python
# search_title()

from libgen_api_enhanced import LibgenSearch
s = LibgenSearch()
results = s.search_title("Pride and Prejudice") # a list of Book objects
```

### Author:

```python
# search_author()

from libgen_api_enhanced import LibgenSearch
s = LibgenSearch()
results = s.search_author("Jane Austen") # a list of Book objects
```

Check out the [results layout](#results-layout) to see available fields and how the results data is formatted.

## Filtered Searching

- You can define a set of filters, and then use them to filter the search results that get returned.
- By default, filtering will remove results that do not match the filters exactly (case-sensitive) -
  - This can be adjusted by setting `exact_match=False` when calling one of the filter methods, which allows for case-insensitive and substring filtering.

### Filtered Title Searching

```python
# search_title_filtered()

from libgen_api_enhanced import LibgenSearch

tf = LibgenSearch()
title_filters = {"year": "2007", "extension": "epub"}
titles = tf.search_title_filtered("Pride and Prejudice", title_filters, exact_match=True) # a list of Book objects
```

### Filtered Author Searching

```python
# search_author_filtered()

from libgen_api_enhanced import LibgenSearch

af = LibgenSearch()
author_filters = {"language": "German", "year": "2009"}
titles = af.search_author_filtered("Agatha Christie", author_filters, exact_match=True) # a list of Book objects
```

### Non-exact Filtered Searching

```python
# search_author_filtered(exact_match = False)

from libgen_api_enhanced import LibgenSearch

ne_af = LibgenSearch()
partial_filters = {"year": "200"}
titles = ne_af.search_author_filtered("Agatha Christie", partial_filters, exact_match=False) # a list of Book objects

```
## Getting Direct Download Links

The previous books.ms source is no longer available, so this package now provides two options:

- tor_download_link — a prebuilt direct link to the LibGen onion mirror.
- resolved_download_link — a direct HTTP link resolved at runtime from one of the available mirrors.

Example:

```python
from libgen_api_enhanced import LibgenSearch

s = LibgenSearch()
results = s.search_default("Pride and Prejudice")  # returns a list of Book objects

book = results[0]

# Option 1: Use the prebuilt onion mirror link
print(book.tor_download_link)

# Option 2: Resolve an HTTP direct download link from a mirror
book.resolve_direct_download_link()
print(book.resolved_download_link)
```

## Results Layout

Results are returned as a list of Book objects:

```
[
    Book(
        id="123456",
        title="Title",
        author="John Smith",
        publisher="Publisher",
        year="2021",
        language="German",
        pages="410",
        size="1005 Kb",
        extension="epub",
        md5="ABCDEF1234567890",
        mirrors=[
            "http://example.com/mirror1",
            "http://example.com/mirror2",
            "http://example.com/mirror3",
            "http://example.com/mirror4"
        ],
        tor_download_link="http://example.com/tor",
        resolved_download_link="http://example.com/direct"
    )
]
```

## Contributors

Please don't hesitate to raise an issue, or fork this project and improve on it.

Thanks to the following people:

- [harrison-broadbent](https://github.com/harrison-broadbent) who wrote the original Libgen API.
- [calmoo](https://github.com/calmoo)
- [HENRYMARTIN5](https://github.com/HENRYMARTIN5)
