#!/usr/bin/env python3

"""
Programmatically set language type by paragraph in an ODT file.
"""

# References:
#   https://github.com/eea/odfpy/wiki

import re
import shutil
import string
import sys

from odf.opendocument import load
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties
from odf.text import P
from pathlib import Path

import hs


def determine_language(words, last_text_lang, hs_dics):
    lang_code = ''
    regex_punctuation = re.compile(f'[{re.escape(string.punctuation)}]')
    word_counts_by_lg = count_occurrences_by_lg(words, regex_punctuation, hs_dics)
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

def get_hs_dics(dir, lang_codes):
    hs_dics = {}
    for lc in lang_codes:
        hs_dics[lc] = hs.get_hs_dic(dir, lc)
    return hs_dics

def count_occurrences_by_lg(text_words, regex, hs_dics):
    counts = {}
    counts['words'] = 0
    for lang_code in hs_dics.keys():
        counts[lang_code] = 0
    for t in text_words:
        counts['words'] += 1
        t = t.lower()
        for lang_code, d in hs_dics.items():
            if not d:
                pass
            elif hs.lookup_word(d, t):
                counts[lang_code] += 1
    return counts

def update_autostyles(doc, lang_codes):
    """
    Update The automatic paragraph styles of the given ODT document to include
    the given languages.
    """
    for lang_code in lang_codes:
        [lg, CN] = lang_code.split('_')
        pstyle = Style(
            name=lang_code,
            family="paragraph",
        )
        pstyle.addElement(TextProperties(language=lg, country=CN))
    return doc

def update_paragraphs_styles(doc, hs_dics):
    results = []
    last_text_lang = None
    ct = 0
    for p in doc.body.getElementsByType(P):
        # Show progress dots: 1 for every X paragraphs.
        x = 50
        ct += 1
        if ct % x == 0:
            sys.stdout.write('.')
            sys.stdout.flush()

        # Determine language code of paragraph.
        words = []
        for n in p.childNodes:
            try:
                words.extend(n.data.split())
            except AttributeError:
                pass
        if words:
            first_words = ' '.join(words[:4])
            lang_code = determine_language(words, last_text_lang, hs_dics)
            if lang_code:
                p.setAttribute('stylename', lang_code)
        else:
            lang_code = None
            first_words = None

        last_text_lang = lang_code
        results.append([f"{first_words} ...", lang_code])
    print()
    return doc, results

def print_summary(results, hs_dics):
    """
    Print summary statistics about number of paragraphs found for each language code.
    """
    total_p_ct = len(results)
    blank_p_ct = len([r for r in results if r[1] == None])
    sp = ' '*3
    print(f"\n{total_p_ct} paragraphs in the document:\n{sp}{blank_p_ct} are empty")
    p_ct_unknown = total_p_ct - blank_p_ct
    p_ct_by_lang = {}
    for lang_code in hs_dics.keys():
        ct = len([r for r in results if r[1] == lang_code])
        p_ct_by_lang[lang_code] = ct
        p_ct_unknown -= ct
        print(f"{sp}{ct} are {lang_code}")
    # for r in results:
    #     print(r[0])
    print(f"{sp}{p_ct_unknown} are unknown.")

def print_results(results, hs_dics, start=0, end=-1):
    """
    Print language code and initial paragraph text for the given range.
    """
    print()
    total_p_ct = len(results)
    #digit_ct = len(total_p_ct)
    for i, r in enumerate(results[start:end]):
        if r[1] is not None:
            print(f"{i+1+start}. {r[1]}: {r[0]}")

def main():
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
    if infile.is_file() and infile.suffix == '.odt':
        infile = infile.resolve()
        # Load content.
        doc = load(infile)
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

    # Get hunspell dictionaries.
    hs_dics = get_hs_dics(dict_dir, languages)

    # Update XML tree.
    print(f"\nDetermining the language of each paragraph...")
    doc = update_autostyles(doc, hs_dics.keys())
    doc, results = update_paragraphs_styles(doc, hs_dics)

    # Write out the updated file.
    doc.save(outfile)

    # Print summary data.
    print_summary(results, hs_dics)
    #print_results(results, hs_dics, start=10, end=30)


if __name__ == '__main__':
    main()
