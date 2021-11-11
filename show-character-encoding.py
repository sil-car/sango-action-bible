#!/usr/bin/env python3

import sys
import unicodedata

charstr = sys.stdin.read().rstrip('\n')
chars = [c for c in charstr]
for i, c in enumerate(chars):
    cname = unicodedata.name(c, None)
    cnfd = unicodedata.decomposition(c)
    is_nfc = True
    if not cnfd:
        cnfd = None
        is_nfc = False

    print(f"{i}:  {c}\t{hex(ord(c))}\tNFC?: {is_nfc}, name: {cname}")
