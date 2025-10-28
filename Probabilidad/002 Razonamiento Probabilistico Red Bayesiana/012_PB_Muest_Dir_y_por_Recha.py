"""
MUESTREO DIRECTO Y POR RECHAZO EN RED BAYESIANA TRON - INFERENCIA APROXIMADA

Este código implementa dos métodos de inferencia aproximada basados en muestreo:
- Muestreo Directo (Prior Sampling): Genera muestras de la distribución conjunta
- Muestreo por Rechazo (Rejection Sampling): Filtra muestras inconsistentes con evidencia

Estos métodos son alternativas prácticas cuando la inferencia exacta es computacionalmente
costosa. Proporcionan estimaciones aproximadas que convergen a los valores reales cuando
el número de muestras tiende a infinito.

Aplicación en TRON: Estima probabilidades sobre el estado del sistema mediante
simulación estadística, útil para monitoreo en tiempo real y toma de decisiones
bajo incertidumbre con recursos computacionales limitados.
"""

import random
from typing import Dict, List, Tuple

# -------------------------------------------------------
# CONFIGURACIÓN DE LA RED BAYESIANA TRON
# -------------------------------------------------------

# Dominio de valores posibles para cada variable del sistema
DOMAIN = {
    "Power":    ["Good", "Bad"],      # Estado del sistema de poder
    "Gate":     ["Open", "Closed"],   # Estado de la compuerta
    "Sensor":   ["OK", "Alert"],      # Lectura del sensor
    "SafePath": ["Yes", "No"]         # Seguridad del camino
}

# Estructura de dependencias (relaciones padre-hijo)
PARENTS = {
    "Power":    [],           # Variable raíz sin padres
    "Gate":     ["Power"],    # Gate depende del estado del Power
    "Sensor":   ["Power"],    # Sensor depende del estado del Power
    "SafePath": ["Gate"]      # SafePath depende del estado de Gate
}

# Tablas de Probabilidad Condicional (Conditional Probability Tables)
CPT = {
    "Power": {
        tuple(): {"Good": 0.8, "Bad": 0.2}  # Distribución marginal de Power
    },
    "Gate": {
        ("Good",): {"Open": 0.9, "Closed": 0.1},  # P(Gate | Power=Good)
        ("Bad",):  {"Open": 0.3, "Closed": 0.7}   # P(Gate | Power=Bad)
    },
    "Sensor": {
        ("Good",): {"OK": 0.9, "Alert": 0.1},     # P(Sensor | Power=Good)
        ("Bad",):  {"OK": 0.3, "Alert": 0.7}      # P(Sensor | Power=Bad)
    },
    "SafePath": {
        ("Open",):   {"Yes": 0.95, "No": 0.05},   # P(SafePath | Gate=Open)
        ("Closed",): {"Yes": 0.2,  "No": 0.8}     # P(SafePath | Gate=Closed)
    }
}

# Orden topológico para muestreo (padres antes de hijos)
TOPO = ["Power", "Gate", "Sensor", "SafePath"]

# -------------------------------------------------------
# FUNCIONES AUXILIARES PARA PROBABILIDAD Y MUESTREO
# -------------------------------------------------------

def P(var: str, val: str, assignment: Dict[str, str]) -> float:
    """
    Obtiene probabilidad condicional P(var=val | padres) de la CPT.
    
    Args:
        var: Variable de interés
        val: Valor específico de la variable
        assignment: Asignación actual de valores a todas las variables
        
    Returns:
        Probabilidad condicional de la CPT
    """
    parents = PARENTS[var]
    # Construir clave para la CPT basada en valores de los padres
    key = tuple(assignment[p] for p in parents) if parents else tuple()
    return CPT[var][key][val]

def sample_from_dist(dist: Dict[str, float]) -> str:
    """
    Muestrea un valor de una distribución discreta.
    
    Args:
        dist: Distribución como diccionario {valor: probabilidad}
        
    Returns:
        Valor muestreado aleatoriamente según la distribución
    """
    vals, probs = zip(*dist.items())  # Separar valores y probabilidades
    return random.choices(vals, weights=probs, k=1)[0]  # Muestrear según pesos

# -------------------------------------------------------
# MUESTREO DIRECTO (PRIOR SAMPLING)
# -------------------------------------------------------

def prior_sample() -> Dict[str, str]:
    """
    Genera una muestra completa del sistema siguiendo orden topológico.
    
    El muestreo directo genera muestras de la distribución conjunta completa
    recorriendo las variables en orden causal (padres antes de hijos) y
    muestreando cada variable condicionada a sus padres ya asignados.
    
    Returns:
        Muestra completa del sistema con valores para todas las variables
    """
    sample = {}
    for var in TOPO:
        # Obtener distribución condicional para esta variable
        parents = PARENTS[var]
        # Construir clave para CPT basada en padres ya muestreados
        key = tuple(sample[p] for p in parents) if parents else tuple()
        dist = CPT[var][key]  # Distribución P(var | padres)
        # Muestrear valor para esta variable
        sample[var] = sample_from_dist(dist)
    return sample

