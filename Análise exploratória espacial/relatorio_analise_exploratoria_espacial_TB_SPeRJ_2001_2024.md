# Relatório técnico — Análise exploratória espacial da tuberculose em São Paulo e Rio de Janeiro, 2001–2024

**Arquivo analisado:** `ANÁLISE EXPLORATÓRIA ESPACIAL.ipynb`  
**Base empírica:** casos de tuberculose por município-ano, população municipal interpolada e malhas municipais de SP e RJ.  
**Período:** 2001 a 2024.  
**Unidade de análise:** município-ano para análise temporal e município para análise espacial agregada.

---

## 1. Síntese executiva

O notebook executa a seção de **análise exploratória espacial** do projeto de tuberculose para os estados de São Paulo e Rio de Janeiro. A análise reconstrói o painel município-ano, incorpora população municipal anual, calcula incidência por 100 mil habitantes, agrega os dados por período completo e por blocos temporais, constrói matrizes de vizinhança do tipo **queen** e aplica três famílias de métodos espaciais exploratórios:

1. **Moran Global**, para testar autocorrelação espacial global;
2. **LISA**, para identificar agrupamentos locais do tipo Alto-Alto, Baixo-Baixo, Alto-Baixo e Baixo-Alto;
3. **Getis-Ord Gi\***, para identificar áreas quentes e frias, isto é, concentração local de valores altos ou baixos.

A conclusão central é que a tuberculose apresenta **dependência espacial estatisticamente significativa** nos dois estados, mas com padrões distintos. No Rio de Janeiro, a autocorrelação espacial da incidência é mais forte e mais evidente no período completo e em vários blocos temporais. Em São Paulo, a autocorrelação da incidência bruta é mais fraca em alguns recortes, mas se torna mais clara quando se usa transformação logarítmica ou medidas acumuladas. Isso sugere que SP tem maior heterogeneidade interna e maior influência de valores extremos, zeros e municípios pequenos.

Do ponto de vista da modelagem, os resultados sustentam a inclusão de um componente espacial estruturado, como **CAR/BYM/BYM2**, nos modelos bayesianos espaço-temporais. A presença de agrupamentos locais também reforça que a análise não deve ser apenas temporal ou estadual agregada; a escala municipal contém informação territorial epidemiologicamente relevante.

---

## 2. Objetivo do notebook

O código declara explicitamente os seguintes objetivos analíticos:

- reconstruir o painel município-ano;
- carregar as malhas municipais;
- construir matriz de vizinhança queen por estado;
- calcular Moran Global;
- calcular LISA;
- calcular Getis-Ord Gi\*;
- gerar mapas e tabelas diagnósticas.

Portanto, o notebook corresponde à etapa de **análise exploratória espacial**, equivalente à seção metodológica 5.7 do projeto. Sua função não é ainda ajustar o modelo bayesiano final, mas diagnosticar se há estrutura espacial suficiente para justificar a modelagem espaço-temporal posterior.

---

## 3. Configurações gerais e decisões analíticas

O notebook define:

- anos analisados: **2001 a 2024**;
- anos selecionados para mapas anuais: **2001, 2005, 2010, 2015, 2019, 2020 e 2024**;
- número de permutações: **999**;
- nível de significância: **5%**;
- variáveis principais: estado, código municipal, município, ano, casos, população e incidência por 100 mil habitantes.

A escolha de 999 permutações é adequada para análise exploratória, pois permite estimar significância pseudoaleatória para Moran, LISA e Gi\*. O nível de 5% é o padrão usual para identificação inicial de autocorrelação e clusters, mas é importante lembrar que LISA e Gi\* envolvem múltiplos testes locais. Assim, seus resultados devem ser tratados como **exploratórios**, não como prova confirmatória isolada.

---

## 4. Reconstrução do painel município-ano

O notebook lê os arquivos de casos de tuberculose de SP e RJ, padroniza os nomes dos municípios, transforma a base de formato largo para formato longitudinal e combina os registros de casos com a base populacional anual.

A base final reconstruída apresenta:

| estado   |   linhas |   municipios |   ano_min |   ano_max |   casos_total |   incidencia_media |
|:---------|---------:|-------------:|----------:|----------:|--------------:|-------------------:|
| RJ       |     2208 |           92 |      2001 |      2024 |        356603 |             48.697 |
| SP       |    15480 |          645 |      2001 |      2024 |        479036 |             33.391 |

