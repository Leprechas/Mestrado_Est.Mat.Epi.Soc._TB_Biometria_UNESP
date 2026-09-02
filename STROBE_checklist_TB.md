# Checklist STROBE — estudo ecológico da tuberculose em SP e RJ, 2001–2024

Adaptado para **estudo ecológico** (unidade de análise = município-ano). Itens sobre indivíduos não se aplicam e estão marcados como tal. Referência: von Elm et al., STROBE Statement.

| # | Item STROBE | Onde está no manuscrito / status |
|---|---|---|
| 1a | Desenho no título ou resumo | Título traz "estudo ecológico"; resumo estruturado. **OK** |
| 1b | Resumo informativo e equilibrado | Resumo (objetivo, métodos, resultados, conclusão), ≤250 palavras. **OK** |
| 2 | Justificativa/contexto | Introdução (carga da TB, determinação social, heterogeneidade espacial). **OK** |
| 3 | Objetivos | Introdução, último parágrafo. **OK** |
| 4 | Desenho do estudo | Métodos: ecológico de séries temporais, unidade município-ano. **OK** |
| 5 | Contexto (local, período) | Métodos: 645 municípios SP + 92 RJ, 2001–2024. **OK** |
| 6 | Participantes/unidades | Ecológico — unidades = municípios; critérios de inclusão (todos os municípios dos dois estados). **OK** |
| 7 | Variáveis | Desfecho: incidência/100 mil (bruta e log); SIR; tendência. Preditores sociais: **a incluir se fizer o Nível 1-2**. **Parcial** |
| 8 | Fontes de dados / mensuração | Métodos: casos Sinan/DataSUS; população IBGE (corrigida por CAGR); malhas IBGE. **OK** |
| 9 | Viés | Limitações: subnotificação, município de notificação ≠ residência, denominador interpolado. **OK** |
| 10 | Tamanho do estudo | 17.688 observações município-ano (645+92 × 24). **OK** |
| 11 | Variáveis quantitativas | Métodos: incidência do período (pessoa-ano), log(1+x), blocos quinquenais. **OK** |
| 12a | Métodos estatísticos | Prais-Winsten (VPA/IC95%); Moran global; LISA; Getis-Ord Gi\*; **Bayes empírico**; **varredura espaço-temporal (SaTScan)**. **OK (atualizar Métodos)** |
| 12b | Subgrupos/interações | Análise por estado e por blocos temporais. **OK** |
| 12c | Dados faltantes | Painel sem lacunas de população; Marinópolis (SP) sem casos declarado. **OK** |
| 12d | Dependência espacial/temporal | Prais-Winsten (autocorrelação serial); matriz *queen*, 999 permutações. **OK** |
| 12e | Análises de sensibilidade | Escala bruta vs. log; **robustez por Bayes empírico** (Moran mantém-se); janela do SaTScan (25%/50%). **OK** |
| 13 | Fluxo de unidades | 737 municípios; 1 sem casos (Marinópolis); 1 ilha na matriz *queen* (Ilhabela). **OK** |
| 14 | Dados descritivos | Resultados: casos, incidência, sobredispersão, zeros, porte. **OK** |
| 15 | Dados de desfecho | Resultados: incidência por estado/bloco; VPA. **OK** |
| 16 | Resultados principais | Resultados: Moran/LISA/Gi\*, clusters caracterizados, EB. **OK** |
| 17 | Outras análises | Sensibilidade de escala; EB; hot spots nomeados. **OK** |
| 18 | Resultados-chave | Discussão, 1º parágrafo. **OK** |
| 19 | Limitações | Discussão → Limitações (ecológico, sem covariáveis ajustadas, múltiplos testes, taxas brutas). **OK** |
| 20 | Interpretação | Discussão (utilidade para priorização regionalizada). **OK** |
| 21 | Generalização | Discussão (dois estados do Sudeste; cautela ao extrapolar). **OK** |
| 22 | Financiamento | Declarações → **a declarar** (FAPESP/CAPES/CNPq?). **Pendente** |

## Itens que ainda dependem de você
- **7 (variáveis sociais):** só ficam "OK" se incluir a associação com determinantes sociais (Nível 1-2). Sem isso, declarar explicitamente que não houve ajuste por covariáveis (já consta nas Limitações).
- **22 (financiamento):** informar vínculo/agência.
- **Disponibilidade de dados (exigência RESS):** depositar painel + códigos em repositório com DOI (Zenodo/figshare).
