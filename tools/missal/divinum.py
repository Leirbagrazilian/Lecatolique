"""Leitor dos arquivos de dados do Divinum Officium (https://github.com/DivinumOfficium/divinum-officium).

Lê os arquivos de texto da Missa como DADOS. Não executa nenhum código do projeto.
Reproduz, em Python, só o necessário do formato deles para a versão "Rubrics 1960 - 1960"
(o Missal Romano de 1962, sem os acréscimos posteriores):

  * seções [Nome] com condição opcional, ex.: [Rank] (sed rubrica 1960)
  * linhas condicionais, ex.: (sed rubrica 196) ... (nisi tempore paschali) ...
  * inclusões @Arquivo:Seção:substituições, de arquivo inteiro e de seção
  * a tabela Tabulae/Tempora/Generale.txt (troca de arquivos conforme a versão)
  * o calendário Tabulae/Kalendaria (1570 + alterações até 1960)

A lógica das condições é um porte fiel de web/cgi-bin/DivinumOfficium/SetupString.pl.
Licença dos dados: MIT (ver data/missal/LICENCA-DivinumOfficium.txt).
"""
import os
import re

VERSAO = 'Rubrics 1960 - 1960'
TAG_TRANSFER = '1960'
CADEIA_KALENDARIA = ['1570', '1888', '1906', '1939', '1954', '1955', '1960']


# ---------------------------------------------------------------- condições
class Contexto:
    """Valores do 'dia' que algumas condições consultam."""

    def __init__(self, tempus='post Pentecosten', feria='', die='', missa='', mense=''):
        self.tempus, self.feria, self.die, self.missa, self.mense = tempus, feria, die, missa, mense


SUBJECTS = {
    'rubricis': lambda c: VERSAO, 'rubrica': lambda c: VERSAO, 'communi': lambda c: VERSAO,
    'tempore': lambda c: c.tempus, 'missa': lambda c: c.missa, 'die': lambda c: c.die,
    'feria': lambda c: c.feria, 'commune': lambda c: '', 'votiva': lambda c: '',
    'officio': lambda c: '', 'ad': lambda c: 'missam', 'mense': lambda c: c.mense,
    'anno': lambda c: '', 'dioecesis': lambda c: '', 'tonus': lambda c: '', 'toni': lambda c: '',
}
PREDICATES = {
    'tridentina': lambda s: bool(re.search('Trident', str(s))),
    'monastica': lambda s: bool(re.search('Monastic', str(s))),
    'innovata': lambda s: bool(re.search('2020 USA|NewCal', str(s), re.I)),
    'innovatis': lambda s: bool(re.search('2020 USA|NewCal', str(s), re.I)),
    'paschali': lambda s: bool(re.search('Paschæ|Ascensionis|Octava Pentecostes', str(s), re.I)),
    'post septuagesimam': lambda s: bool(re.search('Septua|Quadra|Passio', str(s), re.I)),
    'prima': lambda s: str(s) == '1', 'secunda': lambda s: str(s) == '2', 'tertia': lambda s: str(s) == '3',
    'longior': lambda s: str(s) == '1', 'brevior': lambda s: str(s) == '2',
    'summorum pontificum': lambda s: bool(re.search(r'194[2-9]\]|195[45]|196', str(s))),
    'feriali': lambda s: bool(re.search('feria|vigilia', str(s), re.I)),
    'in solemnitatibus': lambda s: bool(re.search('solemnis|resurrectionis', str(s), re.I)),
    'in hieme': lambda s: bool(re.search('hieme|Adventus|Nativitatis|Epiphani|gesimæ|Passionis', str(s), re.I)),
    'in æstate': lambda s: not re.search('hieme|Adventus|Nativitatis|Epiphani|gesimæ|Passionis', str(s), re.I),
}


