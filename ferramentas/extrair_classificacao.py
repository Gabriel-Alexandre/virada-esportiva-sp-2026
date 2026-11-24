"""Extrai a classificação das propostas do edital 002/SEME/2026 (a Virada 2026) das atas da Comissão de Seleção: a posição, o
lote, o CNPJ, a data do protocolo, a pontuação e se foi desclassificada. É o 2º caminho para contar as propostas (as atas dizem o
número no cabeçalho de cada lote; aqui se contam as linhas).

Fontes: "ATA DE REUNIÃO RESULTADO PRELIM PARCIAL LOTE 2.pdf" (lote 2) e "ATA DEFINITIVA LOTES 1 E 3.pdf" (lotes 1 e 3).
Saída: dados/classificacao_002_2026.csv. Uso: python ferramentas/extrair_classificacao.py
"""
import csv
import re
from pathlib import Path

import pypdf

RAIZ = Path(__file__).resolve().parents[1]
DOC = RAIZ / "dados" / "documentos" / "seme-2026"
FONTES = ["ATA DE REUNIÃO RESULTADO PRELIM PARCIAL LOTE 2.pdf", "ATA DEFINITIVA LOTES 1 E 3.pdf"]
LINHA = re.compile(r"\b(\d{1,2}) VIRADA ESPORTIVA 2026 (ARENA .+?) (DESCLASSIFICADO )?([123]) "
                   r"(\d{2}\.\d{3}\.\d{3}/\d{4}) ?-(\d{2}) (\d{2}/\d{2}/\d{4}) (\d+)")


def texto(p):
    t = " ".join(pg.extract_text() or "" for pg in pypdf.PdfReader(p).pages)
    t = re.sub(r"Ata [^\n]{0,80}?\(\d{9}\) SEI 6019\.2026/0000547-9 / pg\. \d+", " ", t)  # o rodapé que corta a tabela
    return re.sub(r"\s+", " ", t)


def main():
    linhas, vistos = [], set()
    for f in FONTES:
        t = texto(DOC / f)
        for m in LINHA.finditer(t):
            pos, arena_osc, desc, lote, raiz, dv, data, pts = m.groups()
            cnpj = re.sub(r"\D", "", raiz + dv)
            if (lote, cnpj) in vistos:
                continue
            vistos.add((lote, cnpj))
            linhas.append({"lote": lote, "posicao": int(pos), "cnpj": cnpj, "arena_e_entidade": arena_osc.strip(),
                           "protocolo": data, "pontos": int(pts), "desclassificada": bool(desc), "fonte": f})
    linhas.sort(key=lambda x: (x["lote"], x["posicao"]))
    with open(RAIZ / "dados" / "classificacao_002_2026.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    for lote in "123":
        ls = [x for x in linhas if x["lote"] == lote]
        print(f"lote {lote}: {len(ls)} propostas, {sum(x['desclassificada'] for x in ls)} desclassificadas")


if __name__ == "__main__":
    main()
