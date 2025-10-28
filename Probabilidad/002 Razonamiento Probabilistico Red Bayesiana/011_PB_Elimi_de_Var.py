# Eliminación de Variables — Ejemplo simple con temática TRON
#
# Red Bayesiana: Power → {Gate, Sensor}, Gate → SafePath
# Objetivo: Inferir P(SafePath | Sensor=OK)

from typing import Dict, List, Tuple
from itertools import product

# -------------------------------------------------------
# Definición de la Red Bayesiana
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
        ("Closed",): {"Yes": 0.20, "No": 0.80}
    }
}

# -------------------------------------------------------
# Representación de factores
# -------------------------------------------------------

class Factor:
    def __init__(self, vars: List[str], values: Dict[Tuple[str, ...], float]):
        self.vars = vars
        self.values = values

    def __str__(self):
        return f"Factor({self.vars}, {len(self.values)} filas)"

def make_factor(var: str, evidence: Dict[str, str]) -> Factor:
    """Crea un factor P(var | padres(var)) con evidencia aplicada."""
    parents = PARENTS[var]
    scope = parents + [var]
    values = {}
    for assign in product(*(DOMAIN[v] for v in scope)):
        a_dict = dict(zip(scope, assign))
        # aplicar evidencia
        consistent = all(a_dict[e] == val for e, val in evidence.items() if e in a_dict)
        if not consistent:
            continue
        key = tuple(a_dict[v] for v in scope)
        p = CPT[var][tuple(a_dict[p] for p in parents)][a_dict[var]]
        values[key] = p
    return Factor(scope, values)

def multiply(f1: Factor, f2: Factor) -> Factor:
    """Multiplica dos factores."""
    vars_new = list(dict.fromkeys(f1.vars + f2.vars))
    values = {}
    for assign in product(*(DOMAIN[v] for v in vars_new)):
        a_dict = dict(zip(vars_new, assign))
        def lookup(f: Factor):
            key = tuple(a_dict[v] for v in f.vars)
            return f.values.get(key, 0)
        values[tuple(a_dict[v] for v in vars_new)] = lookup(f1) * lookup(f2)
    return Factor(vars_new, values)

def sum_out(var: str, f: Factor) -> Factor:
    """Elimina una variable (marginalización)."""
    vars_new = [v for v in f.vars if v != var]
    values = {}
    for assign in product(*(DOMAIN[v] for v in vars_new)):
        a_dict = dict(zip(vars_new, assign))
        total = 0.0
        for val in DOMAIN[var]:
            a_dict[var] = val
            key_full = tuple(a_dict[v] for v in f.vars)
            total += f.values.get(key_full, 0)
        values[tuple(a_dict[v] for v in vars_new)] = total
    return Factor(vars_new, values)

# -------------------------------------------------------
# Inferencia por Eliminación de Variables
# -------------------------------------------------------

def variable_elimination(query: str, evidence: Dict[str, str]) -> Dict[str, float]:
    factors = [make_factor(var, evidence) for var in DOMAIN]

    hidden_vars = [v for v in DOMAIN if v not in evidence and v != query]

    for h in hidden_vars:
        # Multiplicar todos los factores que contengan h
        related = [f for f in factors if h in f.vars]
        others = [f for f in factors if h not in f.vars]
        if not related:
            continue
        new_factor = related[0]
        for f in related[1:]:
            new_factor = multiply(new_factor, f)
        # Sumar (eliminar) h
        new_factor = sum_out(h, new_factor)
        factors = others + [new_factor]

    # Multiplicar los factores restantes
    result = factors[0]
    for f in factors[1:]:
        result = multiply(result, f)

    # Normalizar la distribución final
    probs = {}
    total = 0.0
    for val in DOMAIN[query]:
        for key, p in result.values.items():
            key_dict = dict(zip(result.vars, key))
            if key_dict.get(query) == val:
                total += p
                probs[val] = probs.get(val, 0) + p
    Z = sum(probs.values())
    return {k: v / Z for k, v in probs.items()}

# -------------------------------------------------------
# Ejemplo demostrativo
# -------------------------------------------------------

def demo():
    print("Eliminación de Variables en TRON")
    print("-------------------------------")

    q = "SafePath"
    e = {"Sensor": "OK"}
    posterior = variable_elimination(q, e)

    print(f"\nConsulta: P({q} | Sensor=OK)")
    for val, p in posterior.items():
        print(f"  {val}: {p:.4f}")

    print("\nInterpretación:")
    print("El método elimina variables ocultas (Power y Gate) mediante multiplicación y marginalización,")
    print("obteniendo la probabilidad exacta de SafePath dado que el Sensor indica 'OK'.")

if __name__ == "__main__":
    demo()