"""
ELIMINACIÓN DE VARIABLES EN RED BAYESIANA TRON - INFERENCIA EXACTA EFICIENTE

Este código implementa el algoritmo de Eliminación de Variables para inferencia 
exacta en redes bayesianas. A diferencia de la enumeración que considera todas las 
combinaciones posibles, este método elimina variables sistemáticamente mediante 
operaciones de multiplicación de factores y marginalización, resultando en mayor 
eficiencia computacional para muchas redes.

Características principales:
- Inferencia exacta como enumeración pero más eficiente
- Elimina variables en orden óptimo para minimizar computación
- Opera sobre factores (distribuciones sobre subconjuntos de variables)
- Aprovecha la estructura de la red para reducir complejidad

Aplicación en TRON: Calcula P(SafePath | Sensor=OK) eliminando variables ocultas
(Power y Gate) de manera sistemática.
"""

from typing import Dict, List, Tuple
from itertools import product

# -------------------------------------------------------
# DEFINICIÓN DE LA RED BAYESIANA TRON
# -------------------------------------------------------

# Dominio de valores para cada variable del sistema
DOMAIN = {
    "Power":    ["Good", "Bad"],      # Estado del sistema de poder
    "Gate":     ["Open", "Closed"],   # Estado de la compuerta
    "Sensor":   ["OK", "Alert"],      # Lectura del sensor
    "SafePath": ["Yes", "No"]         # Seguridad del camino
}

# Estructura de dependencias (padres de cada variable)
PARENTS = {
    "Power":    [],           # Variable raíz
    "Gate":     ["Power"],    # Gate depende de Power
    "Sensor":   ["Power"],    # Sensor depende de Power
    "SafePath": ["Gate"]      # SafePath depende de Gate
}

# Tablas de Probabilidad Condicional (CPT)
CPT = {
    "Power": {
        tuple(): {"Good": 0.8, "Bad": 0.2}  # P(Power)
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
        ("Closed",): {"Yes": 0.20, "No": 0.80}    # P(SafePath | Gate=Closed)
    }
}

# -------------------------------------------------------
# REPRESENTACIÓN DE FACTORES PARA ELIMINACIÓN DE VARIABLES
# -------------------------------------------------------

class Factor:
    """
    Representa un factor como una distribución sobre un conjunto de variables.
    
    Un factor es una función que asigna valores a cada combinación de valores
    de sus variables. Puede representar una CPT completa o un factor intermedio
    durante el proceso de eliminación.
    """
    def __init__(self, vars: List[str], values: Dict[Tuple[str, ...], float]):
        self.vars = vars      # Variables en el ámbito del factor
        self.values = values  # Valores para cada combinación de variables

    def __str__(self):
        return f"Factor({self.vars}, {len(self.values)} filas)"

def make_factor(var: str, evidence: Dict[str, str]) -> Factor:
    """
    Crea un factor a partir de una CPT aplicando evidencia.
    
    Args:
        var: Variable para la cual crear el factor
        evidence: Evidencia observada (valores fijos para algunas variables)
        
    Returns:
        Factor que representa P(var | padres) con evidencia aplicada
    """
    parents = PARENTS[var]
    scope = parents + [var]  # Ámbito del factor: padres + variable
    values = {}
    
    # Generar todas las combinaciones posibles de valores en el ámbito
    for assign in product(*(DOMAIN[v] for v in scope)):
        a_dict = dict(zip(scope, assign))  # Convertir a diccionario
        
        # Verificar consistencia con la evidencia
        consistent = all(a_dict[e] == val for e, val in evidence.items() if e in a_dict)
        if not consistent:
            continue  # Saltar asignaciones inconsistentes con evidencia
            
        # Construir clave para el factor
        key = tuple(a_dict[v] for v in scope)
        # Obtener probabilidad de la CPT
        parent_key = tuple(a_dict[p] for p in parents)
        p = CPT[var][parent_key][a_dict[var]]
        values[key] = p
        
    return Factor(scope, values)

def multiply(f1: Factor, f2: Factor) -> Factor:
    """
    Multiplica dos factores para producir un nuevo factor.
    
    La multiplicación de factores combina sus distribuciones mediante
    producto punto a punto sobre las asignaciones compatibles.
    
    Args:
        f1, f2: Factores a multiplicar
        
    Returns:
        Nuevo factor con ámbito unión de los ámbitos de entrada
    """
    # Unión de variables manteniendo orden (sin duplicados)
    vars_new = list(dict.fromkeys(f1.vars + f2.vars))
    values = {}
    
    # Para cada combinación de valores en el nuevo ámbito
    for assign in product(*(DOMAIN[v] for v in vars_new)):
        a_dict = dict(zip(vars_new, assign))
        
        def lookup(f: Factor):
            """Busca valor en un factor para la asignación actual."""
            key = tuple(a_dict[v] for v in f.vars)
            return f.values.get(key, 0)  # 0 si no existe
            
        # Producto de los valores en ambos factores
        values[tuple(a_dict[v] for v in vars_new)] = lookup(f1) * lookup(f2)
        
    return Factor(vars_new, values)

