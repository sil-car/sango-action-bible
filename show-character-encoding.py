#!/usr/bin/env python3

import sys
import unicodedata

# print(sys.stdin.read())
charstr = sys.stdin.read().rstrip('\n')
chars = [c for c in charstr]
for c in chars:
    cname = unicodedata.name(c, None)
    if cname:
        cchar = unicodedata.lookup(cname)
    cunicode = c.encode('UTF-8').decode()
    cnfd = unicodedata.decomposition(c)
    is_nfc = True
    if not cnfd:
        cnfd = None
        is_nfc = False

    # is_nfc = unicodedata.is_normalized('NFC', c)
    print(f"{c}: NFC?: {is_nfc}, NFD: {cnfd}, {cname}")
