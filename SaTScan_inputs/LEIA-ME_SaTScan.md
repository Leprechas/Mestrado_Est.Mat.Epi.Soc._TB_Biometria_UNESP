# Varredura espaço-temporal (SaTScan) — TB SP e RJ, 2001–2024

Arquivos gerados (um conjunto por estado — a análise é **separada por estado**, coerente com o desenho do trabalho):

| Arquivo | Formato (colunas) |
|---|---|
| `SP.cas` / `RJ.cas` | `cod_mun6  casos  ano` (só linhas com casos > 0) |
| `SP.pop` / `RJ.pop` | `cod_mun6  ano  população` |
| `SP.geo` / `RJ.geo` | `cod_mun6  latitude  longitude` (centroide do município) |

Validação: total de casos nos `.cas` = **479.036 (SP)** e **356.603 (RJ)**.
Marinópolis (SP) tem população mas 0 casos → aparece em `.geo`/`.pop`, ausente do `.cas` (o SaTScan trata como risco 0, correto).

## Como rodar (SaTScan gratuito — Kulldorff; www.satscan.org)

Rodar **duas vezes** (uma para SP, outra para RJ).

**Aba Input**
- Case File: `SP.cas`
- Population File: `SP.pop`
- Coordinates File: `SP.geo`
- Coordinates: **Lat/Long**
- Time Precision: **Year**
- Study Period: **2001/1/1** a **2024/12/31**

**Aba Analysis**
- Type of Analysis: **Retrospective → Space-Time**
- Probability Model: **Discrete Poisson**
- Scan For Areas With: **High Rates**
- Time Aggregation: **1 Year**

**Aba Advanced → Spatial Window**
- Maximum Spatial Cluster Size: **50% da população em risco** (padrão) e repita com **25%** como sensibilidade (para TB, 50% costuma gerar clusters grandes demais).

**Aba Advanced → Temporal Window**
- Maximum Temporal Cluster Size: **50%** do período (ou 25% em sensibilidade).

**Aba Advanced → Inference**
- Monte Carlo replications: **999**

**Aba Output**
- Main results file (.txt) e, se quiser mapear, marque a saída **shapefile/GeoJSON** dos clusters.

## O que reportar no artigo
- Cluster **mais provável** (primário) e clusters secundários: municípios incluídos, período (anos), **RR**, casos observados/esperados, **LLR** e **p**.
- Compare a localização dos clusters espaço-temporais com os *hot spots* do Gi\* (Baixada Fluminense/capital no RJ; Baixada Santista e oeste paulista em SP) — convergência reforça o achado.

## Observações honestas
- Os centroides foram calculados pela fórmula de área (shoelace) sobre a malha municipal — adequados para o SaTScan (que usa 1 ponto por área).
- O modelo Poisson usa a **população anual** como denominador (já fornecida); não há ajuste por covariáveis aqui — é análise não ajustada, exploratória, como o resto do trabalho.