def estimate_prior(query_var: str, value: str, N: int = 10000) -> float:
    """
    Estima probabilidad marginal P(query_var=value) mediante muestreo directo.
    
    Args:
        query_var: Variable de interés
        value: Valor específico a estimar
        N: Número de muestras a generar
        
    Returns:
        Probabilidad estimada P(query_var=value)
    """
    count = 0
    for _ in range(N):
        s = prior_sample()  # Generar muestra completa
        if s[query_var] == value:
            count += 1  # Contar si coincide con el valor consultado
    return count / N  # Estimación por frecuencia relativa

# -------------------------------------------------------
# MUESTREO POR RECHAZO (REJECTION SAMPLING)
# -------------------------------------------------------

def rejection_sampling(query_var: str, value: str, evidence: Dict[str, str], N: int = 10000) -> float:
    """
    Estima P(query_var=value | evidence) mediante muestreo por rechazo.
    
    El método genera muestras de la distribución conjunta y rechaza aquellas
    que no son consistentes con la evidencia observada. Usa las muestras
    consistentes para estimar la probabilidad condicional.
    
    Args:
        query_var: Variable de consulta
        value: Valor específico de la variable consulta
        evidence: Evidencia observada {variable: valor}
        N: Número máximo de muestras a generar
        
    Returns:
        Probabilidad condicional estimada P(query_var=value | evidence)
    """
    consistent = []  # Almacenar muestras consistentes con evidencia
    
    for _ in range(N):
        s = prior_sample()  # Generar muestra completa
        
        # Verificar si la muestra es consistente con toda la evidencia
        if all(s[e] == v for e, v in evidence.items()):
            consistent.append(s)  # Guardar muestra consistente
    
    # Si no hay muestras consistentes, retornar 0
    if not consistent:
        return 0.0
    
    # Contar cuántas muestras consistentes tienen el valor consultado
    count = sum(1 for s in consistent if s[query_var] == value)
    
    # Estimación = frecuencia relativa en muestras consistentes
    return count / len(consistent)

# -------------------------------------------------------
# DEMOSTRACIÓN Y ANÁLISIS COMPARATIVO
# -------------------------------------------------------

def main():
    """
    Demuestra ambos métodos de muestreo con ejemplos prácticos en TRON.
    """
    random.seed(7)  # Semilla para reproducibilidad
    
    print("INFERENCIA POR MUESTREO - SISTEMA TRON")
    print("=" * 65)
    
    print("CONFIGURACIÓN DE LA RED:")
    print("- Power → Gate, Power → Sensor, Gate → SafePath")
    print("- P(Power=Good) = 0.8, P(Sensor=OK | Power=Good) = 0.9")
    print("- P(SafePath=Yes | Gate=Open) = 0.95")
    print()
    
    # Ejemplo 1: Probabilidad marginal con muestreo directo
    print("1) ESTIMACIÓN CON MUESTREO DIRECTO")
    print("-" * 40)
    p_prior = estimate_prior("SafePath", "Yes")
    print(f"P(SafePath=Yes) ≈ {p_prior:.4f}")
    print("Método: Generar muestras completas y contar frecuencia")
    print("Aplicación: Entender comportamiento general del sistema")
    
    # Ejemplo 2: Probabilidad condicional con muestreo por rechazo
    print("\n2) ESTIMACIÓN CON MUESTREO POR RECHAZO")
    print("-" * 40)
    p_reject = rejection_sampling("SafePath", "Yes", {"Sensor": "OK"})
    print(f"P(SafePath=Yes | Sensor=OK) ≈ {p_reject:.4f}")
    print("Método: Filtrar muestras inconsistentes con Sensor=OK")
    print("Aplicación: Diagnosticar estado dado evidencia observada")
    
    print("\n" + "=" * 65)
    print("ANÁLISIS COMPARATIVO DE MÉTODOS")
    print("=" * 65)
    
    print("MUESTREO DIRECTO (Prior Sampling):")
    print("* Ventaja: Simple y eficiente para probabilidades marginales")
    print("X Desventaja: Ineficiente para evidencia rara (muchas muestras rechazadas)")
    
    print("\nMUESTREO POR RECHAZO (Rejection Sampling):")
    print("* Ventaja: Conceptualmente simple, fácil de implementar")
    print("X Desventaja: Muy ineficiente con evidencia de baja probabilidad")
    print("X Desventaja: Desperdicia muestras inconsistentes")

if __name__ == "__main__":
    main()