

from xml.dom import minidom

def build_notes_xml(user, comments):

    root = minidom.Document()
    xml = root.createElement('CommentList')
    root.appendChild(xml)

    attribs = [
        'Thread',
        'VerseRef',
        'Date',
    ]
    for c in comments:
        c_xml = root.createElement('Comment')
        # print(c)
        for a in attribs:
            c_xml.setAttribute(a, c.get(a))
        c_xml.setAttribute('User', user)
        c_xml.setAttribute('Language', 'sg')
        xml.appendChild(c_xml)

        for k, v in c.items():
            if k in attribs:
                continue
            tx = root.createTextNode(v)
            ch = root.createElement(k)
            ch.appendChild(tx)
            c_xml.appendChild(ch)

    xml_str = root.toprettyxml(indent="  ")
    return xml_str
