# -*- coding: utf-8 -*-
"""
Figuras do artigo RESS SEM geopandas (le o GeoJSON com json puro).
Requer apenas numpy, pandas, matplotlib.

- Figura 1: incidencia do periodo, ESCALA DE COR COMUM a SP e RJ (quantis), colorbar unica
- Figura 3: Getis-Ord Gi* (categorico), legenda unica
- Elementos cartograficos numa FAIXA reservada abaixo do mapa (nao sobrepoe os estados):
  barra de escala (km) a esquerda e seta de Norte a direita.
Saidas: PDF, SVG e PNG.
"""
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.collections import PathCollection
from matplotlib.colors import BoundaryNorm
from matplotlib.patches import Patch, Rectangle, Polygon
import matplotlib as mpl

mpl.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "svg.fonttype": "none"})

BASE = r"C:\Users\Vitor\Claude\Tuberculose Bioestatistica"
SEC  = os.path.join(BASE, "Análise exploratória espacial", "secao_5_7_analise_exploratoria_espacial")
GEO  = {"SP": os.path.join(BASE, "DADOS-BASE-MAPA", "SP_geojs-35-mun.json"),
        "RJ": os.path.join(BASE, "DADOS-BASE-MAPA", "RJ_geojs-33-mun.json")}
OUT  = os.path.join(BASE, "figuras_artigo")
os.makedirs(OUT, exist_ok=True)

BAND = 0.17          # altura da faixa de elementos cartograficos (fracao da altura do mapa)

# ---------------- geometria ----------------
def rings_of(g):
    """TODOS os aneis. Neste GeoJSON os aneis extras sao PARTES SEPARADAS (ilhas:
    Ilha Grande, Ilhabela, Bertioga, Cananeia...), nao buracos — verificado:
    0 aneis internos no RJ, 1 minusculo em SP (Sao Pedro, 0,5% da area)."""
    t, c = g["type"], g["coordinates"]
    if t == "Polygon":
        return list(c)
    return [r for poly in c for r in poly]

def load_geo(uf):
    gj = json.load(open(GEO[uf], encoding="utf-8"))
    out = []
    for f in gj["features"]:
        code = str(f["properties"]["id"])[:6]
        for r in rings_of(f["geometry"]):
            out.append((code, np.asarray(r, float)))
    return out

def plot_uf(ax, recs, cor_de):
    """Desenha os municipios; cor_de(code) -> cor. Reserva faixa inferior."""
    paths = [Path(xy) for _, xy in recs]
    cols  = [cor_de(code) for code, _ in recs]
    ax.add_collection(PathCollection(paths, facecolors=cols,
                                     edgecolors="0.35", linewidths=0.12))
    allxy = np.vstack([xy for _, xy in recs])
    x0, y0 = allxy.min(axis=0); x1, y1 = allxy.max(axis=0)
    dx, dy = x1 - x0, y1 - y0
    ax.set_xlim(x0 - dx * 0.03, x1 + dx * 0.03)
    ax.set_ylim(y0 - dy * BAND, y1 + dy * 0.04)      # <-- faixa livre embaixo
    lat = (y0 + y1) / 2
    ax.set_aspect(1.0 / np.cos(np.radians(abs(lat))))
    ax.set_axis_off()
    return dict(x0=x0, y0=y0, x1=x1, y1=y1, lat=lat)

# --------- elementos cartograficos (dentro da faixa inferior) ---------
def barra_escala(ax, ext, frac=0.26):
    km_grau = 111.320 * np.cos(np.radians(abs(ext["lat"])))
    xa_lim, xb_lim = ax.get_xlim(); ya_lim, yb_lim = ax.get_ylim()
    largura = xb_lim - xa_lim
    alvo = largura * km_grau * frac
    passo = min([25, 50, 100, 150, 200, 250, 300, 400, 500],
                key=lambda v: abs(v - alvo))
    L = passo / km_grau
    xa = xa_lim + largura * 0.03
    yb = ya_lim + (yb_lim - ya_lim) * 0.045          # dentro da faixa
    h  = (yb_lim - ya_lim) * 0.012
    # barra bicolor (padrao cartografico)
    ax.add_patch(Rectangle((xa, yb), L / 2, h, facecolor="k", edgecolor="k", lw=0.6, zorder=6))
    ax.add_patch(Rectangle((xa + L / 2, yb), L / 2, h, facecolor="w", edgecolor="k", lw=0.6, zorder=6))
    ax.text(xa, yb + h * 1.6, "0", ha="center", va="bottom", fontsize=7)
    ax.text(xa + L, yb + h * 1.6, f"{passo} km", ha="center", va="bottom", fontsize=7)
    return (xa + L - xa_lim) / largura          # fracao onde a barra termina

def seta_norte(ax, xfrac=0.40):
    """Seta compacta com N acima, ancorada ao lado da barra de escala."""
    xa, xb = ax.get_xlim(); ya, yb = ax.get_ylim()
    W, H = xb - xa, yb - ya
    cx = xa + W * xfrac
    base = ya + H * 0.030
    alt  = H * 0.085
    meia = W * 0.016
    ax.add_patch(Polygon([[cx, base + alt], [cx - meia, base], [cx, base + alt * 0.28],
                          [cx + meia, base]], closed=True,
                         facecolor="k", edgecolor="k", lw=0.5, zorder=6))
    ax.text(cx, base + alt * 1.15, "N", ha="center", va="bottom",
            fontsize=8.5, fontweight="bold", zorder=6)

