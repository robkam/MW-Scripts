# Scripts extracted from ChatGPT

Use at your own risk.

## pcmread.py

The pcmread.py script logs into a MediaWiki wiki, retrieves the page content model for every page in namespaces 0 to 15, and saves the results into a CSV file.

The pcmread.ini file contains the username and password required to log in to the wiki, along with the URL of the wiki. Edit it to suit your requirements.

## pcmwrite.py

The pcmwrite.py script reads a CSV file, logs into a MediaWiki wiki and for every page listed checks the content model and updates it to match if there is a difference.

The pcmwrite.ini file contains the username and password required to log in to the wiki, along with the URL of the wiki and the filename of the CSV file. Edit it to suit your requirements.