def vero(cond, ctx):
    cond = cond.strip()
    if not cond:
        return True
    for alt in re.split(r'\baut\b', cond):
        negation = False
        ok = True
        for part in re.split(r'\b(et|nisi)\b', alt):
            if part in ('et', 'nisi'):
                if part == 'nisi':
                    negation = True
                continue
            part = re.sub(r'\s+', ' ', part.strip())
            bits = part.split(' ', 1)
            subject, predicate = (bits[0], bits[1]) if len(bits) == 2 else ('', bits[0])
            if subject and subject.lower() not in SUBJECTS:
                predicate, subject = subject + ' ' + predicate, ''
            subject = subject or 'tempore'
            fn = PREDICATES.get(predicate.lower())
            if fn is None:
                pat = predicate
                fn = lambda s, pat=pat: bool(re.search(pat, str(s), re.I))
            sval = SUBJECTS[subject.lower()](ctx)
            if not (fn(sval) != negation):  # xor
                ok = False
                break
        if ok:
            return True
    return False


STOP_WEIGHTS = {'sed': 1, 'vero': 1, 'atque': 2, 'attamen': 3, 'si': 0, 'deinde': 1}
BACKSCOPED = {'sed', 'vero', 'atque', 'attamen'}
_STOP = '|'.join(STOP_WEIGHTS)
_SCOPE = (r'(?:\bloco\s+(?:hu[ij]us\s+versus|horum\s+versuum)\b)?\s*(?:\b(?:(?:dicitur|dicuntur)(?:\s+semper)?'
          r'|(?:hic\s+versus\s+)?omittitur|(?:hoc\s+versus\s+)?omittitur|(?:hæc\s+versus\s+)?omittuntur'
          r'|(?:hi\s+versus\s+)?omittuntur|(?:haec\s+versus\s+)?omittuntur)\b)?')
COND_RE = r'\(\s*((?:' + _STOP + r')\b)*(.*?)(' + _SCOPE + r')?\s*\)'
LINE_COND = re.compile(r'^\s*' + COND_RE + r'\s*(.*)$', re.I)
SECTION_RE = re.compile(r'^\s*\[([\w #,:-]+)\](?:\s*' + COND_RE + r')?', re.I)
BLANK = re.compile(r'^\s*_?\s*$')
S_NULL, S_LINE, S_CHUNK, S_NEST = 0, 1, 2, 3


def parse_conditional(stop, cond, scope, ctx):
    stop = stop or ''
    words = stop.lower().split()
    strength = sum(STOP_WEIGHTS.get(w, 0) for w in words)
    result = vero(cond, ctx)
    implicit = any(w in BACKSCOPED for w in words)
    scope = scope or ''
    if re.search('versuum|omittuntur', scope, re.I):
        back = S_NEST
    elif re.search('versus|omittitur', scope, re.I):
        back = S_CHUNK
    elif not re.search('semper', scope, re.I) and implicit:
        back = S_LINE
    else:
        back = S_NULL
    if re.search('omittitur|omittuntur', scope, re.I):
        fwd = S_NULL
    elif re.search('dicuntur', scope, re.I):
        fwd = S_CHUNK if back == S_CHUNK else S_NEST
    else:
        fwd = S_CHUNK if back in (S_CHUNK, S_NEST) else S_LINE
    return strength, result, back, fwd