def rotulo(ax, txt):
    ax.text(0.0, 1.0, txt, transform=ax.transAxes, ha="left", va="top",
            fontweight="bold", fontsize=11)

# ---------------- dados ----------------
base = pd.read_csv(os.path.join(SEC, "base_municipal_periodo_total.csv"))
base["cod_mun6"] = base.cod_mun6.astype(str).str.zfill(6)
V = "incidencia_periodo_100mil_pessoa_ano"
vals = {uf: dict(zip(base[base.estado == uf].cod_mun6, base[base.estado == uf][V]))
        for uf in ("SP", "RJ")}

qs = [0, .20, .40, .60, .80, .95, 1.0]
bins = np.unique(np.quantile(base[V].dropna().values, qs)).round(1)
cmap = plt.get_cmap("YlOrRd", len(bins) - 1)
norm = BoundaryNorm(bins, cmap.N)
print("Classes comuns (quantis):", list(bins))

# ---------------- FIGURA 1 ----------------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.9))
for ax, uf, rot in zip(axes, ("SP", "RJ"), ("(A)", "(B)")):
    recs = load_geo(uf); v = vals[uf]
    def cor(code, v=v):
        x = v.get(code, np.nan)
        return "#d9d9d9" if x is None or (isinstance(x, float) and np.isnan(x)) else cmap(norm(x))
    ext = plot_uf(ax, recs, cor)
    fim = barra_escala(ax, ext); seta_norte(ax, fim + 0.09); rotulo(ax, rot)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
cb = fig.colorbar(sm, ax=axes, orientation="horizontal", fraction=0.045, pad=0.03, ticks=bins)
cb.ax.set_xticklabels([f"{b:.0f}" for b in bins]); cb.ax.tick_params(labelsize=8)
cb.set_label("Incidência de tuberculose por 100 mil pessoas-ano", fontsize=9)
for e in ("pdf", "svg", "png"):
    fig.savefig(os.path.join(OUT, f"Figura1_incidencia_escala_comum.{e}"),
                bbox_inches="tight", dpi=300)
plt.close(fig); print("Figura 1 OK")

# ---------------- FIGURA 3 (Gi*) ----------------
GI_ORD = ["Hot spot", "Cold spot", "Não significativo"]
GI_COR = {"Hot spot": "#b2182b", "Cold spot": "#2166ac", "Não significativo": "#f0f0f0"}
gi = {}
for uf in ("SP", "RJ"):
    d = pd.read_csv(os.path.join(
        SEC, f"getis_ord_gi_{uf}_incidencia_periodo_100mil_pessoa_ano_2001_2024.csv"))
    d["cod_mun6"] = d.cod_mun6.astype(str).str.zfill(6)
    gi[uf] = dict(zip(d.cod_mun6, d.classe_gi))

fig, axes = plt.subplots(2, 1, figsize=(5.4, 7.4))
for ax, uf, rot in zip(axes, ("SP", "RJ"), ("(A)", "(B)")):
    recs = load_geo(uf); g = gi[uf]
    ext = plot_uf(ax, recs, lambda c, g=g: GI_COR.get(g.get(c), "#d9d9d9"))
    fim = barra_escala(ax, ext); seta_norte(ax, fim + 0.09); rotulo(ax, rot)
fig.legend(handles=[Patch(facecolor=GI_COR[c], edgecolor="0.3", label=c) for c in GI_ORD],
           loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.015), fontsize=8.5)
for e in ("pdf", "svg", "png"):
    fig.savefig(os.path.join(OUT, f"Figura3_getis_ord.{e}"), bbox_inches="tight", dpi=300)
plt.close(fig); print("Figura 3 OK")

# ---------------- FIGURA 2 (LISA) ----------------
LI_ORD = ["Alto-Alto", "Baixo-Baixo", "Alto-Baixo", "Baixo-Alto", "Não significativo"]
LI_COR = {"Alto-Alto": "#b2182b", "Baixo-Baixo": "#2166ac", "Alto-Baixo": "#ef8a62",
          "Baixo-Alto": "#67a9cf", "Não significativo": "#f0f0f0"}
li = {}
for uf in ("SP", "RJ"):
    d = pd.read_csv(os.path.join(
        SEC, f"lisa_{uf}_incidencia_periodo_100mil_pessoa_ano_2001_2024.csv"))
    d["cod_mun6"] = d.cod_mun6.astype(str).str.zfill(6)
    li[uf] = dict(zip(d.cod_mun6, d.classe_lisa))

fig, axes = plt.subplots(2, 1, figsize=(5.4, 7.4))
for ax, uf, rot in zip(axes, ("SP", "RJ"), ("(A)", "(B)")):
    recs = load_geo(uf); g = li[uf]
    ext = plot_uf(ax, recs, lambda c, g=g: LI_COR.get(g.get(c), "#d9d9d9"))
    fim = barra_escala(ax, ext); seta_norte(ax, fim + 0.09); rotulo(ax, rot)
fig.legend(handles=[Patch(facecolor=LI_COR[c], edgecolor="0.3", label=c) for c in LI_ORD],
           loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.005), fontsize=8.5)
for e in ("pdf", "svg", "png"):
    fig.savefig(os.path.join(OUT, f"Figura2_lisa.{e}"), bbox_inches="tight", dpi=300)
plt.close(fig); print("Figura 2 OK")
