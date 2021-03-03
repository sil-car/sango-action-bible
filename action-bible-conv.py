#!/usr/bin/env python3

'''
Attempt to programmatically set language type by paragraph in the Action Bible English/Sango text.

References:
- https://sodocumentation.net/python/topic/479/manipulating-xml
'''

import sys
import xml.etree.ElementTree as ET

from pathlib import Path


def build_wordlist(dir, lang):
    wordlist = []
    for f in dir.iterdir():
        if f.stem[:2] == lang[:2]:
            with open(f, 'r') as l:
                for line in l.readlines():
                    #word = line.split('/')[0].strip()
                    wordlist.append(line.split('/')[0].strip())
    return list(set(wordlist))


# Define global variables.
infile = ''
outfile = ''
repo_root = Path(__file__).resolve().parents[0]
dict_dir = repo_root / 'dict'

# Ensure that a file was passed as an argument.
if len(sys.argv) > 1:
    infile = Path(sys.argv[1])
else:
    print("Error: Need to pass file as argument.")
    exit(1)

# Ensure that file exists.
if infile.is_file():
    tree = ET.parse(infile)
    outfile = infile.resolve().with_name(f"{infile.stem}-mod{infile.suffix}")
else:
    print("Error: Input file does not exist.")
    exit(1)

# Build English wordlist.
eng_wordlist = build_wordlist(dict_dir, 'english')

# Build Sango wordlist.
sag_wordlist = build_wordlist(dict_dir, 'sango')

# Remove any terms in Sango list from English list.
eng_uniq_wordlist = [w for w in eng_wordlist if w not in sag_wordlist]

# Evaluate XML file.
root = tree.getroot()
pstyle = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name'
for part in root:
    if part.tag.split('}')[1] == 'automatic-styles':
        # TODO: Add in styles for P2 (English) and P3 (Sango).
        '''
        <office:automatic-styles>
          <style:style style:name="P1" style:family="paragraph" style:parent-style-name="Preformatted_20_Text">
            <style:text-properties officeooo:paragraph-rsid="00169b6b"/>
          </style:style>
          <style:style style:name="P2" style:family="paragraph" style:parent-style-name="Preformatted_20_Text">
            <style:text-properties fo:language="en" fo:country="US" officeooo:paragraph-rsid="00169b6b"/>
          </style:style>
        </office:automatic-styles>
        '''
        #part.set('style', 'P2')
        pass
    if part.tag.split('}')[1] == 'body':
        for paragraphs in part:
            total = len(paragraphs)
            ct = 0
            eng_paragraph_ct = 0
            null_paragraph_ct = 0
            other_paragraph_ct = 0
            for p in paragraphs:
                ct += 1
                if p.attrib and p.text:
                    #print(f"{p.attrib[pstyle]} {p.text}")
                    eng_word_ct = 0
                    words = []
                    for word in p.text.split():
                        if word.lower() in eng_uniq_wordlist:
                            # Wait until at least 3 English words are found in paragraph.
                            eng_word_ct += 1
                            words.append(word)
                            if eng_word_ct > 2:
                                eng_paragraph_ct += 1
                                print(f"{ct}/{total} paragraphs checked: English ({', '.join(words)})")
                                p.set(pstyle, 'P2')
                                break
                        else:
                            #print(f"{p.attrib[pstyle]} Other")
                            pass
                    other_paragraph_ct += 1
                else:
                    null_paragraph_ct += 1

# Write out the updated file.
tree.write(outfile)

# Print out stats.
print(f"{total} paragraphs: {null_paragraph_ct} are empty, {eng_paragraph_ct} are English, {other_paragraph_ct} are \"other\"")

# Recompress file to ODT with:
# ~(subfiles folder)$ zip -r ../<filename>.odt mimetype .
