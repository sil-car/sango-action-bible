import hunspell


def get_hs_dic(dir, lang_code):
    aff = None
    dic = None
    hs_dic = None
    for f in dir.iterdir():
        if f.stem == lang_code:
            if f.suffix == '.aff':
                aff = f
            elif f.suffix == '.dic':
                dic = f
    if aff and dic:
        hs_dic = hunspell.HunSpell(dic, aff)
    return hs_dic

def lookup_word(hs_dic, word):
    return hs_dic.spell(word)

def build_wordlist(dir, lang):
    """Create a word list from files whose filename matches the given language code. """
    wordlist = set()
    for f in dir.iterdir():
        if f.stem[:5] == lang:
            with open(f, 'r') as l:
                for line in l.readlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        wordlist.add(line.split('/')[0].split()[0].strip())
                    except IndexError as e:
                        print(f"{repr(e)} for \"{line}\"")
    return wordlist
