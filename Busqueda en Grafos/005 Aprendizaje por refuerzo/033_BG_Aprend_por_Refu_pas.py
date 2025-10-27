# Aprendizaje por Refuerzo Pasivo en TRON
# - Política fija π (determinista y simple)
# - Simulación de episodios en un entorno estocástico
# - Actualización de valores V(s) con TD(0)
# - Sin librerías externas

from typing import Dict, List, Tuple, Optional
import random

State = str

# ------------------------------------------------------------
# Entorno TRON (pequeño grafo)
# ------------------------------------------------------------
VECINOS: Dict[State, List[State]] = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": [],  # terminal
}

TERMINALES = {"Nucleo_Central"}

# Recompensas por transición
R_PASO = -0.5
R_AVANCE = +2.0
R_DESVIO = -3.0
R_QUEDARSE = -1.0
R_OBJETIVO = +150.0

# Dinámica estocástica
P_SUCCESS = 0.80   # ir al vecino elegido
P_STAY    = 0.10   # quedarse
# 1 - P_SUCCESS - P_STAY se reparte entre desvíos

GAMMA = 0.95  # descuento

# ------------------------------------------------------------
# Política fija π(s): regla simple "acércate al núcleo"
# ------------------------------------------------------------
def politica_fija(s: State) -> Optional[State]:
    if s in TERMINALES or not VECINOS[s]:
        return None
    vecinos = VECINOS[s]
    if "Nucleo_Central" in vecinos:
        return "Nucleo_Central"
    if "Torre_IO" in vecinos:
        return "Torre_IO"
    if "Arena" in vecinos:
        return "Arena"
    return vecinos[0]

# ------------------------------------------------------------
# Dinámica del entorno
# ------------------------------------------------------------
def transicion(s: State, destino: Optional[State], rng: random.Random) -> Tuple[State, float]:
    if s in TERMINALES or destino is None:
        return s, 0.0

    vecinos = VECINOS[s]
    otros = [v for v in vecinos if v != destino]
    p_desvio = max(0.0, 1.0 - P_SUCCESS - P_STAY)

    dist: List[Tuple[State, float]] = []
    dist.append((destino, P_SUCCESS))
    dist.append((s, P_STAY))
    if otros:
        p_each = p_desvio / len(otros)
        for v in otros:
            dist.append((v, p_each))
    else:
        # si no hay otros, suma desvío a quedarse
        dist[-1] = (s, P_STAY + p_desvio)

    # muestrear siguiente estado
    estados, probs = zip(*dist)
    s2 = rng.choices(estados, weights=probs, k=1)[0]

    # recompensa por transición
    if s2 == s:
        r = R_PASO + R_QUEDARSE
    elif s2 == destino:
        r = R_PASO + (R_OBJETIVO if s2 == "Nucleo_Central" else R_AVANCE)
    else:
        r = R_PASO + (R_OBJETIVO if s2 == "Nucleo_Central" else R_DESVIO)

    return s2, r

# ------------------------------------------------------------
# Aprendizaje pasivo TD(0) sobre V(s)
# ------------------------------------------------------------
def aprender_td0(
    alpha: float = 0.1,
    episodios: int = 500,
    max_pasos: int = 60,
    semilla: int = 7
) -> Dict[State, float]:
    rng = random.Random(semilla)
    V: Dict[State, float] = {s: 0.0 for s in VECINOS}  # inicialización

    for _ in range(episodios):
        s = "Base"
        pasos = 0
        while s not in TERMINALES and pasos < max_pasos:
            a = politica_fija(s)
            s2, r = transicion(s, a, rng)
            # TD(0): V(s) <- V(s) + alpha * [r + gamma V(s') - V(s)]
            objetivo = r + (0.0 if s2 in TERMINALES else GAMMA * V[s2])
            V[s] += alpha * (objetivo - V[s])
            s = s2
            pasos += 1
    return V

# ------------------------------------------------------------
# Utilidades de impresión y demo
# ------------------------------------------------------------
def imprimir_valores(V: Dict[State, float]):
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    for s in orden:
        print(f"{s:15s}: V(s) = {V[s]:8.3f}")

def simular_politica(pasos: int = 20, semilla: int = 17):
    rng = random.Random(semilla)
    s = "Base"
    G = 0.0
    t = 0
    print("\nSimulación siguiendo la política fija:")
    while s not in TERMINALES and t < pasos:
        a = politica_fija(s)
        s2, r = transicion(s, a, rng)
        print(f"t={t:2d}  s={s:12s}  a-> {str(a):12s}  s'={s2:12s}  r={r:6.1f}")
        G += (GAMMA ** t) * r
        s = s2
        t += 1
    print(f"Retorno descontado aproximado: {G:.2f}")

def demo():
    print("Aprendizaje por Refuerzo Pasivo (TD(0)) en TRON")
    V = aprender_td0(alpha=0.15, episodios=800, max_pasos=50, semilla=42)
    print("\nValores aprendidos V(s) bajo la política fija:")
    imprimir_valores(V)
    simular_politica(pasos=25, semilla=11)

if __name__ == "__main__":
    demo()