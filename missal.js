/* =====================================================================
   MISSAL ROMANO DE 1962 — aba #missa
   Latim: dados do projeto Divinum Officium (licença MIT), gerados por
   tools/missal/gerar_missal.py. Português: tradução de apoio, não oficial.
   Depende do script principal (index.html): $, esc, store, diaLiturgico,
   datas, SANTORAL, ORACOES, chave, iso, fromIso, add, diff, same, D, HOJE...
   Leia CLAUDE.md (seção Missal) antes de alterar.
   ===================================================================== */

const MISSAL = { la: null, pt: { T: {}, S: {} }, ordo: null, laOrdo: null, kal: null, carregando: null, erro: null };
const ARQ_MISSAL = ['la-tempora', 'la-sancti', 'la-ordo', 'kalendarium', 'ordinario', 'pt-tempora', 'pt-sancti'];

function carregarMissal() {
  if (MISSAL.carregando) return MISSAL.carregando;
  const get = n => fetch('data/missal/' + n + '.json').then(r => { if (!r.ok) throw new Error(n + ': ' + r.status); return r.json(); });
  const opcional = n => get(n).catch(() => ({}));
  MISSAL.carregando = Promise.all([get('la-tempora'), get('la-sancti'), get('la-ordo'), get('kalendarium'), get('ordinario'), opcional('pt-tempora'), opcional('pt-sancti')])
    .then(([t, s, lo, k, o, pt, ps]) => { MISSAL.la = { T: t, S: s }; MISSAL.laOrdo = lo; MISSAL.kal = k; MISSAL.ordo = o; MISSAL.pt = { T: pt, S: ps }; })
    .catch(e => { MISSAL.erro = e; MISSAL.carregando = null; throw e; });
  return MISSAL.carregando;
}

/* ---------- Preferências ---------- */
/* Lidas na primeira abertura da aba: este arquivo carrega antes do script principal (store). */
let missaDia = null;                                   /* data escolhida (null = hoje) */
let MLANG = null;                                      /* la | pt | ambos */
let mModo = null;                                      /* completa | proprio */
let mRub = null;                                       /* mostrar rubricas */
let mOpcao = {};                                       /* escolha entre várias Missas no mesmo dia */
function lerPreferenciasMissa() {
  if (MLANG !== null) return;
  MLANG = store.get('missaLang', 'ambos'); mModo = store.get('missaModo', 'completa'); mRub = store.get('missaRub', true);
}

/* ---------- Data -> Missa ---------- */
const pad2 = n => String(n).padStart(2, '0');

/* Chave do Próprio do Tempo (nomes do Divinum Officium) ou null nos dias do Santoral do Natal */
function chaveTempora(dt) {
  const y = dt.getFullYear(), k = datas(y), wd = dt.getDay(), m = dt.getMonth() + 1, d = dt.getDate();
  if (dt >= k.adv1 && dt < k.natal) return 'Adv' + (Math.floor(diff(k.adv1, dt) / 7) + 1) + '-' + wd;
  if (m === 12 && d >= 25) return wd === 0 ? 'Nat1-0' : null;
  if (m === 1 && d <= 13) {
    if (same(dt, k.santoNome)) return 'Nat2-0';
    if (d >= 2 && d <= 5) return 'Nat0' + d;
    if (d >= 7 && d <= 12) return wd === 0 ? 'Epi1-0' : 'Epi1-' + wd;
    return null;
  }
  if (dt < k.septuagesima) {
    const n = Math.min(6, Math.max(1, Math.floor(diff(k.sagradaFamilia, dt) / 7) + 1));
    return 'Epi' + n + '-' + wd;
  }
  if (dt < k.quad1) return 'Quadp' + (Math.floor(diff(k.septuagesima, dt) / 7) + 1) + '-' + wd;
  if (dt < k.pascoa) return 'Quad' + (Math.floor(diff(k.quad1, dt) / 7) + 1) + '-' + wd;
  const ep = diff(k.pascoa, dt);
  if (ep <= 55) return 'Pasc' + Math.floor(ep / 7) + '-' + wd;
  if (temporasDe(dt) === 'de Setembro') return '093-' + wd;
  const n = Math.floor(diff(k.pentecostes, dt) / 7);
  const total = diff(k.pentecostes, add(k.adv1, -7)) / 7;      /* nº do último domingo depois de Pentecostes */
  if (n >= total) return 'Pent24-' + wd;
  if (n >= 24) return 'PentEpi' + (6 - (total - 1 - n)) + '-' + wd;
  return 'Pent' + pad2(n) + '-' + wd;
}

