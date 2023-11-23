import configparser

import mwclient


def get_credentials():
    # Read credentials from a configuration file
    config = configparser.ConfigParser()
    config.read("pcmread.ini")

    username = config.get("Credentials", "username")
    password = config.get("Credentials", "password")

    return username, password


def get_site_info():
    # Read site information from a configuration file
    config = configparser.ConfigParser()
    config.read("pcmread.ini")

    url = config.get("Site", "url")
    path = config.get("Site", "path")
    scheme = config.get("Site", "scheme")

    return mwclient.Site(url, path=path, scheme=scheme)


def login(site):
    # Get credentials
    username, password = get_credentials()

    print(f"Logging in with username: {username}")
    site.login(username, password)


def get_all_pages_in_namespace(site, namespace):
    all_pages = []
    params = {
        "generator": "allpages",
        "gapnamespace": namespace,
        "prop": "info",
        "inprop": "contentmodel",
        "gaplimit": 500,
    }

    while True:
        try:
            result = site.api("query", **params)
            query = result["query"]
            pages = query.get("pages", {})
        except KeyError:
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
    site = get_site_info()

    # Login to the wiki
    login(site)

    # Set the namespaces to query, including 0 to 15 and the additional values
    namespaces = list(range(16)) + [100, 101, 118, 119, 710, 711, 828, 829]

    # Collect all pages in all namespaces
    all_pages = []
    for namespace in namespaces:
        try:
            # Fetch all pages in the specified namespace
            pages_in_namespace = get_all_pages_in_namespace(site, namespace)
            all_pages.extend(pages_in_namespace)

        except mwclient.errors.APIError as e:
            print(f"Error in namespace {namespace}: {e}")

    # Print the list of all page titles and content models for all namespaces
    for title, content_model in all_pages:
        print(f'"{title}","{content_model}"')

    # Write the results to a single file
    file_name = "pages_content_model.csv"
    with open(file_name, "w", encoding="utf-8") as file:
        for title, content_model in all_pages:
            file.write(f'"{title}","{content_model}"\n')

    print(f"Results for all namespaces saved to: {file_name}")


if __name__ == "__main__":
    main()
