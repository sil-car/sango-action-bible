#!/usr/bin/env python3

"""
Split out text to multiple text files by language type.
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


def get_paragraphs(doc):
    # Create a list of word strings.
    paragraphs = []
    for p in doc.body.getElementsByType(P):
        # Get text of each paragraph.
        words = []
        for n in p.childNodes:
            try:
                words.extend(n.data.split())
            except AttributeError:
                pass
        paragraphs.append(words)
    return paragraphs

def get_lines(text_file):
    with open(text_file) as f:
        lines = f.readlines()
    # Strip newlines.
    lines = [p.strip().split() for p in lines[:]]
    return lines

def determine_language(words, hs_dics, default_lang):
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
        lang_code = None
    elif lc_length == 1:
        lang_code = lang_codes[0]
    else:
        # Multiple matches.
        if total_words == 1:
            # One word that matches multiple languages. No way to tell for sure
            #   which language is correct. Default to first language code.
            lang_code = default_lang
        else:
            # Default to 'en_US' if matched, or just pick first match.
            if 'en_US' in lang_codes:
                lang_code = 'en_US'
            else:
                lang_code = default_lang
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
    default_lang = languages[0]
    repo_root = Path(__file__).resolve().parents[0]
    dict_dir = repo_root / 'dict'

    # Ensure that a file was passed as an argument.
    suffix = Path(sys.argv[1]).suffix.lower()
    if len(sys.argv) > 1 and suffix == '.odt' or suffix == '.txt':
        infile = Path(sys.argv[1])
    else:
        print("Error: Need to pass an ODT or TXT file as the first argument.")
        exit(1)

    # Ensure that file exists.
    if infile.is_file():
        infile = infile.resolve()
    else:
        print("Error: Input file does not exist.")
        exit(1)

    # Create outfiles dictionary.
    languages.append('unknown')
    outfiles = {l: infile.with_name(f"{infile.stem}_{l}.txt") for l in languages}
    outtext = {l: [] for l in languages}

    # Get hunspell dictionaries.
    hs_dics = get_hs_dics(dict_dir, languages)

    # Load file content; set dependent variables.
    if suffix == '.odt':
        file_type = 'ODT'
        unit = 'paragraph'
        end = '\n'
        doc = load(infile)
        parts = get_paragraphs(doc)
    elif suffix == '.txt':
        file_type = 'TXT'
        unit = 'line'
        end = '\n'
        parts = get_lines(infile)
    else:
        print("Error: not an ODT or TXT file.")
        exit(1)

    # Determine the language of each unit.
    results = []
    for words in parts:
        if not words:
            continue
        # print(words)
        first_words = ' '.join(words[:4])
        # last_lang = None
        lang_code = determine_language(words, hs_dics, default_lang)
        if not lang_code:
            lang_code = 'unknown'
        outtext[lang_code].append(' '.join(words))
        results.append([f"{first_words} ...", lang_code])

    # Write outtext to outfiles.
    for l, f in outfiles.items():
        if outtext[l]:
            f.write_text('\n'.join(outtext[l]))

    # Print summary data.
    # print_results(results, hs_dics, start=0, end=-1)
    print_summary(results, hs_dics)


if __name__ == '__main__':
    main()
