# Iteración de Valores (MDP) con temática TRON
# - Estados: sectores del Grid
# - Acciones: rutas hacia vecinos
# - Dinámica estocástica: éxito, desvío por interferencia o quedarse
# - Recompensas: paso, colisión, llegada al Núcleo
# - Output: V* y política óptima π*, más una simulación ejemplo

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import random

State = str
Action = str

# ---------------------------------------------------------------------
# Definición del Grid TRON
# ---------------------------------------------------------------------
# Grafo de sectores (vecinos directos)
VECINOS: Dict[State, List[State]] = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": [],  # estado terminal
}

# Algunas rutas son "frágiles" frente a interferencia (más desvíos)
RUTAS_FRAGILES = {
    ("Arena", "Torre_IO"),
    ("Torre_IO", "Nucleo_Central"),
    ("Portal", "Arena"),
}

# Recompensas por transición
R_AVANCE = +2.0          # avanzar a un vecino deseado
R_DESVIO = -3.0          # te desvían a un vecino distinto
R_QUEDARSE = -1.0        # no te mueves por colisión leve
R_OBJETIVO = +150.0      # llegar al Núcleo
R_PASO = -0.5            # costo energético por paso (siempre)

# Probabilidades base de la dinámica (sin firewall)
P_SUCCESS = 0.80         # prob. de ir al vecino elegido
P_STAY = 0.10            # prob. de quedarse por colisión leve
# El resto (1 - P_SUCCESS - P_STAY) se reparte entre desvíos

# Penalización adicional por rutas frágiles (menor éxito, más desvíos)
DELTA_FRAGIL = 0.20      # reduce éxito y aumenta desvío en rutas frágiles

# Descuento y criterio de convergencia
GAMMA = 0.95
THETA = 1e-6


@dataclass
class MDP:
    estados: List[State]
    acciones: Dict[State, List[Action]]
    transicion: Dict[Tuple[State, Action], List[Tuple[State, float, float]]]
    terminales: List[State]


def construir_mdp_tron() -> MDP:
    """
    Construye un MDP a partir del grafo:
    - Acciones: 'to:<vecino>' desde cada estado no terminal.
    - Transición estocástica: éxito, quedarse, desvío a otro vecino.
    - Recompensa por transición: R_PASO + {R_AVANCE, R_DESVIO, R_QUEDARSE, R_OBJETIVO}.
    """
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
            destino_elegido = a.split("to:")[1]

            # Ajuste de probabilidades si la ruta es frágil
            success = P_SUCCESS
            stay = P_STAY
            if (s, destino_elegido) in RUTAS_FRAGILES:
                success = max(0.0, P_SUCCESS - DELTA_FRAGIL)
                # trasladamos la diferencia a desvío, no a "stay"
                # para conservar un poco de 'atascos' constantes
            p_desvio = max(0.0, 1.0 - success - stay)

            otros = [v for v in vecinos if v != destino_elegido]
            trans: List[Tuple[State, float, float]] = []

            # Éxito: ir al destino elegido
            r = R_PASO + (R_OBJETIVO if destino_elegido == "Nucleo_Central" else R_AVANCE)
            trans.append((destino_elegido, success, r))

            # Quedarse en el mismo estado
            trans.append((s, stay, R_PASO + R_QUEDARSE))

            # Repartir desvío uniformemente entre otros vecinos
            if otros:
                p_cada = p_desvio / len(otros)
                for valt in otros:
                    rdiv = R_PASO + (R_OBJETIVO if valt == "Nucleo_Central" else R_DESVIO)
                    trans.append((valt, p_cada, rdiv))
            else:
                # Si no hay otros vecinos, sumamos el p_desvio a quedarse
                # para que la distribución de prob sea 1.
                # Reemplazamos el registro stay con stay+p_desvio
                s_, p_old, r_old = trans[1]
                trans[1] = (s_, p_old + p_desvio, r_old)

            # Normaliza por seguridad
            sprob = sum(p for _, p, _ in trans)
            if abs(sprob - 1.0) > 1e-9:
                # normalización suave
                trans = [(sp, p / sprob, r) for (sp, p, r) in trans]

            transicion[(s, a)] = trans

    return MDP(estados=estados, acciones=acciones, transicion=transicion, terminales=terminales)


