#!/usr/bin/env python3

"""
Filter out text by language type from an ODT file.
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


def get_styles_dict(doc):
    return doc.styles_dict

def get_relevant_paragraph_styles(styles_dict, language, country):
    relevant_p_styles = set()

    # Determine paragraph styles marked with given language and country.
    ns_fo = set()
    for k, v in styles_dict.items():
        ns = v.namespaces
        # if not ns_fo:
        for n, d in ns.items():
            if d == 'fo':
                ns_fo.add(n)

        for c in v.childNodes:
            attribs = c.attributes
            ns_fo_list = list(ns_fo)
            ns_fo_list.sort()
            curr_lang = attribs.get((ns_fo_list[0], 'language'))
            curr_ctry = attribs.get((ns_fo_list[0], 'country'))
            set(ns_fo)
            if curr_lang == language and curr_ctry == country:
                relevant_p_styles.add(k)
    # print(ns_fo)
    return relevant_p_styles

def get_all_paragraphs(doc):
    return list(doc.getElementsByType(P))

def get_text_from_paragraph(paragraph):
    ptext = []
    for c in paragraph.childNodes:
        try:
            # print(f"{c.data}\n")
            ptext.append(c.data.strip())
        except AttributeError:
            pass
    return ptext

def filter_by_language(all_paragraphs, language, country, relevant_p_styles):
    matched_paragraphs = []

    # Search document for matching paragraph styles and print their text to sdtout.
    matched_styles = set()
    for p in all_paragraphs:
        curr_style = p.getAttribute('stylename')
        # print(curr_style)
        if curr_style in relevant_p_styles:
            matched_styles.add(curr_style)
            ptext = get_text_from_paragraph(p)
            if ptext:
                # print(ptext)
                matched_paragraphs.append(' '.join(ptext))

        # Check child nodes.
        ptext = []
        for c in p.childNodes:
            # Skip child nodes that have no attributes.
            # if not c.attributes:
            #     continue
            # Get curr_style from child node.
            # curr_style = None
            # for a, s in c.attributes.items():
            #     if a[1] == 'style-name':
            #         curr_style = s

            # Skip child nodes that have no curr_style.
            # if not curr_style:
            #     continue

            ctext = get_text_from_paragraph(c)
            # if curr_style in relevant_p_styles:
            #     # Add child node text if curr_style is relevant.
            #     matched_styles.add(curr_style)
            #     if ctext:
            #         # print(f"matchedA: {ctext}")
            #         ptext.append(''.join(ctext))
            # elif len(ctext) == 1 and len(ctext[0]) == 1 and ctext[0].isalpha() and ctext[0].upper() == ctext[0]:
            #     # Add all single capital letters; they seem to be from capitalization fixes.
            #     # print(f"matchedB: {ctext}")
            #     ptext.append(''.join(ctext))
            # else:
            #     print(f"ignored: {ctext}")
            #     pass
            ptext.append(''.join(ctext))
        if ptext:
            # print(f"text added: {ptext}")
            matched_paragraphs.append(' '.join(ptext))

    return matched_paragraphs, matched_styles

def print_sorted_list_from_set(input_set):
    input_list = list(input_set)
    input_list.sort()
    print(input_list)

def main():
    # Parse options (language, ODT file).
    infile = ''
    language = ''
    country = ''

    # Ensure that a language and file were passed as arguments.
    if len(sys.argv) > 2 and Path(sys.argv[2]).suffix == '.odt':
        infile = Path(sys.argv[2])
        lang_code = sys.argv[1].split('-')
        language = lang_code[0]
        country = lang_code[1]
    else:
        print(f"Usage: {sys.argv[0]} LANG file.odt\n\n\tLANG is in the format \"en-US\"")
        exit(1)
    # print(f"language:\t{language}\ncountry:\t{country}\n")

    # Ensure that input file exists.
    if infile.is_file() and infile.suffix == '.odt':
        infile = infile.resolve()
        # Load content.
        doc = load(infile)
    else:
        print("Error: Input file does not exist.")
        exit(1)

    # Get all document styles.
    all_styles_dict = doc._styles_dict
    # print(all_styles_dict)

    # Filter for relevant paragraph styles.
    relevant_p_styles = get_relevant_paragraph_styles(all_styles_dict, language, country)
    # print_sorted_list_from_set(relevant_p_styles)

    # Get all paragraphs from document.
    all_paragraphs = get_all_paragraphs(doc)

    # Keep only paragraphs marked with input language.
    matched_paragraphs, matched_styles = filter_by_language(all_paragraphs, language, country, relevant_p_styles)

    # Send text to STDOUT.
    print('\n\n'.join(matched_paragraphs))
    # print(matched_styles)

    exit()

if __name__ == '__main__':
    main()