### Interpretação

A estrutura final está correta para o objetivo do estudo:

- RJ possui **92 municípios × 24 anos = 2.208 observações**;
- SP possui **645 municípios × 24 anos = 15.480 observações**;
- o total é **17.688 observações município-ano**;
- o Rio de Janeiro apresenta menor número absoluto de municípios, mas maior incidência média municipal;
- São Paulo apresenta maior número total de casos acumulados, coerente com sua população e quantidade de municípios.

A diferença entre `casos_total` e `incidencia_media` é epidemiologicamente relevante. São Paulo concentra maior carga absoluta, enquanto o Rio de Janeiro mostra maior intensidade relativa média. Isso é compatível com a leitura já adotada no projeto: SP tem magnitude absoluta e heterogeneidade territorial; RJ tem maior intensidade epidemiológica relativa.

---

## 5. Cálculo da incidência e variáveis derivadas

A incidência municipal anual foi calculada como:

\[
\text{Incidência}_{it} = \frac{\text{casos}_{it}}{\text{população}_{it}} \times 100.000
\]

Além da incidência anual bruta, foram criadas variáveis auxiliares:

- `log_pop`: logaritmo da população, útil para posterior offset;
- `incidencia_ma3`: média móvel de 3 anos da incidência, com janela centralizada;
- `log_casos_mais1`: `log(1 + casos)`;
- `log_inc_mais1`: `log(1 + incidência)`.

### Interpretação

A média móvel de 3 anos é uma decisão adequada para análise espacial exploratória porque reduz oscilações abruptas em municípios pequenos. Em tuberculose, municípios de baixa população podem ter incidências muito altas com poucos casos, fenômeno associado à instabilidade de pequenas áreas. A média móvel não substitui o modelo estatístico, mas facilita a leitura visual de padrões espaciais persistentes.

A transformação `log(1 + x)` também é adequada porque:

- reduz a influência de valores extremos;
- mantém zeros definidos;
- melhora a visualização de distribuições assimétricas;
- ajuda a comparar padrões quando há grande diferença entre municípios pequenos e grandes.

---

## 6. Agregações espaciais construídas

O notebook produz duas bases espaciais principais.

### 6.1. Agregado municipal do período completo

Para cada município, foram calculados:

- casos acumulados no período;
- população pessoa-ano;
- população média;
- incidência média anual;
- incidência mediana anual;
- incidência máxima anual;
- número de anos com casos;
- número de anos com zero caso;
- incidência do período por 100 mil pessoa-ano;
- `log(1 + casos acumulados)`;
- `log(1 + incidência do período)`.

A incidência do período foi calculada como:

\[
\text{Incidência do período}_i =
\frac{\sum_t \text{casos}_{it}}{\sum_t \text{população}_{it}}
\times 100.000
\]

Essa é uma métrica mais estável do que a média simples das incidências anuais, pois pondera naturalmente pela exposição populacional acumulada.

### 6.2. Agregados por blocos temporais

Os anos foram agrupados em:

- 2001–2005;
- 2006–2010;
- 2011–2015;
- 2016–2019;
- 2020–2024.

A divisão separa blocos históricos relativamente interpretáveis, com destaque para o bloco **2020–2024**, que captura o período da pandemia de COVID-19 e o pós-pandemia imediato. Essa escolha é útil porque a pandemia pode ter afetado diagnóstico, notificação, acesso aos serviços e continuidade do cuidado.

---

## 7. Carregamento das malhas municipais

Foram carregadas as malhas municipais de RJ e SP a partir dos arquivos GeoJSON. O notebook confirma:

| estado   |   municipios_malha |
|:---------|-------------------:|
| RJ       |                 92 |
| SP       |                645 |

### Interpretação

A malha está compatível com a estrutura municipal esperada:

- RJ: 92 municípios;
- SP: 645 municípios.

A compatibilidade entre número de municípios na malha e número de municípios no painel é um ponto forte do notebook, pois reduz o risco de perda de unidades na junção entre dados epidemiológicos e geometria.

---

## 8. Matriz de vizinhança queen