def process_conditional_lines(lines, ctx):
    """Porte de process_conditional_lines (SetupString.pl)."""
    AFF, NOT_YET, DUMMY = 1, 0, 2
    out = []
    stack = [[AFF, S_NEST]]
    offsets = [-1]
    for line in lines:
        m = LINE_COND.match(line)
        if m:
            strength, result, back, fwd = parse_conditional(m.group(1), m.group(2), m.group(3), ctx)
            line = m.group(4)
            n_off = len(offsets) - 1
            if stack[-1][0] == AFF or strength >= n_off:
                if strength >= n_off:
                    stack = []
                elif strength >= n_off - (len(stack) - 1):
                    del stack[n_off - strength:]
                if result:
                    fence = offsets[strength] if n_off >= strength else -1
                    if back == S_LINE:
                        if len(out) - 1 > fence:
                            out.pop()
                    elif back == S_CHUNK:
                        while len(out) - 1 > fence and not BLANK.match(out[-1]):
                            out.pop()
                        while len(out) - 1 > fence and BLANK.match(out[-1]):
                            out.pop()
                    elif back == S_NEST:
                        del out[fence + 1:]
                if fwd == S_NULL:
                    fwd, result = S_NEST, True
                if result:
                    while len(offsets) <= strength:
                        offsets.append(-1)
                    for i in range(strength + 1):
                        offsets[i] = len(out) - 1
                while strength < (len(offsets) - 1) - (len(stack) - 1) - 1:
                    stack.append([DUMMY, fwd])
                stack.append([AFF if result else NOT_YET, fwd])
            if not line:
                continue
        if line.startswith('~'):
            line = line[1:]
        if stack[-1][0] == AFF:
            out.append(line)
        while stack[-1][1] == S_LINE or (stack[-1][1] == S_CHUNK and BLANK.match(line)):
            while True:
                stack.pop()
                if not (stack and stack[-1][0] == DUMMY):
                    break
            if not stack:
                stack.append([AFF, S_NEST])
    return out


# ---------------------------------------------------------------- arquivos
INCL = re.compile(r'^\s*@([^\n:]+)?(?::([^\n:]+?))?[^\S\n\r]*(?::(.*))?$\n?', re.M)


