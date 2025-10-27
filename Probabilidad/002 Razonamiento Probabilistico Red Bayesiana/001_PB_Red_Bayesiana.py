# Red Bayesiana simple (TRON)
from typing import Dict, List, Tuple

# -------------------------------
# Representación de la Red Bayesiana
# -------------------------------

class BayesNet:
    def __init__(self):
        self.parents = {}     # var -> lista de padres
        self.cpt = {}         # var -> { tuple(padres): {valor: prob} }
        self.domain = {}      # var -> lista de valores

    def add_var(self, var: str, domain: List[str], parents: List[str], table: Dict[Tuple, Dict[str, float]]):
        self.parents[var] = parents[:]
        self.cpt[var] = table
        self.domain[var] = domain[:]

    def P(self, var: str, val: str, assignment: Dict[str, str]) -> float:
        key = tuple(assignment[p] for p in self.parents[var]) if self.parents[var] else tuple()
        return self.cpt[var][key][val]

# ------------------------------------------------
# Construcción de la Red Bayesiana TRON (simple)
# ------------------------------------------------

def tron_bn() -> BayesNet:
    bn = BayesNet()

    # Power: Good/Bad
    bn.add_var(
        "Power",
        ["Good", "Bad"],
        [],
        {
            tuple(): {"Good": 0.8, "Bad": 0.2}
        }
    )

    # Gate | Power
    bn.add_var(
        "Gate",
        ["Open", "Closed"],
        ["Power"],
        {
            ("Good",): {"Open": 0.9, "Closed": 0.1},
            ("Bad",):  {"Open": 0.3, "Closed": 0.7},
        }
    )

    # Sensor | Power
    bn.add_var(
        "Sensor",
        ["OK", "Alert"],
        ["Power"],
        {
            ("Good",): {"OK": 0.85, "Alert": 0.15},
            ("Bad",):  {"OK": 0.3, "Alert": 0.7},
        }
    )

    # SafePath | Gate
    bn.add_var(
        "SafePath",
        ["Yes", "No"],
        ["Gate"],
        {
            ("Open",):   {"Yes": 0.95, "No": 0.05},
            ("Closed",): {"Yes": 0.20, "No": 0.80},
        }
    )

    return bn

# ---------------------------------------
# Inferencia exacta por enumeración
# ---------------------------------------

def enumerate_ask(query_var: str, evidence: Dict[str, str], bn: BayesNet) -> Dict[str, float]:
    Q = {}
    for x in bn.domain[query_var]:
        ev = evidence.copy()
        ev[query_var] = x
        Q[x] = enumerate_all(list(bn.domain.keys()), ev, bn)
    s = sum(Q.values())
    return {k: v / s for k, v in Q.items()}

def enumerate_all(vars_list: List[str], assignment: Dict[str, str], bn: BayesNet) -> float:
    if not vars_list:
        return 1.0
    Y = vars_list[0]
    rest = vars_list[1:]
    if Y in assignment:
        p = bn.P(Y, assignment[Y], assignment)
        return p * enumerate_all(rest, assignment, bn)
    else:
        total = 0.0
        for y in bn.domain[Y]:
            assignment[Y] = y
            total += bn.P(Y, y, assignment) * enumerate_all(rest, assignment, bn)
        del assignment[Y]
        return total

# -----------------
# Ejemplos de uso
# -----------------

def demo():
    bn = tron_bn()

    print("1) P(SafePath | Sensor=OK)")
    res = enumerate_ask("SafePath", {"Sensor": "OK"}, bn)
    print(res)

    print("\n2) P(SafePath | Sensor=Alert)")
    res = enumerate_ask("SafePath", {"Sensor": "Alert"}, bn)
    print(res)

    print("\n3) P(Power | Sensor=Alert)")
    res = enumerate_ask("Power", {"Sensor": "Alert"}, bn)
    print(res)

    print("\n4) P(SafePath | Gate=Open)")
    res = enumerate_ask("SafePath", {"Gate": "Open"}, bn)
    print(res)

    print("\n5) P(SafePath) sin evidencia")
    res = enumerate_ask("SafePath", {}, bn)
    print(res)

if __name__ == "__main__":
    demo()