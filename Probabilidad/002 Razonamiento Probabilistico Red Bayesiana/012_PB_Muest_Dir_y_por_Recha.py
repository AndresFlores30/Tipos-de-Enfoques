# Muestreo Directo y por Rechazo — Ejemplo simple con temática TRON
# Red Bayesiana: Power → {Gate, Sensor}, Gate → SafePath

import random
from typing import Dict, List, Tuple

# -------------------------------------------------------
# Red Bayesiana base
# -------------------------------------------------------

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

CPT = {
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
        ("Closed",): {"Yes": 0.2,  "No": 0.8}
    }
}

TOPO = ["Power", "Gate", "Sensor", "SafePath"]

# -------------------------------------------------------
# Funciones de probabilidad condicional
# -------------------------------------------------------

def P(var: str, val: str, assignment: Dict[str, str]) -> float:
    parents = PARENTS[var]
    key = tuple(assignment[p] for p in parents) if parents else tuple()
    return CPT[var][key][val]

def sample_from_dist(dist: Dict[str, float]) -> str:
    vals, probs = zip(*dist.items())
    return random.choices(vals, weights=probs, k=1)[0]

# -------------------------------------------------------
# Muestreo directo (Prior Sampling)
# -------------------------------------------------------

def prior_sample() -> Dict[str, str]:
    """Genera una muestra completa siguiendo el orden topológico."""
    sample = {}
    for var in TOPO:
        dist = {}
        parents = PARENTS[var]
        key = tuple(sample[p] for p in parents) if parents else tuple()
        dist = CPT[var][key]
        sample[var] = sample_from_dist(dist)
    return sample

def estimate_prior(query_var: str, value: str, N: int = 10000) -> float:
    """Estima P(query_var=value) con muestreo directo."""
    count = 0
    for _ in range(N):
        s = prior_sample()
        if s[query_var] == value:
            count += 1
    return count / N

# -------------------------------------------------------
# Muestreo por rechazo (Rejection Sampling)
# -------------------------------------------------------

def rejection_sampling(query_var: str, value: str, evidence: Dict[str, str], N: int = 10000) -> float:
    """Estima P(query_var=value | evidence) rechazando muestras inconsistentes."""
    consistent = []
    for _ in range(N):
        s = prior_sample()
        if all(s[e] == v for e, v in evidence.items()):
            consistent.append(s)
    if not consistent:
        return 0.0
    count = sum(1 for s in consistent if s[query_var] == value)
    return count / len(consistent)

# -------------------------------------------------------
# Ejemplo demostrativo
# -------------------------------------------------------

def demo():
    random.seed(7)

    print("Muestreo Directo y por Rechazo en TRON")
    print("--------------------------------------")

    # 1) P(SafePath=Yes)
    p_prior = estimate_prior("SafePath", "Yes")
    print(f"P(SafePath=Yes) ≈ {p_prior:.4f} (muestreo directo)")

    # 2) P(SafePath=Yes | Sensor=OK)
    p_reject = rejection_sampling("SafePath", "Yes", {"Sensor": "OK"})
    print(f"P(SafePath=Yes | Sensor=OK) ≈ {p_reject:.4f} (muestreo por rechazo)")

    print("\nInterpretación:")
    print("El muestreo directo genera estados completos desde la red.")
    print("El muestreo por rechazo descarta aquellos que no coinciden con la evidencia,")
    print("permitiendo estimar probabilidades condicionadas aproximadas.")

if __name__ == "__main__":
    demo()