class Divinum:
    def __init__(self, raiz):
        self.www = os.path.join(raiz, 'web', 'www')
        self.missa = os.path.join(self.www, 'missa', 'Latin')
        self.horas = os.path.join(self.www, 'horas', 'Latin')
        self._cache = {}
        self.transfer = self._ler_transfer()

    # Tabulae/Tempora/Generale.txt: troca de arquivo conforme a versão
    def _ler_transfer(self):
        t = {}
        with open(os.path.join(self.www, 'Tabulae', 'Tempora', 'Generale.txt'), encoding='utf-8') as f:
            for ln in f:
                ln = ln.strip()
                if not ln or ln.startswith('#') or ';;' not in ln:
                    continue
                regra, tags = ln.split(';;', 1)
                if TAG_TRANSFER in tags.split() and '=' in regra:
                    a, b = regra.split('=', 1)
                    t[a] = b
        return t

    def arquivo_versao(self, nome):
        return self.transfer.get(nome, nome)

    def caminho(self, nome):
        """Missa primeiro; Commune e o que faltar, nas Horas (como o setupstring_layers)."""
        rel = nome + '.txt'
        m = os.path.join(self.missa, rel)
        h = os.path.join(self.horas, rel)
        if re.search(r'C\d', nome) and os.path.exists(h):
            return h
        if os.path.exists(m):
            return m
        if os.path.exists(h):
            return h
        return None

    def existe(self, nome):
        return self.caminho(nome) is not None

    def _parse(self, nome, ctx):
        path = self.caminho(nome)
        if not path:
            return None
        with open(path, encoding='utf-8') as f:
            linhas = f.read().replace('\r', '').split('\n')
        secs, key, usar = {}, '__preamble', True
        secs[key] = []
        for ln in linhas:
            m = SECTION_RE.match(ln) if ln.startswith('[') else None
            if m:
                cond = m.group(3)
                if not cond or vero(cond, ctx):
                    usar, key = True, m.group(1)
                    secs[key] = []
                else:
                    usar = False
            elif usar:
                if ln.startswith('@') and key != '__preamble':
                    mm = INCL.match(ln)
                    if mm:
                        ln = '@' + (mm.group(1) or nome) + ':' + (mm.group(2) or key) + (':' + mm.group(3) if mm.group(3) else '')
                secs[key].append(ln)
        return {k: '\n'.join(process_conditional_lines(v, ctx) + ['']) for k, v in secs.items()}

    def secoes(self, nome, ctx, completo=True, _prof=0):
        """Seções do arquivo. Inclusões de arquivo inteiro sempre; de seção só se completo=True
        (como setupstring com RESOLVE_ALL; os arquivos incluídos vêm com RESOLVE_WHOLEFILE)."""
        chave = (nome, ctx.tempus, ctx.feria, ctx.missa, completo)
        if chave in self._cache:
            return dict(self._cache[chave])
        base = self._parse(nome, ctx)
        if base is None:
            return None
        secs = dict(base)
        pre = secs.pop('__preamble', '')
        for mm in INCL.finditer(pre):
            if mm.group(1) and _prof < 8 and mm.group(1) != nome:
                inc = self.secoes(mm.group(1), ctx, False, _prof + 1) or {}
                for k, v in inc.items():
                    secs.setdefault(k, v)
        if completo:
            for k in list(secs):
                n = 0
                while '@' in secs[k] and INCL.search(secs[k]):
                    n += 1
                    if n > 7:
                        secs[k] = 'Cannot resolve too deeply nested Hashes'
                        break
                    secs[k] = INCL.sub(lambda mm, k=k: self._inclusao(secs, nome, mm, k, ctx), secs[k])
        if 'Officium' in secs and 'Rank' in secs:
            secs['Rank'] = re.sub(r'^.*?;;', secs['Officium'].strip() + ';;', secs['Rank'], count=1)
        self._cache[chave] = dict(secs)
        return secs

    def _inclusao(self, secs, nome, mm, key, ctx):
        arq, sec, subs = mm.group(1), mm.group(2) or key, mm.group(3)
        alvo = (self.secoes(arq, ctx, False) or {}) if arq and arq != nome else secs
        txt = alvo.get(sec)
        if txt is None:
            return '%s:%s is missing!\n' % (arq, sec)
        txt = re.sub(r'\n+$', '\n', txt)
        if subs:
            txt = substituicoes(txt, subs)
        return txt

    # ------------------------------------------------------- calendário
    def kalendarium(self):
        """MM-DD -> (arquivo principal, nome latino) para 1960 (1570 + alterações)."""
        kal = {}
        for nome in CADEIA_KALENDARIA:
            with open(os.path.join(self.www, 'Tabulae', 'Kalendaria', nome + '.txt'), encoding='utf-8') as f:
                for ln in f:
                    ln = ln.strip()
                    if not ln or ln.startswith('#') or ln.startswith('*') or '=' not in ln:
                        continue
                    partes = ln.split('=')
                    dia = partes[0]
                    if not re.match(r'^\d\d-\d\d$', dia):
                        continue
                    if partes[1].startswith('XXXXX'):
                        kal.pop(dia, None)
                        continue
                    arqs = partes[1].split('~')
                    kal[dia] = {'arquivo': 'Sancti/' + arqs[0], 'nome': partes[2] if len(partes) > 2 else '',
                                'comem': ['Sancti/' + a for a in arqs[1:]]}
        return kal


def substituicoes(txt, subs):
    """do_inclusion_substitutions: s/a/b/flags ou seleção de linhas (1-based, '!' exclui)."""
    for m in re.finditer(r'(?:s/(?P<s>[^/]*)/(?P<r>[^/]*)/(?P<f>[gism]*))|(?:(?P<n>!?)(?P<b>\d+)(-(?P<e>\d+))?)', subs):
        if m.group('b'):
            s = int(m.group('b')) - 1
            l = int(m.group('e')) - s if m.group('e') else 1
            linhas = txt.split('\n')
            sel = linhas[s:s + l]
            resto = linhas[:s] + linhas[s + l:]
            txt = '\n'.join(resto if m.group('n') else sel) + '\n'
        else:
            flags = 0
            fl = m.group('f') or ''
            if 'i' in fl:
                flags |= re.I
            if 's' in fl:
                flags |= re.S
            if 'm' in fl:
                flags |= re.M
            rep = re.sub(r'\$(\d)', r'\\\1', m.group('r'))
            try:
                txt = re.sub(m.group('s'), rep, txt, count=0 if 'g' in fl else 1, flags=flags)
            except re.error:
                pass
    return txt
