"""Os gráficos do projeto, 1920x1080, só a partir de resultados/RESUMO.json.

Uso:  python ferramentas/graficos.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "resultados" / "figuras"
REPO = "github.com/Gabriel-Alexandre/virada-esportiva-sp-2026"
COR = {"destaque": "#D9822B", "base": "#5B7DA6", "cinza": "#B8B8B8", "texto": "#1F1F1F", "verde": "#2E7D5B", "vermelho": "#B23A3A"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 22, "axes.edgecolor": "#BBBBBB",
                     "axes.spines.top": False, "axes.spines.right": False, "text.parse_math": False})
CURTO = {
    "INSTITUTO MOVIMENTO AO ESPORTE, LAZER E CULTURA": "IMELC (a gerenciadora)",
    "ASSOCIACAO ESPORTIVA E CULTURAL CNB": "Associação CNB",
    "INSTITUTO PANGEA DE ACAO CULTURAL E ESPORTIVA - IPACE": "Instituto Pangea (IPACE)",
    "SOCIEDADE ESPORTIVA RECREATIVA E CULTURAL SANTA MARIA": "SERC Santa Maria",
    "FEDERACAO NACIONAL DAS ENTIDADES DO TERCEIRO SETOR": "Fenats",
    "INSTITUTO SOU MAIS JOVEM": "Instituto Sou Mais Jovem",
    "ASSOCIACAO CAMINHO DO ESPORTE - ACE": "Associação Caminho do Esporte",
    "INSTITUTO PARCEIROS DA CIDADANIA": "Instituto Parceiros da Cidadania",
    "FEDERACAO UNIVERSITARIA PAULISTA DE ESPORTES": "Federação Universitária Paulista (FUPE)",
    "INSTITUTO NACIONAL DE DESENVOLVIMENTO ECONOMICO EDUCACIONAL CULTURAL E": "Instituto Nacional de Desenvolvimento (INDES)",
    "INSTITUTO CULTURAL DO TRABALHO, ESPORTE E EDUCACAO": "Instituto Cultural do Trabalho (ICTE)",
    "ASSOCIACAO PAULISTA DE DESPORTOS": "Associação Paulista de Desportos",
    "FEDERACAO DOS DESPORTOS NO ESTADO DE SAO PAULO": "Federação dos Desportos de SP",
    "FEDERACAO PROGRAMA CIDADAO": "Federação Programa Cidadão",
    "LIGA NACIONAL DE TAEKWONDO": "Liga Nacional de Taekwondo",
    "ASSOCIACAO UNIDOS JARDIM IPORANGA": "Associação Unidos Jardim Iporanga",
}
PROG = {"Virada Esportiva 2026 (as arenas)": "Virada 2026", "Virada Esportiva 2025": "Virada 2025",
        "Colaboração Estrutural / Virada Esportiva 2026 (a gestão)": "gestão da Virada 2026"}


def curto(n):
    for k, v in CURTO.items():
        if n.startswith(k):
            return v
    return n.title()[:38]


def mi(v):
    return f"R$ {v / 1e6:.2f} mi".replace(".", ",")


def mil(v):
    return f"R$ {v / 1e3:,.0f} mil".replace(",", ".")


def figura(titulo, subtitulo):
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor="white")
    fig.text(0.05, 0.93, titulo, fontsize=44, weight="bold", color=COR["texto"], va="top")
    fig.text(0.05, 0.845, subtitulo, fontsize=24, color="#444444", va="top")
    return fig


def rodape(fig, fonte):
    fig.text(0.05, 0.035, f"Fonte: {fonte}", fontsize=16, color="#555555")
    fig.text(0.05, 0.008, f"{REPO} · conta feita com o auxílio do Claude (IA)", fontsize=15, color="#777777")


SEME = "Secretaria de Esportes de SP (SEME), edital 002/SEME/2026: homologações e atas, lidas em 24/11/2026"


def g01(r):
    v = r["virada_2026"]
    ents = v["por_entidade"]
    top, resto = ents[:9], ents[9:]
    barras = [(curto(e["entidade"]), e["valor"], COR["destaque"] if e["cnpj"] == r["gerenciadora"]["cnpj"] else COR["base"]) for e in top]
    barras.append((f"as outras {len(resto)} entidades", sum(e["valor"] for e in resto), COR["cinza"]))
    fig = figura(f"Para onde foram os {mi(v['total'])}", f"Virada Esportiva 2026: {v['entidades']} entidades, {v['contratos']} contratos")
    ax = fig.add_axes([0.36, 0.12, 0.56, 0.68])
    for i, (n, val, cor) in enumerate(reversed(barras)):
        ax.barh(i, val, color=cor, height=0.62)
        ax.text(val + 8e4, i, mi(val), va="center", fontsize=21, color=COR["texto"])
        fig.text(0.35, 0.12 + (i + 0.5) * 0.68 / len(barras), n, ha="right", va="center", fontsize=21, color=COR["texto"],
                 weight="bold" if cor == COR["destaque"] else "normal")
    ax.set_xlim(0, max(b[1] for b in barras) * 1.22); ax.set_ylim(-0.5, len(barras) - 0.5); ax.set_yticks([]); ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    rodape(fig, SEME + "; a gestão, pela representação")
    fig.savefig(FIG / "g01_para_onde_foram_os_21_milhoes.png"); plt.close(fig)


def g02(r):
    pl = r["virada_2026"]["por_lote"]
    cl = r["classificacao_002"]["por_lote"]
    linhas = [("Gestão do evento", 1, 1, 1),
              ("Lote 1 (até R$ 45 mil)", pl["1"]["vagas"], pl["1"]["propostas"], cl["1"]["com_parceria"]),
              ("Lote 2 (até R$ 250 mil)", pl["2"]["vagas"], pl["2"]["propostas"], cl["2"]["com_parceria"]),
              ("Lote 3 (até R$ 1,67 mi)", pl["3"]["vagas"], pl["3"]["propostas"], cl["3"]["com_parceria"])]
    fig = figura("Quanta concorrência teve?", "Vagas do edital, propostas recebidas e parcerias assinadas")
    ax = fig.add_axes([0.08, 0.14, 0.86, 0.58])
    w = 0.26
    for i, (n, vagas, props, ganhou) in enumerate(linhas):
        for k, (val, cor, rot) in enumerate([(vagas, COR["cinza"], "vagas"), (props, COR["base"], "propostas"), (ganhou, COR["destaque"], "assinadas")]):
            ax.bar(i + (k - 1) * w, val, w * 0.92, color=cor)
            ax.text(i + (k - 1) * w, val + 0.35, str(val), ha="center", fontsize=24, weight="bold", color=COR["texto"])
    ax.set_xticks(range(len(linhas))); ax.set_xticklabels([l[0] for l in linhas], fontsize=22); ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    for k, (cor, rot) in enumerate([(COR["cinza"], "vagas no edital"), (COR["base"], "propostas"), (COR["destaque"], "parcerias assinadas")]):
        fig.text(0.40 + k * 0.19, 0.78, "■", color=cor, fontsize=30, va="center"); fig.text(0.425 + k * 0.19, 0.78, rot, fontsize=20, va="center")
    rodape(fig, SEME + "; gestão: representação")
    fig.savefig(FIG / "g02_concorrencia_por_lote.png"); plt.close(fig)


def g03(r):
    pl = r["virada_2026"]["por_lote"]
    fig = figura("Cada entidade pediu quanto do teto?", "Valor de cada parceria em % do teto do lote no edital")
    ax = fig.add_axes([0.10, 0.14, 0.84, 0.62])
    import csv
    parc = [p for p in csv.DictReader(open(RAIZ / "dados" / "parcerias.csv", encoding="utf-8")) if p["edital"] == "002/SEME/2026"]
    for i, lote in enumerate(("1", "2", "3")):
        teto = pl[lote]["teto_por_projeto"]
        xs = sorted(100 * float(p["valor"]) / teto for p in parc if p["lote"] == lote)
        ax.scatter(xs, [i] * len(xs), s=420, color=COR["base"], alpha=0.75, edgecolor="white", linewidth=2, zorder=3)
        ax.text(95.35, i + 0.28, f"lote {lote}: média {pl[lote]['pct_do_teto_media']:.1f}%".replace(".", ","), fontsize=22, color=COR["texto"])
    gz = r["virada_2026"]
    ax.scatter([gz["gestao_pct_do_teto"]], [3], s=520, color=COR["destaque"], zorder=3)
    ax.text(95.35, 3.28, f"gestão: {gz['gestao_pct_do_teto']:.1f}%".replace(".", ","), fontsize=22, color=COR["texto"])
    ax.axvline(100, color=COR["vermelho"], lw=3); ax.text(99.95, 3.75, "teto", ha="right", fontsize=22, color=COR["vermelho"])
    ax.set_xlim(95.2, 100.4); ax.set_ylim(-0.6, 4.0); ax.set_yticks([])
    ax.set_xticks([96, 97, 98, 99, 100]); ax.set_xticklabels(["96%", "97%", "98%", "99%", "100%"], fontsize=20)
    rodape(fig, SEME + "; tetos: editais 002 e 009")
    fig.savefig(FIG / "g03_valor_contra_o_teto.png"); plt.close(fig)


def g04(r):
    gz = r["gerenciadora"]
    nomes = {"009/SEME/2026": "Gestão da Virada\n(edital 009)", "002/SEME/2026": "Uma arena da Virada\n(edital 002, lote 3)",
             "005/SEME/2026": "Agita + Férias 2026\n(edital 005)"}
    cs = sorted(gz["contratos_2026"], key=lambda c: -c["valor"])
    fig = figura(f"A gerenciadora levou {mi(gz['total_2026'])} em 2026", "Instituto Movimento ao Esporte, Lazer e Cultura (IMELC): os 3 contratos com a Secretaria de Esportes")
    ax = fig.add_axes([0.08, 0.17, 0.86, 0.57])
    for i, c in enumerate(cs):
        ax.bar(i, c["valor"], 0.6, color=COR["destaque"] if "009" in c["edital"] or "002" in c["edital"] else COR["base"])
        ax.text(i, c["valor"] + 1.2e5, mi(c["valor"]), ha="center", fontsize=28, weight="bold", color=COR["texto"])
    ax.set_xticks(range(len(cs))); ax.set_xticklabels([nomes[c["edital"]] for c in cs], fontsize=22); ax.set_yticks([])
    ax.spines["left"].set_visible(False); ax.set_ylim(0, max(c["valor"] for c in cs) * 1.2)
    rodape(fig, "SEME, homologações dos editais 002 e 005/SEME/2026; a gestão (009) pela representação do vice-prefeito")
    fig.savefig(FIG / "g04_gerenciadora_13_milhoes.png"); plt.close(fig)


def g05(r):
    rep = r["repetem_de_2025"]["repetem"]
    fig = figura(f"{len(rep)} das {r['repetem_de_2025']['virada_2025_lotes_1_e_3_entidades']} entidades de 2025 voltaram em 2026",
                 "Virada Esportiva: o que cada uma recebeu em 2025 (lotes 1 e 3) e em 2026")
    ax = fig.add_axes([0.40, 0.12, 0.52, 0.66])
    h = 0.36
    n = len(rep)
    for i, e in enumerate(rep):
        y = n - 1 - i
        for k, (val, cor, ano) in enumerate([(e["valor_2025"], COR["cinza"], "2025"), (e["valor_2026"], COR["base"], "2026")]):
            yy = y + (h / 2 if k == 0 else -h / 2)
            ax.barh(yy, val, h * 0.9, color=cor)
            ax.text(val + 3e4, yy, f"{ano}: {mi(val) if val >= 1e6 else mil(val)}", va="center", fontsize=19,
                    weight="bold" if k else "normal", color=COR["texto"])
        fig.text(0.39, 0.12 + (y + 0.5) * 0.66 / n, curto(e["entidade"]), ha="right", va="center", fontsize=22, color=COR["texto"])
    ax.set_ylim(-0.6, n - 0.4); ax.set_xlim(0, 2.6e6); ax.set_yticks([]); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
    rodape(fig, "SEME, homologações dos editais 001/SEME/2025 e 002/SEME/2026 (página de chamamentos, 24/11/2026)")
    fig.savefig(FIG / "g05_repetem_de_2025.png"); plt.close(fig)


def g06(r):
    c = r["cadastro"]
    tel, end = c["mesmo_telefone"][0], c["mesmo_endereco"][0]
    fig = figura("O que o cadastro das entidades tem em comum", "Receita Federal: telefone e endereço declarados no CNPJ")
    for col, (gr, titulo) in enumerate([(tel, "Mesmo telefone: (11) 2440-8477"), (end, "Mesmo endereço: Al. Franca, 267")]):
        x0 = 0.05 + col * 0.47
        fig.text(x0, 0.74, titulo, fontsize=30, weight="bold", color=COR["destaque"])
        for i, e in enumerate(gr["entidades"]):
            y = 0.64 - i * 0.12
            fig.text(x0, y, curto(e["entidade"]), fontsize=23, color=COR["texto"], weight="bold")
            fig.text(x0, y - 0.045, f"{mi(e['valor_seme_2025_2026'])} · {', '.join(PROG.get(p, p) for p in e['programas'])}", fontsize=18, color="#555555")
        fig.text(x0, 0.14, f"juntas: {mi(gr['valor_somado'])} em 2025 e 2026", fontsize=24, color=COR["texto"])
    rodape(fig, "Receita Federal, cadastro de CNPJ (pela BrasilAPI, 24/11/2026); valores das homologações da SEME de 2025 e 2026")
    fig.savefig(FIG / "g06_cadastro_em_comum.png"); plt.close(fig)


def g07(r):
    cp = r["classificacao_002"]["lote_2_complementar"]
    fig = figura("As 2 vagas a mais do lote 2", "O edital previa 15 projetos; saíram 17, os 2 últimos dias antes do evento")
    marcos = [("23/04", "as 20 propostas do lote 2 entregues", COR["base"]),
              ("24/08", "15 parcerias homologadas", COR["base"]),
              ("11/09", "complementar: a 17ª colocada (80 pontos), " + mil(cp["parcerias"][1]["valor"]), COR["destaque"]),
              ("15/09", "complementar: a 15ª colocada (89 pontos), " + mil(cp["parcerias"][0]["valor"]), COR["destaque"]),
              ("19 e 20/09", "a Virada Esportiva", COR["verde"])]
    x = 0.12
    fig.add_artist(plt.Line2D([x, x], [0.20, 0.72], color="#999999", lw=4, transform=fig.transFigure))
    for k, (data, rot, cor) in enumerate(marcos):
        y = 0.72 - k * 0.13
        fig.add_artist(plt.Circle((x, y), 0.012, color=cor, transform=fig.transFigure, zorder=3))
        fig.text(x + 0.03, y, data, fontsize=28, weight="bold", va="center", color=COR["texto"])
        fig.text(x + 0.20, y, rot, fontsize=26, va="center", color=COR["texto"])
    fig.text(0.05, 0.10, f"As 2 levaram {mil(cp['valor'])}; o lote 1 teve 1 projeto de 12 e sobraram {mil(cp['sobra_do_lote_1'])}",
             fontsize=24, color=COR["texto"])
    rodape(fig, SEME + " (despachos 164875844 e 165038206)")
    fig.savefig(FIG / "g07_lote_2_complementar.png"); plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    r = json.loads((RAIZ / "resultados" / "RESUMO.json").read_text(encoding="utf-8"))
    for g in (g01, g02, g03, g04, g05, g06, g07):
        g(r)
    print(f"{len(list(FIG.glob('*.png')))} figuras em {FIG}")


if __name__ == "__main__":
    main()
