# Iteración de Políticas (MDP) con temática TRON
# - Estados: sectores del Grid
# - Acciones: rutas hacia vecinos
# - Dinámica estocástica con desvíos
# - Recompensas por transición
# - Algoritmo: Policy Iteration (evaluación iterativa + mejora codiciosa)

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random

State = str
Action = str

# ---------------------------------------------------------------------
# Definición del Grid TRON
# ---------------------------------------------------------------------
VECINOS: Dict[State, List[State]] = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": [],  # terminal
}

# Rutas más frágiles ante interferencia
RUTAS_FRAGILES = {
    ("Arena", "Torre_IO"),
    ("Torre_IO", "Nucleo_Central"),
    ("Portal", "Arena"),
}

# Recompensas por transición
R_AVANCE = +2.0
R_DESVIO = -3.0
R_QUEDARSE = -1.0
R_OBJETIVO = +150.0
R_PASO = -0.5

# Probabilidades base
P_SUCCESS = 0.80
P_STAY = 0.10
DELTA_FRAGIL = 0.20  # reduce éxito en rutas frágiles; el resto va a desvío

# Descuento y tolerancias
GAMMA = 0.95
THETA_EVAL = 1e-8   # para evaluación de política
MAX_EVAL_ITERS = 10_000


@dataclass
class MDP:
    estados: List[State]
    acciones: Dict[State, List[Action]]
    transicion: Dict[Tuple[State, Action], List[Tuple[State, float, float]]]
    terminales: List[State]


def construir_mdp_tron() -> MDP:
    estados = list(VECINOS.keys())
    terminales = ["Nucleo_Central"]
    acciones: Dict[State, List[Action]] = {}
    transicion: Dict[Tuple[State, Action], List[Tuple[State, float, float]]] = {}

    for s in estados:
        if s in terminales:
            acciones[s] = []
            continue

        vecinos = VECINOS[s]
        acciones[s] = [f"to:{v}" for v in vecinos]

        for a in acciones[s]:
            destino = a.split("to:")[1]

            success = P_SUCCESS
            stay = P_STAY
            if (s, destino) in RUTAS_FRAGILES:
                success = max(0.0, P_SUCCESS - DELTA_FRAGIL)
            p_desvio = max(0.0, 1.0 - success - stay)

            otros = [v for v in vecinos if v != destino]
            trans: List[Tuple[State, float, float]] = []

            # Ir al destino elegido
            r_ok = R_PASO + (R_OBJETIVO if destino == "Nucleo_Central" else R_AVANCE)
            trans.append((destino, success, r_ok))

            # Quedarse
            trans.append((s, stay, R_PASO + R_QUEDARSE))

            # Desvíos
            if otros:
                p_cada = p_desvio / len(otros)
                for v_alt in otros:
                    r_alt = R_PASO + (R_OBJETIVO if v_alt == "Nucleo_Central" else R_DESVIO)
                    trans.append((v_alt, p_cada, r_alt))
            else:
                # sin otros vecinos: assignar desvío a quedarse
                sp, p_old, r_old = trans[1]
                trans[1] = (sp, p_old + p_desvio, r_old)

            # Normalizar por seguridad
            sprob = sum(p for _, p, _ in trans)
            if abs(sprob - 1.0) > 1e-9:
                trans = [(sp, p / sprob, r) for (sp, p, r) in trans]

            transicion[(s, a)] = trans

    return MDP(estados=estados, acciones=acciones, transicion=transicion, terminales=terminales)

# ---------------------------------------------------------------------
# Evaluación de política (iterativa)
# ---------------------------------------------------------------------

def evaluar_politica(mdp: MDP, pi: Dict[State, Action], gamma: float = GAMMA,
                     theta: float = THETA_EVAL, max_iters: int = MAX_EVAL_ITERS) -> Dict[State, float]:
    V = {s: 0.0 for s in mdp.estados}
    for s in mdp.terminales:
        V[s] = 0.0

    for _ in range(max_iters):
        delta = 0.0
        for s in mdp.estados:
            if s in mdp.terminales:
                continue
            a = pi[s]
            q = 0.0
            for sp, p, r in mdp.transicion[(s, a)]:
                q += p * (r + gamma * V[sp])
            delta = max(delta, abs(q - V[s]))
            V[s] = q
        if delta < theta:
            break
    return V

# ---------------------------------------------------------------------
# Mejora de política
# ---------------------------------------------------------------------

