"""Consulta o cadastro público de CNPJ (Receita Federal, pela BrasilAPI) de cada entidade de dados/parcerias.csv e guarda a
resposta inteira em dados/cnpj/<cnpj>.json, com a data da consulta. Uma por vez, com pausa, e sem refazer o que já está guardado.

⛔ O que sai daqui para o relatório é só dado da entidade (abertura, município, situação, natureza, atividade). Nome de pessoa
física do quadro de sócios não entra em nenhum arquivo de resultado.

Uso: python ferramentas/consultar_cnpj.py
"""
import csv
import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "dados" / "cnpj"
API = "https://brasilapi.com.br/api/cnpj/v1/{}"


def consultar(cnpj):
    req = urllib.request.Request(API.format(cnpj), headers={"User-Agent": "analise-de-dados-publicos/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    PASTA.mkdir(parents=True, exist_ok=True)
    cnpjs = sorted({l["cnpj"] for l in csv.DictReader(open(RAIZ / "dados" / "parcerias.csv", encoding="utf-8"))})
    for c in cnpjs:
        destino = PASTA / f"{c}.json"
        if destino.exists():
            continue
        if "?" in c:
            print(f"{c}: CNPJ incompleto no documento, sem consulta")
            continue
        for tentativa in range(3):
            try:
                d = consultar(c)
                d["_consulta"] = {"fonte": API.format(c), "em": datetime.now().isoformat(timespec="seconds")}
                if "qsa" in d:  # nomes de pessoas do quadro de sócios não se guardam no projeto público
                    d["qsa"] = f"retirado: {len(d['qsa'])} registros do quadro de sócios (nomes de pessoas não se publicam neste projeto)"
                d["email"] = None
                destino.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"{c}: {d.get('razao_social')} · {d.get('municipio')} · aberta em {d.get('data_inicio_atividade')}")
                break
            except Exception as e:  # noqa: BLE001
                print(f"{c}: falhou ({e}), tentativa {tentativa + 1}")
                time.sleep(5)
        time.sleep(1.5)


if __name__ == "__main__":
    main()
