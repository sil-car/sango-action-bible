# sang-action-bible

This is a collection of scripts written to aid SIL CAR's checking of the Sango Action Bible, originally drafted by someone else. The draft text was ultimately converted into Paratext project files.

Requres:
```bash
$ sudo apt install python3-dev libhunspell-dev
```

### Conversion from ODT to SFM

- Download ODT from Drive. [5 min]
- Move to Sango Action Bible folder; rename to add current date. [1 min]
- Open ODT and turn off Track Changes tracking & visibilty; re-save & close. [10 min]
- Move text to new ODT file to remove tracked changes: New > Insert text from document... [2 min]
- Use Find/Replace to change language of P### paragraphs to English.
- Use Find/Replace to select all English text.
- Copy to new text file with same name + en-US.
- Use Find/Replace to change language of P### paragraphs to Sango.
- Use Find/Replace to select all Sango text.
- Copy to new text file with same name + sg-CF.
- Export comments?
- Clean up text files:
  - remove progress markers: xxx###
  - remove work records: #/##/##

### To-Do List
- build in native handling of namespace: [StackOverflow explanation](https://stackoverflow.com/questions/14853243/parsing-xml-with-namespace-in-python-via-elementtree#14853417)