def mejorar_politica(mdp: MDP, V: Dict[State, float], gamma: float = GAMMA) -> Tuple[Dict[State, Action], bool]:
    pi_new: Dict[State, Action] = {}
    estable = True

    for s in mdp.estados:
        if s in mdp.terminales or not mdp.acciones[s]:
            continue

        # Acción actual para comparar estabilidad (si la hay en pi_new)
        mejor_a, mejor_q = None, float("-inf")
        for a in mdp.acciones[s]:
            q = 0.0
            for sp, p, r in mdp.transicion[(s, a)]:
                q += p * (r + gamma * V[sp])
            if q > mejor_q:
                mejor_q, mejor_a = q, a
        pi_new[s] = mejor_a

    return pi_new, estable

# ---------------------------------------------------------------------
# Iteración de políticas (Howard)
# ---------------------------------------------------------------------

def policy_iteration(mdp: MDP, gamma: float = GAMMA,
                     theta_eval: float = THETA_EVAL) -> Tuple[Dict[State, float], Dict[State, Action]]:
    # Política inicial: elegir el primer vecino disponible
    pi: Dict[State, Action] = {}
    for s in mdp.estados:
        if s in mdp.terminales or not mdp.acciones[s]:
            continue
        pi[s] = mdp.acciones[s][0]

    while True:
        # Evaluar política actual
        V = evaluar_politica(mdp, pi, gamma=gamma, theta=theta_eval)

        # Mejorar política de manera codiciosa respecto a V
        pi_mejor: Dict[State, Action] = {}
        estable = True
        for s in mdp.estados:
            if s in mdp.terminales or not mdp.acciones[s]:
                continue

            # Acción actual y su valor
            a_actual = pi[s]
            q_actual = sum(p * (r + gamma * V[sp]) for sp, p, r in mdp.transicion[(s, a_actual)])

            # Mejor acción posible
            mejor_a, mejor_q = a_actual, q_actual
            for a in mdp.acciones[s]:
                q = sum(p * (r + gamma * V[sp]) for sp, p, r in mdp.transicion[(s, a)])
                if q > mejor_q + 1e-12:
                    mejor_q = q
                    mejor_a = a

            pi_mejor[s] = mejor_a
            if mejor_a != a_actual:
                estable = False

        pi = pi_mejor
        if estable:
            return V, pi

# ---------------------------------------------------------------------
# Utilidades de impresión
# ---------------------------------------------------------------------

def pretty_values(V: Dict[State, float]) -> str:
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    out = []
    for s in orden:
        out.append(f"{s:15s}: V_pi = {V[s]:8.4f}")
    return "\n".join(out)

def pretty_policy(pi: Dict[State, Action]) -> str:
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal"]
    out = []
    for s in orden:
        if s in pi:
            out.append(f"{s:15s} -> {pi[s]}")
        else:
            out.append(f"{s:15s} -> (sin acción)")
    out.append(f"{'Nucleo_Central':15s} -> (terminal)")
    return "\n".join(out)

# ---------------------------------------------------------------------
# Simulación bajo π
# ---------------------------------------------------------------------

def simular(mdp: MDP, pi: Dict[State, Action], s0: State = "Base",
            pasos: int = 30, seed: Optional[int] = 5) -> Tuple[List[Tuple[State, Action, State, float]], float]:
    rnd = random.Random(seed)
    s = s0
    traj: List[Tuple[State, Action, State, float]] = []
    G = 0.0
    t = 0
    while t < pasos and s not in mdp.terminales:
        a = pi.get(s)
        if a is None:
            break
        dist = mdp.transicion[(s, a)]
        u = rnd.random()
        acc = 0.0
        sp, r = s, 0.0
        for s2, p, rew in dist:
            acc += p
            if u <= acc:
                sp, r = s2, rew
                break
        traj.append((s, a, sp, r))
        G += (GAMMA ** t) * r
        s = sp
        t += 1
    return traj, G

def pretty_traj(traj: List[Tuple[State, Action, State, float]]) -> str:
    if not traj:
        return "(sin pasos)"
    return "\n".join(f"{s} --{a}--> {sp}   r={r:.1f}" for s, a, sp, r in traj)

# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------

def demo():
    mdp = construir_mdp_tron()
    V_star, pi_star = policy_iteration(mdp, gamma=GAMMA, theta_eval=THETA_EVAL)

    print("Valores bajo la política óptima encontrada (tras convergencia):")
    print(pretty_values(V_star))
    print("\nPolítica óptima π*:")
    print(pretty_policy(pi_star))

    traj, G = simular(mdp, pi_star, s0="Base", pasos=30, seed=17)
    print("\nSimulación siguiendo π* desde Base:")
    print(pretty_traj(traj))
    print(f"\nRetorno acumulado descontado: {G:.2f}")

if __name__ == "__main__":
    demo()