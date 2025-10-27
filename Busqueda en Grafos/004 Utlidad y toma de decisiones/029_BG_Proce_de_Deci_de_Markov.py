# Proceso de Decisión de Markov (MDP) con temática TRON
# - Definición del MDP: estados, acciones, transiciones y recompensas
# - Evaluación de Política (iterativa)
# - Iteración de Políticas
# - Iteración de Valores
# - Simulación de trayectoria con la política encontrada

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random

State = str
Action = str
Transition = List[Tuple[State, float, float]]  # (siguiente_estado, prob, recompensa)

# ---------------------------------------------------------------------
# Parámetros globales del entorno TRON
# ---------------------------------------------------------------------

# Grafo de sectores (vecindad)
VECINOS: Dict[State, List[State]] = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": [],  # terminal
}

# Rutas más frágiles a interferencia (más desvíos, menos éxito)
RUTAS_FRAGILES = {
    ("Arena", "Torre_IO"),
    ("Torre_IO", "Nucleo_Central"),
    ("Portal", "Arena"),
}

# Recompensas por transición
R_PASO = -0.5
R_AVANCE = +2.0
R_DESVIO = -3.0
R_QUEDARSE = -1.0
R_OBJETIVO = +150.0

# Dinámica base
P_SUCCESS = 0.80
P_STAY = 0.10
DELTA_FRAGIL = 0.20  # reduce P_SUCCESS en rutas frágiles; el resto va a desvío

# Descuento y tolerancias
GAMMA = 0.95
THETA_EVAL = 1e-8
THETA_VI = 1e-6
MAX_EVAL_ITERS = 10000


@dataclass
class MDP:
    estados: List[State]
    acciones: Dict[State, List[Action]]
    transicion: Dict[Tuple[State, Action], Transition]
    terminales: List[State]


def construir_mdp_tron() -> MDP:
    """
    Construye un MDP a partir del grafo VECINOS.
    Acciones: 'to:<vecino>' desde cada estado no terminal.
    Transición: éxito al vecino elegido, quedarse, o desvío a otros vecinos.
    Recompensa: R_PASO + {R_AVANCE, R_DESVIO, R_QUEDARSE} y R_OBJETIVO al entrar al Núcleo.
    """
    estados = list(VECINOS.keys())
    terminales = ["Nucleo_Central"]
    acciones: Dict[State, List[Action]] = {}
    transicion: Dict[Tuple[State, Action], Transition] = {}

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
            trans: Transition = []

            # Éxito
            r_ok = R_PASO + (R_OBJETIVO if destino == "Nucleo_Central" else R_AVANCE)
            trans.append((destino, success, r_ok))

            # Quedarse
            trans.append((s, stay, R_PASO + R_QUEDARSE))

            # Desvíos
            if otros:
                p_cada = p_desvio / len(otros)
                for alt in otros:
                    r_alt = R_PASO + (R_OBJETIVO if alt == "Nucleo_Central" else R_DESVIO)
                    trans.append((alt, p_cada, r_alt))
            else:
                # Si no hay otros vecinos, agrega el desvío a "quedarse"
                sp, p_old, r_old = trans[1]
                trans[1] = (sp, p_old + p_desvio, r_old)

            # Normaliza por seguridad
            sprob = sum(p for _, p, _ in trans)
            if abs(sprob - 1.0) > 1e-9:
                trans = [(sp, p / sprob, r) for (sp, p, r) in trans]

            transicion[(s, a)] = trans

    return MDP(estados=estados, acciones=acciones, transicion=transicion, terminales=terminales)


# ---------------------------------------------------------------------
# Utilidades de impresión
# ---------------------------------------------------------------------

def pretty_values(V: Dict[State, float]) -> str:
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    return "\n".join(f"{s:15s}: {V[s]:9.4f}" for s in orden)

def pretty_policy(pi: Dict[State, Action]) -> str:
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal"]
    out = []
    for s in orden:
        out.append(f"{s:15s} -> {pi.get(s, '(sin acción)')}")
    out.append(f"{'Nucleo_Central':15s} -> (terminal)")
    return "\n".join(out)

def pretty_traj(traj: List[Tuple[State, Action, State, float]]) -> str:
    if not traj:
        return "(sin pasos)"
    return "\n".join(f"{s} --{a}--> {sp}   r={r:.1f}" for s, a, sp, r in traj)


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
            q = sum(p * (r + gamma * V[sp]) for sp, p, r in mdp.transicion[(s, a)])
            delta = max(delta, abs(q - V[s]))
            V[s] = q
        if delta < theta:
            break
    return V


# ---------------------------------------------------------------------
# Iteración de Políticas (Howard)
# ---------------------------------------------------------------------