O notebook constrói, separadamente por estado, matrizes de vizinhança do tipo **queen**. Nesse critério, dois municípios são considerados vizinhos se compartilham fronteira ou vértice.

Resumo gerado:

| estado   |   municipios |   media_vizinhos |   mediana_vizinhos |   min_vizinhos |   max_vizinhos |   municipios_sem_vizinhos | codigos_sem_vizinhos   |
|:---------|-------------:|-----------------:|-------------------:|---------------:|---------------:|--------------------------:|:-----------------------|
| RJ       |           92 |            4.891 |                  5 |              1 |             10 |                         0 |                        |
| SP       |          645 |            5.674 |                  5 |              0 |             23 |                         1 | 352040.000             |

### Interpretação

A matriz queen funcionou adequadamente para o Rio de Janeiro: todos os 92 municípios possuem pelo menos um vizinho.

Em São Paulo, há um município sem vizinhos sob o critério queen: **código 352040**, correspondente a **Ilhabela**. O aviso repetido no notebook:

> `352040 is an island (no neighbors)`

não indica erro no código. Ele indica que, pela geometria usada, Ilhabela não compartilha fronteira nem vértice com outros municípios. Como é uma ilha, isso é esperado sob contiguidade territorial estrita.

### Implicação metodológica

Esse ponto exige decisão antes da modelagem bayesiana espacial. Em modelos CAR/BYM/BYM2, municípios sem vizinhos podem gerar componentes desconectados ou efeitos espaciais estruturados mal definidos para aquela unidade. As alternativas são:

1. manter Ilhabela como ilha e permitir que seu efeito seja tratado essencialmente pelo componente não estruturado;
2. criar uma conexão artificial com o município continental mais próximo, se houver justificativa territorial/epidemiológica;
3. testar matriz alternativa por k-vizinhos mais próximos em análise de sensibilidade;
4. documentar explicitamente que a matriz queen gera uma ilha em SP.

A alternativa mais conservadora para o projeto é registrar o problema, manter a matriz queen como matriz principal e realizar análise de sensibilidade com uma matriz alternativa.

---

## 9. Moran Global

### 9.1. Método

O Índice de Moran Global mede se valores semelhantes tendem a estar próximos no espaço. Valores positivos indicam autocorrelação espacial positiva; valores negativos indicam dispersão espacial; valores próximos de zero indicam ausência de estrutura espacial global.

A forma geral é:

\[
I =
\frac{n}{S_0}
\frac{\sum_i \sum_j w_{ij}(x_i - \bar{x})(x_j - \bar{x})}
{\sum_i (x_i - \bar{x})^2}
\]

em que:

- \(n\) é o número de municípios;
- \(w_{ij}\) é o peso espacial entre municípios \(i\) e \(j\);
- \(S_0\) é a soma dos pesos espaciais;
- \(x_i\) é a variável analisada;
- \(\bar{x}\) é a média da variável.

O notebook usa permutações para obter `p_sim` e `z_sim`.

### 9.2. Resultados exibidos no notebook

O notebook mostra os primeiros 20 resultados da tabela de Moran Global:

| estado   | contexto   | variavel                             |   n |   I_Moran |   p_sim |   z_sim | erro   |
|:---------|:-----------|:-------------------------------------|----:|----------:|--------:|--------:|:-------|
| RJ       | 2001–2024  | incidencia_periodo_100mil_pessoa_ano |  92 |     0.405 |   0.001 |   6.105 |        |
| RJ       | 2001–2024  | log_inc_periodo_mais1                |  92 |     0.236 |   0.001 |   3.919 |        |
| RJ       | 2001–2024  | log_casos_acumulados_mais1           |  92 |     0.425 |   0.001 |   6.277 |        |
| SP       | 2001–2024  | incidencia_periodo_100mil_pessoa_ano | 645 |     0.133 |   0.001 |   5.703 |        |
| SP       | 2001–2024  | log_inc_periodo_mais1                | 645 |     0.271 |   0.001 |  11.188 |        |
| SP       | 2001–2024  | log_casos_acumulados_mais1           | 645 |     0.387 |   0.001 |  15.819 |        |
| RJ       | 2001–2005  | incidencia_periodo_100mil_pessoa_ano |  92 |     0.301 |   0.001 |   4.733 |        |
| RJ       | 2001–2005  | log_inc_periodo_mais1                |  92 |     0.2   |   0.004 |   3.125 |        |
| RJ       | 2006–2010  | incidencia_periodo_100mil_pessoa_ano |  92 |     0.499 |   0.001 |   7.254 |        |
| RJ       | 2006–2010  | log_inc_periodo_mais1                |  92 |     0.311 |   0.002 |   4.867 |        |
| RJ       | 2011–2015  | incidencia_periodo_100mil_pessoa_ano |  92 |     0.372 |   0.001 |   5.511 |        |
| RJ       | 2011–2015  | log_inc_periodo_mais1                |  92 |     0.235 |   0.001 |   3.719 |        |
| RJ       | 2016–2019  | incidencia_periodo_100mil_pessoa_ano |  92 |     0.302 |   0.001 |   4.573 |        |
| RJ       | 2016–2019  | log_inc_periodo_mais1                |  92 |     0.186 |   0.008 |   2.883 |        |
| RJ       | 2020–2024  | incidencia_periodo_100mil_pessoa_ano |  92 |     0.232 |   0.001 |   3.444 |        |
| RJ       | 2020–2024  | log_inc_periodo_mais1                |  92 |     0.165 |   0.008 |   2.591 |        |
| SP       | 2001–2005  | incidencia_periodo_100mil_pessoa_ano | 645 |    -0.001 |   0.311 |   0.012 |        |
| SP       | 2001–2005  | log_inc_periodo_mais1                | 645 |     0.231 |   0.001 |   9.719 |        |
| SP       | 2006–2010  | incidencia_periodo_100mil_pessoa_ano | 645 |     0.19  |   0.001 |   8.351 |        |
| SP       | 2006–2010  | log_inc_periodo_mais1                | 645 |     0.199 |   0.001 |   8.915 |        |

### 9.3. Interpretação do período completo, 2001–2024

Para o período completo, todos os índices exibidos são positivos e estatisticamente significativos.

No **Rio de Janeiro**:

- incidência do período: **I = 0,405; p = 0,001**;
- log da incidência: **I = 0,236; p = 0,001**;
- log dos casos acumulados: **I = 0,425; p = 0,001**.

Isso indica forte autocorrelação espacial. Municípios com alta incidência tendem a estar próximos de municípios também com alta incidência, e municípios com baixa incidência tendem a estar próximos de municípios com baixa incidência. A magnitude do Moran é elevada para dados epidemiológicos municipais, especialmente considerando que a tuberculose é influenciada por urbanização, vulnerabilidade social, densidade populacional e acesso a serviços.

Em **São Paulo**:

- incidência do período: **I = 0,133; p = 0,001**;
- log da incidência: **I = 0,271; p = 0,001**;
- log dos casos acumulados: **I = 0,387; p = 0,001**.

A autocorrelação espacial também é significativa, mas a incidência bruta acumulada apresenta Moran menor do que no RJ. A transformação logarítmica aumenta a evidência de estrutura espacial na incidência paulista, sugerindo que valores extremos e a grande heterogeneidade municipal mascaram parte do padrão espacial quando se usa a escala bruta.

### 9.4. Interpretação por blocos temporais

No RJ, os blocos temporais exibidos mostram autocorrelação espacial positiva em todos os períodos:

- 2001–2005: I = 0,301 para incidência do período;
- 2006–2010: I = 0,499;
- 2011–2015: I = 0,372;
- 2016–2019: I = 0,302;
- 2020–2024: I = 0,232.

O maior valor aparece em **2006–2010**, indicando forte agrupamento espacial da incidência nesse bloco. Depois há redução progressiva, mas a estrutura espacial permanece significativa até 2020–2024.

Em SP, o bloco 2001–2005 apresenta incidência bruta com Moran praticamente nulo:

- 2001–2005: I = -0,001; p = 0,311.

Contudo, no mesmo bloco, o log da incidência já apresenta autocorrelação positiva:

- 2001–2005, log da incidência: I = 0,231; p = 0,001.

Isso é importante. A incidência bruta paulista no início da série parece dominada por ruído, valores extremos e instabilidade local, mas a transformação logarítmica revela estrutura espacial. A partir de 2006–2010, a incidência bruta em SP passa a apresentar Moran positivo e significativo:

