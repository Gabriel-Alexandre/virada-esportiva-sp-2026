# Relatório: os R$ 21 milhões da Virada Esportiva 2026 de São Paulo

**Rodada 1, 24/11/2026.** Feito por Gabriel Carvalho, com o auxílio do Claude (IA) na coleta, nas contas e na revisão. Os números saem de `resultados/RESUMO.json` (`ferramentas/analise.py`) e foram refeitos por outro caminho em `resultados/VALIDACAO.json` (37 de 37).

## 1. A pergunta e a suspeita

Em 10/11/2026, o vice-prefeito de São Paulo, Coronel Mello Araújo (PL), levou ao Ministério Público uma representação sobre a Virada Esportiva 2026 (19 e 20/09). A Prefeitura pagou R$ 21,28 milhões a 22 organizações da sociedade civil. Segundo a representação, o gabinete dele visitou 15 endereços e não achou 12 sedes. Essas 12 entidades receberam R$ 15,78 milhões (74%). Ele também não achou 6 atividades anunciadas. Em 12/11, o MP pediu à Polícia Civil um inquérito. A Prefeitura e a secretária Érika Coimbra negam irregularidade. Nos canais de direita, a suspeita circula como *"R$ 21 milhões sumiram?"*.

Este projeto não visita endereço e não vê o evento. Ele responde ao que o papel público permite: **quem recebeu, quanto, com quanta concorrência, quanto do teto e o que essas entidades têm em comum.**

## 2. Fontes e método

| Fonte | O que dá | Onde está |
|---|---|---|
| Página de chamamentos da SEME, 2025 e 2026 | editais, atas, despachos de homologação (entidade, CNPJ, lote e valor) | `dados/capturas/`, `dados/documentos/` (sha256 em `dados/MANIFESTO.json`) |
| Edital 002/SEME/2026 | orçamento (R$ 16 milhões), lotes, vagas e teto por projeto (itens 3.6 e 9.1), a regra de uma proposta por lote (9.2), as datas do evento (1.1.1) | `edital_002_seme_2026-pdf.pdf` |
| Edital 009/SEME/2026 | a gestão: teto de R$ 5,4 milhões (item 3.10) | `edital_virada_2026-pdf.pdf` |
| Atas da comissão do edital 002 | propostas por lote, classificação, pontos e desclassificadas | `dados/classificacao_002_2026.csv` |
| Cadastro de CNPJ (Receita Federal, pela BrasilAPI) | abertura, município, situação, endereço e telefone de cada entidade | `dados/cnpj/` (⛔ o quadro de sócios foi retirado) |
| Representação do vice, pela imprensa (SBT News, BP Money, 11/11) | o valor da gestão (R$ 5,39 milhões) e a proposta única do edital 009 | `dados/complementos.json` |

O extrator (`ferramentas/extrair_parcerias.py`) lê cada *"repasse público de R$ X"* dos despachos e liga o valor ao CNPJ que vem antes dele. A validação (`ferramentas/validacao_independente.py`) relê cada valor pela frase da nota de empenho, que é outra frase do despacho. Os 25 valores batem.

## 3. Resultados

### 3.1 O dinheiro está no papel

| | Valor |
|---|---:|
| Arenas (edital 002), 25 parcerias | R$ 15.892.840,72 |
| Gestão (edital 009), 1 termo de colaboração | R$ 5.390.000,00 |
| **Total** | **R$ 21.282.840,72**, igual ao da representação |

São 22 entidades e 26 contratos. 4 entidades têm 2 contratos: o IMELC (gestão e lote 3), o Instituto Pangea, a SERC Santa Maria e a Associação CNB (lotes 2 e 3). O edital permite isso, porque a regra é *"uma proposta para cada lote"*.

### 3.2 A concorrência

