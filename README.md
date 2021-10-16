# sango-action-bible

This is a collection of scripts written to aid SIL CAR's checking of the Sango Action Bible, originally drafted by someone else. The draft text was ultimately converted into Paratext project files.

Requires:
```bash
$ sudo apt install python3-dev libhunspell-dev
```

### Conversion from ODT to SFM

#### Clean up ODT file and convert to TXT files. [28 min]

- Download ODT from Drive. [2 min]
- Move to Sango Action Bible folder; rename to add current date. [1 min]
- Open ODT and turn off Track Changes tracking & visibility; re-save & close. [15 min]
- Move text to new ODT "no-tracked-changes" file to remove tracked changes: New > Insert text from document... [3 min]
- Use update-odt-lg.py to fix paragraphs that are marked with the incorrect language. [1 min]
- Export comments?
- Copy file and rename by adding _en-US. [1 min]
- Copy file and rename by adding _sg-CF. [1 min]
- en-US file: [2 min]
  - Use Find/Replace to change language of P### paragraphs to English: ```^\s*[pP][0-9]{2,3}```.
  - Use Find/Replace to select all French and Sango text and remove with Backspace.
  - Save As TXT file.
- sg-CF file: [2 min]
  - Use Find/Replace to change language of P### paragraphs to Sango: ```^\s*[pP][0-9]{2,3}```.
  - Use Find/Replace to select and remove all French and English text.
  - Save As TXT file.

#### Clean up text files with clean-up-text.sh [1 min]

- Remove all non-breaking spaces (0xC2 0xA0)
- Remove progress markers: xxx###
- Remove work records: #/##/##
- Remove lines that are all caps and/or spaces.
- Remove lines more than 4 characters that are all caps, and/or spaces, and/or numbers.
- Fix out-of-order P254 near end of file.
- Fix mis-numbered page numbers.
- Fix wrongly formatted page numbers.

#### Convert to SFM with convert-txt-2-sfm.sh [1 min]

- Set output file name and path.
- Add project ID.
- Add chapter markers.
- Add verse markers.
- Add paragraph markers.
- Insert comments from ODT?

### To-Do List
- Build in native handling of namespace: [StackOverflow explanation](https://stackoverflow.com/questions/14853243/parsing-xml-with-namespace-in-python-via-elementtree#14853417)
