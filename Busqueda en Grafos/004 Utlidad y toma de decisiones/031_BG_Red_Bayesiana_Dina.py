# Red Bayesiana Dinámica (DBN) en TRON
# - Cadena oculta: Interf_t -> Interf_{t+1}
# - Emisión: Interf_t -> Sensor_t
# - Simulación del Grid: Loc_{t+1} | Loc_t, Acción_t, Interf_t (para generar trazas)
# - Inferencia: Filtrado (forward) y Suavizado (forward-backward) de Interf_t

from typing import Dict, List, Tuple
import random

# ------------------------------------------------------------
# Mapa TRON (observable)
# ------------------------------------------------------------
Loc = str
VECINOS: Dict[Loc, List[Loc]] = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": []
}
OBJETIVO = "Nucleo_Central"

# ------------------------------------------------------------
# DBN (Interferencia y Sensor)
# ------------------------------------------------------------
# Estados de interferencia
S_HID = ["Baja", "Alta"]
IDX = {"Baja": 0, "Alta": 1}

# Transición oculta P(Interf_{t+1} | Interf_t)
P_STAY = 0.90
T_INTF = [
    [P_STAY, 1 - P_STAY],   # desde Baja -> [Baja, Alta]
    [1 - P_STAY, P_STAY]    # desde Alta -> [Baja, Alta]
]

# Emisión P(Sensor=OK | Interf)
P_OK_BAJA = 0.85
P_OK_ALTA = 0.25

def p_emision(sensor: str, s: str) -> float:
    if sensor == "OK":
        return P_OK_BAJA if s == "Baja" else P_OK_ALTA
    else:
        return (1 - P_OK_BAJA) if s == "Baja" else (1 - P_OK_ALTA)

# Transición de ubicación condicionada a interferencia (para simular)
P_SUCCESS_BAJA = 0.80
P_SUCCESS_ALTA = 0.60
P_STAY_LOC = 0.10

# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------
def normalize(v: List[float]) -> List[float]:
    s = sum(v)
    if s <= 0:
        return [1.0 / len(v)] * len(v)
    return [x / s for x in v]

def sample_from_pairs(pairs: List[Tuple[str, float]], rng: random.Random) -> str:
    vals, probs = zip(*pairs)
    return rng.choices(vals, weights=probs, k=1)[0]

# ------------------------------------------------------------
# Política de movimiento (simple): ir hacia el objetivo si se puede
# ------------------------------------------------------------
def elegir_accion(loc: Loc) -> Loc:
    if loc == OBJETIVO or not VECINOS[loc]:
        return loc
    # Heurística tonta: si hay un vecino que acerca al objetivo, tómalo; si no, el primero
    vecinos = VECINOS[loc]
    if OBJETIVO in vecinos:
        return OBJETIVO
    if "Torre_IO" in vecinos:
        return "Torre_IO"
    if "Arena" in vecinos:
        return "Arena"
    return vecinos[0]

def transicion_loc(loc: Loc, destino: Loc, interf: str, rng: random.Random) -> Loc:
    p_success = P_SUCCESS_BAJA if interf == "Baja" else P_SUCCESS_ALTA
    p_desvio = max(0.0, 1.0 - p_success - P_STAY_LOC)
    otros = [v for v in VECINOS[loc] if v != destino]

    dist: List[Tuple[Loc, float]] = []
    dist.append((destino, p_success))
    dist.append((loc, P_STAY_LOC))
    if otros:
        p_each = p_desvio / len(otros)
        for v in otros:
            dist.append((v, p_each))
    else:
        # si no hay otros vecinos, agregar desvío a quedarse
        dist[-1] = (loc, P_STAY_LOC + p_desvio)

    return sample_from_pairs(dist, rng)

