"""
INDEPENDENCIA CONDICIONAL EN ENTORNO TRON - MODELADO DE DEPENDENCIAS

Este código demuestra el concepto de independencia condicional en redes bayesianas.
Dos variables pueden ser dependientes en general, pero independientes cuando
conocemos el estado de una tercera variable que las influencia.

Escenario TRON: 
- Gate (Compuerta) afecta tanto a Sensor como a SafePath
- Sensor y SafePath están correlacionados por su causa común (Gate)
- Pero dado que conocemos el estado de Gate, Sensor y SafePath son independientes
"""

from typing import Dict

# -------------------------------------------------------
# PROBABILIDADES BASE - MODELO DE RED BAYESIANA
# -------------------------------------------------------
# Estructura causal: Gate → Sensor, Gate → SafePath
# Sensor y SafePath comparten la causa común "Gate"

# P(Gate) - Probabilidad del estado de la compuerta
P_Gate = {"Open": 0.6, "Closed": 0.4}

# P(Sensor | Gate) - Cómo el estado de la compuerta afecta las lecturas del sensor
P_Sensor_given_Gate = {
    ("Open",):   {"OK": 0.9, "Alert": 0.1},    # Compuerta abierta: 90% OK
    ("Closed",): {"OK": 0.4, "Alert": 0.6},    # Compuerta cerrada: 60% Alertas
}

# P(SafePath | Gate) - Cómo el estado de la compuerta afecta la seguridad del camino
P_SafePath_given_Gate = {
    ("Open",):   {"Yes": 0.95, "No": 0.05},    # Abierta: 95% seguro
    ("Closed",): {"Yes": 0.2,  "No": 0.8},     # Cerrada: 20% seguro
}

# -------------------------------------------------------
# FUNCIONES DE CÁLCULO PROBABILÍSTICO
# -------------------------------------------------------

def joint(sensor: str, safepath: str) -> float:
    """
    Calcula la probabilidad conjunta P(Sensor, SafePath) marginalizando sobre Gate.
    
    Cuando NO conocemos el estado de Gate, Sensor y SafePath están correlacionados
    porque ambos dependen de la misma variable oculta.
    
    Args:
        sensor: Estado del sensor ("OK" o "Alert")
        safepath: Seguridad del camino ("Yes" o "No")
    
    Returns:
        float: Probabilidad conjunta P(Sensor, SafePath)
    
    Fórmula: P(Sensor, SafePath) = Σ_gate P(Gate) × P(Sensor|Gate) × P(SafePath|Gate)
    """
    total = 0.0
    # Sumar sobre todos los estados posibles de Gate (marginalización)
    for gate, p_gate in P_Gate.items():
        # Probabilidad del sensor dado el estado de la compuerta
        p_sensor = P_Sensor_given_Gate[(gate,)][sensor]
        # Probabilidad de seguridad dado el estado de la compuerta  
        p_safe = P_SafePath_given_Gate[(gate,)][safepath]
        # Contribución de este estado de Gate a la probabilidad conjunta
        total += p_gate * p_sensor * p_safe
    return total

def conditional(sensor: str, safepath: str, gate: str) -> float:
    """
    Calcula la probabilidad condicional P(Sensor, SafePath | Gate).
    
    Cuando SÍ conocemos el estado de Gate, Sensor y SafePath se vuelven 
    independientes porque su única fuente de correlación ha sido fijada.
    
    Args:
        sensor: Estado del sensor
        safepath: Seguridad del camino  
        gate: Estado conocido de la compuerta
    
    Returns:
        float: P(Sensor, SafePath | Gate)
    
    Fórmula (por independencia condicional): 
        P(Sensor, SafePath | Gate) = P(Sensor|Gate) × P(SafePath|Gate)
    """
    # Obtener probabilidad condicional del sensor dado Gate
    p_sensor = P_Sensor_given_Gate[(gate,)][sensor]
    # Obtener probabilidad condicional de seguridad dado Gate
    p_safe = P_SafePath_given_Gate[(gate,)][safepath]
    # Por independencia condicional, la conjunta es el producto
    return p_sensor * p_safe

# -------------------------------------------------------
# DEMOSTRACIÓN Y VERIFICACIÓN DE INDEPENDENCIA CONDICIONAL
# -------------------------------------------------------