# ---------------------------------------------------------------------
# Iteración de Valores
# ---------------------------------------------------------------------

def value_iteration(mdp: MDP, gamma: float = GAMMA, theta: float = THETA) -> Tuple[Dict[State, float], Dict[State, Action]]:
    """
    Devuelve (V*, π*) con iteración de valores estándar.
    """
    V = {s: 0.0 for s in mdp.estados}
    for s in mdp.terminales:
        V[s] = 0.0  # valor base del terminal (recompensa ya viene en transición)

    while True:
        delta = 0.0
        for s in mdp.estados:
            if s in mdp.terminales:
                continue
            mejores_q = []
            for a in mdp.acciones[s]:
                q = 0.0
                for sp, p, r in mdp.transicion[(s, a)]:
                    q += p * (r + gamma * V[sp])
                mejores_q.append(q)
            v_new = max(mejores_q) if mejores_q else V[s]
            delta = max(delta, abs(v_new - V[s]))
            V[s] = v_new
        if delta < theta:
            break

    # Política codiciosa respecto a V*
    pi: Dict[State, Action] = {}
    for s in mdp.estados:
        if s in mdp.terminales or not mdp.acciones[s]:
            continue
        mejor_a, mejor_q = None, float("-inf")
        for a in mdp.acciones[s]:
            q = 0.0
            for sp, p, r in mdp.transicion[(s, a)]:
                q += p * (r + gamma * V[sp])
            if q > mejor_q:
                mejor_q, mejor_a = q, a
        pi[s] = mejor_a
    return V, pi


# ---------------------------------------------------------------------
# Simulación de una trayectoria siguiendo π*
# ---------------------------------------------------------------------

def simular(mdp: MDP, pi: Dict[State, Action], s0: State = "Base", pasos: int = 20, seed: Optional[int] = 7) -> Tuple[List[Tuple[State, Action, State, float]], float]:
    rnd = random.Random(seed)
    s = s0
    tray: List[Tuple[State, Action, State, float]] = []
    retorno = 0.0
    for t in range(pasos):
        if s in mdp.terminales:
            break
        a = pi.get(s)
        if a is None:
            break
        # muestrear siguiente estado según la distribución
        dist = mdp.transicion[(s, a)]
        u = rnd.random()
        acum = 0.0
        next_s, rew = s, 0.0
        for sp, p, r in dist:
            acum += p
            if u <= acum:
                next_s, rew = sp, r
                break
        tray.append((s, a, next_s, rew))
        retorno += rew * (GAMMA ** t)
        s = next_s
    return tray, retorno


# ---------------------------------------------------------------------
# Utilidades para imprimir resultados
# ---------------------------------------------------------------------

def pretty_values(V: Dict[State, float]) -> str:
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    out = []
    for s in orden:
        out.append(f"{s:15s}: V* = {V[s]:8.3f}")
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

def pretty_traj(tray: List[Tuple[State, Action, State, float]]) -> str:
    if not tray:
        return "(sin pasos)"
    lines = []
    for (s, a, sp, r) in tray:
        lines.append(f"{s} --{a}--> {sp}   r={r:.1f}")
    return "\n".join(lines)


# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------

def demo():
    mdp = construir_mdp_tron()
    V, pi = value_iteration(mdp, gamma=GAMMA, theta=THETA)

    print("Valores óptimos V*:")
    print(pretty_values(V))
    print("\nPolítica óptima π* (acción por estado):")
    print(pretty_policy(pi))

    tray, G = simular(mdp, pi, s0="Base", pasos=30, seed=11)
    print("\nSimulación desde Base siguiendo π*:")
    print(pretty_traj(tray))
    print(f"\nRetorno acumulado descontado (gamma={GAMMA}): {G:.2f}")

if __name__ == "__main__":
    demo()