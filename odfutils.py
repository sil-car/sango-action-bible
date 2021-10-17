#!/usr/bin/env python3

from odf.opendocument import load
from odf.style import Style, TextProperties
from odf.text import P


def load_doc(infile):
    doc = load(infile)
    return doc

def update_autostyles(doc, lang_codes):
    """
    Update The automatic paragraph styles of the given ODT document to include
    the given languages.
    """
    for lang_code in lang_codes:
        [lg, CN] = lang_code.split('_')
        pstyle = Style(
            name=lang_code,
            family="paragraph",
        )
        pstyle.addElement(TextProperties(language=lg, country=CN))
        doc.automaticstyles.addElement(pstyle)
    return doc