# ------------------------------------------------------------
# Simulación del mundo (genera secuencias)
# ------------------------------------------------------------
def simular_traza(pasos: int = 12, seed: int = 7):
    rng = random.Random(seed)
    loc = "Base"
    interf = "Alta" if rng.random() < 0.4 else "Baja"

    estados_ocultos = []
    sensores = []
    locs = []

    for _ in range(pasos):
        # Emisión
        obs = "OK" if rng.random() < (P_OK_BAJA if interf == "Baja" else P_OK_ALTA) else "Alerta"

        # Guardar
        estados_ocultos.append(interf)
        sensores.append(obs)
        locs.append(loc)

        # Acción y transición de loc
        dest = elegir_accion(loc)
        loc = transicion_loc(loc, dest, interf, rng)

        # Transición de interferencia
        idx = IDX[interf]
        interf = "Baja" if (rng.random() < T_INTF[idx][0]) else "Alta"

        if loc == OBJETIVO:
            # aún generamos observación y estado oculto del último paso, pero paramos luego
            break

    return estados_ocultos, sensores, locs

# ------------------------------------------------------------
# Inferencia DBN: Filtrado (forward)
# ------------------------------------------------------------
def forward_filtrado(sensores: List[str], prior_alta: float = 0.4) -> List[List[float]]:
    """
    Devuelve lista de creencias alpha_t = [P(Baja), P(Alta)] para cada t.
    """
    alphas: List[List[float]] = []
    # inicial
    alpha = [1 - prior_alta, prior_alta]
    for obs in sensores:
        # predicción: alpha_pred[j] = sum_i T[i->j]*alpha[i]
        alpha_pred = [
            T_INTF[0][0]*alpha[0] + T_INTF[1][0]*alpha[1],
            T_INTF[0][1]*alpha[0] + T_INTF[1][1]*alpha[1],
        ]
        # actualización con evidencia
        like_baja = p_emision(obs, "Baja")
        like_alta = p_emision(obs, "Alta")
        alpha = normalize([alpha_pred[0]*like_baja, alpha_pred[1]*like_alta])
        alphas.append(alpha)
    return alphas

# ------------------------------------------------------------
# Suavizado forward-backward (sobre la cadena de Interf_t)
# ------------------------------------------------------------
def backward_evidencia(sensores: List[str]) -> List[List[float]]:
    """
    Mensajes beta_t = [P(obs_{t+1..}| Interf_t=Baja/Alta)] desde el final.
    beta_T = [1,1]
    """
    n = len(sensores)
    betas: List[List[float]] = [[1.0, 1.0] for _ in range(n)]
    for t in range(n-2, -1, -1):
        obs_next = sensores[t+1]
        like_nb = p_emision(obs_next, "Baja")
        like_na = p_emision(obs_next, "Alta")
        # beta_t[i] = sum_j T[i->j] * like(obs_{t+1} | j) * beta_{t+1}[j]
        b0 = T_INTF[0][0]*like_nb*betas[t+1][0] + T_INTF[0][1]*like_na*betas[t+1][1]
        b1 = T_INTF[1][0]*like_nb*betas[t+1][0] + T_INTF[1][1]*like_na*betas[t+1][1]
        betas[t] = [b0, b1]
        # no normalizamos aquí; se normaliza al combinar con alpha
    return betas

def suavizar(alphas: List[List[float]], betas: List[List[float]]) -> List[List[float]]:
    """
    Posterior suave gamma_t ∝ alpha_t ⊙ beta_t
    """
    gammas: List[List[float]] = []
    for a, b in zip(alphas, betas):
        g = normalize([a[0]*b[0], a[1]*b[1]])
        gammas.append(g)
    return gammas

# ------------------------------------------------------------
# Demo
# ------------------------------------------------------------
def demo():
    # 1) Simular traza
    estados, observaciones, locs = simular_traza(pasos=15, seed=17)

    print("t  Loc             Sensor   Interf_real")
    for t, (loc, obs, st) in enumerate(zip(locs, observaciones, estados)):
        print(f"{t:2d}  {loc:14s}  {obs:7s}  {st}")

    # 2) Filtrado online
    alphas = forward_filtrado(observaciones, prior_alta=0.4)

    print("\nFiltrado (P(Alta) por paso):")
    for t, a in enumerate(alphas):
        print(f"t={t:2d}  P(Alta)={a[1]:.3f}")

    # 3) Suavizado offline
    betas = backward_evidencia(observaciones)
    gammas = suavizar(alphas, betas)

    print("\nSuavizado (posterior P(Alta) por paso):")
    for t, g in enumerate(gammas):
        print(f"t={t:2d}  P(Alta)={g[1]:.3f}")

if __name__ == "__main__":
    demo()