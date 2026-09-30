"""Read saved patent HTML using only the standard library; preserve locators."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import sys

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class Node:
    def __init__(self, tag='', attrs=None, parent=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.parent = parent
        self.children = []
    def text(self):
        return ' '.join(''.join(c if isinstance(c,str) else c.text() for c in self.children).split())
    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root=Node();self.current=self.root
    def handle_starttag(self, tag, attrs):
        node=Node(tag,attrs,self.current);self.current.children.append(node)
        if tag not in VOID:self.current=node
    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag,attrs,self.current))
    def handle_endtag(self, tag):
        node=self.current
        while node.parent is not None:
            if node.tag==tag:
                self.current=node.parent;return
            node=node.parent
    def handle_data(self, data):
        self.current.children.append(data)

def extract(path):
    path=Path(path);p=Parser();p.feed(path.read_text(encoding='utf-8-sig'))
    rows=[]
    for n in p.root.walk():
        cls=n.attrs.get('class','').split()
        if 'description-paragraph' in cls or (n.tag=='div' and 'claim' in cls and n.attrs.get('num')):
            rows.append({'type':'description' if 'description-paragraph' in cls else 'claim',
                         'id':n.attrs.get('id'),'num':n.attrs.get('num'),'text':n.text()})
    return {'source_path':str(path.resolve()),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':rows}

if __name__=='__main__':
    print(json.dumps(extract(sys.argv[1]),ensure_ascii=False,indent=2))