/* Retorna { opcoes: [{f, k, rotulo}], i } — f: 'T' (Tempo) ou 'S' (Santos) */
function missasDoDia(dt) {
  const L = diaLiturgico(dt), mmdd = chave(dt), s = SANTORAL[mmdd], LA = MISSAL.la, kal = MISSAL.kal[mmdd];
  const uma = (f, k) => ({ opcoes: [{ f, k }], i: 0 });
  if (same(dt, L.k.cristoRei)) return uma('S', '10-DUr');
  if (mmdd === '12-25') return { opcoes: [['12-25m1', 'Da noite'], ['12-25m2', 'Da aurora'], ['12-25m3', 'Do dia']].map(([k, r]) => ({ f: 'S', k, rotulo: r })), i: 2 };
  if (mmdd === '11-02' && LA.S['11-02m1']) return { opcoes: [1, 2, 3].map(n => ({ f: 'S', k: '11-02m' + n, rotulo: n + 'ª Missa' })), i: 0 };
  const tk = chaveTempora(dt);
  const santoVence = s && L.titulo === s.nome;
  if (santoVence && kal && LA.S[kal.a]) return uma('S', kal.a);
  if (tk && LA.T[tk]) {
    /* féria simples (4ª classe) com santo de 3ª classe no calendário de 1962 */
    if (L.classe === 4 && !L.domingo && kal && LA.S[kal.a] && LA.S[kal.a].c <= 3) return uma('S', kal.a);
    return uma('T', tk);
  }
  if (kal && LA.S[kal.a]) return uma('S', kal.a);
  const dom = add(dt, -dt.getDay());
  const dk = chaveTempora(dom);
  return dk && LA.T[dk] ? uma('T', dk) : uma('T', 'Pent24-0');
}

/* Missa com a referência resolvida (férias que repetem o domingo) */
function obterMissa(f, k) {
  const m = MISSAL.la[f][k];
  if (!m) return null;
  if (!m.ref) return { ...m, f, k, kp: k };
  const base = MISSAL.la[f][m.ref];
  return { ...base, t: m.t, c: m.c, g: m.g, cr: m.cr, pf: m.pf, pfs: m.pfs, f, k, kp: m.ref, feria: true };
}

/* ---------- Regras que dependem do dia ---------- */
const PREF_1962 = new Set(['Nat', 'Epi', 'Quad', 'Quad5', 'Pasch', 'Asc', 'Cord', 'Regis', 'Spiritu', 'Trinitate', 'Maria', 'Joseph', 'Apostolis', 'Communis', 'Defunctorum']);
const PREF_NOME = { Nat: 'do Natal', Epi: 'da Epifania', Quad: 'da Quaresma', Quad5: 'da Santa Cruz', Pasch: 'Pascal', PaschDie: 'Pascal', Asc: 'da Ascensão', Cord: 'do Sagrado Coração', Regis: 'de Cristo Rei', Spiritu: 'do Espírito Santo', Trinitate: 'da Santíssima Trindade', Maria: 'de Nossa Senhora', Joseph: 'de São José', Apostolis: 'dos Apóstolos', Communis: 'Comum', Defunctorum: 'dos Defuntos' };
const PFS_PT = { 'festivitate': 'Festividade', 'festivitáte': 'Festividade', 'apparitióne': 'Aparição', 'annuntiatióne': 'Anunciação', 'solemnitáte': 'Solenidade', 'visitatióne': 'Visitação', 'commemoratione': 'Comemoração', 'assumptióne': 'Assunção', 'nativitate': 'Natividade', 'transfixióne': 'Transfixão', 'presentatióne': 'Apresentação', 'conceptióne immaculáta': 'Conceição imaculada', 'hodierna die': 'neste dia' };

