# Python scripts for MediaWiki

The scripts were extracted from ChatGPT and have been found to be functional. Usage is at your own risk.

## Page content model reading and editing

Edit pcmread.ini to suit, then do ```python pcmread.py``` to dump a CSV file.

Edit and correct the dumped CSV file. The correct page content models should be apparent.

* Almost every page and all talk pages = wikitext
* Common.css and Print.css pages = css
* Other .css pages = sanitized-css
* .js pages = javascript
* Module pages = scribunto

Edit pcmwrite.ini to suit, then do ```python pcmwrite.py```. It will read the CSV file and alter any mismatched page content models, and write a log file of those changes.

### pcmread.py

The pcmread.py script logs into a MediaWiki wiki, retrieves the page content model for every page, and saves the results into a CSV file.

The pcmread.ini file contains the username and password required to log in to the wiki, along with the URL of the wiki. Edit it to suit your requirements.

### pcmwrite.py

The pcmwrite.py script reads a CSV file, logs into a MediaWiki wiki and for every page listed checks the content model and if there is a difference, updates it to match.

The pcmwrite.ini file contains the username and password required to log in to the wiki, along with the URL of the wiki and the filename of the CSV file. Edit it to suit your requirements.
