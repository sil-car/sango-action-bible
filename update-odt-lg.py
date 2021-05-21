#!/usr/bin/env python3

"""Programmatically set language type by paragraph in an ODT file."""

# References:
#- https://sodocumentation.net/python/topic/479/manipulating-xml

import re
import shutil
import string
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from pathlib import Path


def build_wordlist(dir, lang):
    """Create a word list from files whose filename matches the given language code. """
    wordlist = set()
    for f in dir.iterdir():
        if f.stem[:5] == lang:
            with open(f, 'r') as l:
                for line in l.readlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        wordlist.add(line.split('/')[0].split()[0].strip())
                    except IndexError as e:
                        print(f"{repr(e)} for \"{line}\"")
    return wordlist

def determine_language(words, language_words_dict, last_text_lang):
    lang_code = ''
    regex_punctuation = re.compile(f'[{re.escape(string.punctuation)}]')
    word_counts_by_lg = count_occurrences_by_lg(words, language_words_dict, regex_punctuation)
    total_words = word_counts_by_lg.pop('words')
    max_count = max(word_counts_by_lg.values())
    lang_codes = []
    for lg, count in word_counts_by_lg.items():
        if count == max_count:
            lang_codes.append(lg)
    lc_length = len(lang_codes)
    if lc_length == 0 or total_words == 0:
        lang_code = last_text_lang
    elif lc_length == 1:
        lang_code = lang_codes[0]
    else:
        # Multiple matches.
        if total_words == 1:
            # One word that matches multiple languages. No way to tell for sure
            #   which language is correct. Default to last_text_lang.
            lang_code = last_text_lang
        else:
            # Default to 'en_US' if matched, or just pick first match.
            if 'en_US' in lang_codes:
                lang_code = 'en_US'
            else:
                lang_code = lang_codes[0]
    return lang_code

def count_occurrences_by_lg(text_words, wordlists, regex):
    # wordlists is a dict: {'lg': {*words}}
    counts = {}
    counts['words'] = 0
    for lang_code in wordlists.keys():
        counts[lang_code] = 0
    for t in text_words:
        counts['words'] += 1
        t = regex.sub('', t.lower()) # remove punctuation
        for lang_code, lg_words in wordlists.items():
            if re.match(r'.*[0-9]+.*', t): # includes digits
                counts[lang_code] += 1
            elif t in lg_words:
                counts[lang_code] += 1
    return counts

def update_zip(file_zip, filename, xml_tree):
    """Update a file in the given ODT ZIP file with data in the given XML tree."""
    # Generate a temp file.
    file_tmp = file_zip.with_suffix('.tmp')

    # Create a temp copy of the archive without filename.
    with zipfile.ZipFile(file_zip, 'r') as zin:
        with zipfile.ZipFile(file_tmp, 'w') as zout:
            zout.comment = zin.comment # preserve the comment
            for item in zin.infolist():
                if item.filename != filename:
                    zout.writestr(item, zin.read(item.filename))

    # Replace archive with the temp archive.
    Path.unlink(file_zip)
    Path.rename(file_tmp, file_zip)

    # Add filename with its new data.
    with zipfile.ZipFile(file_zip, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
        with zf.open('content.xml', mode='w') as content_file:
            xml_tree.write(content_file)

def view_xml(xml_tree):
    """Show the values of the given XML tree."""
    root = xml_tree.getroot()
    namespace = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
    }
    intro_office = '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}'
    intro_style = '{urn:oasis:names:tc:opendocument:xmlns:style:1.0}'
    intro_text = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'
    intro_fo = '{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}'
    for part in root:
        print(part.tag)
    auto_styles = root.find('office:automatic-styles', namespace)
    print(auto_styles.tag, auto_styles.attrib)
    #ET.dump(root)

