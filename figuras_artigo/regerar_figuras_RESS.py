# -*- coding: utf-8 -*-
"""
Regera as 3 figuras do artigo RESS em formato VETORIAL (PDF/SVG), com:
  - escala de cor COMUM entre SP e RJ (Figura 1)  -> exigência da norma
  - legenda ÚNICA para o mosaico
  - seta de Norte e barra de escala
  - sem título embutido (o título vai na legenda da figura, no documento)

RODAR NO AMBIENTE DO NOTEBOOK (precisa de geopandas/matplotlib).
    python regerar_figuras_RESS.py
"""
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
import matplotlib as mpl

mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "pdf.fonttype": 42, "svg.fonttype": "none"})

BASE = r"C:\Users\Vitor\Claude\Tuberculose Bioestatistica"
SEC  = os.path.join(BASE, "Análise exploratória espacial", "secao_5_7_analise_exploratoria_espacial")
GEO  = {"SP": os.path.join(BASE, "DADOS-BASE-MAPA", "SP_geojs-35-mun.json"),
        "RJ": os.path.join(BASE, "DADOS-BASE-MAPA", "RJ_geojs-33-mun.json")}
OUT  = os.path.join(BASE, "figuras_artigo")
os.makedirs(OUT, exist_ok=True)

# ---------- dados ----------
base = pd.read_csv(os.path.join(SEC, "base_municipal_periodo_total.csv"))
base["cod_mun6"] = base.cod_mun6.astype(str).str.zfill(6)

def carrega(uf, extra_csv=None, cols=None):
    g = gpd.read_file(GEO[uf])
    g["cod_mun6"] = g["id"].astype(str).str[:6]
    d = base[base.estado == uf]
    g = g.merge(d, on="cod_mun6", how="left")
    if extra_csv:
        e = pd.read_csv(os.path.join(SEC, extra_csv))
        e["cod_mun6"] = e.cod_mun6.astype(str).str.zfill(6)
        g = g.merge(e[["cod_mun6"] + cols], on="cod_mun6", how="left")
    return g.set_crs("EPSG:4674", allow_override=True)

def norte(ax, x=0.06, y=0.92, s=0.055):
    ax.annotate("N", xy=(x, y), xytext=(x, y - s), xycoords="axes fraction",
                ha="center", va="center", fontsize=9, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2))

def barra_escala(ax, gdf, frac=0.28):
    """Barra de escala em km, calculada na projeção métrica (UTM local)."""
    m = gdf.to_crs(gdf.estimate_utm_crs())
    x0, y0, x1, y1 = m.total_bounds
    alvo = (x1 - x0) * frac / 1000.0
    passo = min([1, 2, 5, 10, 20, 25, 50, 100, 150, 200, 250, 500],
                key=lambda v: abs(v - alvo))
    # converte o comprimento de volta p/ coordenadas do eixo (graus)
    gx0, gy0, gx1, gy1 = gdf.total_bounds
    frac_eixo = (passo * 1000.0) / (x1 - x0)
    L = (gx1 - gx0) * frac_eixo
    xa = gx0 + (gx1 - gx0) * 0.06
    ya = gy0 + (gy1 - gy0) * 0.06
    h = (gy1 - gy0) * 0.010
    ax.add_patch(plt.Rectangle((xa, ya), L, h, facecolor="k", edgecolor="k"))
    ax.text(xa + L / 2, ya + h * 1.9, f"{passo} km", ha="center", va="bottom", fontsize=8)

def limpa(ax):
    ax.set_axis_off()

# ============ FIGURA 1 — incidência com ESCALA COMUM ============
gsp, grj = carrega("SP"), carrega("RJ")
V = "incidencia_periodo_100mil_pessoa_ano"
todos = pd.concat([gsp[V], grj[V]]).dropna()
# classes por quantil COMUM (robusto ao outlier de Balbinos)
qs = [0, .20, .40, .60, .80, .95, 1.0]
bins = np.unique(np.quantile(todos, qs))
cmap = plt.get_cmap("YlOrRd", len(bins) - 1)
norm = BoundaryNorm(bins, cmap.N)

fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.4))
for ax, g, rot in zip(axes, [gsp, grj], ["(A)", "(B)"]):
    g.plot(column=V, cmap=cmap, norm=norm, edgecolor="0.4", linewidth=0.12, ax=ax)
    limpa(ax); norte(ax); barra_escala(ax, g)
    ax.set_title(rot, loc="left", fontweight="bold", fontsize=10)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cb = fig.colorbar(sm, ax=axes, orientation="horizontal", fraction=0.045, pad=0.04,
                  ticks=bins, format="%.0f")
cb.set_label("Incidência por 100 mil pessoas-ano")   # LEGENDA ÚNICA
for ext in ("pdf", "svg"):
    fig.savefig(os.path.join(OUT, f"Figura1_incidencia.{ext}"), bbox_inches="tight")
plt.close(fig)
print("Figura 1 OK — escala comum:", np.round(bins, 1))

# ============ FIGURAS 2 e 3 — LISA e Gi* (categóricos) ============
def mosaico_categorico(csv_tpl, coluna, ordem, cores, nome):
    gs = {uf: carrega(uf, csv_tpl.format(uf=uf), [coluna]) for uf in ("SP", "RJ")}
    cmap = ListedColormap([cores[c] for c in ordem])
    fig, axes = plt.subplots(2, 1, figsize=(5.6, 7.2))
    for ax, uf, rot in zip(axes, ("SP", "RJ"), ("(A)", "(B)")):
        g = gs[uf].copy()
        g["_k"] = pd.Categorical(g[coluna], categories=ordem).codes
        g.plot(column="_k", cmap=cmap, vmin=0, vmax=len(ordem) - 1,
               edgecolor="0.4", linewidth=0.12, ax=ax)
        limpa(ax); norte(ax); barra_escala(ax, g)
        ax.set_title(rot, loc="left", fontweight="bold", fontsize=10)
    fig.legend(handles=[Patch(facecolor=cores[c], edgecolor="0.3", label=c) for c in ordem],
               loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
    for ext in ("pdf", "svg"):
        fig.savefig(os.path.join(OUT, f"{nome}.{ext}"), bbox_inches="tight")
    plt.close(fig)
    print(f"{nome} OK")

LISA_ORD = ["Alto-Alto", "Alto-Baixo", "Baixo-Alto", "Baixo-Baixo", "Não significativo"]
LISA_COR = {"Alto-Alto": "#b2182b", "Alto-Baixo": "#ef8a62", "Baixo-Alto": "#67a9cf",
            "Baixo-Baixo": "#2166ac", "Não significativo": "#f0f0f0"}
GI_ORD = ["Hot spot", "Cold spot", "Não significativo"]
GI_COR = {"Hot spot": "#b2182b", "Cold spot": "#2166ac", "Não significativo": "#f0f0f0"}

# ATENÇÃO: confira os nomes dos CSVs de LISA no seu diretório (o Gi* está exportado;
# o LISA pode estar apenas no notebook — nesse caso, exporte-o antes de rodar).
mosaico_categorico("lisa_{uf}_incidencia_periodo_100mil_pessoa_ano_2001_2024.csv",
                   "classe_lisa", LISA_ORD, LISA_COR, "Figura2_LISA")
mosaico_categorico("getis_ord_gi_{uf}_incidencia_periodo_100mil_pessoa_ano_2001_2024.csv",
                   "classe_gi", GI_ORD, GI_COR, "Figura3_GetisOrd")

print("\nArquivos PDF/SVG em:", OUT)
