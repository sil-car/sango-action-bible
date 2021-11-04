#!/usr/bin/env python3

"""Harmonize the verse markers between EAB and SAB Paratext project files."""

import sys

from pathlib import Path as p

# The SAB has all the appropriate verse markers, so its markers just need to be
#   transferred to the EAB.
# The only valid reference points are the chapter markers, so the sequence is:
#   - read both files into memory
#   - make a dictionary of relevant info from SAB:
#       {ch#: {'line-number': #, 'paragraph-count': #p, 'paragraphs': [], 'verses': {1: i_of_p, 2: i_of_p, etc.}}

def get_info_dict(text):
    text_info = {}
    ch = None
    for i, line in enumerate(text.splitlines()):
        if line[:2] == '\c':
            try:
                ch = int(line.split()[1])
            except ValueError:
                pass
            text_info[ch] = {
                'line-number': i,
                'paragraph-count': 0,
                'paragraphs': [],
                'verses': {}
            }
        if ch and line[:2] == '\p':
            text_info[ch]['paragraph-count'] += 1
            text_info[ch]['paragraphs'].append(line)
        if ch and line[:2] == '\\v':
            vn = int(line.split()[1])
            text_info[ch]['verses'][vn] = text_info[ch]['paragraph-count'] - 1
    return text_info

def add_verse_markers(binfo, tinfo):
    output_lines_rev = []
    binfo_chs = [k for k in binfo.keys()]
    for bc in binfo_chs[::-1]:
        bch_vns = [k for k in binfo.get(bc).get('verses').keys()]
        for bvn in bch_vns[::-1]:
            bpi = binfo.get(bc).get('verses').get(bvn)
            # print(f"{bc}:{bvn}, {bpi}")
            current_ptext = tinfo.get(bc).get('paragraphs')[bpi]
            if bvn not in tinfo.get(bc).get('verses'):
                # print(f"Insert verse {bv} at paragraph {bp + 1} of chapter {bc}")
                line_no = tinfo.get(bc).get('line-number') + bpi + 1
                new_ptext = f"\p\n\\v {bvn} {current_ptext[3:]}"
                output_lines_rev.append(new_ptext)
            else:
                output_lines_rev.append(current_ptext)
    return output_lines_rev

def verify_paragraph_count(binfo, tinfo):
    mismatched_paragraphs = {}
    binfo_chs = [k for k in binfo.keys()]
    for bc in binfo_chs[::-1]:
        bch_vns = [k for k in binfo.get(bc).get('verses').keys()]
        b_p_ct = binfo.get(bc).get('paragraph-count')
        t_p_ct = tinfo.get(bc).get('paragraph-count')
        if t_p_ct != b_p_ct:
            # Number of paragraphs don't match. Add all chapter text to output_lines_rev.
            mismatched_paragraphs[bc] = {
                'base': b_p_ct,
                'target': t_p_ct,
            }
    return mismatched_paragraphs

def get_total_paragraph_count(info):
    pct = 0
    for values in info.values():
        pct += values.get('paragraph-count')
    return pct

def main():
    # Parse arguments.
    args = sys.argv[1:]
    if len(args) != 2:
        print("Error: This script requires 2 input files as arguments: SAB.SFM EAB.SFM")
        exit(1)
    basefile, targetfile = args
    basefile = p(basefile).resolve()
    targetfile = p(targetfile).resolve()

    # Read file contents.
    basetext = basefile.read_text()
    targettext = targetfile.read_text()

    # Gather needed info.
    baseinfo = get_info_dict(basetext)
    targetinfo = get_info_dict(targettext)

    # Check paragraph counts.
    mismatched_paragraphs = verify_paragraph_count(baseinfo, targetinfo)
    if mismatched_paragraphs:
        mp_rev = [k for k in mismatched_paragraphs.keys()]
        # for mp, values in mismatched_paragraphs.items():
        for mp in mp_rev[::-1]:
            v = mismatched_paragraphs.get(mp)
            print(f"\c {mp}: base has {v.get('base')}, target has {v.get('target')}")
        total_p_base = get_total_paragraph_count(baseinfo)
        total_p_target = get_total_paragraph_count(targetinfo)
        total_p_diff = total_p_base - total_p_target
        print(f"Paragraph counts differ by {total_p_diff} (base: {total_p_base}, target: {total_p_target})")
        exit(1)

    # Add verse markers into target file's info.
    output_lines_rev = add_verse_markers(baseinfo, targetinfo)
    # Print output lines in proper order.
    for l in output_lines_rev[::-1]:
        print(l)


if __name__ == '__main__':
    main()
