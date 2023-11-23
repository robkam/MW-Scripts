import argparse
import configparser
import csv
import logging
import os

import mwclient

CONFIG_FILE = "pcmwrite.ini"  # Change this to your desired configuration file


def read_config(config_file=CONFIG_FILE):
    # Read configuration from a configuration file
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def get_site_info(config_file=CONFIG_FILE):
    config = read_config(config_file)

    # Explicitly specify the section names and provide default values
    url = config.get("Site", "url", fallback="")
    path = config.get("Site", "path", fallback="")
    scheme = config.get("Site", "scheme", fallback="")

    username = config.get("Credentials", "username", fallback="")
    password = config.get("Credentials", "password", fallback="")

    csv_file_path = config.get("Files", "csv_file_path", fallback="")

    return username, password, url, path, scheme, csv_file_path


def login(site, username, password):
    logging.info(f"Logging in with username: {username}")
    site.login(username, password)


def edit_content_model(
    site, page_title, current_content_model, new_content_model, csv_log_writer
):
    try:
        # Get the edit token for the user
        token = site.get_token("edit")

        # Use mwclient to get the current content of the page
        page = site.pages[page_title]

        # Get the current content
        current_content = page.text() or ""

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
            logging.error(
                f"Failed to edit page {page_title}: {result['error']['info']}"
            )
        else:
            logging.info(
                f"Page {page_title} content model changed from {current_content_model} to: {new_content_model}"
            )
            csv_log_writer.writerow(
                [page_title, current_content_model, new_content_model]
            )

    except mwclient.errors.APIError as api_error:
        logging.error(f"MWClient API error: {api_error}")


def edit_pages_via_csv(site, csv_file_path):
    # Prepare log file path
    log_file_path = os.path.splitext(csv_file_path)[0] + ".log"

    # Open log file for writing
    with open(log_file_path, "w", newline="") as log_file:
        csv_log_writer = csv.writer(log_file)

        # Get the edit token for the user
        token = site.get_token("edit")

        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.reader(csvfile)

            for row in csv_reader:
                if len(row) >= 2:  # Ensure each row has at least two columns
                    new_content_model = row[-1].strip()
                    page_title = ",".join(row[:-1]).strip()
                    page = site.pages[page_title]

                    if not page.exists:
                        logging.warning(f"Page {page_title} does not exist. Skipping.")
                        continue

                    page_info = page._info
                    current_content_model = page_info.get("contentmodel", "unknown")

                    logging.debug(
                        f"Page: {page_title}, Current Content Model: {current_content_model}"
                    )

                    # Compare the content models
                    if current_content_model == new_content_model:
                        logging.info(
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


def parse_args():
    parser = argparse.ArgumentParser(description="Your script description.")
    parser.add_argument(
        "--log-level", default="INFO", help="Logging level (default: INFO)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level)

    username, password, wiki_url, path, scheme, csv_file_path = get_site_info(
        config_file=CONFIG_FILE
    )
    site = mwclient.Site(wiki_url, path=path, scheme=scheme)

    try:
        login(site, username, password)
        edit_pages_via_csv(site, csv_file_path)

    except mwclient.errors.LoginError as login_error:
        logging.error(f"Login failed: {login_error}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
