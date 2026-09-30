"""Read saved patent HTML anchors without network or third-party libraries."""
from html.parser import HTMLParser
from pathlib import Path
import re

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.rows=[]
    def handle_starttag(self, tag, attrs):
        if tag in {'meta','link','br','hr','img','input','source','wbr','area','base','embed','param','track','col'}:
            return
        attrs=dict(attrs)
        self.stack.append([tag,attrs,[]])
    def handle_data(self, data):
        for frame in self.stack:
            if re.fullmatch(r'(?:[a-z]{2}-)?(?:cl|clm-|c|p)\d+',frame[1].get('id','')):
                frame[2].append(data)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                for _,attrs,parts in self.stack[i:]:
                    anchor=attrs.get('id','')
                    if re.fullmatch(r'(?:[a-z]{2}-)?(?:cl|clm-|c|p)\d+',anchor):
                        text=re.sub(r'\s+',' ',' '.join(parts)).strip()
                        self.rows.append({'anchor':anchor,'text':text})
                del self.stack[i:]
                break

def read_anchors(path):
    parser=Anchors()
    parser.feed(Path(path).read_text(encoding='utf-8-sig'))
    return {r['anchor']:r['text'] for r in parser.rows}

if __name__=='__main__':
    import sys,json
    print(json.dumps(read_anchors(sys.argv[1]),ensure_ascii=False,indent=2))
