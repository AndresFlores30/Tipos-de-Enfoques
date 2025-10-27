# Q-Learning simple en un pequeño Grid temático TRON

import random

# --------------------------
# Entorno (estados y acciones)
# --------------------------
VECINOS = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": [],  # terminal
}
TERMINAL = "Nucleo_Central"

# Recompensas por transición
R_PASO = -0.5
R_AVANCE = +2.0
R_DESVIO = -3.0
R_QUEDARSE = -1.0
R_OBJETIVO = +150.0

# Estocasticidad del movimiento
P_SUCCESS = 0.80   # llegar al vecino elegido
P_STAY    = 0.10   # quedarse en el mismo estado
# El resto se reparte como desvíos a los otros vecinos

GAMMA = 0.95  # descuento

def acciones(s):
    return VECINOS[s]

def step(s, a, rng):
    """Evoluciona el entorno desde s eligiendo acción a (vecino destino)."""
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

# --------------------------
# Q-Learning
# --------------------------
def elegir_accion(Q, s, eps, rng):
    acts = acciones(s)
    if not acts:
        return None
    if rng.random() < eps:
        return rng.choice(acts)
    # argmax_a Q(s,a)
    mejor_val = float("-inf")
    mejores = []
    for a in acts:
        q = Q.get((s, a), 0.0)
        if q > mejor_val + 1e-12:
            mejor_val, mejores = q, [a]
        elif abs(q - mejor_val) <= 1e-12:
            mejores.append(a)
    return rng.choice(mejores)

def maxQ(Q, s):
    acts = acciones(s)
    return 0.0 if not acts else max(Q.get((s, a), 0.0) for a in acts)

def entrenar_qlearning(alpha=0.2, gamma=GAMMA,
                       eps_ini=0.6, eps_fin=0.05,
                       episodios=1200, max_pasos=60, semilla=7):
    rng = random.Random(semilla)
    Q = {}
    for ep in range(episodios):
        s = "Base"
        # decaimiento lineal de epsilon
        eps = eps_fin + (eps_ini - eps_fin) * (1 - ep / max(1, episodios - 1))
        pasos = 0
        while s != TERMINAL and pasos < max_pasos:
            a = elegir_accion(Q, s, eps, rng)
            s2, r = step(s, a, rng)
            target = r + (0.0 if s2 == TERMINAL else gamma * maxQ(Q, s2))
            Q[(s, a)] = Q.get((s, a), 0.0) + alpha * (target - Q.get((s, a), 0.0))
            s = s2
            pasos += 1
    return Q

def politica_greedy(Q):
    pi = {}
    for s in VECINOS.keys():
        acts = acciones(s)
        if not acts:
            pi[s] = None
        else:
            pi[s] = max(acts, key=lambda a: Q.get((s, a), 0.0))
    return pi

# --------------------------
# Utilidades de impresión y demo
# --------------------------
def imprimir_politica(pi):
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    print("Política aprendida (greedy sobre Q):")
    for s in orden:
        print(f"  {s:15s} -> {pi.get(s)}")

def simular(pi, pasos=25, semilla=11):
    rng = random.Random(semilla)
    s = "Base"
    G = 0.0
    t = 0
    print("\nSimulación con la política aprendida:")
    while s != TERMINAL and t < pasos:
        a = pi.get(s)
        s2, r = step(s, a, rng)
        print(f"t={t:2d}  s={s:12s}  a={str(a):12s}  s'={s2:12s}  r={r:6.1f}")
        G += (GAMMA ** t) * r
        s = s2
        t += 1
    print(f"Retorno descontado aproximado: {G:.2f}")

def main():
    print("Q-Learning simple en TRON")
    Q = entrenar_qlearning(alpha=0.2, eps_ini=0.6, eps_fin=0.05,
                           episodios=1200, max_pasos=60, semilla=42)
    pi = politica_greedy(Q)
    imprimir_politica(pi)
    simular(pi, pasos=25, semilla=13)

if __name__ == "__main__":
    main()