function contexto(dt, m) {
  const k = datas(dt.getFullYear()), ep = diff(k.pascoa, dt), t = diaLiturgico(dt).tempo.id;
  const tk = m.f === 'T' ? m.k : '';
  const defuntos = /^11-02/.test(m.k) || m.cm === 'C9';
  return {
    dt, ep, tk, defuntos,
    domingo: dt.getDay() === 0,
    paixao: m.f === 'T' && /^Quad[56]/.test(m.k),
    pascal: ep >= 0 && ep <= 49,                              /* Vidi aquam: Páscoa a Pentecostes */
    oitavaPascoa: ep >= 0 && ep <= 6,
    tracto: ['septuagesima', 'quaresma', 'paixao', 'semanasanta'].includes(t),
    gradPascal: ep >= 0 && ep <= 55,
    triduo: m.f === 'T' && /^Quad6-[56]/.test(m.k)
  };
}

function nomePrefacio(m, c) {
  if (m.pf && PREF_1962.has(m.pf)) return m.pf === 'Pasch' && c.oitavaPascoa ? 'PaschDie' : m.pf;
  if (c.defuntos) return 'Defunctorum';
  const k = datas(c.dt.getFullYear()), mm = c.dt.getMonth() + 1, d = c.dt.getDate(), tk = m.f === 'T' ? m.kp : (chaveTempora(c.dt) || '');
  if (dentroAdvento(c.dt, k)) return c.domingo ? 'Trinitate' : 'Communis';   /* 1962: não há Prefácio do Advento */
  if ((mm === 12 && d > 24) || (mm === 1 && d === 1)) return 'Nat';
  if (mm === 1 && d > 5 && d < 14) return 'Epi';
  if (/^Quad[1-4]/.test(tk)) return 'Quad';
  if (/^Quad[56]/.test(tk)) return 'Quad5';
  if (/^Pasc0/.test(tk)) return 'PaschDie';
  if (/^Pasc[1-4]/.test(tk) || (/^Pasc5/.test(tk) && c.dt.getDay() < 4)) return 'Pasch';
  if (/^Pasc[56]/.test(tk)) return 'Asc';
  if (/^Pasc7/.test(tk)) return 'Spiritu';
  if (m.bmv) return 'Maria';
  if (/^C1/.test(m.cm || '') || /^C[234]b/.test(m.cm || '')) return 'Apostolis';
  return c.domingo ? 'Trinitate' : 'Communis';
}
const dentroAdvento = (dt, k) => dt >= k.adv1 && dt < k.natal;

function nomeCommunicantes(c) {
  const mm = c.dt.getMonth() + 1, d = c.dt.getDate(), tk = chaveTempora(c.dt) || '';
  if ((mm === 12 && d > 24) || (mm === 1 && d === 1)) return 'C-Nat1962';
  if (mm === 1 && d === 6) return 'C-Epi1962';
  if (/^Pasc0/.test(tk)) return 'C-Pasc1962';
  if (tk === 'Pasc5-4') return 'C-Asc1962';
  if (/^Pasc7/.test(tk) || tk === 'Pasc6-6') return 'C-Pent1962';
  return 'C-common1962';
}

/* ---------- Texto ---------- */
const LIVROS = { Ps: 'Sl', Psalm: 'Sl', Matt: 'Mt', Matth: 'Mt', Marc: 'Mc', Luc: 'Lc', Joann: 'Jo', Joan: 'Jo', Rom: 'Rm', Cor: 'Cor', Gal: 'Gl', Eph: 'Ef', Ephes: 'Ef', Phil: 'Fl', Philipp: 'Fl', Col: 'Cl', Thess: 'Ts', Tim: 'Tm', Tit: 'Tt', Hebr: 'Hb', Heb: 'Hb', Jac: 'Tg', Petri: 'Pd', Pet: 'Pd', Apoc: 'Ap', Act: 'At', Gen: 'Gn', Exod: 'Ex', Lev: 'Lv', Num: 'Nm', Deut: 'Dt', Jos: 'Js', Judic: 'Jz', Par: 'Cr', Tob: 'Tb', Judith: 'Jt', Esth: 'Est', Job: 'Jó', Prov: 'Pr', Eccl: 'Ecl', Cant: 'Ct', Sap: 'Sb', Eccli: 'Eclo', Is: 'Is', Isa: 'Is', Jer: 'Jr', Thren: 'Lm', Bar: 'Br', Ezech: 'Ez', Dan: 'Dn', Osee: 'Os', Joel: 'Jl', Joël: 'Jl', Amos: 'Am', Jon: 'Jn', Mich: 'Mq', Hab: 'Hab', Soph: 'Sf', Agg: 'Ag', Zach: 'Zc', Mal: 'Ml', Malach: 'Ml', Mach: 'Mc' };
const REG = { '1': '1Sm', '2': '2Sm', '3': '1Rs', '4': '2Rs' };
function citacaoPT(s) {
  return s.replace(/(?:([1-4])\s*)?([A-ZÆ][A-Za-zæëé]*)\.?\s*:?\s*(?=\d)/g, (all, n, livro) => {
    if (livro === 'Reg' && n) return REG[n] + ' ';
    const pt = LIVROS[livro];
    return pt ? (n ? n : '') + pt + ' ' : all;
  }).replace(/(\d):(\d)/g, '$1, $2');
}
const RUB_PT = { 'Tractus': 'Tracto', 'Oratio super populum': 'Oração sobre o povo', 'Oratio super Populum': 'Oração sobre o povo', 'Sequentia': 'Sequência', 'Graduale': 'Gradual', 'Evangelium': 'Evangelho', 'Lectio prima': 'Primeira leitura', 'Oratio': 'Oração', 'Hymnus': 'Hino', 'Canticum': 'Cântico', 'Responsorium': 'Responsório', 'Antiphona.': 'Antífona' };