| | Vagas | Propostas | Parcerias |
|---|---:|---:|---:|
| Gestão (009) | 1 | 1 | 1 |
| Lote 1 (até R$ 45 mil) | 12 | 1 | 1 |
| Lote 2 (até R$ 250 mil) | 15 | 20 (2 desclassificadas) | 17 |
| Lote 3 (até R$ 1,67 milhão) | 7 | 9 | 7 |

- 25 entidades se inscreveram nas arenas e 22 receberam: **88%**. Entre as que não foram desclassificadas, 22 de 23 receberam (**96%**).
- No lote 2, levaram 17 das 18 classificadas, inclusive a 18ª (77 pontos). A única classificada que não levou foi a 8ª (112 pontos). O documento público não diz por quê.
- No lote 3, a 2ª colocada (Instituto Parceiros da Cidadania) não levou o lote 3, mas levou o lote 2. A 9ª também ficou de fora no lote 3 e levou no lote 2.
- **No resto da Secretaria é igual.** Em 2026, os editais 005 (Agita + Férias), 006 (Alto Rendimento), 007 (Vamos Trilhar) e 010 (Mulheres que Transformam Mulheres) tiveram uma entidade só, pelas atas e homologações.

### 3.3 O valor contra o teto

| Lote | Teto por projeto | Média | Mínimo |
|---|---:|---:|---:|
| 1 | R$ 45.000,00 | 99,99% | 99,99% |
| 2 | R$ 250.000,00 | 99,38% | 96,59% |
| 3 | R$ 1.672.857,14 | 99,27% | 96,02% |
| Gestão | R$ 5.400.000,00 | 99,81% | |

As 25 parcerias das arenas ficaram acima de 95% do teto. O edital apresenta cada lote *"com valor de R$ X"*, então o teto funciona como preço. Cada despacho diz que o parecer técnico analisou *"a economicidade e compatibilidade com valores de mercado"*. Esses pareceres não estão na página.

### 3.4 A gerenciadora

O IMELC (CNPJ 10.711.726/0001-96, aberto em 2009) ficou com **R$ 7,06 milhões da Virada, 33% do total**. Em 2026, recebeu da Secretaria **R$ 13,05 milhões** em 3 contratos:

| Edital | Programa | Valor | Concorrência |
|---|---|---:|---|
| 005/SEME/2026 | Agita + Férias | R$ 5.995.229,34 | a homologação classifica só o IMELC |
| 009/SEME/2026 | Gestão da Virada | R$ 5.390.000,00 | proposta única, pela representação |
| 002/SEME/2026 | Arena Kids e da Família (lote 3) | R$ 1.666.235,03 | 1º de 9 |

O endereço do IMELC no CNPJ é a Rua dos Caetés, 773, em Perdizes. É o endereço que, segundo a representação, o gabinete do vice visitou em 06/10 e onde achou uma residência.

### 3.5 Quem repete de 2025

A página de 2025 traz as homologações com valor dos lotes 1 e 3 da Virada 2025: 8 entidades e R$ 10,04 milhões. **5 dessas 8 voltaram em 2026:**

| Entidade | 2025 | 2026 |
|---|---:|---:|
| Associação CNB | R$ 44.906,00 | R$ 1.921.896,00 |
| Fenats | R$ 1.671.000,00 | R$ 1.672.403,20 |
| Associação Caminho do Esporte | R$ 1.596.373,00 | R$ 1.606.273,00 |
| Instituto Parceiros da Cidadania | R$ 1.672.685,76 | R$ 249.685,52 |
| Federação Universitária Paulista (FUPE) | R$ 44.996,00 | R$ 44.996,00 |

O IMELC concorreu no lote 2 de 2025 (5º colocado, pela ata). A homologação com valor do lote 2 de 2025 não está na página, então o lote 2 de 2025 fica fora desta conta.

### 3.6 O que o cadastro tem em comum

