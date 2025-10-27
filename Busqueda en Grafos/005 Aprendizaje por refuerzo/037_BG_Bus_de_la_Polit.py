# Búsqueda de la Política (REINFORCE) en TRON
# - Política π(a|s) = softmax(preferencias_theta[s,a])
# - Actualización Monte Carlo por episodios completos
# - Entorno estocástico en grafo pequeño

import math
import random

State = str
Action = str

# ------------------------------------------------------------
# Entorno TRON (grafo y recompensas)
# ------------------------------------------------------------
VECINOS = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": [],  # terminal
}
TERMINAL = "Nucleo_Central"

R_PASO = -0.5
R_AVANCE = +2.0
R_DESVIO = -3.0
R_QUEDARSE = -1.0
R_OBJETIVO = +150.0

P_SUCCESS = 0.80
P_STAY    = 0.10
GAMMA     = 0.95

def acciones(s: State):
    return VECINOS[s]

def step(s: State, a: Action, rng: random.Random):
    if s == TERMINAL or a is None:
        return s, 0.0
    vecinos = VECINOS[s]
    dest = a
    otros = [v for v in vecinos if v != dest]
    p_desvio = max(0.0, 1.0 - P_SUCCESS - P_STAY)

    dist = [(dest, P_SUCCESS), (s, P_STAY)]
    if otros:
        p_each = p_desvio / len(otros)
        for v in otros:
            dist.append((v, p_each))
    else:
        dist[-1] = (s, P_STAY + p_desvio)

    estados, probs = zip(*dist)
    s2 = rng.choices(estados, weights=probs, k=1)[0]

    if s2 == s:
        r = R_PASO + R_QUEDARSE
    elif s2 == dest:
        r = R_PASO + (R_OBJETIVO if s2 == TERMINAL else R_AVANCE)
    else:
        r = R_PASO + (R_OBJETIVO if s2 == TERMINAL else R_DESVIO)
    return s2, r

# ------------------------------------------------------------
# Política softmax con parámetros por (estado, acción)
# ------------------------------------------------------------
def softmax_probs(theta, s: State):
    acts = acciones(s)
    if not acts:
        return {}, None
    prefs = [theta.get((s, a), 0.0) for a in acts]
    # estabilización numérica
    m = max(prefs)
    exps = [math.exp(p - m) for p in prefs]
    Z = sum(exps)
    probs = [x / Z for x in exps]
    return {a: p for a, p in zip(acts, probs)}, acts

def sample_action(theta, s: State, rng: random.Random):
    probs, acts = softmax_probs(theta, s)
    if not probs:
        return None
    a = rng.choices(list(probs.keys()), weights=list(probs.values()), k=1)[0]
    return a, probs

# ------------------------------------------------------------
# REINFORCE (episodic, sin baseline y con baseline opcional simple)
# ------------------------------------------------------------
def reinforce(
    alpha=0.05,        # tasa de aprendizaje
    episodios=2000,
    max_pasos=60,
    use_baseline=True,
    seed=7
):
    rng = random.Random(seed)
    theta = {}  # preferencias por (s,a)
    baseline = {s: 0.0 for s in VECINOS}  # valor base por estado (promedio retorno), opcional
    counts   = {s: 1e-9 for s in VECINOS}

    for ep in range(episodios):
        # 1) Generar un episodio siguiendo π_theta
        traj = []  # [(s,a,r,pi(a|s)), ...]
        s = "Base"
        t = 0
        while s != TERMINAL and t < max_pasos:
            a, probs = sample_action(theta, s, rng)
            s2, r = step(s, a, rng)
            traj.append((s, a, r, probs[a]))
            s = s2
            t += 1

        # 2) Retornos hacia atrás y actualización de theta
        G = 0.0
        for t in reversed(range(len(traj))):
            s, a, r, pi_sa = traj[t]
            G = r + GAMMA * G  # retorno desde t
            b = baseline[s] if use_baseline else 0.0
            ventaja = G - b
            # Gradiente log π(a|s) para softmax con preferencias por acción:
            # ∂/∂θ(s,a') log π(a|s) = 1 - π(a|s) si a'=a; = -π(a'|s) si a'≠a
            probs, acts = softmax_probs(theta, s)
            for a_prime in acts:
                grad = (1.0 - probs[a_prime]) if a_prime == a else (-probs[a_prime])
                theta[(s, a_prime)] = theta.get((s, a_prime), 0.0) + alpha * ventaja * grad

        # 3) Actualizar baseline por promedio incremental
        if use_baseline:
            for s, a, r, _ in traj:
                counts[s] += 1.0
                baseline[s] += (G - baseline[s]) / counts[s]  # aproximación simple

    return theta

# ------------------------------------------------------------
# Política greedy de impresión y simulación
# ------------------------------------------------------------
def politica_greedy(theta):
    pi = {}
    for s in VECINOS.keys():
        acts = acciones(s)
        if not acts:
            pi[s] = None
            continue
        # acción con mayor probabilidad softmax actual
        probs, _ = softmax_probs(theta, s)
        pi[s] = max(probs, key=probs.get)
    return pi

def imprimir_politica(pi):
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    print("Política aprendida (acción más probable por estado):")
    for s in orden:
        print(f"  {s:15s} -> {pi.get(s)}")

def simular(pi, pasos=25, semilla=17):
    rng = random.Random(semilla)
    s = "Base"
    G = 0.0
    t = 0
    print("\nSimulación siguiendo la política aprendida:")
    while s != TERMINAL and t < pasos:
        a = pi.get(s)
        s2, r = step(s, a, rng)
        print(f"t={t:2d}  s={s:12s}  a={str(a):12s}  s'={s2:12s}  r={r:6.1f}")
        G += (GAMMA ** t) * r
        s = s2
        t += 1
    print(f"Retorno descontado aproximado: {G:.2f}")

# ------------------------------------------------------------
# Demo
# ------------------------------------------------------------
def main():
    print("Búsqueda de la Política (REINFORCE) en TRON — versión simple")
    theta = reinforce(alpha=0.05, episodios=2500, max_pasos=60, use_baseline=True, seed=42)
    pi = politica_greedy(theta)
    imprimir_politica(pi)
    simular(pi, pasos=25, semilla=11)

if __name__ == "__main__":
    main()