- 2006–2010: I = 0,190; p = 0,001.

### 9.5. Séries anuais de Moran Global

O notebook gera três gráficos anuais:

- Moran Global anual da incidência bruta;
- Moran Global anual da incidência média móvel de 3 anos;
- Moran Global anual do log da incidência.

A leitura visual dos gráficos indica:

- no RJ, a autocorrelação espacial da incidência aumenta no início da série, atinge valores altos por volta da segunda metade dos anos 2000 e depois declina;
- em SP, a autocorrelação da incidência bruta é mais baixa, mas se mantém positiva em boa parte da série;
- a média móvel de 3 anos suaviza oscilações e torna a trajetória do Moran mais legível;
- o log da incidência reduz a dominância de valores extremos e revela estrutura espacial em SP de forma mais clara.

### Conclusão do Moran Global

O Moran Global confirma que há dependência espacial. Assim, modelos que assumem independência entre municípios seriam metodologicamente frágeis. Para a etapa bayesiana, isso justifica a inclusão de componente espacial estruturado, como BYM2.

---

## 10. LISA — Indicadores Locais de Associação Espacial

### 10.1. Método

O LISA identifica onde a autocorrelação espacial ocorre. Enquanto o Moran Global resume o padrão espacial em um único número, o LISA classifica municípios conforme sua relação com os vizinhos.

As classes utilizadas são:

- **Alto-Alto:** município com valor alto cercado por municípios de valores altos;
- **Baixo-Baixo:** município com valor baixo cercado por municípios de valores baixos;
- **Alto-Baixo:** município com valor alto cercado por municípios de valores baixos;
- **Baixo-Alto:** município com valor baixo cercado por municípios de valores altos;
- **Não significativo:** sem associação local estatisticamente significativa a 5%.

### 10.2. LISA para o período completo

O notebook produz mapas LISA para:

- RJ, incidência do período 2001–2024;
- RJ, log da incidência do período;
- SP, incidência do período 2001–2024;
- SP, log da incidência do período.

A leitura dos mapas indica padrões locais consistentes com os resultados do Moran Global.

No **Rio de Janeiro**, os clusters Alto-Alto aparecem de forma mais territorialmente concentrada. Isso é compatível com a forte autocorrelação global observada. A região metropolitana e áreas urbanizadas/litorâneas parecem concentrar maior parte dos agrupamentos de alta incidência, enquanto áreas interiores aparecem com maior frequência como Baixo-Baixo ou não significativas.

Em **São Paulo**, os agrupamentos são mais fragmentados. Há presença de clusters Alto-Alto, mas eles aparecem em áreas mais dispersas, com influência de regiões metropolitanas, litoral e alguns polos regionais. A maior quantidade de municípios em SP produz um mosaico espacial mais complexo, com muitos municípios não significativos e vários outliers locais.

### 10.3. LISA por anos selecionados

O notebook gera mapas LISA para os anos:

- 2001;
- 2005;
- 2010;
- 2015;
- 2019;
- 2020;
- 2024.

Para cada ano, são avaliadas:

- incidência anual bruta;
- incidência média móvel de 3 anos.

A comparação entre incidência bruta e média móvel é importante:

- a incidência bruta captura o ano específico, mas é mais sensível a flutuações;
- a média móvel reduz ruído e destaca padrões mais persistentes.

### 10.4. Interpretação dos mapas anuais

No RJ, os mapas anuais mostram que os clusters de alta incidência não são aleatórios. A região de maior risco local tende a persistir em parte da série, embora sua extensão varie conforme o ano e conforme se usa incidência bruta ou média móvel.

Em SP, os mapas anuais mostram maior dispersão dos agrupamentos locais. Isso está de acordo com a estrutura territorial do estado: muitos municípios, grande heterogeneidade populacional, regiões metropolitanas, áreas litorâneas, municípios pequenos e polos regionais com padrões diferentes.

O notebook exibe uma tabela resumida das classes LISA, mas a visualização impressa no notebook aparece truncada. Ainda assim, a prévia mostra, por exemplo:

- RJ em 2001, incidência bruta: 7 municípios Alto-Alto, 7 Baixo-Baixo, 4 Baixo-Alto e 74 não significativos;
- SP em 2024, média móvel de 3 anos: 17 Alto-Alto, 8 Alto-Baixo, 22 Baixo-Alto, 58 Baixo-Baixo e 540 não significativos.

