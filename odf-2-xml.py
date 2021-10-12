#!/usr/bin/env python3

"""
Filter out text by language type from an ODT file.
"""

# References:
#   https://github.com/eea/odfpy/wiki

import sys

from odf.opendocument import load
from pathlib import Path


def convert_to_xml(doc):
    return doc.xml().decode()

def main():
    # Parse options.
    infile = ''

    # Ensure that a file was passed as an argument.
    if len(sys.argv) == 2 and Path(sys.argv[1]).suffix == '.odt':
        infile = Path(sys.argv[1])
    else:
        print(f"Usage: {sys.argv[0]} /PATH/TO/FILE.odt")
        exit(1)

    # Ensure that input file exists.
    if infile.is_file() and infile.suffix == '.odt':
        infile = infile.resolve()
        # Load content.
        doc = load(infile)
    else:
        print("Error: Input file does not exist.")
        exit(1)

    # Get XML and print to sdtout.
    print(convert_to_xml(doc))

    exit()

if __name__ == '__main__':
    main()
