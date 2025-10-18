from bs4_extract import extract

def format_extract_results_for_agent(tavily_result):
    """
    Format Tavily extract results into a well-structured string for language models.

    Args:
        tavily_result (Dict): A Tavily extract result dictionary

    Returns:
        str: A formatted string with extract results organized for easy consumption by LLMs
    """
    if not tavily_result or "results" not in tavily_result:
        return "No extract results found."

    formatted_results = []

    # Process successful results
    results = tavily_result.get("results", [])
    for i, doc in enumerate(results, 1):
        url = doc.get("url", "No URL")
        raw_content = doc.get("raw_content", "")
        images = doc.get("images", [])

        formatted_doc = f"\nEXTRACT RESULT {i}:\n"
        formatted_doc += f"URL: {url}\n"

        if raw_content:
            # Truncate very long content for readability
            if len(raw_content) > 5000:
                formatted_doc += f"Content: {raw_content}\n" # no limit
            else:
                formatted_doc += f"Content: {raw_content}\n"
        else:
            formatted_doc += "Content: No content extracted\n"

        if images:
            formatted_doc += f"Images found: {len(images)} images\n"
            for j, image_url in enumerate(images[:3], 1):  # Show up to 3 images
                formatted_doc += f"  Image {j}: {image_url}\n"
            if len(images) > 3:
                formatted_doc += f"  ... and {len(images) - 3} more images\n"

        formatted_results.append(formatted_doc)

    # Process failed results if any
    failed_results = tavily_result.get("failed_results", [])
    if failed_results:
        formatted_results.append("\nFAILED EXTRACTIONS:\n")
        for i, failure in enumerate(failed_results, 1):
            url = failure.get("url", "Unknown URL")
            error = failure.get("error", "Unknown error")
            formatted_results.append(f"Failed {i}: {url} - {error}\n")



    return "\n" + "".join(formatted_results)

def web_extract(urls: str | list[str], include_images: bool = False, extract_depth: str = "basic"
) -> str:
    """Extract content from one or more web pages using Tavily's extract API.

    Args:
        urls (str | list[str]): A single URL string or a list of URLs to extract content from.
        include_images (bool, optional): Whether to also extract image URLs from the pages.
                                       Defaults to False.
        extract_depth (str, optional): The depth of extraction. 'basic' provides standard
                                     content extraction, 'advanced' provides more detailed
                                     extraction. Defaults to "basic".

    Returns:
        str: A formatted string containing the extracted content from each URL, including
             the full raw content, any images found (if requested), and information about
             any URLs that failed to be processed.
    """
    try:
        # Ensure urls is always a list for the API call
        if isinstance(urls, str):
            urls_list = [urls]
        else:
            urls_list = urls

        # Clean and validate URLs
        cleaned_urls = []
        for url in urls_list:
            if url.strip().startswith("{") and '"url":' in url:
                import re

                m = re.search(r'"url"\s*:\s*"([^"]+)"', url)
                if m:
                    url = m.group(1)

            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            cleaned_urls.append(url)

        api_response = extract(cleaned_urls)

        # Format the results for the agent
        formatted_results = format_extract_results_for_agent(api_response)
        return formatted_results

    except Exception as e:
        return f"Error during extraction: {e}\nURLs attempted: {urls}\nFailed to extract content."



