# Aprendizaje por Refuerzo Activo (Q-learning) en TRON
# - Entorno estocástico sobre un grafo pequeño
# - Acciones: elegir vecino al que moverse
# - Política ε-greedy, con decaimiento de ε
# - Actualización Q-learning
# - Impresión de la política aprendida y simulación

from typing import Dict, List, Tuple, Optional
import random

State = str
Action = str

# ------------------------------------------------------------
# Entorno TRON (grafo pequeño)
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
# El resto se reparte en desvíos uniformes a otros vecinos

GAMMA = 0.95  # descuento

# ------------------------------------------------------------
# Dinámica del entorno
# ------------------------------------------------------------
def step(s: State, a: Optional[Action], rng: random.Random) -> Tuple[State, float]:
    """
    Ejecuta un paso en el entorno.
    a es el nombre del vecino destino (o None si terminal).
    Devuelve (siguiente_estado, recompensa).
    """
    if s in TERMINALES or a is None:
        return s, 0.0

    vecinos = VECINOS[s]
    destino = a
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
        # si no hay otros, el desvío se suma a quedarse
        dist[-1] = (s, P_STAY + p_desvio)

    estados, probs = zip(*dist)
    s2 = rng.choices(estados, weights=probs, k=1)[0]

    if s2 == s:
        r = R_PASO + R_QUEDARSE
    elif s2 == destino:
        r = R_PASO + (R_OBJETIVO if s2 == "Nucleo_Central" else R_AVANCE)
    else:
        r = R_PASO + (R_OBJETIVO if s2 == "Nucleo_Central" else R_DESVIO)

    return s2, r

# ------------------------------------------------------------
# Q-learning básico
# ------------------------------------------------------------
def acciones(s: State) -> List[Action]:
    return VECINOS[s]

def elegir_accion_epsilon_greedy(Q: Dict[Tuple[State, Action], float],
                                 s: State, eps: float, rng: random.Random) -> Optional[Action]:
    acts = acciones(s)
    if not acts:
        return None
    if rng.random() < eps:
        return rng.choice(acts)
    # explotación: argmax_a Q(s,a)
    mejores = []
    mejor_val = float("-inf")
    for a in acts:
        q = Q.get((s, a), 0.0)
        if q > mejor_val + 1e-12:
            mejores = [a]
            mejor_val = q
        elif abs(q - mejor_val) <= 1e-12:
            mejores.append(a)
    return rng.choice(mejores)

def entrenar_qlearning(
    alpha: float = 0.15,
    gamma: float = GAMMA,
    eps_inicial: float = 0.6,
    eps_final: float = 0.05,
    episodios: int = 1500,
    max_pasos: int = 80,
    semilla: int = 7
) -> Dict[Tuple[State, Action], float]:
    rng = random.Random(semilla)
    Q: Dict[Tuple[State, Action], float] = {}

    def maxQ(s: State) -> float:
        acts = acciones(s)
        if not acts:
            return 0.0
        return max(Q.get((s, a), 0.0) for a in acts)

    for ep in range(episodios):
        s = "Base"
        eps = eps_final + (eps_inicial - eps_final) * max(0.0, (episodios - 1 - ep) / (episodios - 1))
        pasos = 0
        while s not in TERMINALES and pasos < max_pasos:
            a = elegir_accion_epsilon_greedy(Q, s, eps, rng)
            s2, r = step(s, a, rng)
            target = r + (0.0 if s2 in TERMINALES else gamma * maxQ(s2))
            viejo = Q.get((s, a), 0.0)
            Q[(s, a)] = viejo + alpha * (target - viejo)
            s = s2
            pasos += 1

    return Q

# ------------------------------------------------------------
# Política derivada y simulación
# ------------------------------------------------------------
def politica_greedy(Q: Dict[Tuple[State, Action], float]) -> Dict[State, Optional[Action]]:
    pi: Dict[State, Optional[Action]] = {}
    for s in VECINOS.keys():
        acts = acciones(s)
        if not acts:
            pi[s] = None
            continue
        best_a, best_q = None, float("-inf")
        for a in acts:
            q = Q.get((s, a), 0.0)
            if q > best_q:
                best_q, best_a = q, a
        pi[s] = best_a
    return pi

def imprimir_politica(pi: Dict[State, Optional[Action]]):
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    print("Política greedy derivada de Q:")
    for s in orden:
        a = pi.get(s)
        print(f"  {s:15s} -> {str(a)}")

def simular(pi: Dict[State, Optional[Action]], pasos: int = 25, semilla: int = 17):
    rng = random.Random(semilla)
    s = "Base"
    G = 0.0
    t = 0
    print("\nSimulación siguiendo la política aprendida:")
    while s not in TERMINALES and t < pasos:
        a = pi.get(s)
        s2, r = step(s, a, rng)
        print(f"t={t:2d}  s={s:12s}  a-> {str(a):12s}  s'={s2:12s}  r={r:6.1f}")
        G += (GAMMA ** t) * r
        s = s2
        t += 1
    print(f"Retorno descontado aproximado: {G:.2f}")

# ------------------------------------------------------------
# Demo
# ------------------------------------------------------------
def demo():
    print("Aprendizaje por Refuerzo Activo (Q-learning) en TRON")
    Q = entrenar_qlearning(
        alpha=0.20,
        gamma=GAMMA,
        eps_inicial=0.6,
        eps_final=0.05,
        episodios=1500,
        max_pasos=60,
        semilla=42
    )
    pi = politica_greedy(Q)
    imprimir_politica(pi)
    simular(pi, pasos=25, semilla=11)

if __name__ == "__main__":
    demo()