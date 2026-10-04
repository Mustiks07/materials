import re, json, subprocess, sys, time
from bs4 import BeautifulSoup

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
CJ="cj2.txt"

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

def clean(t):
    return re.sub(r'\s+',' ', t.replace('\xa0',' ').replace('\t',' ')).strip()

def parse(html, with_answers=False):
    soup = BeautifulSoup(html,'lxml')
    root = soup.select_one('.ent-questions-list')
    variant = clean(root.select_one('.variant-number').get_text())
    blocks=[]
    for grp in root.select('.form-group'):
        d = grp.select_one('.ent-description-block')
        desc = clean(d.get_text()) if d else ''
        dimgs = [i.get('src') for i in d.select('img')] if d else []
        qs=[]
        for item in grp.select('.ent-test-item'):
            p = item.select_one('p.form-text')
            qtext = clean(p.get_text()) if p else ''
            qimgs = [i.get('src') for i in item.select('img')]
            ans=[]
            for fc in item.select('.form-check'):
                lab = fc.select_one('label')
                raw = clean(lab.get_text()) if lab else ''
                correct=None
                if with_answers:
                    if raw.endswith('- Дұрыс жауап'):
                        correct=True;  raw = raw[:-len('- Дұрыс жауап')].strip()
                    elif raw.endswith('- Дұрыс емес жауап'):
                        correct=False; raw = raw[:-len('- Дұрыс емес жауап')].strip()
                aimgs=[i.get('src') for i in lab.select('img')] if lab else []
                qimgs=[x for x in qimgs if x not in aimgs]
                ans.append({'text':raw,'correct':correct,'images':aimgs})
            qs.append({'q':qtext,'images':qimgs,'answers':ans})
        if qs or desc:
            blocks.append({'desc':desc,'desc_images':dimgs,'questions':qs})
    return {'variant':variant,'blocks':blocks}

sh(f'rm -f {CJ}')
page = sh(f'curl -s -c {CJ} -A "{UA}" "https://e-history.kz/kz/ent/kazakhstan-history"')
tok = re.search(r'name="_token" value="([^"]+)"', page).group(1)

result=[]
for vid in (6,12,10):
    sh(f'curl -s -b {CJ} -c {CJ} -A "{UA}" -e "https://e-history.kz/kz/ent/kazakhstan-history" '
       f'-X POST "https://e-history.kz/kz/ent/variant" --data "_token={tok}&variant={vid}" -o /dev/null')
    html = sh(f'curl -s -b {CJ} -c {CJ} -A "{UA}" "https://e-history.kz/kz/ent/kazakhstan-history/{vid}"')
    q = parse(html)
    names=[]
    for bi,b in enumerate(q['blocks']):
        for qi,_ in enumerate(b['questions']):
            names.append(f"block-{bi}-question-{qi}[0]=on")
    t2 = re.search(r'name="_token" value="([^"]+)"', html).group(1)
    open('post.tmp','w').write(f"_token={t2}&"+"&".join(names))
    ah = sh(f'curl -s -b {CJ} -c {CJ} -A "{UA}" -e "https://e-history.kz/kz/ent/kazakhstan-history/{vid}" '
            f'-X POST "https://e-history.kz/kz/ent/check-answers?variant={vid}" --data @post.tmp')
    qa = parse(ah, with_answers=True)
    qa['source_variant_id']=vid
    nq=sum(len(b['questions']) for b in qa['blocks'])
    nc=sum(1 for b in qa['blocks'] for x in b['questions'] for a in x['answers'] if a['correct'])
    print(f"vid={vid} {qa['variant']}: questions={nq} correct_marked={nc}")
    result.append(qa)
    time.sleep(1)

json.dump(result, open('e-history-variants.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("saved e-history-variants.json")