Esses números ilustram uma diferença importante: em SP, mesmo quando há muitos municípios classificados em padrões locais, a maior parte permanece não significativa. Isso é esperado em um estado com 645 municípios e grande heterogeneidade municipal.

### Conclusão do LISA

O LISA confirma que a dependência espacial não é uniforme no território. Existem áreas específicas de concentração local de risco e áreas de baixa ocorrência. Portanto, a modelagem bayesiana não deve apenas estimar um efeito estadual médio; ela precisa permitir variação espacial municipal.

---

## 11. Getis-Ord Gi\*

### 11.1. Método

A estatística Getis-Ord Gi\* identifica concentração local de valores altos ou baixos. Diferentemente do LISA, que classifica combinações entre valor do município e valor dos vizinhos, o Gi\* procura regiões onde os valores altos ou baixos se acumulam espacialmente.

As classes usadas no notebook são:

- **Hot spot:** área quente, concentração significativa de valores altos;
- **Cold spot:** área fria, concentração significativa de valores baixos;
- **Não significativo:** ausência de concentração local estatisticamente significativa.

### 11.2. Resumo dos resultados Gi\*

O notebook gerou o seguinte resumo completo das classes Gi\*:

| estado_analise   | contexto_analise   | variavel_analise                     |   Hot spot |   Cold spot |   Não significativo |
|:-----------------|:-------------------|:-------------------------------------|-----------:|------------:|--------------------:|
| RJ               | 2001               | incidencia_ma3                       |         10 |           7 |                  75 |
| RJ               | 2001–2024          | incidencia_periodo_100mil_pessoa_ano |         14 |          10 |                  68 |
| RJ               | 2001–2024          | log_inc_periodo_mais1                |         14 |           4 |                  74 |
| RJ               | 2005               | incidencia_ma3                       |         15 |          11 |                  66 |
| RJ               | 2010               | incidencia_ma3                       |         13 |           8 |                  71 |
| RJ               | 2015               | incidencia_ma3                       |         11 |           6 |                  75 |
| RJ               | 2019               | incidencia_ma3                       |         12 |           5 |                  75 |
| RJ               | 2020               | incidencia_ma3                       |          9 |           7 |                  76 |
| RJ               | 2024               | incidencia_ma3                       |         10 |           8 |                  74 |
| SP               | 2001               | incidencia_ma3                       |         48 |          50 |                 547 |
| SP               | 2001–2024          | incidencia_periodo_100mil_pessoa_ano |         41 |          67 |                 537 |
| SP               | 2001–2024          | log_inc_periodo_mais1                |         74 |          60 |                 511 |
| SP               | 2005               | incidencia_ma3                       |         48 |          54 |                 543 |
| SP               | 2010               | incidencia_ma3                       |         40 |          49 |                 556 |
| SP               | 2015               | incidencia_ma3                       |         36 |          60 |                 549 |
| SP               | 2019               | incidencia_ma3                       |         37 |          58 |                 550 |
| SP               | 2020               | incidencia_ma3                       |         38 |          66 |                 541 |
| SP               | 2024               | incidencia_ma3                       |         40 |          55 |                 550 |

### 11.3. Interpretação para o Rio de Janeiro

No período completo 2001–2024, o RJ apresenta:

- 14 hot spots para incidência do período;
- 10 cold spots para incidência do período;
- 14 hot spots para log da incidência;
- 4 cold spots para log da incidência.

A leitura dos mapas indica concentração de áreas quentes em torno do eixo metropolitano/urbano-litorâneo e áreas frias mais associadas ao interior. Esse padrão é epidemiologicamente plausível, pois a tuberculose tende a se concentrar em territórios com maior densidade populacional, vulnerabilidade social, circulação de pessoas e desigualdade urbana.

Nos anos selecionados, os hot spots no RJ variam entre aproximadamente 9 e 15 municípios, dependendo do ano. Isso indica persistência relativa de áreas quentes, mas também alguma mudança temporal.

### 11.4. Interpretação para São Paulo

Em SP, para o período completo:

- incidência do período: 41 hot spots, 67 cold spots;
- log da incidência do período: 74 hot spots, 60 cold spots.

