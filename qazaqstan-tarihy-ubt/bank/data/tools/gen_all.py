# -*- coding: utf-8 -*-
import json, re, os
from normtext import fix
from split_ctx import split_context

OUT = '/home/user/materials/qazaqstan-tarihy-ubt'
LET = 'ABCD'
os.makedirs(f'{OUT}/bank/data', exist_ok=True)

IMGMAP = {'/storage/images/ent-tests/4xt24UvyCfKrH758T5eu8UVyu9MVORlFjCOH0HGJ.png':
          ('img/nusqa-01-karta-jibek-joly.png', 'VI–XII ғғ. Қазақстан қалалары және Ұлы Жібек жолы картасы'),
          '/storage/images/ent-tests/HKl4tuyCqUCh930trmR6ouWcMznPYFYUPMS0e7we.png':
          ('img/nusqa-02-industrialandyru.png', 'Индустрияландыру жылдарындағы құрылыстар сызбасы')}

LEADS = ['Сізге контекст негізіндегі ұсынылған төрт жауаптан бір дұрыс жауапты таңдауғаарналған тест тапсырмалары беріледі. Контексті мұқият оқып, берілгентапсырмаларға дұрыс жауап беріңіз.',
         'Сізге контекст негізіндегі ұсынылған төрт жауаптан бір дұрыс жауапты таңдауға арналған тест тапсырмалары беріледі. Контексті мұқият оқып, берілген тапсырмаларға дұрыс жауап беріңіз.',
         'Сізге берілген төрт жауап нұсқасынан бір дұрыс жауаптытаңдауға арналған тапсырмалар беріледі.',
         'Сізге берілгентөрт жауап нұсқасынан бір дұрыс жауаптытаңдауға арналған тапсырмалар беріледі.']

INSTR_SINGLE = ('> *Нұсқау: Сізге берілген төрт жауап нұсқасынан бір дұрыс жауапты '
                'таңдауға арналған тапсырмалар беріледі.*\n')
INSTR_CTX = ('> *Нұсқау: Сізге контекст негізіндегі ұсынылған төрт жауаптан бір дұрыс '
             'жауапты таңдауға арналған тест тапсырмалары беріледі. Контексті мұқият оқып, '
             'берілген тапсырмаларға дұрыс жауап беріңіз.*\n')

def keytable(keys):
    L = []
    for a, b in ((0, 10), (10, 20)):
        L.append('| № | ' + ' | '.join(str(i+1) for i in range(a, b)) + ' |')
        L.append('|---|' + '---|' * (b - a))
        L.append('| **Жауап** | ' + ' | '.join(keys[a:b]) + ' |')
        L.append('')
    return L

def render_q(n, stem, answers, note=None):
    L = [f'**{n}.** {stem}\n']
    for i, a in enumerate(answers):
        L.append(f'- **{LET[i]})** {a}')
    if note:
        L.append(f'\n> ⚠️ {note}')
    L.append('')
    return L

# ─────────────── 1–3-нұсқа: e-history.kz ───────────────
EH = json.load(open('e-history-variants.json', encoding='utf-8'))
EH_URL = {6: 6, 12: 12, 10: 10}
ALL = {}

def clean_desc(d):
    d = fix(d)
    d = re.sub(r'^\s*Нұсқау\s*:?\s*', '', d)
    for lead in LEADS:
        if d.startswith(fix(lead)):
            d = d[len(fix(lead)):].strip()
        if d.startswith(lead):
            d = d[len(lead):].strip()
    return d.strip()

for idx, v in enumerate(EH, start=1):
    vid = v['source_variant_id']
    L = [f'# ҰБТ «ҚАЗАҚСТАН ТАРИХЫ» — {idx}-нұсқа\n',
         f'> **Дереккөз:** e-history.kz — «Қазақстан тарихы» ұлттық порталының ҰБТ сұрақтары '
         f'бөлімі ({v["variant"]}). Бұл бөлім Ұлттық тестілеу орталығымен бірлесіп дайындалған.',
         f'> <https://e-history.kz/kz/ent/kazakhstan-history/{vid}>\n',
         '> **Жауап кілті** — порталдың өз тексеру жүйесінен алынған кілт.\n',
         '**Құрылымы:** 1–10 — бір дұрыс жауап · 11–15 — 1-мәнмәтін · 16–20 — 2-мәнмәтін.',
         'Бұл — ҰТО спецификациясындағы құрылыммен толық сәйкес келетін нұсқа.\n', '---\n']
    n, keys = 0, []
    for bi, b in enumerate(v['blocks']):
        if bi == 0:
            L += ['## 1-блок. Бір дұрыс жауапты таңдауға арналған тапсырмалар (1–10)\n', INSTR_SINGLE]
        else:
            L += [f'## {bi+1}-блок. Мәнмәтін негізіндегі тапсырмалар ({n+1}–{n+5})\n', INSTR_CTX]
            for src in b['desc_images']:
                if src in IMGMAP:
                    p, alt = IMGMAP[src]
                    L.append(f'![{alt}]({p})\n')
                    L.append(f'*Сурет: {alt}. Тапсырмамен бірге берілген түпнұсқа кескін.*\n')
            L += ['### Мәнмәтін\n', clean_desc(b['desc']) + '\n']
        for q in b['questions']:
            n += 1
            ans = [re.sub(r'^[A-D]\)\s*', '', fix(a['text'])) for a in q['answers']]
            L += render_q(n, fix(q['q']), ans)
            keys.append(next((LET[i] for i, a in enumerate(q['answers']) if a['correct']), '—'))
        L.append('---\n')
    L += ['## Жауап кілті\n'] + keytable(keys)
    open(f'{OUT}/{idx:02d}-NUSQA-{idx}.md', 'w', encoding='utf-8').write('\n'.join(L))
    ALL[idx] = keys

