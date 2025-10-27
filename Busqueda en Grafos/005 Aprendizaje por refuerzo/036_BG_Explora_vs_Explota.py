# Exploración vs. Explotación (bandits) en TRON
# - 3 "brazos" (rutas): Sector_Luz, Portal, Arena
# - Recompensas Bernoulli estacionarias (éxito=1, fallo=0)
# - Estrategias: ε-greedy (ε decae) y UCB1
# - Sin dependencias externas

import math
import random
from typing import Dict, List, Tuple

# ------------------------------------------------------------
# Entorno bandit (rutas TRON con prob. de éxito distintas)
# ------------------------------------------------------------
ACTIONS = ["Sector_Luz", "Portal", "Arena"]

# Probabilidades de éxito reales (desconocidas para el agente)
# Ajusta para experimentar diferentes dificultades:
P_SUCCESS = {
    "Sector_Luz": 0.55,   # brazo medio
    "Portal":     0.40,   # brazo débil
    "Arena":      0.70,   # mejor brazo (óptimo)
}

def pull(action: str, rng: random.Random) -> int:
    """Devuelve 1 con probabilidad p, si no 0 (Bernoulli)."""
    return 1 if rng.random() < P_SUCCESS[action] else 0

# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------
def argmax_ties_random(items: List[Tuple[str, float]], rng: random.Random) -> str:
    """Devuelve una clave con valor máximo, rompiendo empates al azar."""
    best_val = max(v for _, v in items)
    candidates = [k for k, v in items if abs(v - best_val) <= 1e-12]
    return rng.choice(candidates)

def summary(name: str, Q: Dict[str, float], N: Dict[str, int], rewards: List[float]):
    print(f"\n=== {name} ===")
    print("Estimaciones Q(a) y conteos N(a):")
    for a in ACTIONS:
        print(f"  {a:12s}  Q={Q[a]:6.3f}  N={N[a]}")
    avg_reward = sum(rewards) / len(rewards)
    opt = "Arena"  # por definición arriba
    opt_rate = sum(1 for r in selected_actions if r == opt) / len(selected_actions)
    print(f"Recompensa media: {avg_reward:.3f}")
    print(f"Frecuencia de acción óptima ({opt}): {opt_rate*100:.1f}%")

# ------------------------------------------------------------
# ε-greedy con decaimiento lineal
# ------------------------------------------------------------
def run_eps_greedy(steps: int, eps_ini: float, eps_fin: float, seed: int) -> Tuple[Dict[str, float], Dict[str, int], List[float], List[str]]:
    rng = random.Random(seed)
    Q = {a: 0.0 for a in ACTIONS}   # estimación de valor
    N = {a: 0   for a in ACTIONS}   # conteo de selecciones
    rewards: List[float] = []
    actions_taken: List[str] = []

    for t in range(1, steps + 1):
        eps = eps_fin + (eps_ini - eps_fin) * max(0.0, (steps - t) / max(1, steps - 1))
        if rng.random() < eps:
            a = rng.choice(ACTIONS)
        else:
            a = argmax_ties_random([(k, Q[k]) for k in ACTIONS], rng)

        r = pull(a, rng)
        N[a] += 1
        # Actualización por promedio incremental
        Q[a] += (r - Q[a]) / N[a]
        rewards.append(r)
        actions_taken.append(a)

    return Q, N, rewards, actions_taken

# ------------------------------------------------------------
# UCB1 (Upper Confidence Bound)
# ------------------------------------------------------------
def run_ucb1(steps: int, c: float, seed: int) -> Tuple[Dict[str, float], Dict[str, int], List[float], List[str]]:
    rng = random.Random(seed)
    Q = {a: 0.0 for a in ACTIONS}
    N = {a: 0   for a in ACTIONS}
    rewards: List[float] = []
    actions_taken: List[str] = []

    # Inicializa tocando cada brazo una vez para evitar división por cero
    t = 0
    for a in ACTIONS:
        r = pull(a, rng)
        N[a] += 1
        Q[a] = r * 1.0
        rewards.append(r)
        actions_taken.append(a)
        t += 1
        if t >= steps:
            return Q, N, rewards, actions_taken

    # Resto de pasos con UCB1
    for t in range(t + 1, steps + 1):
        total = sum(N.values())
        scores = []
        for a in ACTIONS:
            bonus = c * math.sqrt(math.log(total) / N[a])
            scores.append((a, Q[a] + bonus))
        a = argmax_ties_random(scores, rng)
        r = pull(a, rng)
        N[a] += 1
        Q[a] += (r - Q[a]) / N[a]
        rewards.append(r)
        actions_taken.append(a)

    return Q, N, rewards, actions_taken

# ------------------------------------------------------------
# Demo
# ------------------------------------------------------------
if __name__ == "__main__":
    STEPS = 2000

    # Ejecutar ε-greedy
    Q_eps, N_eps, R_eps, selected_actions = run_eps_greedy(
        steps=STEPS, eps_ini=0.6, eps_fin=0.02, seed=7
    )
    print("Probabilidades reales de éxito:")
    for a in ACTIONS:
        print(f"  {a:12s}: p={P_SUCCESS[a]:.2f}")
    summary("ε-greedy (ε decae 0.60 → 0.02)", Q_eps, N_eps, R_eps)

    # Ejecutar UCB1
    Q_ucb, N_ucb, R_ucb, selected_actions = run_ucb1(
        steps=STEPS, c=2.0, seed=7
    )
    summary("UCB1 (c=2.0)", Q_ucb, N_ucb, R_ucb)