function fmt(s) {
  return esc(s)
    .replace(/\*/g, '')
    .replace(/✠/g, '<span class="cruz">✠</span>')
    .replace(/\(([^)]{2,160})\)/g, '<span class="rub-i">($1)</span>');
}
const MARCA = { V: '℣.', R: '℟.', S: 'S.', M: 'M.' };

/* Uma linha (latim e português) conforme o idioma escolhido */
function linha(tipo, la, pt, sufixo = '') {
  const marca = MARCA[tipo] ? `<span class="quem">${MARCA[tipo]}</span> ` : '';
  const cls = tipo === 'h' ? ' ml-h' : tipo === 'C' ? ' ml-c' : '';
  const L = `<div class="ml${cls}">${marca}${fmt(la)}${sufixo}</div>`;
  const P = pt ? `<div class="mp${cls}">${marca}${fmt(pt)}${sufixo}</div>` : '';
  if (MLANG === 'la' || !pt) return `<div class="mlin${!pt && MLANG === 'pt' ? ' sem' : ''}">${L}</div>`;
  if (MLANG === 'pt') return `<div class="mlin">${P}</div>`;
  return `<div class="mlin par">${L}${P}</div>`;
}
const rub = (s, extra = '') => mRub ? `<p class="mrub${extra}">${fmt(s)}</p>` : '';

/* Linhas no formato "x|texto" + tradução alinhada (só h, t, V, R) */
function linhasHTML(latinas, ptArr) {
  let i = 0, out = '';
  for (const ln of latinas || []) {
    const t = ln[0], s = ln.slice(2);
    if (t === 's') { out += '<div class="msep"></div>'; continue; }
    if (t === 'c') { out += `<p class="mcit">${esc(MLANG === 'la' ? s : citacaoPT(s))}</p>`; continue; }
    if (t === 'r') { out += mRub ? `<p class="mrub">${fmt(MLANG === 'la' ? s : (RUB_PT[s] || s))}</p>` : ''; continue; }
    if (t === 'k') { out += fixoHTML('or:' + aliasFixo(s)); continue; }
    const pt = ptArr ? ptArr[i] : null; i++;
    out += linha(t, s, pt);
  }
  return out;
}
const aliasFixo = s => ({ 'DominusVobiscum': 'Dominus vobiscum', 'Glória': 'Gloria', 'Per Dominum.': 'Per Dominum' }[s] || s);

function fixoHTML(chaveFixo, trocar) {
  let la = MISSAL.laOrdo[chaveFixo], pt = MISSAL.ordo.fixos[chaveFixo];
  if (!la) return '';
  if (trocar) { la = la.map(l => trocar(l, 'la')); pt = pt && pt.map(l => trocar(l, 'pt')); }
  const ptRes = pt ? pt.map((x, i, arr) => /^=\d+$/.test(x) ? arr[+x.slice(1) - 1] : x) : null;
  return linhasHTML(la, ptRes);
}

