import configparser
import csv
import os

import mwclient


def get_site_info():
    config = configparser.ConfigParser()
    config.read("pcmwrite.ini")

    url = config.get("Site", "url")
    path = config.get("Site", "path")
    scheme = config.get("Site", "scheme")

    username = config.get("Credentials", "username")
    password = config.get("Credentials", "password")

    csv_file_path = config.get("Files", "csv_file_path")

    return username, password, url, path, scheme, csv_file_path


def login(site, username, password):
    print(f"Logging in with username: {username}")
    site.login(username, password)


def edit_content_model(
    site, page_title, current_content_model, new_content_model, csv_log_writer
):
    # Get the edit token for the user
    token = site.get_token("edit")

    # Use mwclient to get the current content of the page
    page = site.pages[page_title]

    # Get the current content
    current_content = page.text()

    # Ensure current_content is not None
    if current_content is None:
        current_content = ""

    # Use mwclient to make the API call
    result = site.post(
        "edit",
        title=page_title,
        token=token,
        format="json",
        contentmodel=new_content_model,
        text=current_content,
    )

    # Check for successful edit
    if "error" in result:
        print(f"Failed to edit page {page_title}: {result['error']['info']}")
    else:
        print(
            f"Page {page_title} content model changed from {current_content_model} to: {new_content_model}"
        )
        csv_log_writer.writerow([page_title, current_content_model, new_content_model])


def edit_pages_via_csv(site, csv_file_path):
    # Prepare log file path
    log_file_path = os.path.splitext(csv_file_path)[0] + ".log"

    # Open log file for writing
    with open(log_file_path, "w", newline="") as log_file:
        csv_log_writer = csv.writer(log_file)

        # Read and process the CSV file
        with open(csv_file_path, newline="") as csvfile:
            csv_reader = csv.reader(csvfile)

            # Get the edit token for the user
            token = site.get_token("edit")

            for row in csv_reader:
                if len(row) == 2:  # Ensure each row has two columns
                    page_title, new_content_model = row

                    # Use mwclient to get the current content of the page
                    page = site.pages[page_title]

                    # Check if the page exists
                    if not page.exists:
                        print(f"Page {page_title} does not exist. Skipping.")
                        continue

                    # Get the current content model by making a separate API request
                    page_info = page._info
                    current_content_model = page_info.get("contentmodel", "unknown")

                    # Print the current content model for debugging
                    print(
                        f"Page: {page_title}, Current Content Model: {current_content_model}"
                    )

                    # Compare the content models
                    if current_content_model == new_content_model:
                        print(
                            f"Page {page_title} content model is already: {new_content_model}. Skipping."
                        )
                        continue

                    # Edit the page using mwclient
                    edit_content_model(
                        site,
                        page_title,
                        current_content_model,
                        new_content_model,
                        csv_log_writer,
                    )


def main():
    username, password, wiki_url, path, scheme, csv_file_path = get_site_info()
    site = mwclient.Site(wiki_url, path=path, scheme=scheme)

    try:
        login(site, username, password)
        edit_pages_via_csv(site, csv_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
