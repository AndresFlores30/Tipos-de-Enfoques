# - Dos funciones de utilidad: CRRA y CARA (elige con MODE)
# - Loterías como listas de (probabilidad, energía)
# - Métricas: utilidad esperada (EU), equivalente cierto (CE), prima de riesgo (RP)
# - Comparación rápida de 3 rutas del Grid TRON

import math

# =========================
#  Utilidades de decisión
# =========================

def u_crra(x: float, r: float) -> float:
    if x <= 0:
        return float("-inf")
    return math.log(x) if r == 1.0 else x**(1.0 - r)/(1.0 - r)

def inv_crra(uval: float, r: float) -> float:
    if r == 1.0:
        return math.exp(uval)
    base = (1.0 - r)*uval
    return 0.0 if base <= 0 else base**(1.0/(1.0 - r))

def u_cara(x: float, a: float) -> float:
    return -math.exp(-a*x)

def inv_cara(uval: float, a: float) -> float:
    if uval >= 0:
        raise ValueError("Para CARA, u(x) < 0.")
    return -math.log(-uval)/a

def expected_utility(lottery, ufun):
    return sum(p*ufun(x) for p, x in lottery)

def certainty_equivalent(lottery, ufun, inv_ufun):
    ue = expected_utility(lottery, ufun)
    return inv_ufun(ue)

def risk_premium(lottery, ce):
    ve = sum(p*x for p, x in lottery)
    return ve - ce

# =========================
#  Escenario TRON (simple)
# =========================

def escenario_tron():
    # Cada ruta es una lotería: lista de (prob, energía)
    ruta_A = [(0.90, 80),  (0.10, 40)]                      # estable/modesta
    ruta_B = [(0.60, 50),  (0.35, 120), (0.05, 5)]          # alta varianza
    ruta_C = [(0.15, 200), (0.25, 100), (0.30, 30), (0.30, 1)]  # extrema
    return {
        "Ruta_A_SectorLuz_TorreIO": ruta_A,
        "Ruta_B_Portal_Arena": ruta_B,
        "Ruta_C_Base_Nucleo": ruta_C,
    }

# =========================
#  Demo
# =========================

def comparar_loterias(mode="CRRA", r=1.0, a=0.01):
    lotes = escenario_tron()

    if mode == "CRRA":
        ufun = lambda x: u_crra(x, r)
        invu = lambda u: inv_crra(u, r)
        titulo = f"CRRA (r={r})"
    elif mode == "CARA":
        ufun = lambda x: u_cara(x, a)
        invu = lambda u: inv_cara(u, a)
        titulo = f"CARA (a={a})"
    else:
        raise ValueError("mode debe ser 'CRRA' o 'CARA'.")

    print(f"=== Teoría de la Utilidad TRON — {titulo} ===")
    mejor, mejor_eu = None, float("-inf")

    for nombre, L in lotes.items():
        eu = expected_utility(L, ufun)
        ce = certainty_equivalent(L, ufun, invu)
        rp = risk_premium(L, ce)
        ve = sum(p*x for p, x in L)
        print(f"{nombre:24s}  VE={ve:7.2f}  EU={eu:9.6f}  CE={ce:7.2f}  RP={rp:7.2f}")
        if eu > mejor_eu:
            mejor_eu, mejor = eu, nombre

    print(f"\nMejor por utilidad esperada: {mejor}")

if __name__ == "__main__":
    # Elige MODE y parámetro:
    # MODE="CRRA" con r∈[0,∞) (usa r=1.0 para log)
    # MODE="CARA" con a>0
    MODE = "CRRA"   # "CRRA" o "CARA"
    R = 1.0         # solo para CRRA (r=1 => log)
    A = 0.01        # solo para CARA

    comparar_loterias(mode=MODE, r=R, a=A)