/* ---------- Próprio ---------- */
function ptParte(m, parte) {
  const tr = MISSAL.pt[m.f][m.kp];
  return tr ? tr[parte] || null : null;
}
function parteHTML(m, c, parte, titulo) {
  const p = { ...m.p, ...(c.gradPascal && m.pP ? m.pP : {}) };
  if (!p[parte]) return '';
  const pt = (c.gradPascal && m.pP && m.pP[parte]) ? ptParte(m, 'P:' + parte) : ptParte(m, parte);
  return (titulo ? `<h3 class="mparte">${titulo}</h3>` : '') + linhasHTML(p[parte], pt);
}
function gradualHTML(m, c) {
  let g = 'Graduale';
  if (c.tracto && m.p.Tractus) g = 'Tractus';
  else if (c.gradPascal && m.p.GradualeP) g = 'GradualeP';
  else if (m.feria && c.dt.getDay() > 0 && m.p.GradualeF) g = 'GradualeF';
  return parteHTML(m, c, g) + (m.p.Sequentia ? parteHTML(m, c, 'Sequentia', MLANG === 'la' ? 'Sequentia' : 'Sequência') : '');
}
function oratioHTML(m, c) {
  let out = '';
  const extras = (m.ord || []).filter(x => /^LectioL\d/.test(x)).length;
  if (extras && !c.gradPascal) out += linha('V', 'Flectámus génua.', 'Ajoelhemo-nos.') + linha('R', 'Leváte.', 'Levantai-vos.');
  out += parteHTML(m, c, 'Oratio');
  for (let i = 1; i <= extras; i++) {
    out += parteHTML(m, c, 'LectioL' + i, MLANG === 'la' ? 'Lectio' : 'Leitura');
    out += parteHTML(m, c, 'GradualeL' + i, MLANG === 'la' ? 'Graduale' : 'Gradual');
    if (i === extras) out += linha('V', 'Dóminus vobíscum.', 'O Senhor esteja convosco.') + linha('R', 'Et cum spíritu tuo.', 'E com o vosso espírito.');
    out += linha('S', 'Orémus.', 'Oremos.');
    if (i < extras && !c.gradPascal) out += linha('V', 'Flectámus génua.', 'Ajoelhemo-nos.') + linha('R', 'Leváte.', 'Levantai-vos.');
    out += parteHTML(m, c, 'OratioL' + i);
  }
  return out;
}
function proprioHTML(m, c, parte) {
  if (parte === 'Oratio') return oratioHTML(m, c);
  if (parte === 'Graduale') return gradualHTML(m, c);
  if (parte === 'Postcommunio') return parteHTML(m, c, 'Postcommunio') + (m.p['Super populum'] ? parteHTML(m, c, 'Super populum', MLANG === 'la' ? 'Oratio super populum' : 'Oração sobre o povo') : '');
  return parteHTML(m, c, parte);
}
function prefacioHTML(m, c) {
  const nome = nomePrefacio(m, c);
  const pfsPT = m.pfs ? (PFS_PT[m.pfs.toLowerCase()] || m.pfs) : null;
  const trocar = (l, lang) => {
    if (lang === 'la') {
      const tipo = l[0], s = l.slice(2);
      return tipo + '|' + (m.pfs ? s.replace(/\*[^*]*\*/, m.pfs) : s.replace(/\*/g, '')).replace(/\s{2,}/g, ' ');
    }
    return (pfsPT ? l.replace(/\*[^*]*\*/, pfsPT) : nome === 'Spiritu' ? l.replace(/\s*\*[^*]*\*/, '') : l.replace(/\*/g, '')).replace(/\s{2,}/g, ' ');
  };
  return `<h3 class="mparte">Prefácio ${PREF_NOME[nome] || ''}</h3>` + fixoHTML('pf:' + nome, trocar);
}

