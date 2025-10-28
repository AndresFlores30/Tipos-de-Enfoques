"""
INFERENCIA POR ENUMERACIÓN EXACTA EN RED BAYESIANA TRON

Este código implementa el algoritmo de enumeración exacta para realizar inferencia
probabilística en una red bayesiana. La enumeración es un método completo y exacto
que calcula probabilidades posteriores sumando sobre todas las posibles asignaciones
de variables no observadas.

Características del algoritmo:
- Inferencia exacta (no aproximada)
- Completo para redes bayesianas discretas
- Basado en recorrido recursivo del espacio de posibles estados
- Sigue el enfoque del libro "Artificial Intelligence: A Modern Approach" (AIMA)

Aplicación en TRON: Calcula probabilidades condicionadas sobre el estado del sistema
dada evidencia parcial de sensores y componentes.
"""

from typing import Dict, List, Tuple

# -------------------------------
# DEFINICIÓN DE LA RED BAYESIANA TRON
# -------------------------------
# Estructura: Power -> {Gate, Sensor}, Gate -> SafePath

# Dominio de valores para cada variable
DOMAIN = {
    "Power":    ["Good", "Bad"],      # Estado del sistema de poder
    "Gate":     ["Open", "Closed"],   # Estado de la compuerta
    "Sensor":   ["OK", "Alert"],      # Lectura del sensor
    "SafePath": ["Yes", "No"]         # Seguridad del camino
}

# Relaciones de dependencia (padres de cada variable)
PARENTS = {
    "Power":    [],           # Variable raíz sin padres
    "Gate":     ["Power"],    # Gate depende de Power
    "Sensor":   ["Power"],    # Sensor depende de Power  
    "SafePath": ["Gate"]      # SafePath depende de Gate
}

# Tablas de Probabilidad Condicional (CPT)
# CPT[var][tuple(padres_en_orden)]['valor'] = probabilidad
CPT: Dict[str, Dict[Tuple[str, ...], Dict[str, float]]] = {
    "Power": {
        # Probabilidad marginal de Power
        tuple(): {"Good": 0.8, "Bad": 0.2}
    },
    "Gate": {
        # P(Gate | Power=Good)
        ("Good",): {"Open": 0.9, "Closed": 0.1},
        # P(Gate | Power=Bad)  
        ("Bad",):  {"Open": 0.3, "Closed": 0.7}
    },
    "Sensor": {
        # P(Sensor | Power=Good)
        ("Good",): {"OK": 0.9, "Alert": 0.1},
        # P(Sensor | Power=Bad)
        ("Bad",):  {"OK": 0.3, "Alert": 0.7}
    },
    "SafePath": {
        # P(SafePath | Gate=Open)
        ("Open",):   {"Yes": 0.95, "No": 0.05},
        # P(SafePath | Gate=Closed)
        ("Closed",): {"Yes": 0.20, "No": 0.80}
    }
}

# Orden topológico para procesamiento (padres antes de hijos)
TOPO = ["Power", "Gate", "Sensor", "SafePath"]

def P(var: str, val: str, assignment: Dict[str, str]) -> float:
    """
    Obtiene la probabilidad condicional P(var=val | padres) de la CPT.
    
    Args:
        var: Variable de interés
        val: Valor de la variable
        assignment: Asignación actual de valores a todas las variables
        
    Returns:
        Probabilidad condicional P(var=val | padres(var))
    """
    parents = PARENTS[var]  # Obtener lista de padres
    # Construir clave para la CPT usando valores de los padres
    key = tuple(assignment[p] for p in parents) if parents else tuple()
    return CPT[var][key][val]  # Retornar probabilidad de la CPT

# -------------------------------
# ALGORITMO DE INFERENCIA POR ENUMERACIÓN
# -------------------------------
def enumerate_ask(query_var: str, evidence: Dict[str, str]) -> Dict[str, float]:
    """
    Calcula la distribución de probabilidad posterior P(query_var | evidence).
    
    Args:
        query_var: Variable sobre la que queremos consultar
        evidence: Evidencia observada (variables con valores conocidos)
        
    Returns:
        Distribución de probabilidad posterior para query_var normalizada
    """
    Q = {}  # Almacenará probabilidades no normalizadas
    # Para cada valor posible de la variable consulta
    for x in DOMAIN[query_var]:
        # Extender la evidencia con el valor de consulta
        extended = dict(evidence)
        extended[query_var] = x
        # Calcular probabilidad conjunta P(query_var=x, evidence)
        Q[x] = enumerate_all(TOPO, extended)
    
    # Normalizar las probabilidades
    Z = sum(Q.values())  # Factor de normalización (probabilidad de la evidencia)
    return {k: v / Z for k, v in Q.items()}  # Retornar distribución posterior normalizada

