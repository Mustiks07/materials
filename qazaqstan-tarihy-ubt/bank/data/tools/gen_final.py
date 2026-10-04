# -*- coding: utf-8 -*-
import json, re, os
from normtext import fix
from split_ctx import split_context
import edits

OUT='/home/user/materials/qazaqstan-tarihy-ubt'
LET='ABCD'
EH=json.load(open('e-history-variants.json',encoding='utf-8'))
UST=json.load(open('ust-build.json',encoding='utf-8'))
IMG={'/storage/images/ent-tests/4xt24UvyCfKrH758T5eu8UVyu9MVORlFjCOH0HGJ.png':
     ('img/nusqa-01-karta-jibek-joly.png','VI–XII ғғ. Қазақстан қалалары және Ұлы Жібек жолы картасы'),
     '/storage/images/ent-tests/HKl4tuyCqUCh930trmR6ouWcMznPYFYUPMS0e7we.png':
     ('img/nusqa-02-industrialandyru.png','Индустрияландыру жылдарындағы құрылыстар сызбасы')}
PICREF=re.compile(r'(Картада|Картаға|Картаны|Карта бойынша|Кестеде|Кестедегі|суретте|Суреттерде|Сызбаны|сызба)')

def q_from_ust(f,n):
    q={x['n']:x for x in UST[f]}[n]
    return {'q':fix(q['q']),'answers':[fix(a['text']) for a in q['answers']],
            'key':q['key'] or None,'derived':None,'src':(f,n)}

# ── нұсқалардың құрамын жинау ──
variants={}

# 1–3: e-history
for idx,v in enumerate(EH,1):
    blocks=[];n=0
    for bi,b in enumerate(v['blocks']):
        qs=[]
        for q in b['questions']:
            qs.append({'q':fix(q['q']),
                       'answers':[re.sub(r'^[A-D]\)\s*','',fix(a['text'])) for a in q['answers']],
                       'key':next((LET[i] for i,a in enumerate(q['answers']) if a['correct']),None),
                       'derived':None,'src':('e-history',v['source_variant_id'])})
        if bi==0:
            blocks.append({'kind':'single','questions':qs})
        else:
            ctx=fix(re.sub(r'^\s*Нұсқау\s*:?\s*','',b['desc']))
            for lead in ['Сізге контекст негізіндегі ұсынылған төрт жауаптан бір дұрыс жауапты таңдауғаарналған тест тапсырмалары беріледі. Контексті мұқият оқып, берілгентапсырмаларға дұрыс жауап беріңіз.',
                         'Сізге контекст негізіндегі ұсынылған төрт жауаптан бір дұрыс жауапты таңдауға арналған тест тапсырмалары беріледі. Контексті мұқият оқып, берілген тапсырмаларға дұрыс жауап беріңіз.']:
                if ctx.startswith(lead): ctx=ctx[len(lead):].strip()
            blocks.append({'kind':'ctx','context':ctx,
                           'images':[IMG[s] for s in b['desc_images'] if s in IMG],'questions':qs})
    variants[idx]={'source':'e-history.kz',
        'url':f'https://e-history.kz/kz/ent/kazakhstan-history/{v["source_variant_id"]}',
        'label':v['variant'],'keys':'портал кілті','blocks':blocks}

UMAP=[(4,'ust-n3.patched.txt','3-нұсқа','qazaqstan_tarihynan_ubt_suraqtary_20_suarq-357455',
       [('single',1,10),('ctx',11,15),('ctx',16,20)]),
      (5,'ust-n4.patched.txt','4-нұсқа','qazaqstan_tarihy_4_nusqa_ubt_suraqtarf_test-357457',
       [('single',1,10),('ctx',11,15),('ctx',16,20)]),
      (6,'ust-n5.patched.txt','5-нұсқа','ubt_test_qazaqstan_tarihy_20_suraq-358038',
       [('single',1,10),('ctx',11,15),('ctx',16,20)]),
      (7,'ust-n6.patched.txt','6-нұсқа','qazaqstan_tarihy_ubt_test_6_nusqa_20_suraq-359046',
       [('single',[2,4,5,6,7,8,9,10,13,14]),('ctx',16,20),('new',)]),
      (8,'ust-n7.patched.txt','7-нұсқа','qazaqstan_tarihynan_ubt_suraqtary_7_si_nusqa-361256',
       [('single',1,10),('ctx',11,15),('ctx',16,20)]),
      (9,'ust-n8.patched.txt','8-нұсқа','ubt_test_qazaqstan_tarihy_8_nusqa-365122',
       [('single',[6,7,8,9,10,11,17,18,19,20]),('ctx',1,5),('ctx',12,16)]),
      (10,'ust-n10.patched.txt','10-нұсқа','qazaqstan_tarihy_ubt_test_10_nusqa_jangartylgan_bagdarlama_boiynsa-382216',
       [('single',[1,2,3,4,5,6,7],'moved'),('ctx',8,12),('ctx',16,20)])]

for num,f,label,slug,spec in UMAP:
    blocks=[]
    for item in spec:
        if item[0]=='single':
            nums=item[1] if isinstance(item[1],list) else list(range(item[1],item[2]+1))
            qs=[q_from_ust(f,n) for n in nums]
            if len(item)>2 and item[2]=='moved':
                qs += [q_from_ust(ff,nn) for ff,nn in edits.MOVE_TO_V10]
            blocks.append({'kind':'single','questions':qs})
        elif item[0]=='ctx':
            a,b=item[1],item[2]
            first=q_from_ust(f,a)
            ctx,stem=split_context(first['q'])
            qs=[]
            for n in range(a,b+1):
                q=q_from_ust(f,n)
                if n==a: q['q']=stem
                dk=edits.DERIVED_KEYS.get((f,n))
                if dk: q['key'],q['derived']=dk
                qs.append(q)
            blocks.append({'kind':'ctx','context':ctx,'images':[],'questions':qs})
        else:  # new
            nc=edits.NEW_CONTEXT_V7
            qs=[{'q':t,'answers':a,'key':k,'derived':why,'src':('new',0)}
                for t,a,k,why in nc['questions']]
            blocks.append({'kind':'ctx','context':nc['context'],'images':[],'questions':qs,
                           'extra_source':nc})
    # бір жауап блогындағы шығарылған кілттер
    for b in blocks:
        for q in b['questions']:
            dk=edits.DERIVED_KEYS.get(q['src']) if isinstance(q['src'],tuple) else None
            if dk and not q['derived']: q['key'],q['derived']=dk
    variants[num]={'source':'ust.kz','url':f'https://ust.kz/word/{slug}.html',
                   'label':label,'keys':'дереккөздегі «+» белгісі','blocks':blocks}

# ── 5. қайталанған тапсырмаларды ауыстыру ──
for (vn, qn), rep in edits.REPLACE.items():
    i = 0
    for b in variants[vn]['blocks']:
        for k, q in enumerate(b['questions']):
            i += 1
            if i == qn:
                b['questions'][k] = {'q': rep['q'], 'answers': rep['answers'],
                                     'key': rep['key'], 'derived': rep['derived'],
                                     'src': ('replaced', rep['src_url'])}

# ── тексеру ──
for n in sorted(variants):
    v=variants[n]
    shape=[(b['kind'],len(b['questions'])) for b in v['blocks']]
    tot=sum(x[1] for x in shape)
    ok = shape==[('single',10),('ctx',5),('ctx',5)]
    print(f"{n:>2}-нұсқа: {shape} = {tot}  {'OK' if ok else '!!! СӘЙКЕС ЕМЕС'}")
json.dump({str(k):v for k,v in variants.items()},
          open('variants-final.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
