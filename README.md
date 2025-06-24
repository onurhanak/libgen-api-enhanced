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
Use the default search or search by title or author:

### Default:

```python
# search_default()

from libgen_api_enhanced import LibgenSearch
s = LibgenSearch()
results = s.search_default("Pride and Prejudice")
print(results)
```

### Title:

```python
# search_title()

from libgen_api_enhanced import LibgenSearch
s = LibgenSearch()
results = s.search_title("Pride and Prejudice")
print(results)
```

### Author:

```python
# search_author()

from libgen_api_enhanced import LibgenSearch
s = LibgenSearch()
results = s.search_author("Jane Austen")
print(results)
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
title_filters = {"Year": "2007", "Extension": "epub"}
titles = tf.search_title_filtered("Pride and Prejudice", title_filters, exact_match=True)
print(titles)
```

### Filtered Author Searching

```python
# search_author_filtered()

from libgen_api_enhanced import LibgenSearch

af = LibgenSearch()
author_filters = {"Language": "German", "Year": "2009"}
titles = af.search_author_filtered("Agatha Christie", author_filters, exact_match=True)
print(titles)
```

### Non-exact Filtered Searching

```python
# search_author_filtered(exact_match = False)

from libgen_api_enhanced import LibgenSearch

ne_af = LibgenSearch()
partial_filters = {"Year": "200"}
titles = ne_af.search_author_filtered("Agatha Christie", partial_filters, exact_match=False)
print(titles)

```

## Results Layout

Results are returned as a list of dictionaries:

```json
[
  {
    "ID": "123456",
    "Author": "John Smith",
    "Title": "Title",
    "Publisher": "Publisher",
    "Year": "2021"
    "Pages": "410",
    "Language": "German",
    "Size": "1005 Kb",
    "Extension": "epub",
    "Mirror_1": "http://example.com",
    "Mirror_2": "http://example.com",
    "Mirror_3": "http://example.com",
    "Mirror_4": "http://example.com",
    "Mirror_5": "http://example.com",
    "Direct_Download_Link": "http://example.com",
    "Cover": "https://covers.openlibrary.org/b/olid/OL1234-M.jpg"
  }]
```

## Contributors

Please don't hesitate to raise an issue, or fork this project and improve on it.

Thanks to the following people:

- [harrison-broadbent](https://github.com/harrison-broadbent) who wrote the original Libgen API.
- [calmoo](https://github.com/calmoo)
- [HENRYMARTIN5](https://github.com/HENRYMARTIN5)
