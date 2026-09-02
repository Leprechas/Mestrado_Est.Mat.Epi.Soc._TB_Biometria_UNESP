# Tuberculose nos municípios dos estados de São Paulo e do Rio de Janeiro, 2001–2024

Dados, códigos e resultados do estudo ecológico sobre a distribuição espaço-temporal e a
dependência espacial da tuberculose nos municípios dos estados de São Paulo e do Rio de
Janeiro entre 2001 e 2024.

Programa de Pós-Graduação em Biometria, Instituto de Biociências, UNESP — Botucatu/SP.

## Resumo do estudo

Estudo ecológico com unidade de análise município-ano, cobrindo **645 municípios do estado de
São Paulo** e **92 do estado do Rio de Janeiro** ao longo de 24 anos (**17.688 observações**).
Foram registrados 356.603 casos no estado do Rio de Janeiro e 479.036 no estado de São Paulo.

Principais achados:

- Incidência do período de **91,6** por 100 mil pessoas-ano no estado do Rio de Janeiro contra
  **47,9** no estado de São Paulo (razão de 1,91).
- Tendência temporal **estacionária** nos dois estados pela regressão de Prais-Winsten
  (VPA: Rio de Janeiro −0,56%, p=0,374; São Paulo 0,44%, p=0,255).
- **Dependência espacial positiva e significativa**: índice de Moran global da incidência do
  período de 0,405 (Rio de Janeiro) e 0,133 (São Paulo), p=0,001.
- Agrupamentos de alto risco (LISA alto-alto) na capital e na Baixada Fluminense, e no oeste
  e litoral sul paulistas.
- A dependência espacial **persiste após suavização bayesiana empírica** (Moran 0,427 e 0,133),
  indicando que não decorre da instabilidade de taxas em municípios pouco populosos.

## Fontes de dados

| Fonte | Uso |
|---|---|
| Sinan / DataSUS | Casos de tuberculose por município de notificação e ano |
| IBGE | Estimativas populacionais municipais e malhas municipais digitais |

A população municipal anual foi obtida por **interpolação log-linear com taxa geométrica de
crescimento (CAGR)** entre os pontos censitários.

## Estrutura

```
Casos-TB-2001-2024/                 casos notificados, por município e ano
População-Final-GitHub/             população municipal corrigida (CAGR) e auditorias
DADOS-BASE-MAPA/                    malhas municipais (GeoJSON, SP e RJ)

Analise inicial/                    análise exploratória inicial
Análise descritiva e comparação epidemiologica/
                                    análise descritiva e comparação entre estados
Análise exploratória espacial/      matriz de vizinhança, Moran, LISA e Getis-Ord Gi*
  secao_5_7_.../                    painel municipal e saídas espaciais (CSV e mapas)

resultados/                         resultados derivados usados no artigo
figuras_artigo/                     figuras do artigo (PDF/SVG/PNG) e scripts que as geram
SaTScan_inputs/                     arquivos de entrada para varredura espaço-temporal
STROBE_checklist_TB.md              checklist de relato (estudo observacional)
```

## Dicionário dos principais arquivos

**`Análise exploratória espacial/secao_5_7_analise_exploratoria_espacial/`**

- `base_municipal_periodo_total.csv` — painel municipal agregado no período completo.
  Colunas: `estado`, `cod_mun6`, `municipio`, `casos_acumulados`, `pop_pessoa_ano`,
  `pop_media`, `incidencia_periodo_100mil_pessoa_ano`, `anos_zero`, entre outras.
- `base_municipal_periodos.csv` — o mesmo, por blocos quinquenais.
- `arestas_matriz_vizinhanca_queen.csv` — lista de arestas da matriz de contiguidade
  *queen* (`estado`, `origem`, `destino`), construída separadamente por estado.
- `lisa_{SP,RJ}_...csv` — Moran local: `lisa_I`, `lisa_p`, `classe_lisa`.
- `getis_ord_gi_{SP,RJ}_...csv` — Getis-Ord Gi\*: `gi_z`, `gi_p`, `classe_gi`.

**`resultados/`**

- `incidencia_anual_estado_2001_2024.csv` — série anual de incidência por estado.
- `tabela2_moran.csv` — índice de Moran (I, z, p) por estado, variável e recorte temporal.
- `incidencia_EB_{RJ,SP}.csv` — taxas suavizadas por estimadores bayesianos empíricos.
- `hotspots_gi_{RJ,SP}.csv` — municípios classificados como *hot spot*.

## Reprodução

Os códigos de análise estão nos notebooks Jupyter. As figuras do artigo são geradas por:

```bash
python figuras_artigo/gerar_figuras_sem_geopandas.py   # Figuras 1, 2 e 3
python figuras_artigo/calcular_lisa.py                 # LISA com permutação condicional
```

O gerador de figuras depende apenas de `numpy`, `pandas` e `matplotlib` — lê o GeoJSON
diretamente, sem necessidade de `geopandas`.

> **Atenção ao GeoJSON:** nos arquivos de malha, os anéis extras de cada polígono são
> **partes separadas (ilhas)**, não buracos. Usar apenas `coordinates[0]` remove Ilha Grande,
> Ilhabela e o litoral recortado, produzindo mapas infiéis. Utilize todos os anéis.

A varredura espaço-temporal requer o software [SaTScan](https://www.satscan.org/);
as instruções estão em `SaTScan_inputs/LEIA-ME_SaTScan.md`.

## Licença

- **Código** (scripts e notebooks): [MIT](LICENSE)
- **Dados e figuras**: [CC BY 4.0](LICENSE-DATA)

Os dados de origem (Sinan/DataSUS e IBGE) são de domínio público.

## Aspectos éticos

Estudo baseado exclusivamente em dados secundários, agregados, de domínio público e sem
identificação individual — situação de dispensa de apreciação por Comitê de Ética em Pesquisa,
nos termos do parágrafo único do artigo 1º da Resolução CNS nº 510, de 7 de abril de 2016.