def sum_out(var: str, f: Factor) -> Factor:
    """
    Elimina una variable de un factor mediante marginalización.
    
    Suma sobre todos los valores posibles de la variable especificada,
    efectivamente eliminándola del ámbito del factor.
    
    Args:
        var: Variable a eliminar
        f: Factor del cual eliminar la variable
        
    Returns:
        Nuevo factor sin la variable especificada
    """
    vars_new = [v for v in f.vars if v != var]  # Ámbito sin la variable
    values = {}
    
    # Para cada combinación en el nuevo ámbito
    for assign in product(*(DOMAIN[v] for v in vars_new)):
        a_dict = dict(zip(vars_new, assign))
        total = 0.0
        
        # Sumar sobre todos los valores de la variable a eliminar
        for val in DOMAIN[var]:
            a_dict[var] = val
            key_full = tuple(a_dict[v] for v in f.vars)
            total += f.values.get(key_full, 0)  # Sumar probabilidades
            
        values[tuple(a_dict[v] for v in vars_new)] = total
        
    return Factor(vars_new, values)

# -------------------------------------------------------
# ALGORITMO DE ELIMINACIÓN DE VARIABLES
# -------------------------------------------------------

def variable_elimination(query: str, evidence: Dict[str, str]) -> Dict[str, float]:
    """
    Ejecuta el algoritmo de eliminación de variables para inferencia.
    
    Args:
        query: Variable de consulta
        evidence: Evidencia observada
        
    Returns:
        Distribución de probabilidad posterior para la variable consulta
    """
    # 1. Inicializar factores a partir de las CPTs con evidencia aplicada
    factors = [make_factor(var, evidence) for var in DOMAIN]
    
    # 2. Identificar variables ocultas (no en evidencia ni en consulta)
    hidden_vars = [v for v in DOMAIN if v not in evidence and v != query]
    
    # 3. Eliminar cada variable oculta en orden
    for h in hidden_vars:
        # Encontrar todos los factores que contengan la variable actual
        related = [f for f in factors if h in f.vars]
        others = [f for f in factors if h not in f.vars]
        
        if not related:
            continue  # Si no hay factores con esta variable, continuar
            
        # Multiplicar todos los factores relacionados
        new_factor = related[0]
        for f in related[1:]:
            new_factor = multiply(new_factor, f)
            
        # Eliminar la variable mediante marginalización
        new_factor = sum_out(h, new_factor)
        
        # Reemplazar factores relacionados por el nuevo factor
        factors = others + [new_factor]
    
    # 4. Multiplicar factores restantes para obtener distribución conjunta
    result = factors[0]
    for f in factors[1:]:
        result = multiply(result, f)
    
    # 5. Normalizar para obtener distribución posterior
    probs = {}
    total = 0.0
    for val in DOMAIN[query]:
        for key, p in result.values.items():
            key_dict = dict(zip(result.vars, key))
            if key_dict.get(query) == val:
                total += p
                probs[val] = probs.get(val, 0) + p
                
    # Normalización final
    Z = sum(probs.values())
    return {k: v / Z for k, v in probs.items()}

# -------------------------------------------------------
# DEMOSTRACIÓN Y ANÁLISIS
# -------------------------------------------------------

def main():
    """
    Demuestra el algoritmo de eliminación de variables en TRON.
    """
    print("ELIMINACIÓN DE VARIABLES - INFERENCIA EN SISTEMA TRON")
    print("=" * 65)
    
    # Consulta: Probabilidad de camino seguro dado sensor OK
    q = "SafePath"
    e = {"Sensor": "OK"}
    posterior = variable_elimination(q, e)
    
    print(f"\nCONSULTA: P({q} | Sensor=OK)")
    print("-" * 40)
    for val, p in posterior.items():
        print(f"  P(SafePath={val} | Sensor=OK) = {p:.4f}")
    
    print(f"\nINTERPRETACIÓN:")
    print("El algoritmo eliminó las variables ocultas Power y Gate mediante:")
    print("1. Multiplicación de factores que contenían cada variable")
    print("2. Marginalización (suma) sobre los valores de la variable")
    print("3. Obtención de distribución exacta para SafePath dado Sensor=OK")
    
    print(f"\nVENTAJAS SOBRE ENUMERACIÓN:")
    print("- Evita computar todo el espacio de estados simultáneamente")
    print("- Opera localmente sobre subconjuntos de variables")
    print("- Más eficiente en memoria y computación para redes grandes")

def explicacion_pasos():
    """
    Explica los pasos detallados del algoritmo.
    """
    print(f"\n" + "="*65)
    print("PASOS DETALLADOS DEL ALGORITMO")
    print("="*65)
    print("1. INICIALIZACIÓN: Crear factores desde CPTs con evidencia")
    print("   - Factor_Power: P(Power)")
    print("   - Factor_Gate: P(Gate | Power)")  
    print("   - Factor_Sensor: P(Sensor | Power) con Sensor=OK")
    print("   - Factor_SafePath: P(SafePath | Gate)")
    print()
    print("2. ELIMINACIÓN: Remover variables ocultas (Power, Gate)")
    print("   - Multiplicar factores que contengan Power")
    print("   - Sumar sobre Power -> eliminar Power")
    print("   - Multiplicar factores que contengan Gate") 
    print("   - Sumar sobre Gate -> eliminar Gate")
    print()
    print("3. COMBINACIÓN: Multiplicar factores restantes")
    print("4. NORMALIZACIÓN: Obtener distribución posterior final")

if __name__ == "__main__":
    main()
    explicacion_pasos()