- **O mesmo telefone, (11) 2440-8477**, em 4 entidades: Associação CNB, FUPE, INDES e ICTE. Somadas, receberam R$ 3,98 milhões da Secretaria em 2025 e 2026. Em 2025, as **2 únicas propostas do lote 1** eram da CNB e da FUPE. Em 2026, a **única proposta do lote 1** era da FUPE, e no lote 2 a CNB e o INDES disputaram e levaram. Um telefone em comum pode ser o de um escritório de contabilidade; o cadastro não diz.
- **O mesmo endereço, Alameda Franca, 267**, em 3 entidades: Fenats, Associação Paulista de Desportos e Federação dos Desportos no Estado de SP. Somadas, receberam R$ 6,29 milhões (a Fenats na Virada; as outras 2 no SP Fight 2026, edital 001). Federações dividirem sede é comum.
- **Fora da capital:** 4 das 22 entidades têm sede em outro município. São a Liga de Karatê de Osasco, a Liga Vale-paraibana (São José dos Campos), a Veredas (Guarulhos) e a SERC Santa Maria (São Caetano do Sul). A SERC recebeu R$ 1,92 milhão.
- **Todas as 22 estão ativas.** Só 1 foi aberta depois de 2020 (Associação Movimento Elite para Todos, abril de 2024). A mais antiga é a SERC, de 1974.
- O quadro de sócios não mostra a mesma pessoa em 2 entidades. Vínculo entre dirigentes, se existir, não aparece no dado público.

### 3.7 As 2 vagas a mais do lote 2

O edital previa 15 projetos no lote 2. Em 24/08 saíram 15 homologações, que não seguem a ordem da classificação: entraram a 16ª e a 18ª e ficaram de fora a 8ª, a 15ª e a 17ª. Em 11/09 e 15/09, a 4 e 8 dias do evento, saíram 2 homologações *"LOTE 02 complementar"*, *"conforme ordem de análise processual"*. A 17ª colocada (Associação Unidos Jardim Iporanga, 80 pontos) recebeu R$ 249.494,00, e a 15ª (Liga Nacional de Taekwondo, 89 pontos), R$ 249.980,00. Juntas, levaram R$ 499.474,00. O lote 1 deixou R$ 495.004,00 sem uso, porque teve 1 projeto para 12 vagas.

## 4. O que o dado público não mostra

- Se as atividades aconteceram, e quantas pessoas atenderam. Isso está na prestação de contas de cada termo, que não é pública.
- O preço real de mercado de cada item. A estimativa de R$ 72 mil para os caiaques da SERC é do gabinete do vice.
- Quais são as 12 entidades não achadas. A representação não foi publicada inteira.
- Intenção de ninguém.

## 5. Veredito

| Pergunta | O que o dado diz | Veredito |
|---|---|---|
| Os R$ 21 milhões saíram da Prefeitura? | 26 contratos, R$ 21.282.840,72, a mesma conta da representação | ✅ confirmado |
| Houve disputa de verdade? | gestão com 1 proposta; lote 1 com 1 para 12 vagas; 22 de 25 inscritas receberam | ⚠️ concorrência quase nula, o mesmo padrão de outros 4 editais da Secretaria |
| Os valores estão acima do mercado? | todos entre 96% e 100% do teto; o teto é o preço do edital | ⬜ o dado não responde; o parecer de mercado não é público |
| As entidades têm ligação entre si? | 4 com o mesmo telefone, disputando o mesmo lote em 2025 e 2026; 3 no mesmo endereço | ⚠️ coincidência no cadastro; ligação entre dirigentes não aparece |
| O dinheiro sumiu? | o papel público não mostra sumiço nem entrega | ⬜ aberto: quem fecha é a prestação de contas, com a Polícia Civil e o MP |

**Em uma frase:** a conta do vice está certa. O papel público não prova desvio, mas mostra uma disputa sem concorrência, preços no teto e entidades com o mesmo telefone disputando entre si. É o que justifica abrir a prestação de contas.
