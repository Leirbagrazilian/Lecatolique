"""Compila a tradução de apoio dos Próprios (data/missal/traducao/*.txt) para o app.

Formato dos arquivos de tradução:

    === T:Pent24-0              (T: Próprio do Tempo · S: Próprio dos Santos)
    # Introitus
    Diz o Senhor: Eu tenho pensamentos de paz...
    Abençoastes, Senhor, a vossa terra...
    =1                          (repete a 1ª linha traduzida desta parte)
    # Oratio
    @T:Epi3-0                   (copia esta parte já traduzida de outra Missa)
    ...

Cada linha traduz, na ordem, uma linha latina de texto (títulos de leitura, texto, ℣ e ℟).
Citações bíblicas, rubricas e conclusões ("Per Dominum...") não se traduzem aqui: o app cuida delas.

Uso:
    python3 -I tools/missal/compilar_traducao.py               compila e valida
    python3 -I tools/missal/compilar_traducao.py T:Pent24-0    mostra o latim numerado, para traduzir
"""
import glob
import json
import os
import re
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DADOS = os.path.join(RAIZ, 'data', 'missal')
TRADUZIVEIS = ('h', 't', 'V', 'R')


def carregar_latim():
    with open(os.path.join(DADOS, 'la-tempora.json'), encoding='utf-8') as f:
        t = json.load(f)
    with open(os.path.join(DADOS, 'la-sancti.json'), encoding='utf-8') as f:
        s = json.load(f)
    return {'T': t, 'S': s}


def linhas_latinas(missa, parte):
    if parte.startswith('P:'):
        src = (missa.get('pP') or {}).get(parte[2:], [])
    else:
        src = missa.get('p', {}).get(parte, [])
    return [ln[2:] for ln in src if ln[0] in TRADUZIVEIS]


def modelo(chave, latim):
    fonte, k = chave.split(':', 1)
    m = latim[fonte][k]
    if 'ref' in m:
        print('(%s repete a Missa %s)' % (chave, m['ref']))
        return
    print('=== ' + chave + '   ' + m['t'])
    for parte in m['ord'] + ['P:' + x for x in (m.get('pP') or {})]:
        print('# ' + parte)
        for i, ln in enumerate(linhas_latinas(m, parte), 1):
            print('  %d) %s' % (i, ln))


def compilar(latim):
    saida = {'T': {}, 'S': {}}
    erros = []
    pendentes = []  # partes copiadas de outra Missa (@T:Chave), resolvidas no fim
    for arq in sorted(glob.glob(os.path.join(DADOS, 'traducao', '*.txt'))):
        chave = parte = None
        buf = {}
        nome = os.path.basename(arq)

        def fechar():
            if chave is None:
                return
            fonte, k = chave.split(':', 1)
            m = latim.get(fonte, {}).get(k)
            if m is None:
                erros.append('%s: Missa desconhecida %s' % (nome, chave))
                return
            res = {}
            for p, linhas in buf.items():
                lat = linhas_latinas(m, p)
                if len(linhas) == 1 and linhas[0].startswith('@'):
                    pendentes.append((fonte, k, p, linhas[0][1:].strip(), len(lat), nome))
                    continue
                final = []
                for ln in linhas:
                    mm = re.match(r'^=(\d+)$', ln)
                    if mm:
                        idx = int(mm.group(1)) - 1
                        final.append(final[idx] if 0 <= idx < len(final) else '')
                    else:
                        final.append(ln)
                if len(final) != len(lat):
                    erros.append('%s: %s [%s] tem %d linhas, o latim tem %d' % (nome, chave, p, len(final), len(lat)))
                    continue
                res[p] = final
            saida[fonte][k] = res

        with open(arq, encoding='utf-8') as f:
            for ln in f:
                ln = ln.rstrip('\n').strip()
                if not ln or ln.startswith('//'):
                    continue
                if ln.startswith('==='):
                    fechar()
                    chave = ln[3:].strip().split()[0]
                    parte, buf = None, {}
                elif ln.startswith('# '):
                    parte = ln[2:].strip()
                    buf[parte] = []
                elif parte is not None:
                    buf[parte].append(ln)
            fechar()
    for fonte, k, p, ref, n, nome in pendentes:
        rf, rk = ref.split(':', 1)
        txt = saida.get(rf, {}).get(rk, {}).get(p)
        if txt is None:
            erros.append('%s: %s:%s [%s] copia %s, que não tem essa parte traduzida' % (nome, fonte, k, p, ref))
        elif len(txt) != n:
            erros.append('%s: %s:%s [%s] copia %s com %d linhas, o latim tem %d' % (nome, fonte, k, p, ref, len(txt), n))
        else:
            saida[fonte].setdefault(k, {})[p] = txt
    return saida, erros


def main():
    latim = carregar_latim()
    if len(sys.argv) > 1:
        for chave in sys.argv[1:]:
            modelo(chave, latim)
        return
    saida, erros = compilar(latim)
    for e in erros:
        print('ERRO', e)
    for fonte, nome in (('T', 'pt-tempora.json'), ('S', 'pt-sancti.json')):
        with open(os.path.join(DADOS, nome), 'w', encoding='utf-8') as f:
            json.dump(saida[fonte], f, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
        print('%-16s %3d Missas traduzidas' % (nome, len(saida[fonte])))
    if erros:
        sys.exit(1)


if __name__ == '__main__':
    main()
