# -*- coding: utf-8 -*-
"""Calcula LISA (Moran local, Anselin 1995) com permutacao condicional (999),
classifica em Alto-Alto/Baixo-Baixo/Alto-Baixo/Baixo-Alto/Nao significativo
e VALIDA: media dos I_i deve reproduzir o Moran global publicado."""
import os, numpy as np, pandas as pd

SEC = os.path.join("Análise exploratória espacial", "secao_5_7_analise_exploratoria_espacial")
base = pd.read_csv(os.path.join(SEC, "base_municipal_periodo_total.csv"))
base["cod_mun6"] = base.cod_mun6.astype(str).str.zfill(6)
ar = pd.read_csv(os.path.join(SEC, "arestas_matriz_vizinhanca_queen.csv"))
for c in ("origem", "destino"):
    ar[c] = ar[c].astype(str).str.extract(r"(\d{6})")[0]

V = "incidencia_periodo_100mil_pessoa_ano"
PERMS, SEED, ALPHA = 999, 20260824, 0.05
GLOBAL_PUB = {"RJ": 0.405, "SP": 0.133}       # valores ja validados

def lisa(uf):
    b = base[base.estado == uf].reset_index(drop=True)
    codes = b.cod_mun6.tolist(); idx = {c: i for i, c in enumerate(codes)}
    n = len(codes)
    viz = [[] for _ in range(n)]
    sub = ar[ar.origem.isin(idx) & ar.destino.isin(idx)]
    for o, d in zip(sub.origem, sub.destino):
        viz[idx[o]].append(idx[d])

    x = b[V].to_numpy(float)
    z = x - x.mean()
    m2 = (z ** 2).sum() / n

    lag = np.array([z[v].mean() if v else 0.0 for v in viz])   # w row-standardized
    Ii = z * lag / m2

    # validacao: media dos I_i == Moran global
    print(f"  [{uf}] média(I_i)={Ii.mean():.3f}  (global publicado={GLOBAL_PUB[uf]})")

    # permutacao condicional
    rng = np.random.default_rng(SEED)
    p = np.ones(n)
    for i in range(n):
        k = len(viz[i])
        if k == 0:
            continue
        pool = np.delete(z, i)
        sim = rng.choice(pool, size=(PERMS, k), replace=True).mean(axis=1)
        Isim = z[i] * sim / m2
        maior = (Isim >= Ii[i]).sum()
        if maior > PERMS / 2:
            maior = PERMS - maior
        p[i] = (maior + 1) / (PERMS + 1)

    cl = np.full(n, "Não significativo", dtype=object)
    sig = (p <= ALPHA) & np.array([len(v) > 0 for v in viz])
    cl[sig & (z > 0) & (lag > 0)] = "Alto-Alto"
    cl[sig & (z < 0) & (lag < 0)] = "Baixo-Baixo"
    cl[sig & (z > 0) & (lag < 0)] = "Alto-Baixo"
    cl[sig & (z < 0) & (lag > 0)] = "Baixo-Alto"

    out = pd.DataFrame({"cod_mun6": codes, "municipio": b.municipio,
                        "incidencia": x, "lisa_I": Ii, "lisa_p": p, "classe_lisa": cl})
    f = os.path.join(SEC, f"lisa_{uf}_incidencia_periodo_100mil_pessoa_ano_2001_2024.csv")
    out.to_csv(f, index=False, encoding="utf-8-sig")
    print("   ", out.classe_lisa.value_counts().to_dict())
    return out

print("LISA — permutação condicional, 999 sorteios:")
res = {uf: lisa(uf) for uf in ("RJ", "SP")}
print("\nAlto-Alto no RJ:", ", ".join(res["RJ"].query("classe_lisa=='Alto-Alto'").municipio.head(12)))
print("Alto-Alto em SP:", ", ".join(res["SP"].query("classe_lisa=='Alto-Alto'").municipio.head(12)))