def update_xml(xml_tree, language_words_dict):
    """Update the paragraph styles of the given XML tree to include the given languages."""
    root = xml_tree.getroot()
    intro_office = '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}'
    intro_style = '{urn:oasis:names:tc:opendocument:xmlns:style:1.0}'
    intro_text = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'
    intro_fo = '{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}'

    for part in root:
        # Create new paragraph styles for each input language code.
        if part.tag == f"{intro_office}automatic-styles":
            for lang_code in language_words_dict:
                [lg, CN] = lang_code.split('_')
                p_style = ET.SubElement(part, f"{intro_style}style")
                p_style.set(f"{intro_style}name", lang_code)
                p_style.set(f"{intro_style}family", "paragraph")
                p_style.set(f"{intro_style}parent-style-name", "Preformatted_20_Text")
                p_text = ET.SubElement(p_style, f"{intro_style}text-properties")
                p_text.set(f"{intro_fo}language", lg)
                p_text.set(f"{intro_fo}country", CN)
                #p2_text.set('{http://openoffice.org/2009/office}paragraph-rsid': '00169b6b')

        # Grab text from each paragraph and determine its language code.
        if part.tag == f"{intro_office}body":
            for paragraphs in part:
                results = []
                last_text_lang = None
                ct = 0
                for p in paragraphs:
                    # Show progress dots: 1 for every X paragraphs.
                    x = 50
                    ct += 1
                    if ct % x == 0:
                        sys.stdout.write('.')
                        sys.stdout.flush()

                    # Determine language code of paragraph.
                    if p.attrib and p.text:
                        words = p.text.split()
                        first_words = ' '.join(words[:4])
                        lang_code = determine_language(words, language_words_dict, last_text_lang)
                        if lang_code:
                            p.set(f"{intro_text}style-name", lang_code)
                    else:
                        lang_code = None
                        first_words = None

                    last_text_lang = lang_code
                    results.append([f"{first_words} ...", lang_code])
                print()
    return xml_tree, results

def print_summary(results):
    """Print summary statistics about number of paragraphs found for each language code."""
    total_p_ct = len(results)
    blank_p_ct = len([r for r in results if r[1] == None])
    sp = ' '*3
    print(f"\n{total_p_ct} paragraphs in the document:\n{sp}{blank_p_ct} are empty")
    p_ct_unknown = total_p_ct - blank_p_ct
    p_ct_by_lang = {}
    for lang_code in language_words_dict:
        ct = len([r for r in results if r[1] == lang_code])
        p_ct_by_lang[lang_code] = ct
        p_ct_unknown -= ct
        print(f"{sp}{ct} are {lang_code}")
    print(f"{sp}{p_ct_unknown} are unknown.")

def print_results(results, start=0, end=-1):
    """Print language code and initial paragraph text for the given range."""
    print()
    total_p_ct = len(results)
    #digit_ct = len(total_p_ct)
    for i, r in enumerate(results[start:end]):
        if r[1] is not None:
            print(f"{i+1+start}. {r[1]}: {r[0]}")


# Define global variables.
infile = ''
outfile = ''
languages = ['en_US', 'fr_FR', 'sg_CF']
repo_root = Path(__file__).resolve().parents[0]
dict_dir = repo_root / 'dict'

# Ensure that a file was passed as an argument.
if len(sys.argv) > 1 and Path(sys.argv[1]).suffix == '.odt':
    infile = Path(sys.argv[1])
else:
    print("Error: Need to pass an ODT file as the first argument.")
    exit(1)

# Ensure that file exists.
if zipfile.is_zipfile(infile):
    infile = infile.resolve()
    # Get XML tree content.xml from ODT file.
    with zipfile.ZipFile(infile, 'r') as odt:
        with odt.open('content.xml', 'r') as content:
            tree = ET.parse(content)
else:
    print("Error: Input file does not exist.")
    exit(1)

# Copy infile to outfile, asking for confirmation if it exists.
langstr = f"__{'__'.join(languages)}"
outfile = infile.with_name(f"{infile.stem}{langstr}{infile.suffix}")
if outfile.is_file():
    answer = input(f"\n{outfile} already exists. Replace it? [Y/n]: ")
    try:
        if answer.strip()[0].lower() == 'n':
            exit(0)
    except IndexError:
        # User hit [Enter] with no text. Accept default overwrite.
        pass

shutil.copyfile(infile, outfile)

# Build word lists.
print(f"\nBuilding word lists for {', '.join(languages)}...")
language_words_dict = {}
for lang_code in languages:
    language_words_dict[lang_code] = build_wordlist(dict_dir, lang_code)
    print(f"{lang_code}: {len(language_words_dict[lang_code])} words")

# Update XML tree.
print(f"\nDetermining the language of each paragraph...")
tree, results = update_xml(tree, language_words_dict)

# Write out the updated file.
update_zip(outfile, 'content.xml', tree)

# Print summary data.
print_summary(results)
#print_results(results, start=10, end=30)
