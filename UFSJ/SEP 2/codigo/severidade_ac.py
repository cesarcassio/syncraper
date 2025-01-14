# ruff: noqa: F403, F405 #apenas corrige um erro de extensão do vscode
import pandas as pd
from modules import *

DBAR, DCIR, SAVEPATH, FILEPATH = dados("dados\\dados_sistema13B_EC3_CasoBase.txt")
# DBAR, DCIR, SAVEPATH, FILEPATH = dados("dados\\L2_6B_CasoBase.txt")
# DBAR, DCIR, SAVEPATH, FILEPATH = dados("dados\dados_sistema6B_ATIV.txt")

severidade = []
circuito_removido = []
circuitos_sobrecarregados = []
DSER = pd.DataFrame(columns=["Circ. Removido", "Severidade", "Circ. Sobrecarregado"])

for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
    DBAR, DCIR, _, _ = dados(FILEPATH + ".txt")
    DCIR.loc[i, "LIG(L)DESL(D)"] = "D"
    srv, circs = flow_ac(DBAR, DCIR)
    circuito_removido.append(DCIR.loc[i, "NCIR"])
    circuitos_sobrecarregados.append(circs)
    severidade.append(float(srv))
    DCIR.loc[i, "LIG(L)DESL(D)"] = "L"
# print(DCIR)
DSER["Circ. Removido"] = circuito_removido
DSER["Severidade"] = severidade
DSER["Circ. Sobrecarregado"] = circuitos_sobrecarregados
DSER["Circ. Sobrecarregado"] = DSER["Circ. Sobrecarregado"].apply(
    lambda x: ", ".join(map(str, x))
)

DSER.to_csv("Com_reforco.csv", decimal=",", index=False, sep=";")
DSER.sort_values(
    "Severidade",
    axis=0,
    ascending=False,
    inplace=True,
    kind="quicksort",
    na_position="last",
    ignore_index=False,
)
print(f"{DSER}")
