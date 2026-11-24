"""A validação por outro caminho, sem passar pela lógica do extrator:

1. cada parceria da Virada 2026 relida no PDF de origem pela frase da NOTA DE EMPENHO ("nota de empenho no valor de R$ X"),
   que é outra frase do despacho; o CNPJ tem de aparecer antes do valor, no mesmo documento;
2. a soma das 25 parcerias mais a gestão contra o total da representação (R$ 21,28 milhões, 22 entidades);
3. o número de propostas por lote: o cabeçalho de cada ata contra as linhas contadas da classificação;
4. todo ganhador do edital 002 está na classificação do mesmo lote;
5. o dígito verificador de todo CNPJ;
6. os 4 números que o vídeo diz, refeitos a mão a partir do parcerias.csv: o total da gerenciadora, a média do teto no lote 3,
   as 5 entidades que repetem de 2025 e as 4 entidades com o mesmo telefone.

Uso:  python ferramentas/validacao_independente.py   (grava resultados/VALIDACAO.json; sai com erro se algo não bater)
"""
import csv
import json
import re
import sys
from pathlib import Path

import pypdf

RAIZ = Path(__file__).resolve().parents[1]
DOC = RAIZ / "dados" / "documentos" / "seme-2026"


def texto(p):
    return re.sub(r"\s+", " ", " ".join(pg.extract_text() or "" for pg in pypdf.PdfReader(p).pages))


