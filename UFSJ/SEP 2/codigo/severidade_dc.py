import pandas as pd
from modules.flowdc import *

DBAR, DCIR, savepath, filepath = dados(
    "C:\\Users\\cesarcassio\\Downloads\\dados_sistema13B_EC3_CasoBase.txt"
)
# DBAR, DCIR, savepath = dados("dados_sistema12B_EC3_Base.txt")

severidade = []
circuito_removido = []
circuitos_sobrecarregados = []
DSER = pd.DataFrame(columns=["Circ. Removido", "Severidade", "Circ. Sobrecarregado"])

for i in DCIR.index[DCIR["LIG(L)DESL(D)"] == "L"]:
    DBAR, DCIR, _, _ = dados(filepath + ".txt")
    DCIR.loc[i, "LIG(L)DESL(D)"] = "D"
    if flow_dc(DCIR, DBAR) is None:
        continue
    srv, circs = flow_dc(DCIR, DBAR)
    severidade.append(float(srv))
    circuito_removido.append(DCIR["NCIR"][DCIR["LIG(L)DESL(D)"] != "L"])
    circuitos_sobrecarregados.append(circs)
    DCIR.loc[i, "LIG(L)DESL(D)"] = "L"

DSER["Circ. Removido"] = circuito_removido
DSER["Severidade"] = severidade
DSER["Circ. Sobrecarregado"] = circuitos_sobrecarregados

DSER["Circ. Removido"] = DSER["Circ. Removido"].apply(lambda x: ", ".join(map(str, x)))
DSER["Circ. Sobrecarregado"] = DSER["Circ. Sobrecarregado"].apply(
    lambda x: ", ".join(map(str, x))
)


# DSER.sort_values(
#     "Severidade",
#     axis=0,
#     ascending=False,
#     inplace=True,
#     kind="quicksort",
#     na_position="last",
#     ignore_index=False,
# )
print(f"{DSER}")
