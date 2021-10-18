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

def has_comment(paragraph):
    status = False
    for c in paragraph.childNodes:
        if c.tagName == 'office:annotation':
            status = True
    return status

def get_verse_text(doc_content, ref):
    chapter, verse = ref.split()[1].split(':')
    return doc_content[int(chapter)][int(verse)]

def parse_start_position(words_before):
    return str(len(' '.join(words_before)))

def convert_to_sfm(text, ch_pat_bytes, v_pat_bytes):
    is_chapter = ch_pat_bytes.search(text)
    is_verse = v_pat_bytes.search(text)
    if is_chapter:
        text = text.replace('P', '\\c ', 1)
    if is_verse:
        text = text.replace('Panel', '\\v ', 1)
    return(text)

def extract_comments(doc, book):
    doc_content = {0: {1: []}}
    comments = {}
    ch_pat = '\s*[Pp][0-9]{2,3}'
    v_pat = 'Panel\s*[0-9]+'

    ch_pat_bytes = re.compile(ch_pat)
    v_pat_bytes = re.compile(v_pat)
    chapter = 0
    verse = 1
    verse_text = []
    # is_comment = False
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
            verse = 1
            doc_content[chapter] = {verse: []}
        if v_match:
            verse = int(v_match.group().replace('Panel', '', 1).replace('Panel ', '', 1))
            doc_content[chapter][verse] = []
            verse_text = [] # reset verse_text

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

            verse_text.extend(pwords)
            doc_content[chapter][verse].extend(pwords)

        else:
            verse_text.extend(ptext.split())
            doc_content[chapter][verse].extend(ptext.split())

    return comments, doc_content, comment_count

def main():
    # Ensure that a file was passed as an argument.
    infile = verify_infile_as_arg(sys.argv)
    doc = odfutils.load_doc(infile)

    # Extract comments from ODT file.
    comments_dict, doc_content, comment_count = extract_comments(doc, 'XXA')

    # Add in verse text.
    for u, comments in comments_dict.items():
        for c in comments:
            c['Verse'] = ' '.join(get_verse_text(doc_content, c.get('VerseRef')))

    # print(f"{comment_count} comments found by script.")
    # print(f"406 comments found by grepping XML for 'office:annotation'")

    # Convert comments to Paratext XML.
    for user, comments in comments_dict.items():
        xml = xmlutils.build_notes_xml(user, comments)
        file_name = f"Notes_{user}.xml"
        outfile = infile.with_name(file_name)
        outfile.write_text(xml)
        # print(xml)

if __name__ == '__main__':
    main()
