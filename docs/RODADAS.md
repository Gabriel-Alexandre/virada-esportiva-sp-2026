# Rodadas

## Rodada 1 (24/11/2026)

**Pedido:** o vídeo 32 do canal, pela regra da suspeita com dado: refazer a conta dos R$ 21 milhões da Virada Esportiva 2026 pelos documentos públicos.

**Feito:**
- baixados os editais 002 e 009 de 2026, as atas da comissão do 002 e os despachos de homologação e extratos da página de chamamentos da Secretaria (2026) e as capturas da página de 2025 (sha256 em `dados/MANIFESTO.json`);
- extraídas 40 parcerias da Secretaria em 2025 e 2026, 25 delas da Virada 2026 (`extrair_parcerias.py`), e a classificação das 30 propostas do edital 002 (`extrair_classificacao.py`);
- consultados 28 CNPJs na Receita (BrasilAPI), com o quadro de sócios retirado;
- a análise, a validação por outro caminho (a nota de empenho, os cabeçalhos das atas e o dígito do CNPJ: 37 de 37), 7 gráficos e 6 testes.

**Resultado:** `RESUMO_SIMPLES.md`. A soma bate com a representação (R$ 21.282.840,72, 22 entidades).

**Correções no caminho:** o despacho de 2025 publica o CNPJ da ASA com um dígito a menos (completado pela ata, `CORRIGE_CNPJ` no extrator); um PDF quebra *"públ ico"* no meio (o extrator tolera); 9 PDFs da página eram do Bolsa Atleta e do edital 008 (Clube Escola) e saíram do projeto.
