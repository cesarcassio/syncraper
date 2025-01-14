from modules.flowdc import *

# DBAR, DCIR, savepath, filepath = dados("dados\\dados_sistema13B_EC3_CasoBase.txt")
DBAR, DCIR, savepath, filepath = dados("dados\\L2_6B_CasoBase.txt")
tol = 0.001
erro = 1
Sbase = 100
Ref = DBAR[DBAR["TIPO"] == "SW"].index

B = matriz_susceptancia(DCIR, DBAR)
PG = DBAR["PGesp(PU)"].drop(Ref).to_numpy()
PD = DBAR["PD(PU)"].drop(Ref).to_numpy()
P = PG - PD
Theta = calc_theta(B, P, Ref)

while erro > tol:
    calc_perdas(DCIR, Theta)
    Perdas = calc_sum_perdas(DCIR, DBAR)
    P = PG - (PD + Perdas)
    Theta_nv = calc_theta(B, P, Ref)
    erro = abs(Theta_nv - Theta).max()
    Theta = Theta_nv

calc_flow_dc(DCIR, Theta, Sbase)
calc_sobrecarga(DCIR)
DCIR.to_csv(filepath + ".csv", decimal=",", index=False, sep=";")
print(f"Severidade: {DCIR["Sobrecarga"].sum()}")
circuitos = list(DCIR["NCIR"][DCIR["Sobrecarga"] != 0])
print(DCIR)
print(circuitos)
