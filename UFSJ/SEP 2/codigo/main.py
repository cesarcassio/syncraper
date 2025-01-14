import numpy as np
import pandas as pd
from modules import *

S_BASE = 100  # potencia base em MVA
tol = 1e-3  # tolerância
MAX_ITERA = 10  # maximo de iterações
itera = 0  # iteração atual


# DBAR, DCIR, SAVEPATH, FILEPATH = dados("dados_sistema6B_ATIV.txt")
DBAR, DCIR, SAVEPATH, FILEPATH = dados("dados\\L2_6B_CasoBase.txt")
CONTINGENCIA = any(DCIR.index[DCIR["LIG(L)DESL(D)"] != "L"])  # True or False


DCIR["DEF(RAD)"] = np.radians(DCIR["DEF(GRAUS)"])
if CONTINGENCIA:
    DCIR["CAP(PU)"] = 1.15 * DCIR["CAP(PU)"]
ybus = make_ybus(DBAR, DCIR)


# Cria uma lista das Barras SW
Ref = DBAR[DBAR["TIPO"] == "SW"].index.to_list()
PV = DBAR[DBAR["TIPO"] == "PV"].index.to_list()  # Cria uma lista das barras PV
PQ = DBAR[DBAR["TIPO"] == "PQ"].index.to_list()  # Cria uma lista das barras PQ

while itera < MAX_ITERA:
    theta = np.radians(DBAR["Oesp(°)"].values)
    vbus = DBAR["Vesp(PU)"].values
    delta_p, delta_q = calc_delta_pq(DBAR, vbus, theta, ybus)

    if abs(delta_p[sorted(PV + PQ)].max()) < tol and abs(delta_q[PQ].max()) < tol:
        break

    jacob = jacobiana(DBAR, vbus, theta, ybus)
    delta_theta, delta_v = calc_delta_theta_v(DBAR, delta_p, delta_q, jacob)
    theta += delta_theta
    vbus += delta_v
    DBAR["Oesp(°)"] = np.degrees(theta)
    DBAR["Vesp(PU)"] = vbus
    itera += 1
print(f"Convergiu após {itera} iterações.\n")
DBAR["QG(PU)"] = 0
DBAR["PG(PU)"] = 0
# calculando as potencias do circuito
calc_pot(DBAR, vbus, theta, ybus)
# calculando o fluxo
fluxo = calc_fluxo(DBAR, DCIR, S_BASE)
# calculando a sobrecarga dos circuitos
calc_sobrecarga_ac(DCIR, fluxo)
print(fluxo)
print(fluxo["Sobrecarga"].sum())

# results(DBAR, fluxo, S_BASE, SAVEPATH, CONTINGENCIA)
# limite_v(DBAR, SAVEPATH, FILEPATH, CONTINGENCIA)
# limite_gen(DBAR, SAVEPATH)
# limite_lt(fluxo, DCIR, S_BASE, SAVEPATH, CONTINGENCIA)