O aumento de hot spots quando se usa log da incidência indica que a transformação reduz a dominância de grandes extremos e torna mais visíveis agrupamentos de incidência elevada em municípios que talvez fossem mascarados pela escala original.

Nos mapas, os hot spots aparecem de forma mais dispersa do que no RJ. Essa dispersão é coerente com a estrutura territorial paulista, que combina grandes regiões metropolitanas, litoral, interior industrializado, áreas rurais e municípios pequenos. Os cold spots também são numerosos, sugerindo regiões com baixa ocorrência relativa persistente.

### Conclusão do Gi\*

O Gi\* reforça que há áreas quentes e frias espacialmente organizadas, não apenas municípios isolados. Para planejamento em saúde pública, essa informação é útil porque direciona a leitura para conjuntos territoriais e não apenas para rankings municipais.

---

## 12. Mapas numéricos das variáveis usadas

O notebook também gera mapas contínuos das variáveis:

- incidência do período por 100 mil pessoa-ano;
- log da incidência do período;
- log dos casos acumulados.

### Interpretação

Esses mapas cumprem função diagnóstica. Eles permitem visualizar a distribuição espacial das variáveis antes da classificação por LISA ou Gi\*. A comparação entre incidência e casos acumulados é essencial:

- **casos acumulados** tendem a destacar municípios populosos;
- **incidência** destaca intensidade relativa da doença;
- **logaritmo** reduz a influência de valores extremos e melhora a visualização de padrões intermediários.

No RJ, a incidência do período mostra maior concentração em áreas urbanas/metropolitanas, enquanto os casos acumulados enfatizam fortemente os municípios com maior população e maior volume absoluto de notificações.

Em SP, o mapa de casos acumulados destaca áreas de maior população e maior densidade urbana, enquanto a incidência evidencia municípios ou regiões onde o risco relativo é mais elevado, independentemente do tamanho populacional.

---

## 13. Produtos exportados pelo notebook

O notebook salva os resultados em uma pasta específica da seção 5.7:

`saida_exploratoria_TB/secao_5_7_analise_exploratoria_espacial`

Foram exportados:

- painel reconstruído;
- base municipal do período completo;
- base municipal por períodos;
- resumo da matriz de vizinhança queen;
- edgelist de vizinhança;
- tabela de Moran Global;
- tabelas LISA em CSV e GeoJSON;
- tabelas Getis-Ord Gi\* em CSV e GeoJSON;
- mapas de vizinhança;
- séries temporais do Moran Global;
- mapas LISA;
- mapas Gi\*;
- mapas numéricos das variáveis;
- arquivo Excel principal com abas de resumo.

O arquivo Excel final gerado pelo notebook foi:

`secao_5_7_analise_exploratoria_espacial.xlsx`

Esse arquivo é importante porque consolida os principais produtos tabulares da seção.

---

## 14. Principais achados epidemiológicos

### 14.1. Rio de Janeiro

O RJ apresenta padrão espacial mais forte e mais compacto. A autocorrelação global da incidência é alta no período completo e permanece significativa em todos os blocos temporais exibidos. Os mapas LISA e Gi\* indicam persistência de áreas de maior ocorrência, compatíveis com concentração urbana e metropolitana da tuberculose.

A redução do Moran ao longo dos blocos mais recentes pode sugerir mudanças na distribuição espacial, mas isso deve ser interpretado com cautela. Pode refletir mudanças reais na dinâmica da doença, alterações na notificação, efeitos da pandemia, mudanças populacionais ou instabilidade em municípios específicos.

### 14.2. São Paulo

SP apresenta padrão espacial significativo, mas mais heterogêneo. A incidência bruta nem sempre mostra autocorrelação forte, especialmente no início da série. No entanto, as transformações logarítmicas e os casos acumulados apresentam Moran positivo e significativo, indicando que existe estrutura espacial, embora ela seja mais sensível à escala da variável.

Os mapas indicam clusters e hotspots mais distribuídos, não concentrados em uma única grande região. Isso combina com a complexidade territorial do estado, com múltiplos polos urbanos, litoral, regiões metropolitanas, interior heterogêneo e muitos municípios pequenos.

---

## 15. Implicações para a modelagem bayesiana

