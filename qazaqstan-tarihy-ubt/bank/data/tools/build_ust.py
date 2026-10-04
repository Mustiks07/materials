import re, json, sys

WORD = r'0-9A-Za-zА-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүҺһІі'
CYR  = {'А':'A','В':'B','С':'C','Д':'D'}

def flat(p):
    s = open(p, encoding='utf-8').read().replace('Материалдың қысқаша нұсқасы',' ')
    s = re.sub(r'\s+',' ',s).replace('ӛ','ө').replace('Ӛ','Ө').strip()
    return re.sub(r'^\s*\d+\s*-\s*нұсқа\s*','',s)

def groups_of(s):
    marks=[]
    for m in re.finditer(rf'(?<![{WORD}])([ABCDАВСД])\s*(\)\s*|\.\s+)', s):
        L=CYR.get(m.group(1),m.group(1))
        if L in 'ABCD': marks.append((m.start(),m.end(),L))
    gs,i=[],0
    while i<len(marks):
        if marks[i][2]!='A': i+=1; continue
        j=i+1
        while j<len(marks) and marks[j][2]!='B': j+=1
        if j>=len(marks): i+=1; continue
        # A ретінде B-ға ең жақын тұрған A белгісін аламыз (Г.А. тәрізді
        # инициалдар жалған A белгісін тудырады)
        ai=i
        for k in range(i+1,j):
            if marks[k][2]=='A': ai=k
        run=[marks[ai],marks[j]]; j+=1
        for w in 'CD':
            while j<len(marks) and marks[j][2]!=w: j+=1
            if j<len(marks): run.append(marks[j]); j+=1
            else: break
        if len(run)==4 and run[3][0]-run[0][0] < 1500:
            gs.append(run); i=j
        else: i+=1
    return gs

def build(path):
    s, gs = flat(path), None
    gs = groups_of(s)
    qs, stem_start = [], 0
    for gi, run in enumerate(gs):
        nxtA = gs[gi+1][0][0] if gi+1 < len(gs) else len(s)
        stem = s[stem_start:run[0][0]].strip()
        answers=[]
        for k,(a,b,L) in enumerate(run):
            end = run[k+1][0] if k+1 < len(run) else nxtA
            answers.append([L, s[b:end].strip()])
        # split D-option region: find question-number marker for the NEXT question
        dreg = answers[3][1]
        cut = None
        want = gi+2
        for m in re.finditer(rf'(?<![{WORD}.,–-])(\d{{1,2}})\s*\.\s*', dreg):
            if int(m.group(1)) == want:
                cut = m; break
        if cut is None:
            cands=[m for m in re.finditer(rf'(?<![{WORD}.,–-])(\d{{1,2}})\s*\.\s*', dreg)]
            if cands: cut = cands[0]
        if cut is not None:
            answers[3][1] = dreg[:cut.start()].strip()
            stem_start = run[3][1] + cut.end()
        else:
            stem_start = nxtA
        out=[]
        for L,t in answers:
            t=t.strip(); c=t.endswith('+')
            out.append({'letter':L,'text':re.sub(r'\s+',' ',t.rstrip('+').strip()),'correct':c})
        stem = re.sub(rf'^\s*{gi+1}\s*\.\s*','',stem).strip()
        qs.append({'n':gi+1,'q':re.sub(r'\s+',' ',stem),'answers':out,
                   'key':''.join(a['letter'] for a in out if a['correct'])})
    return qs

res={}
for p in sys.argv[1:]:
    qs=build(p); res[p]=qs
    bad=[q['n'] for q in qs if len(q['key'])!=1]
    empty=[q['n'] for q in qs if not q['q']]
    print(f"{p}: {len(qs)} q | multi/no-key:{bad} | empty-stem:{empty}")
json.dump(res, open('ust-build.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
