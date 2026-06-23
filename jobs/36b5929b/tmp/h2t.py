import sys, re, html
from html.parser import HTMLParser

class T(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out=[]
        self.skip=0
        self.cur=''
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','head'): self.skip+=1
        if tag in ('h1','h2','h3','h4','p','li','tr','blockquote','div'):
            self.flush()
        if tag=='h1': self.cur='\n# '
        elif tag=='h2': self.cur='\n## '
        elif tag=='h3': self.cur='\n### '
        elif tag=='h4': self.cur='\n#### '
        elif tag=='li': self.cur='- '
        elif tag in ('br',): self.flush()
        if tag in ('td','th'): self.cur+=' | '
        if tag=='code': self.cur+='`'
        if tag in ('strong','b'): self.cur+='**'
        if tag in ('em','i'): self.cur+='*'
    def handle_endtag(self,tag):
        if tag in ('script','style','head'): self.skip-=1
        if tag=='code': self.cur+='`'
        if tag in ('strong','b'): self.cur+='**'
        if tag in ('em','i'): self.cur+='*'
        if tag in ('h1','h2','h3','h4','p','li','tr','blockquote'):
            self.flush()
    def handle_data(self,data):
        if self.skip: return
        self.cur+=re.sub(r'\s+',' ',data)
    def flush(self):
        t=self.cur.strip()
        if t: self.out.append(t)
        self.cur=''

p=T()
with open(sys.argv[1],encoding='utf-8') as f:
    p.feed(f.read())
p.flush()
print('\n\n'.join(html.unescape(x) for x in p.out))
