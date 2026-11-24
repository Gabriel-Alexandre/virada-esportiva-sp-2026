"""Extrai as parcerias (termos de fomento e de colaboração) das homologações publicadas pela Secretaria Municipal de Esportes
e Lazer de São Paulo (SEME): a página de chamamentos de 2025 e de 2026 (o texto de cada despacho está na própria página) e os
PDFs da Virada Esportiva 2026 (dados/documentos/seme-2026/).

Regra: cada "repasse público de R$ X" num despacho de homologação é uma parceria. Para cada um, o extrator olha para trás,
no mesmo despacho, e pega o último CNPJ, o nome que vem antes dele, o lote e o edital. Repetições (o mesmo despacho na página
e no PDF) saem pela chave (ano, edital, CNPJ, lote, valor).

Saída: dados/parcerias.csv. Uso: python ferramentas/extrair_parcerias.py
"""
import csv
import hashlib
import json
import re
from pathlib import Path

import pypdf

RAIZ = Path(__file__).resolve().parents[1]
DOC = RAIZ / "dados" / "documentos"
CAP = RAIZ / "dados" / "capturas"

VALOR = re.compile(r"repasse\s+p\s*[úu]\s*b\s*l\s*i\s*c\s*o\s+de\s+(?:R\$\s*)?R\$\s*([\d\.]+,\d{2})", re.I)
CNPJ = re.compile(r"CNPJ(?:\s*n[º°o])?\s*:?\s*([\d][\d\.\s/\-]{12,22}\d)", re.I)
EDITAL = re.compile(r"(?:Edital(?:\s+de\s+Chamamento(?:\s+P[úu]blico)?)?\s*n[º°o]?\s*|Chamamento\s+P[úu]blico\s+n[º°o]\s*)(\d{3})\s*/\s*SEME\s*/\s*(\d{4})", re.I)
LOTE = re.compile(r"Lote\s*0?(\d)\b", re.I)


def texto_pdf(p):
    return "\n".join(pg.extract_text() or "" for pg in pypdf.PdfReader(p).pages)


# CNPJ que o despacho publicou com um dígito a menos, completado pela ata de classificação do mesmo edital (a fonte vai junto)
CORRIGE_CNPJ = {"0159892300015": "01598923000150"}   # ASA, 2025: o despacho diz "01.598.923 0001-5"; a ata definitiva, "01.598.923/0001-50"


def norm_cnpj(s):
    d = re.sub(r"\D", "", s)
    d = CORRIGE_CNPJ.get(d, d)
    return d if len(d) == 14 else (d.ljust(14, "?") if 12 <= len(d) < 14 else d)


def valor(s):
    return float(s.replace(".", "").replace(",", "."))


def nome_antes(trecho):
    """O nome da entidade: o que vem antes do último 'CNPJ', depois de '- ', 'e a ', 'e o ' ou 'e:'."""
    t = re.sub(r"\s+", " ", trecho)
    t = re.split(r"(?i)CNPJ(?:\s*n[º°o])?\s*:?\s*[\d][\d\.\s/\-]{12,22}\d[^C]*$", t)[0]
    t = re.sub(r"[\s,\-–]+$", "", t)
    cortes = [m.end() for m in re.finditer(r"(?:\s-\s|\bentre esta Pasta e(?: a| o)?:?\s|\be:\s|\bentidade\s)", t)]
    nome = t[cortes[-1]:] if cortes else t[-90:]
    return nome.strip(" -–,:").strip()


def despachos(texto):
    """Quebra o texto em despachos: cada um começa no 'Conteúdo do Despacho' ou no 'Processo nº'."""
    partes = re.split(r"(?=Conte[úu]do do Despacho|PROCESSO:\s*6019)", texto)
    return [p for p in partes if VALOR.search(p)]


def extrair(texto, origem, ano_padrao):
    out = []
    for d in despachos(texto):
        ed = EDITAL.search(d)
        edital = f"{ed.group(1)}/SEME/{ed.group(2)}" if ed else ""
        ano = int(ed.group(2)) if ed else ano_padrao
        objeto = re.search(r"Objeto da parceria\s*(.{3,160}?)\s*(?:Conte|Local de)", re.sub(r"\s+", " ", d))
        ultimo_fim = -10**9
        for m in VALOR.finditer(d):
            antes = d[max(0, m.start() - 900):m.start()]
            cs = list(CNPJ.finditer(antes))
            if not cs:
                continue
            c = cs[-1]
            ini = cs[-2].end() if len(cs) > 1 else 0
            nome = nome_antes(antes[ini:c.end()])
            lotes = list(LOTE.finditer(antes[c.start():]))
            if out and out[-1]["cnpj"] == norm_cnpj(c.group(1)) and out[-1]["origem"] == origem and m.start() - ultimo_fim < 400:
                out.pop()
            ultimo_fim = m.end()
            out.append({
                "ano": ano, "edital": edital, "objeto": objeto.group(1).strip() if objeto else "",
                "entidade": nome, "cnpj": norm_cnpj(c.group(1)),
                "lote": lotes[0].group(1) if lotes else "",
                "valor": valor(m.group(1)), "origem": origem,
            })
    return out


def main():
    linhas = []
    for ano in (2025, 2026):
        p = CAP / f"seme-chamamentos-{ano}.txt"
        linhas += extrair(p.read_text(encoding="utf-8"), p.name, ano)
    for p in sorted((DOC / "seme-2026").glob("*.pdf")):
        linhas += extrair(texto_pdf(p), p.name, 2026)
    vistos, unicas = set(), []
    for l in linhas:
        k = (l["ano"], l["edital"], l["cnpj"], l["lote"], round(l["valor"], 2))
        if k in vistos:
            continue
        vistos.add(k)
        unicas.append(l)
    unicas.sort(key=lambda l: (l["ano"], l["edital"], l["lote"], -l["valor"]))
    with open(RAIZ / "dados" / "parcerias.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(unicas[0]))
        w.writeheader()
        w.writerows(unicas)
    print(f"{len(unicas)} parcerias ({len(linhas)} achados antes de tirar as repetições)")
    for l in unicas:
        print(f"{l['ano']} {l['edital']:14} L{l['lote'] or '-'} {l['valor']:>14,.2f} {l['cnpj']} {l['entidade'][:60]}")


if __name__ == "__main__":
    main()