def br(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def cnpj_valido(c):
    if len(c) != 14 or not c.isdigit():
        return False
    def dv(base, pesos):
        s = sum(int(a) * b for a, b in zip(base, pesos)) % 11
        return "0" if s < 2 else str(11 - s)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    p2 = [6] + p1
    return c[12] == dv(c[:12], p1) and c[13] == dv(c[:13], p2)


def checar():
    ok, erros, avisos = [], [], []
    parc = list(csv.DictReader(open(RAIZ / "dados" / "parcerias.csv", encoding="utf-8")))
    for p in parc:
        p["valor"] = float(p["valor"])
    comp = json.loads((RAIZ / "dados" / "complementos.json").read_text(encoding="utf-8"))
    v26 = [p for p in parc if p["edital"] == "002/SEME/2026"]

    # 1. a nota de empenho
    textos = {}
    for p in v26:
        f = DOC / p["origem"]
        if not f.exists():
            erros.append(f"documento de origem não achado: {p['origem']}")
            continue
        t = textos.setdefault(p["origem"], texto(f))
        tsp = re.sub(r"\s", "", t)
        cnpj_fmt = f"{p['cnpj'][:2]}.{p['cnpj'][2:5]}.{p['cnpj'][5:8]}/{p['cnpj'][8:12]}-{p['cnpj'][12:]}"
        alvo = f"notadeempenhonovalordeR${br(p['valor'])}"
        i = tsp.find(alvo)
        if i >= 0 and cnpj_fmt in tsp[:i]:
            ok.append(f"empenho {p['cnpj']} lote {p['lote']} R$ {br(p['valor'])}")
        elif f"R${br(p['valor'])}" in tsp and cnpj_fmt in tsp:
            avisos.append(f"sem a frase do empenho, conferido só pelo repasse: {p['cnpj']} lote {p['lote']} R$ {br(p['valor'])} ({p['origem']})")
            ok.append(f"repasse {p['cnpj']} lote {p['lote']} R$ {br(p['valor'])}")
        else:
            erros.append(f"valor não achado no documento: {p['cnpj']} R$ {br(p['valor'])} em {p['origem']}")

    # 2. o total contra a representação
    g = comp["gestao_virada_2026"]
    total = round(sum(p["valor"] for p in v26) + g["valor"], 2)
    entidades = len({p["cnpj"] for p in v26} | {g["entidade_cnpj"]})
    (ok if total == 21282840.72 else erros).append(f"total {total} × representação 21.282.840,72")
    (ok if entidades == 22 else erros).append(f"entidades {entidades} × representação 22")
    (ok if len(v26) == 25 else erros).append(f"parcerias do edital 002: {len(v26)} (esperado 25)")

    # 3. propostas: cabeçalho da ata × linhas contadas
    cls = list(csv.DictReader(open(RAIZ / "dados" / "classificacao_002_2026.csv", encoding="utf-8")))
    t13 = texto(DOC / "ATA DE REUNIÃO RESULTADO PRELIM PARCIAL LOTE 1 E 3.pdf")
    t2 = texto(DOC / "ATA DE REUNIÃO RESULTADO PRELIM PARCIAL LOTE 2.pdf")
    cab = {"2": int(re.search(r"LOTE 02 - \((\d+) Propostas\)", t2).group(1)),
           "3": int(re.search(r"LOTE 03 - \((\d+) Propostas\)", t13).group(1)), "1": 1}
    for lote, n in cab.items():
        contadas = sum(1 for x in cls if x["lote"] == lote)
        (ok if contadas == n == comp["propostas_002_2026"][lote]["propostas"] else erros).append(
            f"lote {lote}: ata {n} × linhas {contadas} × complementos {comp['propostas_002_2026'][lote]['propostas']}")

    # 4. todo ganhador está classificado no mesmo lote
    classif = {(x["lote"], x["cnpj"]) for x in cls if x["desclassificada"] == "False"}
    fora = [f"{p['cnpj']} lote {p['lote']}" for p in v26 if (p["lote"], p["cnpj"]) not in classif]
    (erros if fora else ok).append(f"ganhadores fora da classificação: {fora or 'nenhum'}")

    # 5. dígito verificador
    todos = {p["cnpj"] for p in parc} | {x["cnpj"] for x in cls} | {g["entidade_cnpj"]}
    ruins = sorted(c for c in todos if not cnpj_valido(c))
    (erros if ruins else ok).append(f"CNPJ com dígito errado: {ruins or 'nenhum'} ({len(todos)} conferidos)")

    # 6. os números do vídeo, a mão
    imelc = sum(p["valor"] for p in parc if p["cnpj"] == g["entidade_cnpj"] and p["ano"] == "2026") + g["valor"]
    resumo = json.loads((RAIZ / "resultados" / "RESUMO.json").read_text(encoding="utf-8"))
    (ok if round(imelc, 2) == resumo["gerenciadora"]["total_2026"] else erros).append(f"gerenciadora {imelc:.2f} × análise {resumo['gerenciadora']['total_2026']}")
    l3 = [p["valor"] / 1672857.14 for p in v26 if p["lote"] == "3"]
    m3 = round(100 * sum(l3) / len(l3), 2)
    (ok if m3 == resumo["virada_2026"]["por_lote"]["3"]["pct_do_teto_media"] else erros).append(f"lote 3 média do teto {m3} × análise")
    rep = {p["cnpj"] for p in parc if p["edital"] == "001/SEME/2025"} & ({p["cnpj"] for p in v26} | {g["entidade_cnpj"]})
    (ok if len(rep) == len(resumo["repetem_de_2025"]["repetem"]) == 5 else erros).append(f"repetem de 2025: {len(rep)}")
    cad = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in (RAIZ / "dados" / "cnpj").glob("*.json")}
    tel = sorted(c for c, d in cad.items() if (d.get("ddd_telefone_1") or "").strip() == "1124408477")
    (ok if len(tel) == 4 else erros).append(f"mesmo telefone: {len(tel)} entidades")
    return {"conferidos": len(ok), "erros": erros, "avisos": avisos, "ok": ok}


if __name__ == "__main__":
    r = checar()
    (RAIZ / "resultados" / "VALIDACAO.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{r['conferidos']} conferidos, {len(r['erros'])} erros, {len(r['avisos'])} avisos")
    for e in r["erros"]:
        print("  ERRO", e)
    for a in r["avisos"]:
        print("  aviso", a)
    sys.exit(1 if r["erros"] else 0)
