import configparser
from urllib.parse import urlparse

import mwclient


def read_config(config_file="pcmread.ini"):
    # Read configuration from a configuration file
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def login(site, username, password):
    # Login to the wiki
    print(f"Logging in with username: {username}")
    site.login(username, password)


def get_subdomain(url):
    # Extract subdomain from the URL
    parsed_url = urlparse(url)

    if parsed_url.hostname:
        subdomain = parsed_url.hostname.split(".")[0]
        return subdomain
    elif parsed_url.path:
        # If there's no scheme, but there is a path, try to extract subdomain from the path
        subdomain = parsed_url.path.split(".")[0]
        return subdomain
    else:
        print(
            f"Error: Unable to extract subdomain from the URL. Parsed URL: {parsed_url}"
        )
        return None


def get_all_pages_in_namespace(site, namespace):
    # Skip namespaces -1 and -2
    SKIP_NAMESPACES = [-1, -2]

    if int(namespace) in SKIP_NAMESPACES:
        return []

    all_pages = []
    params = {
        "generator": "allpages",
        "gapnamespace": int(namespace),
        "prop": "info",
        "inprop": "contentmodel",
        "gaplimit": 50000,
    }

    while True:
        try:
            result = site.api("query", **params)
            query = result["query"]
            pages = query.get("pages", {})
        except KeyError as e:
            print(f"Unexpected response structure: {result}")
            break

        # Extract only the necessary information
        all_pages.extend(
            [
                (page["title"], page.get("contentmodel", "Unknown"))
                for page in pages.values()
            ]
        )

        if "continue" in result:
            # Adjust the continue parameter for the next batch
            params["gapfrom"] = result["continue"]["gapcontinue"]
        else:
            break

    return all_pages


def main():
    # Set your wiki site with the correct order of parameters
    config = read_config()
    site_url = config.get("Site", "url")
    site = mwclient.Site(
        site_url, path=config.get("Site", "path"), scheme=config.get("Site", "scheme")
    )

    # Get credentials
    username, password = config.get("Credentials", "username"), config.get(
        "Credentials", "password"
    )

    # Login to the wiki
    login(site, username, password)

    # Get all namespaces from the site
    all_namespaces = site.api("query", meta="siteinfo", siprop="namespaces")["query"][
        "namespaces"
    ]

    # Extract subdomain from the site URL
    subdomain = get_subdomain(site_url)

    # Collect all pages in all namespaces
    all_pages = []
    for namespace, namespace_info in all_namespaces.items():
        print(f"Fetching pages for namespace {namespace}...")
        try:
            # Fetch all pages in the specified namespace
            pages_in_namespace = get_all_pages_in_namespace(site, namespace)
            all_pages.extend(pages_in_namespace)
        except mwclient.errors.APIError as e:
            print(f"Error in namespace {namespace}: {e}")

    # Print the list of all page titles and content models for all namespaces
    for title, content_model in all_pages:
        print(f'"{title}","{content_model}"')

    # Write the results to a single file with the subdomain in the filename
    file_name = f"{subdomain}.csv"
    with open(file_name, "w", encoding="utf-8") as file:
        for title, content_model in all_pages:
            file.write(f'"{title}","{content_model}"\n')

    print(f"Results for all namespaces saved to: {file_name}")


if __name__ == "__main__":
    main()
