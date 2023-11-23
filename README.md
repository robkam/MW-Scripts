# Python scripts for MediaWiki

The scripts were extracted from ChatGPT and have been found functional. Usage is at your own risk.

## Page content model reading and editing

Edit pcmread.ini to suit, then do ```python pcmread.py``` to dump a CSV file.

Edit and correct the dumped CSV file. The correct page content models should be apparent. However, it can vary depending on the version of MediaWiki and the installed extensions. Special:AllPages has a dropdown menu for the namespaces.

* Almost every page and all talk pages = wikitext
* Common.css and Print.css pages = css
* Other .css pages = sanitized-css
* .js pages = javascript
* .json pages = json
* Module pages = scribunto

Edit pcmwrite.ini to suit, then do ```python pcmwrite.py``` to read the CSV file. It will alter any mismatched page content models and write a log file of those changes.

### pcmread.py

The pcmread.py script logs into a MediaWiki wiki, retrieves the page content model for every page in namespaces 0 to 15, and saves the results into a CSV file.

The pcmread.ini file contains the username and password required to log in to the wiki, along with the URL of the wiki. Edit it to suit your requirements.

### pcmwrite.py

The pcmwrite.py script reads a CSV file, logs into a MediaWiki wiki and for every page listed checks the content model and if there is a difference, updates it to match.

The pcmwrite.ini file contains the username and password required to log in to the wiki, along with the URL of the wiki and the filename of the CSV file. Edit it to suit your requirements.
