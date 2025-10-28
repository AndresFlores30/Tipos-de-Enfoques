# Inferencia por Enumeración (exacta) en una BN simple de TRON
# Estructura: Power -> {Gate, Sensor}, Gate -> SafePath

from typing import Dict, List, Tuple

# -------------------------------
# Red Bayesiana — estructura y CPT
# -------------------------------
DOMAIN = {
    "Power":    ["Good", "Bad"],
    "Gate":     ["Open", "Closed"],
    "Sensor":   ["OK", "Alert"],
    "SafePath": ["Yes", "No"]
}

PARENTS = {
    "Power":    [],
    "Gate":     ["Power"],
    "Sensor":   ["Power"],
    "SafePath": ["Gate"]
}

# CPT[var][tuple(padres_en_orden)]['valor'] = prob
CPT: Dict[str, Dict[Tuple[str, ...], Dict[str, float]]] = {
    "Power": {
        tuple(): {"Good": 0.8, "Bad": 0.2}
    },
    "Gate": {
        ("Good",): {"Open": 0.9, "Closed": 0.1},
        ("Bad",):  {"Open": 0.3, "Closed": 0.7}
    },
    "Sensor": {
        ("Good",): {"OK": 0.9, "Alert": 0.1},
        ("Bad",):  {"OK": 0.3, "Alert": 0.7}
    },
    "SafePath": {
        ("Open",):   {"Yes": 0.95, "No": 0.05},
        ("Closed",): {"Yes": 0.20, "No": 0.80}
    }
}

# Orden topológico sencillo
TOPO = ["Power", "Gate", "Sensor", "SafePath"]

def P(var: str, val: str, assignment: Dict[str, str]) -> float:
    """Devuelve P(var=val | padres) usando CPT y la asignación parcial."""
    parents = PARENTS[var]
    key = tuple(assignment[p] for p in parents) if parents else tuple()
    return CPT[var][key][val]

# -------------------------------
# Inferencia por Enumeración
# -------------------------------
def enumerate_ask(query_var: str, evidence: Dict[str, str]) -> Dict[str, float]:
    """Calcula P(query_var | evidence) por enumeración exacta."""
    Q = {}
    for x in DOMAIN[query_var]:
        extended = dict(evidence)
        extended[query_var] = x
        Q[x] = enumerate_all(TOPO, extended)
    Z = sum(Q.values())
    return {k: v / Z for k, v in Q.items()}

def enumerate_all(vars_list: List[str], assignment: Dict[str, str]) -> float:
    """Suma recursiva sobre variables ocultas (AIMA-style)."""
    if not vars_list:
        return 1.0
    Y = vars_list[0]
    rest = vars_list[1:]
    if Y in assignment:
        return P(Y, assignment[Y], assignment) * enumerate_all(rest, assignment)
    else:
        total = 0.0
        for y in DOMAIN[Y]:
            assignment[Y] = y
            total += P(Y, y, assignment) * enumerate_all(rest, assignment)
        del assignment[Y]
        return total

# -------------------------------
# Demos rápidas
# -------------------------------
def demo():
    print("1) P(SafePath | Sensor=OK)")
    print(enumerate_ask("SafePath", {"Sensor": "OK"}))

    print("\n2) P(Power | Sensor=Alert)")
    print(enumerate_ask("Power", {"Sensor": "Alert"}))

    print("\n3) P(SafePath | Gate=Open)")
    print(enumerate_ask("SafePath", {"Gate": "Open"}))

    print("\n4) P(SafePath) sin evidencia")
    print(enumerate_ask("SafePath", {}))

if __name__ == "__main__":
    demo()