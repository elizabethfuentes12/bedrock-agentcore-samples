
extract_target = dict(
    description="""Extract content from one or more web pages using Bs4.
Args:
    urls (str | list[str]): A single URL string or a list of URLs to extract content from.

Returns:
    str: A formatted string containing the extracted content from each URL, including
        the full raw content, any images found (if requested), and information about any URLs that failed to be processed.
""",
    input_schema={
        "properties": {
            "urls": {
                "type": "array",
                "description": "A single URL string or a list of URLs to extract content from.",
                "type": "string",
            },
        },
        "required": ["urls"],
        "type": "object",
    },
    name="web_extract",
)

aws_blogs_search_target = dict(
    description="""Perform a search in official Amazon Connect AWS Blogs. Returns the search results as a json with the title, link, and description of each result ranked by relevance.

Args:
    query (str): The search query to be sent for the blog search.
    page (int | 1, optional): specific page to retrieve (each page has 25 results) Valid values: 1-2, Defaults to 1.
    Returns: results (List[dict]): The blog search results, a list of objects",
""",
    input_schema={
        "properties": {
            "query": {
                "description": "The search query to be sent for the blog search.",
                "type": "string",
            },
            "page": {
                "description": "The page to return, each page has 25 elements.",
                "type": "integer",
            },
        },
        "required": ["query"],
        "type": "object",
    },
    name="aws_blogs_search",
)
