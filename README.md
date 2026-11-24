# Os R$ 21 milhões da Virada Esportiva 2026 de São Paulo

O projeto do vídeo 32 do canal: **R$ 21 milhões sumiram na Virada Esportiva?** Para onde foi o dinheiro da Virada Esportiva 2026, pelos documentos da própria Prefeitura de São Paulo: quem recebeu, quanto, com quanta concorrência, quanto do teto do edital e o que as entidades têm em comum no cadastro da Receita.

- Resultado: `RESUMO_SIMPLES.md` e `RELATORIO.md`
- Onde o trabalho parou: `ESTADO.md`
- Refazer: `python ferramentas/extrair_parcerias.py` → `python ferramentas/extrair_classificacao.py` → `python ferramentas/analise.py` → `python ferramentas/validacao_independente.py` → `python ferramentas/graficos.py` → `python -m pytest -q`
- O cadastro de CNPJ se refaz com `python ferramentas/consultar_cnpj.py` (BrasilAPI); o quadro de sócios não se guarda.

Feito por Gabriel Carvalho, com o auxílio do Claude (IA) na coleta, nas contas e na revisão.
