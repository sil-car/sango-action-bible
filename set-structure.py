#!/usr/bin/env python3

# Find Action Bible page numbers (P###) and panel numbers (Kapa#) from the
#   Sango translation and set the same panel numbers (Panel#) in the English
#   translation.

import re
import sys

from pathlib import Path


def get_lines_from_file(input):
    lines = []
    infile = Path(input).resolve()
    if infile.is_file():
        with open(infile) as f:
            lines = f.readlines()
    else:
        print(usage_text)
        exit(1)
    return lines

def get_page_and_panel_dict(lines):
    pp_dict = {}
    page_pat = 'P[0-9]{2,3}'
    panel_pat = 'Kapa\s?[0-9]{1,2}'
    page_c = re.compile(page_pat)
    panel_c = re.compile(panel_pat)
    last_pg_line = 0
    this_pg = None
    for i, l in enumerate(lines):
        # Check if line is a page number.
        pg_m = page_c.match(l)
        if pg_m:
            # print(pg_m[0])
            last_pg_line = i
            this_pg = pg_m[0]
            pp_dict[this_pg] = [i]
            continue
        # Check if line is a panel number.
        pa_m = panel_c.match(l)
        if pa_m:
            # print(pa_m[0])
            pp_dict[this_pg].append(i - last_pg_line)
            continue

    return pp_dict

def insert_panel_labels(pp_dict, out_lines):
    updated_lines = out_lines[:]

    for p, v in pp_dict.items():
        # print(p, v, file=sys.stderr)
        pgl = v[0]
        pals = v[1:]
        for i, line in enumerate(updated_lines):
            l = line.strip()
            if l == p:
                # print(f"found {p} at line {i}", file=sys.stderr)
                for j, pal in enumerate(pals):
                    # print(pal, file=sys.stderr)
                    updated_lines.insert(i + pal, f"Panel {j + 1}\n")
                    # print(f"inserting \"Panel {j + 1}\" at line {i + pal}", file=sys.stderr)
            continue

    return updated_lines

def main():
    # Read reference file (sg-CF) and file to be modified (en-US).
    usage_text = f"usage: {sys.argv[0]} REF_FILE OUT_FILE"
    if len(sys.argv) != 3:
        print(usage_text)
        exit(1)

    ref_lines = get_lines_from_file(sys.argv[1])
    out_lines = get_lines_from_file(sys.argv[2])


    # Make dictionary with page numbers as keys (P01-P7##).
    # Set values to a list of numbers
    #   - that describe how many lines after the paragraph mark each panel is found.
    pp_dict = get_page_and_panel_dict(ref_lines)

    # In the output file find the corresponding page numbers,
    #   then insert each panel number the correct number of lines after the page number.
    out_text = ''.join(insert_panel_labels(pp_dict, out_lines))

    # Print output.
    # print(ref_lines, file=sys.stderr)
    # print(out_lines, file=sys.stderr)
    # print(pp_dict, file=sys.stderr)
    print(out_text)


if __name__ == '__main__':
    main()
