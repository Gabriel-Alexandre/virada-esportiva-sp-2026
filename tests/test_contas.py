"""Os números que o vídeo diz, travados. Uso: python -m pytest -q"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
R = json.loads((RAIZ / "resultados" / "RESUMO.json").read_text(encoding="utf-8"))


def test_total_bate_com_a_representacao():
    v = R["virada_2026"]
    assert v["total"] == 21282840.72
    assert v["entidades"] == 22
    assert v["contratos"] == 26


def test_concorrencia():
    pl = R["virada_2026"]["por_lote"]
    assert (pl["1"]["propostas"], pl["1"]["vagas"], pl["1"]["parcerias"]) == (1, 12, 1)
    assert (pl["2"]["propostas"], pl["2"]["vagas"], pl["2"]["parcerias"]) == (20, 15, 17)
    assert (pl["3"]["propostas"], pl["3"]["vagas"], pl["3"]["parcerias"]) == (9, 7, 7)
    c = R["classificacao_002"]
    assert (c["entidades_que_se_inscreveram"], c["entidades_com_parceria"]) == (25, 22)


def test_teto():
    pl = R["virada_2026"]["por_lote"]
    assert all(pl[k]["acima_de_95pct_do_teto"] == pl[k]["parcerias"] for k in "123")
    assert pl["3"]["pct_do_teto_minimo"] > 96


def test_gerenciadora_e_repeticoes():
    assert R["gerenciadora"]["total_2026"] == 13051464.37
    assert len(R["repetem_de_2025"]["repetem"]) == 5
    assert len(R["cadastro"]["mesmo_telefone"][0]["entidades"]) == 4


def test_complementares():
    cp = R["classificacao_002"]["lote_2_complementar"]
    assert sorted(p["posicao"] for p in cp["parcerias"]) == [15, 17]
    assert cp["sobra_do_lote_1"] == 495004.0


def test_sem_nome_de_socio_nos_dados_publicos():
    for f in (RAIZ / "dados" / "cnpj").glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        assert not isinstance(d.get("qsa"), list), f.name
    texto = (RAIZ / "resultados" / "RESUMO.json").read_text(encoding="utf-8")
    assert "nome_socio" not in texto and not re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto)
