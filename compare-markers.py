#!/usr/bin/env python3

"""Compare chapter and verse markers between EAB and SAB Paratext project files."""

import sys

from pathlib import Path as p


def get_info_dict(text):
    text_info = {}
    ch = 0
    for i, line in enumerate(text.splitlines()):
        start = line.split()[0]
        valid_lines = [
            '\p',
            '\id',
            '\ip',
        ]
        if not text_info.get(ch):
            text_info[ch] = {
                'line-number': i,
                'paragraph-count': 0,
                'paragraphs': [],
                'verses': {}
            }
        if start == '\c':
            try:
                ch = int(line.split()[1])
            except ValueError:
                pass
        elif start in valid_lines:
            text_info[ch]['paragraph-count'] += 1
            text_info[ch]['paragraphs'].append(line)
        elif start == '\\v':
            try:
                vn = int(line.split()[1])
            except ValueError as e:
                print(e)
                print(f"\c {ch}: {line}")
                exit(1)
            text_info[ch]['verses'][vn] = text_info[ch]['paragraph-count'] - 1
            text_info[ch]['paragraphs'][-1] = f"\p\n{line}"
    return text_info

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
                'diff': b_p_ct - t_p_ct,
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
    base_name = basefile.stem.strip('94XXA')
    target_name = targetfile.stem.strip('94XXA')

    # Read file contents.
    basetext = basefile.read_text()
    targettext = targetfile.read_text()
    len_base = len(basetext.splitlines())
    len_target = len(targettext.splitlines())

    # Gather needed info.
    baseinfo = get_info_dict(basetext)
    targetinfo = get_info_dict(targettext)

    # Check paragraph counts.
    mismatched_paragraphs = verify_paragraph_count(baseinfo, targetinfo)
    mp_rev = [k for k in mismatched_paragraphs.keys()]
    for mp in mp_rev[::-1]:
        v = mismatched_paragraphs.get(mp)
        print(f"\c {mp:3}:\t\tdiff: {v.get('diff'):4}\t{base_name}: {v.get('base'):5}\t{target_name}: {v.get('target'):5}")
    total_p_base = get_total_paragraph_count(baseinfo)
    total_p_target = get_total_paragraph_count(targetinfo)
    total_p_diff = total_p_base - total_p_target
    print(f"Total ps:\tdiff: {total_p_diff:4}\t{base_name}: {total_p_base:5}\t{target_name}: {total_p_target:5}")
    print(f"Total lines:\tdiff: {len_base-len_target:4}\t{base_name}: {len_base:5}\t{target_name}: {len_target:5}")
    exit(1)


if __name__ == '__main__':
    main()
