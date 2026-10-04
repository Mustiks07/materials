import re, json, sys
from bs4 import BeautifulSoup

def clean(t):
    t = t.replace('\xa0',' ').replace('\t',' ')
    t = re.sub(r'\s+',' ',t).strip()
    return t

def parse(path):
    soup = BeautifulSoup(open(path,encoding='utf-8',errors='replace').read(),'lxml')
    root = soup.select_one('.ent-questions-list')
    variant = clean(root.select_one('.variant-number').get_text())
    out = {'variant': variant, 'blocks': []}
    for grp in root.select('.form-group'):
        desc_el = grp.select_one('.ent-description-block')
        desc = clean(desc_el.get_text()) if desc_el else ''
        desc_imgs = [i.get('src') for i in desc_el.select('img')] if desc_el else []
        qs = []
        for item in grp.select('.ent-test-item'):
            ptxt = item.select_one('p.form-text')
            qtext = clean(ptxt.get_text()) if ptxt else ''
            qimgs = [i.get('src') for i in item.select('p.form-text img')] if ptxt else []
            # also images directly in item but not in answers
            answers = []
            for fc in item.select('.form-check'):
                lab = fc.select_one('label')
                atxt = clean(lab.get_text()) if lab else ''
                aimgs = [i.get('src') for i in lab.select('img')] if lab else []
                answers.append({'text':atxt,'images':aimgs})
            qs.append({'q':qtext,'images':qimgs,'answers':answers})
        if qs or desc:
            out['blocks'].append({'instruction_or_context':desc,'context_images':desc_imgs,'questions':qs})
    return out

for p in sys.argv[1:]:
    d = parse(p)
    json.dump(d, open(p.replace('.html','.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    nq = sum(len(b['questions']) for b in d['blocks'])
    print(p, '|', d['variant'], '| blocks:', len(d['blocks']), '| questions:', nq,
          '| imgs:', sum(len(b['context_images']) for b in d['blocks']) + sum(len(q['images']) for b in d['blocks'] for q in b['questions']))