/* ---------- Ordinário ---------- */
function condOK(cond, m, c) {
  switch (cond) {
    case undefined: return true;
    case 'gloria': return !!m.g;
    case 'credo': return !!m.cr;
    case 'judica': return !c.defuntos && !c.paixao;
    case 'defuntos': return c.defuntos;
    case 'naoDefuntos': return !c.defuntos;
    case 'pascal': return c.pascal;
    case 'naoPascal': return !c.pascal;
    case 'domingo': return c.domingo;
    case 'costume': return true;
    case 'iteAleluia': return !c.defuntos && c.oitavaPascoa;
    case 'iteComum': return !c.defuntos && !c.oitavaPascoa;
    default: return true;
  }
}
function itemHTML(it, m, c) {
  if (!condOK(it.cond, m, c)) return '';
  if (it.r) return rub(it.r, it.cond === 'costume' ? ' costume' : '');
  if (it.x === 'proprio') return proprioHTML(m, c, it.p);
  if (it.x === 'prefacio') return prefacioHTML(m, c);
  if (it.x === 'communicantes') return fixoHTML(nomeCommunicantes(c));
  if (it.x === 'hancigitur') return /^Pasc[07]/.test(c.tk) ? fixoHTML('H-Pent') : '';
  if (it.x === 'fixo') return fixoHTML(it.k);
  if (it.x === 'comunhaoEspiritual') {
    const o = ORACOES.comunhao;
    return `<div class="mesp">${rub('Se não puder comungar, faça a comunhão espiritual:')}<p class="mp">${esc(o.pt)}</p></div>`;
  }
  const vezes = it.vezes ? ` <span class="rub-i">(${it.vezes} vezes)</span>` : '';
  return linha(it.w || 't', it.la, it.pt, vezes);
}
function blocoHTML(b, m, c) {
  if (!condOK(b.cond, m, c)) return '';
  const itens = b.itens.map(it => itemHTML(it, m, c)).join('');
  if (!itens.trim()) return '';
  return `<section class="folio mbloco" id="m-${b.id}">
    <div class="mcab"><h2>${esc(b.titulo)}</h2><span class="mla">${esc(b.la)}</span></div>
    ${(b.pos && mRub) ? `<p class="mpos">${esc(b.pos)}</p>` : ''}${(b.nota && mRub) ? `<p class="small muted">${esc(b.nota)}</p>` : ''}
    ${itens}</section>`;
}

const PARTES_PROPRIO = [['Introitus', 'Intróito'], ['Oratio', 'Coleta'], ['Lectio', 'Epístola'], ['Graduale', 'Gradual'], ['Evangelium', 'Evangelho'], ['Offertorium', 'Ofertório'], ['Secreta', 'Secreta'], ['_prefacio', 'Prefácio'], ['Communio', 'Comunhão'], ['Postcommunio', 'Pós-Comunhão']];
const LA_PARTE = { Introitus: 'Introitus', Oratio: 'Oratio', Lectio: 'Lectio', Graduale: 'Graduale', Evangelium: 'Evangelium', Offertorium: 'Offertorium', Secreta: 'Secreta', _prefacio: 'Præfatio', Communio: 'Communio', Postcommunio: 'Postcommunio' };

function soProprioHTML(m, c) {
  return PARTES_PROPRIO.map(([p, t]) => {
    const corpo = p === '_prefacio' ? prefacioHTML(m, c).replace(/^<h3[^>]*>.*?<\/h3>/, '') : proprioHTML(m, c, p);
    if (!corpo.trim()) return '';
    return `<section class="folio mbloco" id="m-p-${p}"><div class="mcab"><h2>${t}</h2><span class="mla">${LA_PARTE[p]}</span></div>${corpo}</section>`;
  }).join('');
}

