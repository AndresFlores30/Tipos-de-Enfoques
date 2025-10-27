# POMDP sencillo en TRON:
# - Estado real: (loc observable, interferencia oculta)
# - Creencia: bAlta = P(Interferencia=Alta)
# - Sensor ruidoso: OK / Alerta
# - Política: elegir acción con mayor recompensa esperada inmediata según la creencia
# - Transición estocástica con éxito, quedarse o desvío

from typing import Dict, List, Tuple
import random

Loc = str

# Grafo TRON (vecinos)
VECINOS: Dict[Loc, List[Loc]] = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": []
}

# Recompensas por transición
R_PASO = -0.5
R_AVANCE = +2.0
R_DESVIO = -3.0
R_QUEDARSE = -1.0
R_OBJETIVO = +150.0

# Dinámica
P_SUCCESS_BASE = 0.80     # prob. de ir al vecino elegido con interferencia baja
DELTA_IF_HIGH  = 0.20     # reducción al éxito si la interferencia es alta
P_STAY         = 0.10     # prob. de quedarse
# El resto va a desvío uniforme a otros vecinos

# Interferencia (oculta) y su persistencia
P_INTF_STAY = 0.90  # prob. de que la interferencia no cambie (memoria alta)

# Sensor
P_OK_DADO_BAJA = 0.85
P_OK_DADO_ALTA = 0.25

# Descuento sólo para reporte (no se usa en la política)
GAMMA = 0.95

# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------

def sample_categorical(pairs: List[Tuple[str, float]], rng: random.Random) -> str:
    states, probs = zip(*pairs)
    return rng.choices(states, weights=probs, k=1)[0]

def actualizar_interferencia_real(intf: str, rng: random.Random) -> str:
    if rng.random() < P_INTF_STAY:
        return intf
    return "Alta" if intf == "Baja" else "Baja"

def observar_sensor(intf: str, rng: random.Random) -> str:
    p_ok = P_OK_DADO_BAJA if intf == "Baja" else P_OK_DADO_ALTA
    return "OK" if rng.random() < p_ok else "Alerta"

def belief_predict(bAlta: float) -> float:
    """Predicción por persistencia de interferencia (HMM)."""
    # b'(Alta) = bAlta*P(stay) + (1-bAlta)*(1-P(stay))
    return bAlta * P_INTF_STAY + (1 - bAlta) * (1 - P_INTF_STAY)

def belief_update(bAlta_pred: float, obs: str) -> float:
    """Actualización Bayes: sólo sobre Alta/Baja usando el sensor."""
    # P(o | Alta/Baja)
    p_o_alta = P_OK_DADO_ALTA if obs == "OK" else (1 - P_OK_DADO_ALTA)
    p_o_baja = P_OK_DADO_BAJA if obs == "OK" else (1 - P_OK_DADO_BAJA)
    num = p_o_alta * bAlta_pred
    den = num + p_o_baja * (1 - bAlta_pred)
    return 0.0 if den == 0 else num / den

def probas_transicion(loc: Loc, destino: Loc, bAlta: float) -> List[Tuple[Loc, float]]:
    """Distribución de próxima ubicación dado que elegimos 'destino' desde 'loc'."""
    vecinos = VECINOS[loc]
    otros = [v for v in vecinos if v != destino]
    # Éxito esperado según la creencia: menor si la interferencia es alta
    p_success = P_SUCCESS_BASE - DELTA_IF_HIGH * bAlta
    if p_success < 0.0: p_success = 0.0
    p_desvio = max(0.0, 1.0 - p_success - P_STAY)

    dist: List[Tuple[Loc, float]] = []
    dist.append((destino, p_success))
    dist.append((loc, P_STAY))
    if otros:
        p_each = p_desvio / len(otros)
        for o in otros:
            dist.append((o, p_each))
    else:
        # si no hay otros, añádelo a quedarse
        dist[-1] = (loc, P_STAY + p_desvio)
    return dist