def policy_iteration(mdp: MDP, gamma: float = GAMMA,
                     theta_eval: float = THETA_EVAL) -> Tuple[Dict[State, float], Dict[State, Action]]:
    # Política inicial: primera acción disponible
    pi: Dict[State, Action] = {}
    for s in mdp.estados:
        if s not in mdp.terminales and mdp.acciones[s]:
            pi[s] = mdp.acciones[s][0]

    while True:
        V = evaluar_politica(mdp, pi, gamma=gamma, theta=theta_eval)

        estable = True
        pi_new: Dict[State, Action] = {}
        for s in mdp.estados:
            if s in mdp.terminales or not mdp.acciones[s]:
                continue

            # Acción actual y su Q
            a_act = pi[s]
            q_act = sum(p * (r + gamma * V[sp]) for sp, p, r in mdp.transicion[(s, a_act)])

            # Mejor acción posible
            mejor_a, mejor_q = a_act, q_act
            for a in mdp.acciones[s]:
                q = sum(p * (r + gamma * V[sp]) for sp, p, r in mdp.transicion[(s, a)])
                if q > mejor_q + 1e-12:
                    mejor_q, mejor_a = q, a
            pi_new[s] = mejor_a
            if mejor_a != a_act:
                estable = False

        pi = pi_new
        if estable:
            return V, pi


# ---------------------------------------------------------------------
# Iteración de Valores
# ---------------------------------------------------------------------

def value_iteration(mdp: MDP, gamma: float = GAMMA, theta: float = THETA_VI) -> Tuple[Dict[State, float], Dict[State, Action]]:
    V = {s: 0.0 for s in mdp.estados}
    for s in mdp.terminales:
        V[s] = 0.0

    while True:
        delta = 0.0
        for s in mdp.estados:
            if s in mdp.terminales:
                continue
            v_old = V[s]
            q_vals = []
            for a in mdp.acciones[s]:
                q = sum(p * (r + gamma * V[sp]) for sp, p, r in mdp.transicion[(s, a)])
                q_vals.append(q)
            V[s] = max(q_vals) if q_vals else V[s]
            delta = max(delta, abs(V[s] - v_old))
        if delta < theta:
            break

    # Política codiciosa respecto a V
    pi: Dict[State, Action] = {}
    for s in mdp.estados:
        if s in mdp.terminales or not mdp.acciones[s]:
            continue
        mejor_a, mejor_q = None, float("-inf")
        for a in mdp.acciones[s]:
            q = sum(p * (r + gamma * V[sp]) for sp, p, r in mdp.transicion[(s, a)])
            if q > mejor_q:
                mejor_q, mejor_a = q, a
        pi[s] = mejor_a
    return V, pi


# ---------------------------------------------------------------------
# Simulación de trayectoria bajo una política
# ---------------------------------------------------------------------

def simular(mdp: MDP, pi: Dict[State, Action], s0: State = "Base",
            pasos: int = 30, gamma: float = GAMMA, seed: Optional[int] = 11) -> Tuple[List[Tuple[State, Action, State, float]], float]:
    rnd = random.Random(seed)
    s = s0
    traj: List[Tuple[State, Action, State, float]] = []
    G = 0.0
    t = 0

    while t < pasos and s not in mdp.terminales:
        a = pi.get(s)
        if a is None:
            break
        # Muestrear transición
        u = rnd.random()
        acc = 0.0
        sp_sel, r_sel = s, 0.0
        for sp, p, r in mdp.transicion[(s, a)]:
            acc += p
            if u <= acc:
                sp_sel, r_sel = sp, r
                break

        traj.append((s, a, sp_sel, r_sel))
        G += (gamma ** t) * r_sel
        s = sp_sel
        t += 1
    return traj, G


# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------

def demo():
    mdp = construir_mdp_tron()

    print("=== MDP TRON: Iteración de Políticas ===")
    V_pi, pi_star = policy_iteration(mdp, gamma=GAMMA, theta_eval=THETA_EVAL)
    print("\nValores bajo la política óptima encontrada:")
    print(pretty_values(V_pi))
    print("\nPolítica óptima π*:")
    print(pretty_policy(pi_star))

    tray, Gret = simular(mdp, pi_star, s0="Base", pasos=30, seed=7)
    print("\nSimulación siguiendo π* desde Base:")
    print(pretty_traj(tray))
    print(f"\nRetorno descontado: {Gret:.2f}")

    print("\n=== MDP TRON: Iteración de Valores ===")
    V_vi, pi_vi = value_iteration(mdp, gamma=GAMMA, theta=THETA_VI)
    print("\nValores óptimos V*:")
    print(pretty_values(V_vi))
    print("\nPolítica codiciosa respecto a V*:")
    print(pretty_policy(pi_vi))

if __name__ == "__main__":
    demo()