/* ---------- Tela ---------- */
function renderMissa() {
  lerPreferenciasMissa();
  const el = $('#v-missa');
  if (!MISSAL.la) {
    el.innerHTML = `<div class="stack-lg"><div class="stack"><span class="rubrica">Missal Romano de 1962</span><h1>Abrindo o missal…</h1>
      <p class="muted">${MISSAL.erro ? 'Não foi possível carregar o missal. Abra o app uma vez com internet para guardá-lo no aparelho.' : 'Na primeira vez, o missal é baixado e guardado para funcionar sem internet.'}</p></div></div>`;
    if (!MISSAL.erro) carregarMissal().then(() => { if (!$('#v-missa').hidden) renderMissa(); }).catch(() => { if (!$('#v-missa').hidden) renderMissa(); });
    return;
  }
  const dt = missaDia || HOJE();
  const L = diaLiturgico(dt);
  const op = missasDoDia(dt);
  const chaveDia = iso(dt);
  const idx = mOpcao[chaveDia] != null ? mOpcao[chaveDia] : op.i;
  const sel = op.opcoes[Math.min(idx, op.opcoes.length - 1)];
  const m = obterMissa(sel.f, sel.k);
  const c = contexto(dt, m);
  const temPT = !!MISSAL.pt[m.f][m.kp];
  const hoje = HOJE(), proxDom = add(hoje, (7 - hoje.getDay()) % 7);
  const tituloRito = m.k === 'Quad6-5' ? 'Ação litúrgica da Paixão' : 'Vigília Pascal';
  const corpo = c.triduo ? '' : mModo === 'proprio' ? soProprioHTML(m, c) : MISSAL.ordo.blocos.map(b => blocoHTML(b, m, c)).join('');
  const indice = c.triduo ? [['m-rito', tituloRito]]
    : mModo === 'proprio'
    ? PARTES_PROPRIO.filter(([p]) => p === '_prefacio' || m.p[p]).map(([p, t]) => [`m-p-${p}`, t])
    : [['m-introito', 'Intróito'], ['m-coleta', 'Coleta'], ['m-epistola', 'Epístola'], ['m-evangelho', 'Evangelho'], ['m-ofertorio', 'Ofertório'], ['m-prefacio', 'Prefácio'], ['m-canon', 'Cânon'], ['m-comunhao', 'Comunhão'], ['m-conclusao', 'Conclusão']];

  el.innerHTML = `
  <div class="stack-lg">
    <div class="stack">
      <span class="rubrica">Missal Romano de 1962</span>
      <h1>${esc(L.titulo)}</h1>
      <p class="mlatim"><i>${esc(m.t)}</i></p>
      <div class="row"><span class="pill">${swatch(L.cor)} ${CORES[L.cor]}</span><span class="pill">${CLASSES[m.c] || CLASSES[L.classe]}</span><span class="pill">${dataCurta(dt)}${dt.getFullYear() !== hoje.getFullYear() ? ' de ' + dt.getFullYear() : ''}</span></div>
      ${L.santo ? `<p class="small muted">${esc(L.santo)}</p>` : ''}
    </div>

    <div class="folio stack">
      <div class="mnav">
        <button class="btn" type="button" id="mPrev" aria-label="Dia anterior">‹</button>
        <input type="date" id="mData" value="${iso(dt)}" aria-label="Escolher o dia">
        <button class="btn" type="button" id="mNext" aria-label="Dia seguinte">›</button>
      </div>
      <div class="row">
        <button class="btn" type="button" id="mHoje" ${same(dt, hoje) ? 'disabled' : ''}>Hoje</button>
        <button class="btn" type="button" id="mDom" ${same(dt, proxDom) ? 'disabled' : ''}>${hoje.getDay() === 0 ? 'Domingo' : 'Próximo domingo'}</button>
      </div>
      ${op.opcoes.length > 1 ? `<div class="seg" role="group" aria-label="Escolha da Missa" id="mOp">${op.opcoes.map((o, i) => `<button type="button" data-i="${i}" aria-pressed="${o === sel}">${esc(o.rotulo)}</button>`).join('')}</div>` : ''}
      <div class="seg" role="group" aria-label="Idioma" id="mLang">${[['la', 'Latim'], ['pt', 'Português'], ['ambos', 'Lado a lado']].map(([v, l]) => `<button type="button" data-v="${v}" aria-pressed="${MLANG === v}">${l}</button>`).join('')}</div>
      <div class="row">
        <div class="seg" role="group" aria-label="O que mostrar" id="mModo">${[['completa', 'Missa inteira'], ['proprio', 'Só o Próprio']].map(([v, l]) => `<button type="button" data-v="${v}" aria-pressed="${mModo === v}">${l}</button>`).join('')}</div>
        <button class="btn" type="button" id="mRub" aria-pressed="${mRub}">${mRub ? 'Rubricas: sim' : 'Rubricas: não'}</button>
      </div>
      <p class="small muted">${esc(MISSAL.ordo.aviso)}${temPT ? '' : ' <span class="rub">O Próprio desta Missa ainda está só em latim.</span>'}${c.triduo ? ' Neste dia a liturgia é própria e vem inteira abaixo, na ordem: não se usa o Ordinário.' : ''}</p>
    </div>

    <nav class="chips" aria-label="Partes da Missa">${indice.map(([id, t]) => `<a href="#missa" data-alvo="${id}">${t}</a>`).join('')}</nav>

    ${m.p.Prelude ? `<section class="folio mbloco" id="m-rito"><div class="mcab"><h2>${c.triduo ? tituloRito : 'Antes da Missa'}</h2><span class="mla">Ritus</span></div>${linhasHTML(m.p.Prelude, ptParte(m, 'Prelude'))}</section>` : ''}
    ${corpo}

    ${emCasaHTML(dt)}
  </div>`;

  const ir = d => { missaDia = d; renderMissa(); window.scrollTo(0, 0); };
  $('#mPrev').addEventListener('click', () => ir(add(dt, -1)));
  $('#mNext').addEventListener('click', () => ir(add(dt, 1)));
  $('#mHoje').addEventListener('click', () => ir(hoje));
  $('#mDom').addEventListener('click', () => ir(proxDom));
  $('#mData').addEventListener('change', e => { if (e.target.value) ir(fromIso(e.target.value)); });
  const seg = (id, fn) => { const s = document.getElementById(id); if (s) s.addEventListener('click', e => { const b = e.target.closest('button'); if (b) fn(b); }); };
  seg('mOp', b => { mOpcao[chaveDia] = +b.dataset.i; renderMissa(); });
  seg('mLang', b => { MLANG = b.dataset.v; store.set('missaLang', MLANG); renderMissa(); });
  seg('mModo', b => { mModo = b.dataset.v; store.set('missaModo', mModo); renderMissa(); });
  $('#mRub').addEventListener('click', () => { mRub = !mRub; store.set('missaRub', mRub); renderMissa(); });
  el.querySelector('.chips').addEventListener('click', e => {
    const a = e.target.closest('a[data-alvo]'); if (!a) return;
    e.preventDefault();
    const alvo = document.getElementById(a.dataset.alvo);
    if (alvo) alvo.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  ligarEmCasa(dt);
}

/* ---------- Domingo em casa (o que já existia na aba) ---------- */
function emCasaHTML(dt) {
  const dom = dt.getDay() === 0 ? dt : add(dt, 7 - dt.getDay());
  const ultConf = store.get('ultimaConfissao', '');
  const dias = ultConf ? diff(fromIso(ultConf), HOJE()) : null;
  const domMarc = store.get('domingo:' + iso(dom), {});
  return `
    <div class="folio">
      <span class="rubrica">Domingo em casa · ${dataCurta(dom)}</span>
      <div class="stack">
        <p>Vá à Missa com o seu pároco e, em casa, una-se à liturgia tradicional do dia.</p>
        <div class="check" id="domCheck">
          ${[['missa', 'Missa com o seu pároco.'], ['proprio', 'Ler o Próprio da Missa de 1962 do dia (acima, em "Só o Próprio").'], ['comunhao', 'Comunhão espiritual, sobretudo se não puder comungar sacramentalmente.'], ['terco', 'Terço em família.'], ['evangelho', 'Evangelho do domingo com um bom comentário.']].map(([id, t]) =>
            `<label for="d-${id}"><input type="checkbox" id="d-${id}" data-id="${id}" ${domMarc[id] ? 'checked' : ''}><span class="t">${esc(t)}</span></label>`).join('')}
        </div>
      </div>
    </div>
    <div class="folio">${oracaoHTML('comunhao')}</div>
    <div class="grid2">
      <div class="folio stack">
        <span class="rubrica">Missa tradicional mais próxima</span>
        <label class="field" for="tlm"><span>Local, horário e distância</span>
          <textarea id="tlm" placeholder="Ex.: Capela de ..., 1º domingo do mês, 10h. 2h de viagem.">${esc(store.get('tlm', ''))}</textarea></label>
        <p class="small muted">Programe-se para ir de tempos em tempos e aproveite para se confessar.</p>
      </div>
      <div class="folio stack">
        <span class="rubrica">Confissão</span>
        <label class="field" for="conf"><span>Última confissão</span><input type="date" id="conf" value="${esc(ultConf)}"></label>
        <p class="${dias != null && dias > 30 ? 'rub' : 'muted'}">${dias == null ? 'Anote a data para acompanhar.' : dias === 0 ? 'Hoje. Deo gratias!' : 'Há ' + dias + ' dias.' + (dias > 30 ? ' Que tal marcar com o seu pároco?' : '')}</p>
      </div>
    </div>`;
}
function ligarEmCasa(dt) {
  const dom = dt.getDay() === 0 ? dt : add(dt, 7 - dt.getDay());
  $('#domCheck').addEventListener('change', e => {
    const id = e.target.dataset.id; if (!id) return;
    const m = store.get('domingo:' + iso(dom), {}); m[id] = e.target.checked; store.set('domingo:' + iso(dom), m);
  });
  $('#tlm').addEventListener('input', e => store.set('tlm', e.target.value));
  $('#conf').addEventListener('change', e => { store.set('ultimaConfissao', e.target.value); renderMissa(); });
}
