#!/usr/bin/env python3

"""
Extract comments from ODT file and output as Paratext XML comments.
"""

# References:
#   https://github.com/eea/odfpy/wiki

import odfutils
import random
import re
import sys
import xmlutils

from pathlib import Path


def verify_infile_as_arg(script_args):
    # Ensure that a file was passed as an argument.
    if len(script_args) > 1 and Path(script_args[1]).suffix == '.odt':
        infile = Path(script_args[1]).resolve()
    else:
        print("Error: Need to pass an ODT file as the first argument.")
        exit(1)

    if not infile.is_file():
        print("Error: File does not exist.")
        exit(1)

    return infile

def explore_element_type(doc, type):
    for p in doc.body.getElementsByType(type):
        print(p)

def get_children(paragraphs, depth=0):
    depth += 1
    for p in paragraphs:
        if p.tagName == 'office:annotation':
            print(f"{depth}: {p}")
            continue
        if p.childNodes:
            get_children(p.childNodes, depth)
            if p.tagName == 'office:annotation':
                print(f"{depth}: {p}")

def recurse_through_paragraphs(doc):
    plist = doc.body.getElementsByType(odfutils.P)
    get_children(plist)

def extract_comments(doc, book):
    doc_content = {0: {1: []}}
    comments = {}
    ch_pat = '\s*[Pp][0-9]{2,3}'
    v_pat = 'Panel\s*[0-9]+'

    ch_pat_bytes = re.compile(ch_pat)
    v_pat_bytes = re.compile(v_pat)
    chapter = 0
    verse = 1
    comment_count = 0
    ct = 0
    for p in doc.body.getElementsByType(odfutils.P):
        if not str(p): # blank line
            continue
        ch_match = ch_pat_bytes.search(str(p))
        v_match = v_pat_bytes.search(str(p))
        ptext = convert_to_sfm(str(p), ch_pat_bytes, v_pat_bytes)
        if ch_match:
            chapter = int(ch_match.group().replace('P', '', 1).replace('p', '', 1))
            if chapter == 317 or chapter == 318:
                chapter += 2
            elif chapter == 748:
                chapter += 1
            verse = 1
            doc_content[chapter] = {verse: []}
        if v_match:
            verse = int(v_match.group().replace('Panel', '', 1).replace('Panel ', '', 1))
            doc_content[chapter][verse] = []

        if has_comment(p):
            # Get list of all comments in paragraph.
            pcomments = []
            for i, c in enumerate(p.childNodes):
                if c.tagName == 'office:annotation':
                    pcomments.append(i)
                    comment_count += 1
            pwords = []
            context_before = []
            context_after = []
            prev_comment = 0
            next_comment = -1
            for i, c in enumerate(p.childNodes):
                if c.tagName == 'office:annotation':
                    # Determine indexes of prev and next comments.
                    for j, k in enumerate(pcomments):
                        if k == i:
                            if len(pcomments) >= 1 + j + 1:
                                next_comment = pcomments[j + 1]
                            if j > 0:
                                prev_comment = pcomments[j - 1]

                    # Determine context before comment.
                    context_before = []
                    for n in p.childNodes[prev_comment:i]:
                        context_before.extend(str(n).split())
                    selected_text = ''

                    # Determine end of comment selection.
                    comment_end = i # if there's no selected text
                    if len(p.childNodes) >= 1 + i + 2:
                        if p.childNodes[i + 2].tagName == 'office:annotation-end':
                            # Next child node has selected text.
                            selected_text = str(p.childNodes[i + 1])
                            comment_end = i + 2

                    # Determine context after comment.
                    context_after = []
                    for n in p.childNodes[comment_end + 1:next_comment]:
                        context_after.extend(str(n).split())

                    # Set paragraph words according to context and selected text.
                    pwords = context_before + selected_text.split() + context_after
                    # print(context_after)
                    user = str(c.childNodes[0])
                    if comments.get(user) is None:
                        comments[user] = []

                    verse_ref = f"{book} {chapter}:{verse}"
                    date = str(c.childNodes[1])
                    initials = str(c.childNodes[2])
                    contents = str(c.childNodes[3])
                    start_position = parse_start_position(context_before)
                    comments[user].append(
                        {
                            'Thread':           '%008x' % random.randrange(16**8),
                            'VerseRef':         verse_ref,
                            'Date':             date,
                            'SelectedText':     selected_text,
                            'StartPosition':    start_position,
                            'ContextBefore':    ' '.join(context_before),
                            'ContextAfter':     ' '.join(context_after),
                            'ConflictType':     'unknownConflictType',
                            'Verse':            '',
                            'HideInTextWindow': 'false',
                            'Contents':         contents,
                        }
                    )
                    prev_comment = i

            doc_content[chapter][verse].extend(pwords)

        else:
            doc_content[chapter][verse].extend(ptext.split())

    return comments, doc_content, comment_count

def main():
    # Ensure that a file was passed as an argument.
    infile = verify_infile_as_arg(sys.argv)
    doc = odfutils.load_doc(infile)

    # explore_element_type(doc, odfutils.H)
    recurse_through_paragraphs(doc)

if __name__ == '__main__':
    main()
