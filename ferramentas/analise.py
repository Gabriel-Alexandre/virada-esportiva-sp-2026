"""A análise: para onde foram os R$ 21 milhões da Virada Esportiva 2026, pelos documentos da própria Prefeitura.

Entradas: dados/parcerias.csv (extrair_parcerias.py), dados/complementos.json (a gestão, os tetos e as propostas, com a fonte de
cada um) e dados/cnpj/*.json (consultar_cnpj.py). Saída: resultados/RESUMO.json e o resumo no terminal.

⛔ Só dado de entidade. Nome de pessoa do quadro de sócios não entra aqui.
Uso: python ferramentas/analise.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
RES = RAIZ / "resultados"


def carregar():
    parcerias = list(csv.DictReader(open(DADOS / "parcerias.csv", encoding="utf-8")))
    for p in parcerias:
        p["valor"] = float(p["valor"])
        p["ano"] = int(p["ano"])
    comp = json.loads((DADOS / "complementos.json").read_text(encoding="utf-8"))
    cad = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in (DADOS / "cnpj").glob("*.json")}
    return parcerias, comp, cad


def nome(cad, cnpj):
    return cad[cnpj]["razao_social"] if cnpj in cad else cnpj


def endereco(d):
    partes = [d.get("descricao_tipo_de_logradouro") or "", d.get("logradouro") or ""]
    return f"{' '.join(p for p in partes if p)}, {d.get('numero') or ''} · {d.get('municipio') or ''}"


def rotulo(c):
    return "gestão" if c["lote"] == "gestão" else "lote " + c["lote"]


def analisar():
    parcerias, comp, cad = carregar()
    g = comp["gestao_virada_2026"]
    ed = comp["edital_002_2026"]
    v26 = [p for p in parcerias if p["edital"] == "002/SEME/2026"]
    gestao = {"ano": 2026, "edital": g["edital"], "entidade": "", "cnpj": g["entidade_cnpj"], "lote": "gestão", "valor": g["valor"]}
    contratos = v26 + [gestao]

    # 1. o total e por lote
    por_lote = {}
    for lote in ("1", "2", "3"):
        ps = [p for p in v26 if p["lote"] == lote]
        teto = ed["lotes"][lote]["teto_por_projeto"]
        pcts = [p["valor"] / teto for p in ps]
        por_lote[lote] = {
            "parcerias": len(ps), "vagas": ed["lotes"][lote]["vagas"], "valor": round(sum(p["valor"] for p in ps), 2),
            "teto_por_projeto": teto,
            "propostas": comp["propostas_002_2026"][lote]["propostas"],
            "desclassificadas": comp["propostas_002_2026"][lote]["desclassificadas"],
            "pct_do_teto_media": round(100 * sum(pcts) / len(pcts), 2),
            "pct_do_teto_minimo": round(100 * min(pcts), 2),
            "pct_do_teto_maximo": round(100 * max(pcts), 2),
            "acima_de_95pct_do_teto": sum(1 for x in pcts if x >= 0.95),
        }
    total_002 = round(sum(p["valor"] for p in v26), 2)
    total = round(total_002 + g["valor"], 2)

    # 2. por entidade
    por_ent = defaultdict(lambda: {"valor": 0.0, "contratos": []})
    for c in contratos:
        e = por_ent[c["cnpj"]]
        e["valor"] += c["valor"]
        e["contratos"].append(f"{rotulo(c)}: {c['valor']:.2f}")
    entidades = sorted(({"cnpj": k, "entidade": nome(cad, k), "valor": round(v["valor"], 2), "contratos": v["contratos"],
                         "pct_do_total": round(100 * v["valor"] / total, 2)} for k, v in por_ent.items()), key=lambda e: -e["valor"])
    top7 = entidades[:7]

    # 3. a gerenciadora em outros editais de 2026 e em 2025
    imelc = g["entidade_cnpj"]
    imelc_2026 = [{"edital": p["edital"], "programa": comp["editais"].get(p["edital"], ""), "lote": p["lote"], "valor": p["valor"]}
                  for p in parcerias if p["cnpj"] == imelc and p["ano"] == 2026]
    imelc_2026.append({"edital": g["edital"], "programa": comp["editais"][g["edital"]], "lote": "gestão", "valor": g["valor"]})
    imelc_total = round(sum(x["valor"] for x in imelc_2026), 2)

    # 4. quem repete da Virada 2025 (os lotes 1 e 3, que têm homologação com valor na página de 2025)
    v25 = [p for p in parcerias if p["edital"] == "001/SEME/2025"]
    cnpj_v25 = {p["cnpj"] for p in v25}
    cnpj_v26 = {c["cnpj"] for c in contratos}

    def soma(lista, c):
        return round(sum(x["valor"] for x in lista if x["cnpj"] == c), 2)

    repetem = [{"cnpj": c, "entidade": nome(cad, c), "valor_2025": soma(v25, c), "valor_2026": soma(contratos, c)}
               for c in sorted(cnpj_v25 & cnpj_v26, key=lambda c: -soma(contratos, c))]

    # 5. o cadastro público das entidades
    todas = sorted({p["cnpj"] for p in parcerias} | {imelc})
    fora_da_capital = [{"cnpj": c, "entidade": nome(cad, c), "municipio": cad[c].get("municipio"), "valor_2026": soma(contratos, c)}
                       for c in sorted(cnpj_v26) if c in cad and cad[c].get("municipio") != "SAO PAULO"]
    abertura = sorted(({"cnpj": c, "entidade": nome(cad, c), "abertura": cad[c].get("data_inicio_atividade")}
                       for c in cnpj_v26 if c in cad), key=lambda x: x["abertura"])
    situacao = defaultdict(int)
    for c in cnpj_v26:
        if c in cad:
            situacao[cad[c].get("descricao_situacao_cadastral")] += 1

    def programas(c):
        ps = {comp["editais"].get(p["edital"], p["edital"]) for p in parcerias if p["cnpj"] == c}
        if c == imelc:
            ps.add(comp["editais"][g["edital"]])
        return sorted(ps)

    def valor_seme(c):
        return round(sum(p["valor"] for p in parcerias if p["cnpj"] == c) + (g["valor"] if c == imelc else 0), 2)

    def grupos(chave):
        gr = defaultdict(list)
        for c in todas:
            if c in cad and chave(cad[c]):
                gr[chave(cad[c])].append(c)
        out = []
        for k, cs in gr.items():
            if len(cs) < 2:
                continue
            ents = [{"cnpj": c, "entidade": nome(cad, c), "valor_seme_2025_2026": valor_seme(c), "programas": programas(c)} for c in cs]
            mesmo_lote = sorted({f"{p['edital']} lote {p['lote']}" for p in parcerias if p["cnpj"] in cs
                                 for q in parcerias if q["cnpj"] in cs and q["cnpj"] != p["cnpj"]
                                 and q["edital"] == p["edital"] and q["lote"] == p["lote"]})
            out.append({"chave": k, "entidades": ents, "na_virada_2026": sum(1 for c in cs if c in cnpj_v26),
                        "valor_somado": round(sum(e["valor_seme_2025_2026"] for e in ents), 2),
                        "ganharam_no_mesmo_lote": mesmo_lote})
        return sorted(out, key=lambda x: (-len(x["entidades"]), -x["valor_somado"]))

    mesmo_telefone = grupos(lambda d: (d.get("ddd_telefone_1") or "").strip() or None)
    mesmo_endereco = grupos(lambda d: endereco(d) if d.get("logradouro") else None)

    # 6. a classificação: quem se inscreveu, quem levou e quem ficou de fora
    cls = list(csv.DictReader(open(DADOS / "classificacao_002_2026.csv", encoding="utf-8")))
    ganhou = {(p["lote"], p["cnpj"]) for p in v26}
    classificacao = {}
    for lote in ("1", "2", "3"):
        ls = [x for x in cls if x["lote"] == lote]
        ok = [x for x in ls if x["desclassificada"] == "False"]
        classificacao[lote] = {
            "propostas": len(ls), "classificadas": len(ok), "com_parceria": sum(1 for x in ls if (lote, x["cnpj"]) in ganhou),
            "classificadas_sem_parceria": [{"posicao": int(x["posicao"]), "pontos": int(x["pontos"]), "cnpj": x["cnpj"],
                                            "entidade": nome(cad, x["cnpj"]) if x["cnpj"] in cad else x["arena_e_entidade"]}
                                           for x in ok if (lote, x["cnpj"]) not in ganhou],
            "ultima_posicao_com_parceria": max((int(x["posicao"]) for x in ls if (lote, x["cnpj"]) in ganhou), default=None),
        }
    proponentes = {x["cnpj"] for x in cls}
    nao_desclass = {x["cnpj"] for x in cls if x["desclassificada"] == "False"}
    ganhadores_002 = {p["cnpj"] for p in v26}
    complementares = [{"cnpj": p["cnpj"], "entidade": nome(cad, p["cnpj"]), "valor": p["valor"], "origem": p["origem"],
                       "posicao": next(int(x["posicao"]) for x in cls if x["lote"] == "2" and x["cnpj"] == p["cnpj"]),
                       "pontos": next(int(x["pontos"]) for x in cls if x["lote"] == "2" and x["cnpj"] == p["cnpj"])}
                      for p in v26 if p["origem"] in comp.get("lote_2_complementar", {}).get("documentos", [])]

    return {
        "classificacao_002": {
            "por_lote": classificacao,
            "entidades_que_se_inscreveram": len(proponentes),
            "entidades_nao_desclassificadas": len(nao_desclass),
            "entidades_com_parceria": len(ganhadores_002),
            "pct_das_inscritas_com_parceria": round(100 * len(ganhadores_002) / len(proponentes), 1),
            "pct_das_nao_desclassificadas_com_parceria": round(100 * len(ganhadores_002) / len(nao_desclass), 1),
            "lote_2_complementar": {"parcerias": complementares, "valor": round(sum(c["valor"] for c in complementares), 2),
                                    "datas": comp.get("lote_2_complementar", {}).get("datas"),
                                    "sobra_do_lote_1": round(ed["lotes"]["1"]["teto_por_projeto"] * ed["lotes"]["1"]["vagas"] - por_lote["1"]["valor"], 2),
                                    "evento": comp.get("lote_2_complementar", {}).get("evento")},
        },
        "virada_2026": {
            "total": total, "entidades": len(cnpj_v26), "contratos": len(contratos),
            "arenas_edital_002": total_002, "gestao_edital_009": g["valor"],
            "gestao_pct_do_total": round(100 * g["valor"] / total, 2),
            "gestao_pct_do_teto": round(100 * g["valor"] / g["teto_do_edital"], 2),
            "gestao_propostas": g["propostas"],
            "orcamento_edital_002": ed["orcamento"],
            "orcamento_002_nao_usado": round(ed["orcamento"] - total_002, 2),
            "propostas_total_002": sum(x["propostas"] for x in por_lote.values()),
            "vagas_total_002": sum(x["vagas"] for x in por_lote.values()),
            "por_lote": por_lote,
            "entidades_com_2_contratos": [e for e in entidades if len(e["contratos"]) > 1],
            "top7": top7, "top7_pct": round(sum(e["pct_do_total"] for e in top7), 2),
            "por_entidade": entidades,
        },
        "gerenciadora": {"cnpj": imelc, "entidade": nome(cad, imelc), "contratos_2026": imelc_2026, "total_2026": imelc_total,
                         "virada_2025": [{"edital": p["edital"], "lote": p["lote"], "valor": p["valor"]}
                                         for p in parcerias if p["cnpj"] == imelc and p["ano"] == 2025]},
        "repetem_de_2025": {"virada_2025_lotes_1_e_3_entidades": len(cnpj_v25),
                            "virada_2025_lotes_1_e_3_total": round(sum(p["valor"] for p in v25), 2),
                            "repetem": repetem,
                            "valor_2026_dos_que_repetem": round(sum(e["valor_2026"] for e in repetem), 2)},
        "cadastro": {"situacao": dict(situacao), "fora_da_capital": fora_da_capital,
                     "abertas_desde_2020": [a for a in abertura if a["abertura"] >= "2020-01-01"],
                     "mais_antiga": abertura[0], "mais_nova": abertura[-1],
                     "mesmo_telefone": mesmo_telefone, "mesmo_endereco": mesmo_endereco},
        "fontes": {"parcerias": "dados/parcerias.csv", "complementos": "dados/complementos.json",
                   "cadastro": "dados/cnpj/ (Receita Federal, pela BrasilAPI)"},
    }


def main():
    r = analisar()
    RES.mkdir(exist_ok=True)
    (RES / "RESUMO.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    v = r["virada_2026"]
    print(f"Virada 2026: R$ {v['total']:,.2f} em {v['entidades']} entidades ({v['contratos']} contratos)")
    print(f"  arenas (002): R$ {v['arenas_edital_002']:,.2f} · gestão (009): R$ {v['gestao_edital_009']:,.2f} "
          f"({v['gestao_pct_do_total']}% do total, {v['gestao_pct_do_teto']}% do teto, {v['gestao_propostas']} proposta)")
    for k, lt in v["por_lote"].items():
        print(f"  lote {k}: {lt['parcerias']} de {lt['vagas']} vagas, {lt['propostas']} propostas, R$ {lt['valor']:,.2f}, "
              f"média {lt['pct_do_teto_media']}% do teto (mín {lt['pct_do_teto_minimo']}%), {lt['acima_de_95pct_do_teto']} acima de 95%")
    print(f"  top 7: {v['top7_pct']}% do total · com 2 contratos: {[e['entidade'][:25] for e in v['entidades_com_2_contratos']]}")
    gz = r["gerenciadora"]
    print(f"Gerenciadora em 2026: R$ {gz['total_2026']:,.2f} em {len(gz['contratos_2026'])} contratos; 2025: {gz['virada_2025']}")
    rp = r["repetem_de_2025"]
    print(f"Repetem de 2025 ({len(rp['repetem'])} de {rp['virada_2025_lotes_1_e_3_entidades']}):",
          [(e['entidade'][:25], e['valor_2025'], e['valor_2026']) for e in rp["repetem"]])
    c = r["cadastro"]
    print("Situação:", c["situacao"], "· mais nova:", c["mais_nova"], "· mais antiga:", c["mais_antiga"])
    print("Fora da capital:", [(e['entidade'][:30], e['municipio']) for e in c["fora_da_capital"]])
    for nomeg in ("mesmo_telefone", "mesmo_endereco"):
        for gr in c[nomeg]:
            print(f"{nomeg}: {gr['chave']} · {len(gr['entidades'])} entidades · {gr['na_virada_2026']} na Virada 2026 · "
                  f"R$ {gr['valor_somado']:,.2f} · mesmo lote: {gr['ganharam_no_mesmo_lote']}")


if __name__ == "__main__":
    main()