def recompensa(loc_actual: Loc, loc_siguiente: Loc) -> float:
    base = R_PASO
    if loc_siguiente == "Nucleo_Central":
        return base + R_OBJETIVO
    if loc_siguiente == loc_actual:
        return base + R_QUEDARSE
    if loc_siguiente in VECINOS[loc_actual]:
        # Puede ser avance deseado o desvío si no era el elegido; como no
        # sabemos cuál fue el elegido en esta función, distinguimos por caller.
        # Aquí sólo devolvemos "avance" si se mueve; el caller ajusta al muestrear.
        return base + R_AVANCE
    return base + R_DESVIO

# ------------------------------------------------------------
# Política miope: elegir acción con mayor recompensa esperada instantánea
# ------------------------------------------------------------

def mejor_accion(loc: Loc, bAlta: float) -> str:
    """Elige el vecino que maximiza la recompensa esperada inmediata."""
    vecinos = VECINOS[loc]
    if not vecinos:
        return ""
    best, best_val = vecinos[0], -1e30
    for v in vecinos:
        # Distribución de próxima ubicación si elegimos v
        dist = probas_transicion(loc, v, bAlta)
        # Recompensa esperada: distingue avance vs desvío
        exp_r = 0.0
        for loc2, p in dist:
            if loc2 == v:
                r = R_PASO + (R_OBJETIVO if loc2 == "Nucleo_Central" else R_AVANCE)
            elif loc2 == loc:
                r = R_PASO + R_QUEDARSE
            else:
                r = R_PASO + (R_OBJETIVO if loc2 == "Nucleo_Central" else R_DESVIO)
            exp_r += p * r
        if exp_r > best_val:
            best_val, best = exp_r, v
    return best  # vecino elegido

# ------------------------------------------------------------
# Simulación
# ------------------------------------------------------------

def simular(seed: int = 7, pasos: int = 20):
    rng = random.Random(seed)

    # Estado real inicial
    loc_real = "Base"
    intf_real = "Alta" if rng.random() < 0.4 else "Baja"

    # Creencia inicial (sobre interferencia)
    bAlta = 0.4  # P(Alta)

    G = 0.0
    t = 0
    print("t  loc  intf?  obs  bAlta  accion  loc'")
    while t < pasos and loc_real != "Nucleo_Central":
        # Observación del sensor y actualización de creencia
        obs = observar_sensor(intf_real, rng)
        bAlta_pred = belief_predict(bAlta)
        bAlta = belief_update(bAlta_pred, obs)

        # Elegir acción con política miope
        if not VECINOS[loc_real]:
            break
        destino = mejor_accion(loc_real, bAlta)

        # Transición de ubicación según la creencia (para la política)
        dist = probas_transicion(loc_real, destino, bAlta)
        loc_next = sample_categorical(dist, rng)

        # Recompensa del paso (distinguiendo éxito/desvío/estancia)
        if loc_next == destino:
            r = R_PASO + (R_OBJETIVO if loc_next == "Nucleo_Central" else R_AVANCE)
        elif loc_next == loc_real:
            r = R_PASO + R_QUEDARSE
        else:
            r = R_PASO + (R_OBJETIVO if loc_next == "Nucleo_Central" else R_DESVIO)

        # Imprimir paso
        print(f"{t:>2}  {loc_real:12s}  {'?':4s}  {obs:6s}  {bAlta:5.2f}  to:{destino:12s}  {loc_next:12s}")

        # Actualizar retorno y estado real (incluye cambio de interferencia real)
        G += (GAMMA ** t) * r
        loc_real = loc_next
        intf_real = actualizar_interferencia_real(intf_real, rng)
        t += 1

    print(f"\nRetorno descontado aproximado: {G:.2f}")

# ------------------------------------------------------------
# Demo
# ------------------------------------------------------------

if __name__ == "__main__":
    simular(seed=17, pasos=15)