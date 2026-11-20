"""Gera os Próprios em latim do Missal de 1962 para o app, a partir dos dados do Divinum Officium.

Uso (com o repositório divinum-officium já baixado em <raiz_do>):
    python3 -I tools/missal/gerar_missal.py <raiz_do>

Saída:
    data/missal/la-tempora.json   Próprio do Tempo (domingos, férias, oitavas, Têmporas)
    data/missal/la-sancti.json    Próprio dos Santos (calendário de 1962) e Missas múltiplas
    data/missal/kalendarium.json  MM-DD -> arquivo do santo e nome latino

Formato de cada Missa:
    t   título latino            c   classe (1-4)
    g   Gloria (bool)            cr  Credo (bool)
    pf  prefácio próprio (nome da seção em Ordo/Prefationes) ou null
    pfs texto que substitui *...* no prefácio (ex.: Conceptióne immaculáta)
    cm  Comum de onde vieram as partes que faltavam (ex.: C11)
    bmv festa de Nossa Senhora (bool)
    ord ordem das partes
    p   partes: nome -> lista de linhas "x|texto", onde x é:
          h título da leitura · c citação bíblica · r rubrica · t texto
          V versículo · R resposta · k conclusão (chave de Ordo/Prayers) · s separador
    pP  partes que mudam no Tempo Pascal (só no Próprio dos Santos)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from divinum import Contexto, Divinum  # noqa: E402

RAIZ_APP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SAIDA = os.path.join(RAIZ_APP, 'data', 'missal')

ORDEM = ['Prelude', 'Introitus', 'Oratio',
         'LectioL1', 'GradualeL1', 'OratioL1', 'LectioL2', 'GradualeL2', 'OratioL2',
         'LectioL3', 'GradualeL3', 'OratioL3', 'LectioL4', 'GradualeL4', 'OratioL4',
         'LectioL5', 'GradualeL5', 'OratioL5',
         'Lectio', 'Graduale', 'GradualeP', 'GradualeF', 'Tractus', 'Sequentia', 'Evangelium',
         'Offertorium', 'Secreta', 'Communio', 'Postcommunio', 'Super populum']
PARTES = set(ORDEM)

# Os 15 prefácios do Missal de 1962. Não entram os acrescentados depois (Advento, Santos, Dedicação etc.).
PREFACIOS_1962 = ['Nat', 'Epi', 'Quad', 'Quad5', 'Pasch', 'Asc', 'Cord', 'Regis', 'Spiritu', 'Trinitate',
                  'Maria', 'Joseph', 'Apostolis', 'Communis', 'Defunctorum']

# Prefácios posteriores (ou "pro aliquibus locis") que o Divinum Officium usa nas rubricas de 1960,
# trocados pelo que manda o Missal típico de 1962. None = regra do tempo (domingo: Trindade; féria: Comum).
PREFACIO_TROCA = {'Sacramento': 'Nat', 'Baptista': 'Communis', 'Dedicatio': 'Communis',
                  'Sanctis': 'Communis', 'Adv': None, 'Chrismatis': None}

TEMPORA_RE = re.compile(r'^(Adv[1-4]-[0-6]|Epi[1-6]-[0-6]|Quadp[1-3]-[0-6]|Quad[1-6]-[0-6]|Pasc[0-7]-[0-6]'
                        r'|Pent[0-2][0-9]-[0-6]|PentEpi[3-6]-[0-6]|Nat1-0|Nat2-0|Nat0[2-5]|093-[356]|10-DUP)$')

CITACAO = re.compile(r'^(?:[1-4]\s*)?[A-ZÆ][A-Za-zæëé]*\.?\s*:?\s*\d[\d\s:,.;\-–&a-zA-Zæë]*$')


def tempus_de(chave):
    """Porte simplificado de get_tempus_id para a chave do Tempo."""
    n = chave.split('/')[-1]
    if n.startswith('Adv'):
        return 'Adventus'
    if n.startswith('Nat'):
        return 'Nativitatis'
    if n.startswith('Epi'):
        return 'post Epiphaniam'
    if n.startswith('Quadp'):
        return 'Septuagesimæ'
    m = re.match(r'Quad(\d)', n)
    if m:
        return 'Quadragesimæ' if int(m.group(1)) < 5 else 'Passionis'
    if n.startswith('Pasc0'):
        return 'Octava Paschæ'
    m = re.match(r'Pasc(\d)-(\d)', n)
    if m:
        w, d = int(m.group(1)), int(m.group(2))
        if w < 5 or (w == 5 and d < 4):
            return 'post Octavam Paschæ'
        if w < 7:
            return 'Octava Ascensionis'
        return 'Octava Pentecostes'
    if n.startswith('PentEpi'):
        return 'post Pentecosten in hieme'
    return 'post Pentecosten'


def classe_de(rank):
    try:
        num = float(rank.split(';;')[2])
    except (IndexError, ValueError):
        return 4
    return 1 if num >= 6 else 2 if num >= 5 else 3 if num >= 2 else 4


def converter(texto):
    """Seção bruta -> lista de linhas 'x|texto'."""
    out = []
    texto = re.sub(r'~\s*\n\s*', ' ', texto)  # "~" no fim da linha: continua na próxima
    for ln in texto.split('\n'):
        ln = ln.rstrip()
        if not ln.strip():
            continue
        s = ln.strip()
        if s == '_':
            out.append('s|')
            continue
        if s.startswith('#'):
            continue  # título interno do arquivo
        if s.startswith('$'):
            out.append('k|' + s[1:].strip().rstrip('.'))
            continue
        if s.startswith('&'):
            nome = s[1:].strip()
            if nome.lower().startswith('gloria'):
                out.append('k|Gloria')
            else:
                out.append('k|' + nome)
            continue
        if s.startswith('!'):
            corpo = s.lstrip('!').strip()
            if not corpo:
                continue
            out.append(('c|' if CITACAO.match(corpo) else 'r|') + corpo)
            continue
        tipo = 't'
        m = re.match(r'^(v|V|R|r|S|M|D|O)\.\s*(.*)$', s)
        if m:
            tipo = {'V': 'V', 'R': 'R'}.get(m.group(1), 't')
            s = m.group(2)
        s = s.replace('++', '✠').replace(' + ', ' ✠ ')
        out.append(tipo + '|' + s)
    # título da leitura: primeira linha de texto antes da citação
    return out


def regra(secs, com_rule='', nome='', domingo=False):
    """Glória, Credo e Prefácio. Porte de gloriflag() e Credo() de propers.pl (Divinum Officium)."""
    r = secs.get('Rule', '')
    rank = secs.get('Rank', '')
    try:
        num = float(rank.split(';;')[2])
    except (IndexError, ValueError):
        num = 0
    sancti = nome.startswith('Sancti/')
    dia = nome.split('/')[-1]
    defunct = bool(re.search(r'C9\b|Defunct', r + com_rule, re.I))
    # Glória (True = diz-se)
    if re.search(r'no Gloria', r, re.I) or (re.search(r'no Gloria', com_rule, re.I) and not re.search(r'Gloria', r, re.I)):
        g = False
    elif re.search(r'Gloria', r) or re.search(r'Gloria', com_rule, re.I):
        g = True
    elif defunct:
        g = False
    elif sancti:
        g = True
    elif re.match(r'(Adv|Quad)', dia):
        g = False
    elif dia.startswith('Pasc'):
        g = True
    else:
        g = domingo
    # Credo
    cr = domingo or (num >= 5 and sancti and not re.search(r'Vigil', rank, re.I)) \
        or (re.search(r'Octav', rank, re.I) and not re.search(r'post Octavam|Simplex', rank, re.I))
    if re.search(r'no Credo', r, re.I) or (re.search(r'no Credo', com_rule, re.I) and not re.search(r'Credo', r, re.I)):
        cr = False
    elif re.search(r'Credo', r, re.I) or re.search(r'Credo', com_rule, re.I):
        cr = True
    if re.search(r'CredoDA', r, re.I):
        cr = False
    pf = pfs = None
    m = re.search(r'Prefatio1960=([A-Za-z0-9]+)', r) or re.search(r'Prefatio=([A-Za-z0-9]+)(?:=([^;\n]*);?)?', r)
    if m:
        pf = m.group(1)
        if m.lastindex and m.lastindex >= 2 and m.group(2):
            pfs = m.group(2).strip()
        if pf in PREFACIO_TROCA:
            pf, pfs = PREFACIO_TROCA[pf], None
    return bool(g), bool(cr), pf, pfs, r


def commune_de(secs):
    r = secs.get('Rule', '') + '\n' + secs.get('Rank', '')
    m = re.search(r'(?:ex|vide)\s+((?:Commune/)?C\d+[a-z]*|Sancti/[\w-]+|Tempora/[\w-]+)', r)
    if not m:
        return None
    c = m.group(1)
    if re.match(r'^C\d', c):
        c = 'Commune/' + c
    return c


def montar(d, nome, ctx, domingo_fallback=None):
    secs = d.secoes(nome, ctx)
    if secs is None:
        return None
    cm = commune_de(secs)
    com = d.secoes(cm, ctx) if cm and d.existe(cm) else {}
    domingo = bool(re.search(r'-0$', nome)) or nome.startswith('Tempora/Nat1-0') or nome.startswith('Tempora/Nat2-0')
    g, cr, pf, pfs, rr = regra(secs, (com or {}).get('Rule', ''), nome, domingo)
    dom = {}
    if domingo_fallback and d.existe(domingo_fallback) and domingo_fallback != nome:
        dom = d.secoes(domingo_fallback, ctx) or {}
    partes = {}
    for k in ORDEM:
        txt = secs.get(k)
        if not txt or not txt.strip():
            txt = (com or {}).get(k)
        if (not txt or not txt.strip()) and k in ('Introitus', 'Oratio', 'Lectio', 'Graduale', 'Evangelium',
                                                  'Offertorium', 'Secreta', 'Communio', 'Postcommunio'):
            txt = dom.get(k)
        if txt and txt.strip() and 'is missing!' not in txt:
            linhas = converter(txt)
            # primeira linha das leituras = título (Léctio..., Sequéntia..., Inítium...)
            if (k.startswith('Lectio') or k == 'Evangelium') and linhas and linhas[0].startswith('t|') \
                    and re.match(r'^(L[ée]ctio|Sequ[ée]ntia|In[íi]tium|P[áa]ssio)', linhas[0][2:]):
                linhas[0] = 'h|' + linhas[0][2:]
            partes[k] = linhas
    # As leituras extras das Têmporas só valem se a regra pede (LectioLn)
    mL = re.search(r'LectioL(\d)', rr)
    nL = int(mL.group(1)) if mL else 0
    for i in range(1, 6):
        if i > nL:
            for k in ('LectioL%d' % i, 'GradualeL%d' % i, 'OratioL%d' % i):
                partes.pop(k, None)
    rank = secs.get('Rank', '').strip().split('\n')[0]
    titulo = (secs.get('Officium') or rank.split(';;')[0]).strip().split('\n')[0]
    if not titulo and cm:
        titulo = ''
    return {
        't': titulo,
        'c': classe_de(rank),
        'g': g, 'cr': cr, 'pf': pf, 'pfs': pfs,
        'cm': (cm or '').replace('Commune/', '') or None,
        'bmv': bool(re.search(r'Beat\w*.*?Mari\w*.*?Virg', rank, re.I)),
        'ord': [k for k in ORDEM if k in partes],
        'p': partes,
    }


def gerar(raiz_do):
    d = Divinum(raiz_do)
    os.makedirs(SAIDA, exist_ok=True)
    pasta_tempora = os.path.join(d.missa, 'Tempora')

    # ---- Próprio do Tempo
    tempora = {}
    for f in sorted(os.listdir(pasta_tempora)):
        base = f[:-4]
        if not TEMPORA_RE.match(base):
            continue
        chave = 'Tempora/' + base
        arq = d.arquivo_versao(chave)
        if arq == 'Tempora/Quad6-4r':
            arq = 'Tempora/Quad6-4rm2'  # Quinta-feira Santa: Missa in Cena Domini (não a do Crisma)
        if arq.startswith('XXXXX') or not d.existe(arq):
            continue
        m = re.match(r'^(.*)-(\d)$', base)
        feria = str(int(m.group(2)) + 1) if m else ''
        dom = None
        if m and m.group(2) != '0':
            dom = d.arquivo_versao('Tempora/' + m.group(1) + '-0')
        ctx = Contexto(tempus=tempus_de(chave), feria=feria)
        missa = montar(d, arq, ctx, dom)
        if missa and missa['p']:
            missa['arq'] = arq
            tempora[base] = missa
    # Férias sem Missa própria repetem o domingo: guardar só a referência
    for base, missa in list(tempora.items()):
        m = re.match(r'^(.*)-([1-6])$', base)
        if not m:
            continue
        dom = tempora.get(m.group(1) + '-0')
        if dom and missa['p'] == dom['p']:
            tempora[base] = {k: v for k, v in missa.items() if k not in ('p', 'ord')}
            tempora[base]['ref'] = m.group(1) + '-0'

    # ---- Próprio dos Santos (calendário de 1962)
    kal = d.kalendarium()
    sancti = {}
    alvos = {v['arquivo'] for v in kal.values()}
    for extra in ('Sancti/12-25m1', 'Sancti/12-25m2', 'Sancti/12-25m3',
                  'Sancti/11-02m1', 'Sancti/11-02m2', 'Sancti/11-02m3', 'Sancti/10-DUr'):
        if d.existe(extra):
            alvos.add(extra)
    for arq in sorted(alvos):
        if not d.existe(arq):
            continue
        normal = montar(d, arq, Contexto(tempus='post Pentecosten'))
        if not normal or not normal['p']:
            continue
        pasc = montar(d, arq, Contexto(tempus='post Octavam Paschæ'))
        if pasc:
            dif = {k: v for k, v in pasc['p'].items() if normal['p'].get(k) != v}
            if dif:
                normal['pP'] = dif
        normal['arq'] = arq
        if re.match(r'Sancti/11-02m\d', arq):
            normal['c'] = 1  # as três Missas de Finados são de 1ª classe
        sancti[arq.split('/', 1)[1]] = normal

    kal_saida = {dia: {'a': v['arquivo'].split('/', 1)[1], 'n': v['nome']} for dia, v in sorted(kal.items())}

    def gravar(nome, obj):
        with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
        print('%-20s %4d itens  %7.0f KB' % (nome, len(obj), os.path.getsize(os.path.join(SAIDA, nome)) / 1024))

    # ---- Textos fixos: os 15 prefácios do Missal de 1962, Communicantes (com S. José), conclusões
    ordo = {}
    pref = d.secoes('Ordo/Prefationes', Contexto())
    pref_pasc = d.secoes('Ordo/Prefationes', Contexto(tempus='Octava Paschæ'))
    for nome in PREFACIOS_1962:
        ordo['pf:' + nome] = converter(pref[nome])
    ordo['pf:PaschDie'] = converter(pref_pasc['Pasch'])
    for nome in ('C-common1962', 'C-Nat1962', 'C-Epi1962', 'C-Pasc1962', 'C-Asc1962', 'C-Pent1962', 'H-Pent'):
        ordo[nome] = converter(pref[nome])
    oracoes = d.secoes('Ordo/Prayers', Contexto())
    for nome in ('Per Dominum', 'Per Dominum eiusdem', 'Per eundem', 'Per eumdem', 'Qui vivis', 'Qui tecum',
                 'Qui tecum eiusdem', 'Qui cum Patre', 'Gloria', 'Deo gratias', 'Dominus vobiscum',
                 'Asperges me', 'Vidi aquam', 'Ultima Evangelium'):
        ordo['or:' + nome] = converter(oracoes[nome])
    gravar('la-ordo.json', ordo)

    gravar('la-tempora.json', tempora)
    gravar('la-sancti.json', sancti)
    gravar('kalendarium.json', kal_saida)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    gerar(sys.argv[1])
