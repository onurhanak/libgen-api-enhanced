<div align="center">
  
# LibgenAPI Enhanced

A python wrapper for Library Genesis that supports new mirrors, fine-grained searching, and provides direct download links.

</div>

## Getting Started

Install the package:

```bash
pip install libgen-api-enhanced
```

## Choosing Libgen Mirror

The library by default uses the .li mirror. You can pass any mirror extension you like (as long as the website structure is the same) such as: .bz, .gs etc. when initializng LibgenSearch() like so:

```python
from libgen_api_enhanced import LibgenSearch

s = LibgenSearch(mirror="bz")
```

## Basic Searching:

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
## Search Types and Topics

The new version provides search configuration options for further narrowing down your queries.

### Search Types

Control which fields are searched:

```python
from libgen_api_enhanced import SearchType

SearchType.TITLE    # search in titles only
SearchType.AUTHOR   # search in authors only
SearchType.DEFAULT  # search across title, author, series, year, publisher, and ISBN
```

### Search Topics

Specify which Libgen topics to search:

```python
from libgen_api_enhanced import SearchTopic

# topics:
SearchTopic.LIBGEN
SearchTopic.COMICS
SearchTopic.FICTION
SearchTopic.ARTICLES
SearchTopic.MAGAZINES
SearchTopic.FICTION_RUS
SearchTopic.STANDARDS
```


### Using SearchRequest Directly with Enums:

```python
from libgen_api_enhanced import SearchRequest, SearchType, SearchTopic

# search only in fiction and comics
search_topics = [SearchTopic.FICTION, SearchTopic.COMICS]
req = SearchRequest(
    query="Douglas Adams",
    search_type=SearchType.AUTHOR,
    search_in=search_topics
)
results = req.aggregate_request_data_libgen()
```

### Specifying Search Topics:

```python
from libgen_api_enhanced import LibgenSearch, SearchTopic

s = LibgenSearch()

# search only in specific topics
my_topics = [SearchTopic.LIBGEN, SearchTopic.ARTICLES]
results = s.search_title("quantum physics", search_in=my_topics)

# search only in fiction
fiction_results = s.search_author("Isaac Asimov", search_in=[SearchTopic.FICTION])
```

## Filtered Searching

- You can define a set of filters, and then use them to filter the search results that get returned.
- By default, filtering will remove results that do not match the filters exactly (case-sensitive)
  - This can be adjusted by setting `exact_match=False` when calling one of the filter methods, which allows for case-insensitive and substring filtering.

### Filtered Title Searching

```python
# search_title_filtered()

from libgen_api_enhanced import LibgenSearch, SearchTopic

tf = LibgenSearch()
title_filters = {"year": "2007", "extension": "epub"}

# search only in fiction database
fiction_topics = [SearchTopic.FICTION]
titles = tf.search_title_filtered(
    "Pride and Prejudice",
    title_filters,
    exact_match=True,
    search_in=fiction_topics
)
```

### Filtered Author Searching

```python
# search_author_filtered()

from libgen_api_enhanced import LibgenSearch, SearchTopic

af = LibgenSearch()
author_filters = {"language": "German", "year": "2009"}

# search in multiple topics
search_topics = [SearchTopic.LIBGEN, SearchTopic.FICTION]
titles = af.search_author_filtered(
    "Agatha Christie",
    author_filters,
    exact_match=True,
    search_in=search_topics
)
```

### Non-exact Filtered Searching

```python
# search_author_filtered(exact_match = False)

from libgen_api_enhanced import LibgenSearch, SearchTopic

ne_af = LibgenSearch()
partial_filters = {"year": "200"}

string_topics = ["libgen", "fiction"]  # str format
enum_topics = [SearchTopic.LIBGEN, SearchTopic.FICTION]  # enum format

titles = ne_af.search_author_filtered(
    "Agatha Christie",
    partial_filters,
    exact_match=False,
    search_in=enum_topics  # or string_topics
)
```
## Getting Direct Download Links

books.ms domain is no longer available, so this package now provides two options for getting download links:

- tor_download_link — a prebuilt direct link to the Libgen onion mirror.
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

## Credits

This library is a fork of [libgen-api](https://github.com/harrison-broadbent/libgen-api) written by [harrison-broadbent](https://github.com/harrison-broadbent).