A análise exploratória espacial sustenta diretamente as decisões metodológicas do projeto.

### 15.1. Inclusão de componente espacial estruturado

Como há autocorrelação espacial significativa, os modelos devem incluir componente espacial estruturado. A parametrização **BYM2** é adequada porque combina:

- efeito espacial estruturado, associado à vizinhança;
- efeito não estruturado, associado à heterogeneidade municipal não explicada pela adjacência.

### 15.2. Modelagem separada por estado

Os resultados reforçam que SP e RJ devem ser modelados separadamente. O RJ apresenta estrutura espacial mais compacta e forte; SP apresenta estrutura mais fragmentada, maior número de municípios, presença de ilha na matriz queen e maior heterogeneidade.

Forçar um único modelo espacial conjunto para os dois estados poderia misturar processos territoriais distintos e dificultar a interpretação dos efeitos.

### 15.3. Cuidado com Ilhabela em SP

A ilha espacial de SP deve ser tratada explicitamente. Para o modelo BYM2, é necessário verificar como o INLA lida com esse grafo desconectado. A recomendação é manter registro da ilha e executar análise de sensibilidade com matriz alternativa, se necessário.

### 15.4. Uso de taxas observadas apenas como etapa exploratória

As taxas observadas são instáveis em municípios pequenos. A modelagem bayesiana deve produzir riscos suavizados, que serão mais adequados para interpretação final do que as taxas brutas e os mapas exploratórios.

---

## 16. Limitações da análise exploratória

A análise é adequada para diagnóstico espacial, mas tem limitações:

1. **Não corrige múltiplos testes locais.** LISA e Gi\* geram muitos testes simultâneos; os resultados devem ser interpretados como exploratórios.
2. **Depende da matriz de vizinhança.** O critério queen pode gerar ilhas e pode considerar como vizinhos municípios que tocam apenas em vértices.
3. **Taxas brutas são instáveis.** Municípios pequenos podem apresentar incidência elevada por poucos casos.
4. **Não ajusta covariáveis.** Os mapas mostram padrões espaciais, mas não explicam causalmente esses padrões.
5. **Não substitui o modelo espaço-temporal.** A análise exploratória orienta a modelagem, mas os resultados finais devem vir dos modelos bayesianos ajustados.

---

## 17. Recomendações para a próxima etapa

1. Manter a matriz queen como estrutura espacial principal, mas documentar a ilha de SP.
2. Testar análise de sensibilidade com k-vizinhos mais próximos ou conexão manual justificada para Ilhabela.
3. Usar BYM2 como componente espacial candidato principal.
4. Ajustar modelos separadamente para RJ e SP.
5. Usar mapas LISA e Gi\* como diagnóstico exploratório, não como resultado inferencial final.
6. Comparar os mapas exploratórios com os riscos suavizados posteriores dos modelos bayesianos.
7. Avaliar se os hotspots persistentes coincidem com regiões de vulnerabilidade social, densidade urbana, cobertura assistencial ou características programáticas.
8. Para apresentação em dissertação ou artigo, priorizar mapas do período completo e poucos anos sentinela, evitando excesso de figuras.

---

## 18. Conclusão geral

O notebook executa corretamente uma análise exploratória espacial robusta para a tuberculose em SP e RJ entre 2001 e 2024. Ele demonstra que a doença apresenta padrões espaciais não aleatórios, com autocorrelação global significativa, agrupamentos locais e áreas quentes/frias nos dois estados.

O Rio de Janeiro apresenta padrão espacial mais forte e concentrado, enquanto São Paulo apresenta padrão mais heterogêneo e fragmentado. Esses achados são coerentes com as diferenças territoriais, demográficas e epidemiológicas entre os estados.

A principal implicação metodológica é clara: a modelagem final deve incorporar estrutura espacial e deve ser conduzida separadamente por estado. Os resultados justificam o uso de modelos bayesianos espaço-temporais com componente espacial estruturado, preferencialmente BYM2, e reforçam a necessidade de interpretação cuidadosa das taxas municipais brutas.

Em termos epidemiológicos, a análise identifica que a tuberculose não se distribui aleatoriamente no território. Existem regiões persistentes de maior e menor ocorrência, o que reforça a relevância de abordagens territorializadas para vigilância, planejamento e controle da doença.