def main():
    """
    Demuestra el concepto de independencia condicional mediante ejemplos numéricos.
    """
    print("INDEPENDENCIA CONDICIONAL EN SISTEMA TRON")
    print("=" * 65)
    print("Estructura causal: Gate → Sensor, Gate → SafePath")
    print("Sensor y SafePath comparten Gate como causa común")
    print()
    
    # Mostrar las probabilidades base del modelo
    print("PROBABILIDADES BASE DEL MODELO:")
    print("-" * 40)
    print("P(Gate):")
    for gate, prob in P_Gate.items():
        print(f"  {gate}: {prob:.2f}")
    
    print("\nP(Sensor | Gate):")
    for gate, dist in P_Sensor_given_Gate.items():
        print(f"  Gate={gate[0]}: OK={dist['OK']:.2f}, Alert={dist['Alert']:.2f}")
    
    print("\nP(SafePath | Gate):")
    for gate, dist in P_SafePath_given_Gate.items():
        print(f"  Gate={gate[0]}: Yes={dist['Yes']:.2f}, No={dist['No']:.2f}")
    
    print("\n" + "="*65)
    print("ANÁLISIS DE DEPENDENCIAS")
    print("="*65)
    
    # Caso 1: Sin información sobre Gate - variables correlacionadas
    print("\n1) SIN conocer Gate (variables DEPENDIENTES):")
    print("-" * 40)
    
    # Calcular probabilidad conjunta sin condicionar
    p_joint = joint("OK", "Yes")
    print(f"P(Sensor=OK, SafePath=Yes) = {p_joint:.4f}")
    
    # Mostrar el cálculo paso a paso
    print("\nCálculo marginalizando sobre Gate:")
    for gate, p_gate in P_Gate.items():
        p_sensor = P_Sensor_given_Gate[(gate,)]["OK"]
        p_safe = P_SafePath_given_Gate[(gate,)]["Yes"]
        print(f"  Gate={gate}: {p_gate:.2f} × {p_sensor:.2f} × {p_safe:.2f} = {p_gate * p_sensor * p_safe:.4f}")
    
    # Caso 2: Con Gate conocida - independencia condicional
    print("\n2) CONOCIDO Gate=Open (INDEPENDENCIA CONDICIONAL):")
    print("-" * 40)
    
    # Calcular probabilidad condicional dado Gate=Open
    p_cond = conditional("OK", "Yes", "Open")
    print(f"P(Sensor=OK, SafePath=Yes | Gate=Open) = {p_cond:.4f}")
    
    # Mostrar que se factoriza por independencia
    p_sensor_given_open = P_Sensor_given_Gate[("Open",)]["OK"]
    p_safe_given_open = P_SafePath_given_Gate[("Open",)]["Yes"]
    print(f"\nVerificación de independencia condicional:")
    print(f"  P(Sensor=OK | Gate=Open) = {p_sensor_given_open:.2f}")
    print(f"  P(SafePath=Yes | Gate=Open) = {p_safe_given_open:.2f}")
    print(f"  Producto = {p_sensor_given_open:.2f} × {p_safe_given_open:.2f} = {p_cond:.4f}")
    
    print("\n" + "="*65)
    print("INTERPRETACIÓN CONCEPTUAL")
    print("="*65)
    
    print("\nANALOGÍA: Dos testigos de un accidente")
    print("• Sin saber si hubo accidente: sus testimonios están correlacionados")
    print("• Sabiendo que SÍ hubo accidente: sus testimonios son independientes")
    print("• La causa común (accidente) explica su correlación")
    
    print("\nEN TRON:")
    print("• Sin conocer Gate: Sensor y SafePath parecen relacionados")
    print("• Conociendo Gate=Open:")
    print("  - Sensor probablemente esté OK (90%)")
    print("  - Camino probablemente seguro (95%)")  
    print("  - Pero un resultado no afecta la probabilidad del otro")
    print("  - Son independientes porque Gate explica toda su correlación")

def verificacion_matematica():
    """
    Verificación matemática adicional de la independencia condicional.
    """
    print("\n" + "="*65)
    print("VERIFICACIÓN MATEMÁTICA")
    print("="*65)
    
    print("\nComprobando definición de independencia condicional:")
    print("X ⫫ Y | Z si P(X,Y|Z) = P(X|Z) × P(Y|Z) para todos X,Y,Z")
    
    # Probar con diferentes combinaciones
    combinaciones = [
        ("OK", "Yes", "Open"),
        ("Alert", "No", "Closed"), 
        ("OK", "No", "Open"),
        ("Alert", "Yes", "Closed")
    ]
    
    print("\nResultados para diferentes combinaciones:")
    for sensor, safepath, gate in combinaciones:
        p_conjunta_cond = conditional(sensor, safepath, gate)
        p_sensor_cond = P_Sensor_given_Gate[(gate,)][sensor]
        p_safe_cond = P_SafePath_given_Gate[(gate,)][safepath]
        producto = p_sensor_cond * p_safe_cond
        
        # Verificar si son iguales (dentro de tolerancia numérica)
        iguales = abs(p_conjunta_cond - producto) < 1e-10
        simbolo = "*" if iguales else "X"
        
        print(f"  {simbolo} P({sensor},{safepath}|{gate}) = {p_conjunta_cond:.4f} = {p_sensor_cond:.2f}×{p_safe_cond:.2f} = {producto:.4f}")
    
    print("\nConclusión: Sensor y SafePath son condicionalmente independientes dado Gate")

if __name__ == "__main__":
    main()
    verificacion_matematica()