# ─────────────── 4–10-нұсқа: ust.kz ───────────────
UST = json.load(open('ust-build.json', encoding='utf-8'))
MAPPING = [
 (4,  'ust-n3.patched.txt',  '3-нұсқа',  'qazaqstan_tarihynan_ubt_suraqtary_20_suarq-357455',
  [('single', 1, 10), ('ctx', 11, 15), ('ctx', 16, 20)]),
 (5,  'ust-n4.patched.txt',  '4-нұсқа',  'qazaqstan_tarihy_4_nusqa_ubt_suraqtarf_test-357457',
  [('single', 1, 10), ('ctx', 11, 15), ('ctx', 16, 20)]),
 (6,  'ust-n5.patched.txt',  '5-нұсқа',  'ubt_test_qazaqstan_tarihy_20_suraq-358038',
  [('single', 1, 10), ('ctx', 11, 15), ('ctx', 16, 20)]),
 (7,  'ust-n6.patched.txt',  '6-нұсқа',  'qazaqstan_tarihy_ubt_test_6_nusqa_20_suraq-359046',
  [('single', 1, 15), ('ctx', 16, 20)]),
 (8,  'ust-n7.patched.txt',  '7-нұсқа',  'qazaqstan_tarihynan_ubt_suraqtary_7_si_nusqa-361256',
  [('single', 1, 10), ('ctx', 11, 15), ('ctx', 16, 20)]),
 (9,  'ust-n8.patched.txt',  '8-нұсқа',  'ubt_test_qazaqstan_tarihy_8_nusqa-365122',
  [('ctx', 1, 5), ('single', 6, 11), ('ctx', 12, 16), ('single', 17, 20)]),
 (10, 'ust-n10.patched.txt', '10-нұсқа', 'qazaqstan_tarihy_ubt_test_10_nusqa_jangartylgan_bagdarlama_boiynsa-382216',
  [('single', 1, 7), ('ctx', 8, 12), ('ctx', 13, 15), ('ctx', 16, 20)]),
]

NOKEY = {('ust-n7.patched.txt', 12), ('ust-n7.patched.txt', 17)}
PICREF = re.compile(r'(Картада|Картаға|Картаны|Карта бойынша|Кестеде|Кестедегі|суретте|Суреттерде|Сызбаны|сызба)')

for num, f, srcname, slug, blocks in MAPPING:
    qs = {q['n']: q for q in UST[f]}
    L = [f'# ҰБТ «ҚАЗАҚСТАН ТАРИХЫ» — {num}-нұсқа\n',
         f'> **Дереккөз:** «Ұстаз тілегі» әдістемелік порталы (ust.kz), «{srcname}» —',
         f'> ҰБТ-ның жаңартылған форматы бойынша дайындалған нұсқа (автор — Бопылова Ш.).',
         f'> <https://ust.kz/word/{slug}.html>\n',
         '> **Жауап кілті** — дереккөздің өзінде дұрыс жауап «+» белгісімен көрсетілген.\n']
    comp = ' · '.join(f'{a}–{b} — ' + ('бір дұрыс жауап' if k == 'single' else 'мәнмәтін')
                      for k, a, b in blocks)
    L += [f'**Құрылымы:** {comp}.\n', '---\n']
    keys = []
    bi_ctx = 0
    for k, a, b in blocks:
        if k == 'single':
            L += [f'## Бір дұрыс жауапты таңдауға арналған тапсырмалар ({a}–{b})\n', INSTR_SINGLE]
        else:
            bi_ctx += 1
            L += [f'## {bi_ctx}-мәнмәтін ({a}–{b})\n', INSTR_CTX]
            first = qs[a]
            ctx, stem = split_context(fix(first['q']))
            L += ['### Мәнмәтін\n', ctx + '\n']
        for n in range(a, b + 1):
            q = qs[n]
            stem_txt = fix(q['q'])
            if k == 'ctx' and n == a:
                _, stem_txt = split_context(stem_txt)
            ans = [fix(x['text']) for x in q['answers']]
            note = None
            if (f, n) in NOKEY:
                note = ('Дереккөзде бұл тапсырманың дұрыс жауабы белгіленбеген. '
                        'Төмендегі кілтте ол «—» деп берілген.')
            elif PICREF.search(stem_txt):
                note = ('Тапсырма картаға / кестеге / суретке сілтейді. Дереккөздің ашық '
                        'көрінісінде кескін берілмеген, сондықтан мәтіні ғана келтірілді.')
            L += render_q(n, stem_txt, ans, note)
            keys.append(q['key'] if q['key'] else '—')
        L.append('---\n')
    L += ['## Жауап кілті\n'] + keytable(keys)
    if '—' in keys:
        L += ['> «—» — дереккөзде дұрыс жауабы белгіленбеген тапсырма. Ойдан жауап қосылмады.\n']
    open(f'{OUT}/{num:02d}-NUSQA-{num}.md', 'w', encoding='utf-8').write('\n'.join(L))
    ALL[num] = keys

json.dump(ALL, open(f'{OUT}/bank/data/kilttér.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('Жазылды:', sorted(ALL), '| барлығы', sum(len(v) for v in ALL.values()), 'тапсырма')
