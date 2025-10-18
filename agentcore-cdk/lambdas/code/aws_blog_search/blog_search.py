import requests


def clean_result(result: dict) -> dict:

    # santity check
    fields = result.get("fields")
    if not fields:
        return {}
    link = fields.get("url")
    if not link:
        return {}

    title = fields.get("title")
    description = fields.get("description", "")

    cleaned_result = {"title": title, "link": link, "description": description}

    return cleaned_result

def clean_results(results: list) -> list:
    filtered_hits = []
    for result in results:
        link = result.get("fields",{}).get("url")
        if "/author/" in link:
            print (link)
            continue
        if "/tag/" in link:
            print (link)
            continue
        filtered_hits.append(clean_result(result))

    return filtered_hits

def aws_blog_search(query: str, include_blog: list = [], page: int = 1) -> dict:
    base_url = "https://aws.amazon.com/search/p/2013-01-01/search"

    start_value = (page - 1) * 25
    return_type = "return=description,title,url,type_display,marketplace_architecture,marketplace_price,marketplace_operating_system,marketplace_vendor_name,marketplace_vendor_url"
    options = """&q.parser=structured&q.options={"defaultOperator":"and","fields":["url^5", "title^2", "description", "entry", "categories"]}&highlight.url={max_phrases:5}&highlight.description={max_phrases:5}&facet.type={}&facet.ami_os={}&facet.ami_provider={}&facet.ami_type={}&facet.blog_name={}"""
    paging = f"size=25&start={start_value}&sort=custom_20160114 desc"

    # (and (not type: 'developertools') (not type: 'solution_providers'))
    blog_filter = ""
    if len(include_blog):
        blog_filter = " ".join([f" blog_name:'{b}' " for b in include_blog])
        q = f"or " + " ".join(
            [
                f"(and '{query}' blog_name:'{b}' type: 'blogs' (and (not type: 'developertools') (not type: 'solution_providers')) (or (term field=lang 'en')) )"
                for b in include_blog
            ]
        )
    else:
        q = f"and (and '{query}' {blog_filter} type: 'blogs' (and (not type: 'developertools') (not type: 'solution_providers')) (or (term field=lang 'en')) )"

    print(q)

    try:
        final_url = f"{base_url}?q=({q})&{paging}&{options}&{return_type}"
        # print(final_url)
        response = requests.get(final_url)
        response.raise_for_status()
        response_json = response.json()
        hits = response_json.get("hits", {}).get("hit", [])
        print(f"Found {len(hits)} results")

        return {"results": clean_results(hits)}

    except Exception as e:
        print(f"Error in search: {e}")
        return {"error": f"Error in search: {e}", "results": []}
