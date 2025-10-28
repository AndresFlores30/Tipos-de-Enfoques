# Red Bayesiana (TRON)
from typing import Dict, List, Tuple

# -------------------------------
# Representación de la Red Bayesiana
# -------------------------------

class BayesNet:
    def __init__(self):
        self.parents = {}     # var -> lista de padres (estructura del grafo)
        self.cpt = {}         # var -> { tuple(padres): {valor: prob} } (tablas de probabilidad condicional)
        self.domain = {}      # var -> lista de valores posibles para cada variable

    def add_var(self, var: str, domain: List[str], parents: List[str], table: Dict[Tuple, Dict[str, float]]):
        # Añade una variable a la red bayesiana con sus padres y tabla de probabilidad condicional
        self.parents[var] = parents[:]  # Copia de la lista de padres
        self.cpt[var] = table           # Tabla de probabilidad condicional
        self.domain[var] = domain[:]    # Dominio de valores posibles

    def P(self, var: str, val: str, assignment: Dict[str, str]) -> float:
        # Obtiene la probabilidad P(var=val | padres) dado un assignment de valores
        # Construye la clave para buscar en la CPT basada en los valores de los padres
        key = tuple(assignment[p] for p in self.parents[var]) if self.parents[var] else tuple()
        return self.cpt[var][key][val]  # Retorna la probabilidad de la CPT

# ------------------------------------------------
# Construcción de la Red Bayesiana TRON (simple)
# ------------------------------------------------

def tron_bn() -> BayesNet:
    bn = BayesNet()

    # Power: Good/Bad - Variable raíz sin padres
    bn.add_var(
        "Power",
        ["Good", "Bad"],  # Dominio: dos estados posibles
        [],               # Sin padres (variable raíz)
        {
            tuple(): {"Good": 0.8, "Bad": 0.2}  # Probabilidad marginal P(Power)
        }
    )

    # Gate | Power - Gate depende de Power
    bn.add_var(
        "Gate",
        ["Open", "Closed"],  # Dos estados posibles para Gate
        ["Power"],           # Padre: Power
        {
            ("Good",): {"Open": 0.9, "Closed": 0.1},  # P(Gate | Power=Good)
            ("Bad",):  {"Open": 0.3, "Closed": 0.7},  # P(Gate | Power=Bad)
        }
    )

    # Sensor | Power - Sensor depende de Power
    bn.add_var(
        "Sensor",
        ["OK", "Alert"],  # Dos lecturas posibles del sensor
        ["Power"],        # Padre: Power
        {
            ("Good",): {"OK": 0.85, "Alert": 0.15},  # P(Sensor | Power=Good)
            ("Bad",):  {"OK": 0.3, "Alert": 0.7},    # P(Sensor | Power=Bad)
        }
    )

    # SafePath | Gate - SafePath depende de Gate
    bn.add_var(
        "SafePath",
        ["Yes", "No"],  # Dos estados de seguridad del camino
        ["Gate"],       # Padre: Gate
        {
            ("Open",):   {"Yes": 0.95, "No": 0.05},   # P(SafePath | Gate=Open)
            ("Closed",): {"Yes": 0.20, "No": 0.80},   # P(SafePath | Gate=Closed)
        }
    )

    return bn

# ---------------------------------------
# Inferencia exacta por enumeración
# ---------------------------------------

def enumerate_ask(query_var: str, evidence: Dict[str, str], bn: BayesNet) -> Dict[str, float]:
    """
    Calcula P(query_var | evidence) usando el algoritmo de enumeración.
    
    Args:
        query_var: Variable sobre la que queremos consultar
        evidence: Evidencia observada (variables con valores conocidos)
        bn: Red bayesiana
    
    Returns:
        Distribución de probabilidad posterior para query_var
    """
    Q = {}  # Almacenará las probabilidades no normalizadas para cada valor de query_var
    for x in bn.domain[query_var]:
        # Para cada valor posible de la variable consulta
        ev = evidence.copy()      # Copia la evidencia
        ev[query_var] = x         # Añade el valor de consulta a la evidencia
        Q[x] = enumerate_all(list(bn.domain.keys()), ev, bn)  # Calcula probabilidad conjunta
    
    s = sum(Q.values())  # Calcula factor de normalización
    return {k: v / s for k, v in Q.items()}  # Normaliza las probabilidades

def enumerate_all(vars_list: List[str], assignment: Dict[str, str], bn: BayesNet) -> float:
    """
    Calcula la probabilidad conjunta P(vars_list, assignment) recursivamente.
    
    Args:
        vars_list: Lista de variables restantes por procesar
        assignment: Asignación actual de valores a variables
        bn: Red bayesiana
    
    Returns:
        Probabilidad conjunta de la asignación
    """
    if not vars_list:
        return 1.0  # Caso base: no hay más variables
    
    Y = vars_list[0]    # Toma la primera variable
    rest = vars_list[1:]  # Resto de variables
    
    if Y in assignment:
        # Si Y tiene valor asignado, usa ese valor
        p = bn.P(Y, assignment[Y], assignment)  # P(Y | padres(Y))
        return p * enumerate_all(rest, assignment, bn)  # Recursión con resto de variables
    else:
        # Si Y no tiene valor asignado, suma sobre todos sus valores posibles
        total = 0.0
        for y in bn.domain[Y]:
            assignment[Y] = y  # Asigna valor temporal
            # Suma: P(Y=y | padres) × P(resto | Y=y)
            total += bn.P(Y, y, assignment) * enumerate_all(rest, assignment, bn)
        del assignment[Y]  # Limpia la asignación temporal
        return total

# -----------------
# Ejemplos de uso
# -----------------

def main():
    bn = tron_bn()  # Construye la red bayesiana de TRON

    print("1) P(SafePath | Sensor=OK)")
    # ¿Qué tan seguro es el camino dado que el sensor está OK?
    res = enumerate_ask("SafePath", {"Sensor": "OK"}, bn)
    print(res)

    print("\n2) P(SafePath | Sensor=Alert)")
    # ¿Qué tan seguro es el camino dado que el sensor alerta?
    res = enumerate_ask("SafePath", {"Sensor": "Alert"}, bn)
    print(res)

    print("\n3) P(Power | Sensor=Alert)")
    # ¿Cuál es el estado del poder dado que el sensor alerta?
    res = enumerate_ask("Power", {"Sensor": "Alert"}, bn)
    print(res)

    print("\n4) P(SafePath | Gate=Open)")
    # ¿Qué tan seguro es el camino si sabemos que la compuerta está abierta?
    res = enumerate_ask("SafePath", {"Gate": "Open"}, bn)
    print(res)

    print("\n5) P(SafePath) sin evidencia")
    # Probabilidad marginal del camino seguro sin evidencia
    res = enumerate_ask("SafePath", {}, bn)
    print(res)

if __name__ == "__main__":
    main()