def enumerate_all(vars_list: List[str], assignment: Dict[str, str]) -> float:
    """
    Calcula recursivamente la probabilidad conjunta de la asignación actual.
    
    El algoritmo recorre las variables en orden topológico, sumando sobre
    variables no observadas y multiplicando probabilidades condicionales.
    
    Args:
        vars_list: Lista de variables restantes por procesar
        assignment: Asignación actual de valores a variables
        
    Returns:
        Probabilidad conjunta de la asignación actual
    """
    # Caso base: no hay más variables por procesar
    if not vars_list:
        return 1.0
        
    Y = vars_list[0]    # Primera variable en la lista
    rest = vars_list[1:]  # Resto de variables
    
    if Y in assignment:
        # Si Y tiene valor asignado, usar ese valor
        prob_y = P(Y, assignment[Y], assignment)  # P(Y | padres(Y))
        # Continuar recursivamente con el resto de variables
        return prob_y * enumerate_all(rest, assignment)
    else:
        # Si Y no tiene valor asignado, sumar sobre todos sus valores posibles
        total = 0.0
        for y in DOMAIN[Y]:
            assignment[Y] = y  # Asignar valor temporalmente
            # Sumar: P(Y=y | padres) × P(resto | Y=y)
            total += P(Y, y, assignment) * enumerate_all(rest, assignment)
        del assignment[Y]  # Limpiar asignación temporal
        return total

# -------------------------------
# DEMOSTRACIONES Y CASOS DE USO
# -------------------------------
def main():
    """
    Ejecuta demostraciones de diferentes tipos de inferencia en TRON.
    """
    print("INFERENCIA POR ENUMERACIÓN EXACTA - SISTEMA TRON")
    print("=" * 60)
    
    # Consulta 1: Inferencia predictiva (de causa a efecto)
    print("1) P(SafePath | Sensor=OK) - Inferencia predictiva")
    print("   ¿Qué tan seguro es el camino si el sensor está OK?")
    result = enumerate_ask("SafePath", {"Sensor": "OK"})
    for valor, prob in result.items():
        print(f"   P(SafePath={valor} | Sensor=OK) = {prob:.4f}")
    
    # Consulta 2: Inferencia diagnóstica (de efecto a causa)  
    print("\n2) P(Power | Sensor=Alert) - Inferencia diagnóstica")
    print("   ¿Cuál es el estado del poder si el sensor alerta?")
    result = enumerate_ask("Power", {"Sensor": "Alert"})
    for valor, prob in result.items():
        print(f"   P(Power={valor} | Sensor=Alert) = {prob:.4f}")
    
    # Consulta 3: Inferencia directa
    print("\n3) P(SafePath | Gate=Open) - Inferencia directa")
    print("   ¿Qué tan seguro es el camino si la compuerta está abierta?")
    result = enumerate_ask("SafePath", {"Gate": "Open"})
    for valor, prob in result.items():
        print(f"   P(SafePath={valor} | Gate=Open) = {prob:.4f}")
    
    # Consulta 4: Probabilidad marginal (sin evidencia)
    print("\n4) P(SafePath) - Probabilidad marginal")
    print("   ¿Cuál es la seguridad general del camino sin evidencia?")
    result = enumerate_ask("SafePath", {})
    for valor, prob in result.items():
        print(f"   P(SafePath={valor}) = {prob:.4f}")

def explicacion_algoritmo():
    """
    Explica el funcionamiento interno del algoritmo de enumeración.
    """
    print("\n" + "=" * 60)
    print("EXPLICACIÓN DEL ALGORITMO DE ENUMERACIÓN")
    print("=" * 60)
    print("1. Orden topológico: Power -> Gate -> Sensor -> SafePath")
    print("2. Para cada valor de la variable consulta:")
    print("   - Fijar ese valor en la evidencia")
    print("   - Calcular P(consulta,evidencia) sumando sobre variables ocultas")
    print("3. Normalizar usando P(evidencia) como factor")
    print()
    print("Complejidad: Exponencial en el número de variables ocultas")
    print("Ventaja: Resultados exactos")
    print("Aplicación: Redes pequeñas o medianas")

if __name__ == "__main__":
    main()
    explicacion_algoritmo()