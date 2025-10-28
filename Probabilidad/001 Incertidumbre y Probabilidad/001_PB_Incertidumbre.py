"""
INFERENCIA BAYESIANA EN ENTORNO TRON - MODELADO DE INCERTIDUMBRE

Este código demuestra cómo el razonamiento probabilístico y el teorema de Bayes
permiten actualizar creencias ante nueva evidencia en un contexto de TRON.

Conceptos clave ilustrados:
- Probabilidades previas (prior): creencia inicial antes de ver evidencia
- Verosimilitud (likelihood): cómo la evidencia se relaciona con las hipótesis
- Probabilidades posteriores (posterior): creencia actualizada después de la evidencia
- Red Bayesiana simple: modelo gráfico de dependencias probabilísticas

Escenario: Determinar la seguridad de un camino en TRON basándose en
observaciones del estado del poder y sensores.
"""

from typing import Dict

# -----------------------------------------------------
# RED BAYESIANA - MODELO PROBABILÍSTICO DEL ENTORNO TRON
# -----------------------------------------------------

# P(Power) - Probabilidad previa del estado del sistema de poder
# Representa nuestra creencia inicial sobre el estado del sistema
P_Power = {"Good": 0.8, "Bad": 0.2}

# P(Gate | Power) - Probabilidad condicional de la compuerta dado el poder
# Cómo el estado del poder afecta la operación de las compuertas
P_Gate_given_Power = {
    ("Good",): {"Open": 0.9, "Closed": 0.1},  # Con buen poder: 90% abierta
    ("Bad",):  {"Open": 0.3, "Closed": 0.7},  # Con mal poder: 70% cerrada
}

# P(Sensor | Power) - Probabilidad condicional del sensor dado el poder
# Cómo el estado del poder afecta la confiabilidad de los sensores
P_Sensor_given_Power = {
    ("Good",): {"OK": 0.85, "Alert": 0.15},  # Buen poder: 15% falsas alarmas
    ("Bad",):  {"OK": 0.3, "Alert": 0.7},    # Mal poder: 70% de alertas reales
}

# P(SafePath | Gate) - Probabilidad condicional del camino seguro dado la compuerta
# Cómo el estado de la compuerta afecta la seguridad del camino
P_SafePath_given_Gate = {
    ("Open",):   {"Yes": 0.95, "No": 0.05},  # Compuerta abierta: 95% seguro
    ("Closed",): {"Yes": 0.2,  "No": 0.8},   # Compuerta cerrada: 20% seguro
}

# -----------------------------------------------------
# INFERENCIA PROBABILÍSTICA - ACTUALIZACIÓN DE CREENCIAS
# -----------------------------------------------------

def prior_probability_safe_path() -> float:
    """
    Calcula la probabilidad previa P(SafePath=Yes) SIN evidencia.
    
    Esta es nuestra creencia inicial sobre la seguridad del camino antes
    de observar cualquier sensor o evidencia. Representa la incertidumbre
    total del sistema.
    
    Returns:
        float: Probabilidad de que el camino sea seguro (0-1)
    
    Cálculo: P(SafePath) = Σ_{Power,Gate} P(Power) * P(Gate|Power) * P(SafePath|Gate)
    """
    total = 0.0
    # Iterar sobre todas las combinaciones posibles de Power y Gate
    for power, p_power in P_Power.items():
        for gate, p_gate in P_Gate_given_Power[(power,)].items():
            # Obtener probabilidad de camino seguro para esta compuerta
            p_safe = P_SafePath_given_Gate[(gate,)]['Yes']
            # Sumar la probabilidad conjunta: P(Power) * P(Gate|Power) * P(SafePath|Gate)
            total += p_power * p_gate * p_safe
    return total

def posterior_given_alert() -> float:
    """
    Calcula la probabilidad posterior P(SafePath=Yes | Sensor=Alert) CON evidencia.
    
    Aplica el teorema de Bayes para actualizar nuestra creencia sobre la seguridad
    del camino después de observar que el sensor está en alerta.
    
    Returns:
        float: Probabilidad actualizada de camino seguro dado Sensor=Alert
    
    Pasos:
    1. Calcular P(Power | Sensor=Alert) usando Bayes
    2. Calcular P(SafePath | Sensor=Alert) propagando la incertidumbre
    """
    # PASO 1: Actualizar creencia sobre Power dado Sensor=Alert
    # P(Power | Sensor=Alert) ∝ P(Power) * P(Sensor=Alert | Power)
    unnormalized = {}
    for power in P_Power:
        # Probabilidad no normalizada: previa * verosimilitud
        unnormalized[power] = P_Power[power] * P_Sensor_given_Power[(power,)]['Alert']
    
    # Normalizar para obtener probabilidades posteriores válidas
    norm = sum(unnormalized.values())
    P_Power_given_Alert = {k: v / norm for k, v in unnormalized.items()}

    # PASO 2: Calcular P(SafePath | Sensor=Alert) usando Power actualizado
    total = 0.0
    for power, p_power in P_Power_given_Alert.items():
        for gate, p_gate in P_Gate_given_Power[(power,)].items():
            p_safe = P_SafePath_given_Gate[(gate,)]['Yes']
            # Usar P(Power | Sensor=Alert) en lugar de P(Power)
            total += p_power * p_gate * p_safe
    return total

# -----------------------------------------------------
# DEMOSTRACIÓN Y ANÁLISIS
# -----------------------------------------------------

def main():
    """
    Ejecuta una demostración completa del razonamiento bayesiano en TRON.
    
    Muestra cómo la evidencia (alerta del sensor) actualiza nuestras creencias
    sobre la seguridad del camino, reduciendo la incertidumbre.
    """
    print("INFERENCIA BAYESIANA EN TRON: MODELADO DE INCERTIDUMBRE")
    print("=" * 65)
    print("Red Bayesiana: Power → {Gate, Sensor} → SafePath")
    print()
    
    # Mostrar las probabilidades base del modelo
    print("PROBABILIDADES BASE DEL MODELO:")
    print(f"- P(Power=Good) = {P_Power['Good']:.2f}")
    print(f"- P(Gate=Open | Power=Good) = {P_Gate_given_Power[('Good',)]['Open']:.2f}")
    print(f"- P(Sensor=Alert | Power=Bad) = {P_Sensor_given_Power[('Bad',)]['Alert']:.2f}")
    print(f"- P(SafePath=Yes | Gate=Open) = {P_SafePath_given_Gate[('Open',)]['Yes']:.2f}")
    print()

    # Calcular probabilidad previa (sin evidencia)
    p_prior = prior_probability_safe_path()
    print("1) PROBABILIDAD PREVIA (sin evidencia):")
    print(f"   P(SafePath=Yes) = {p_prior:.4f}")
    print("   -> Creencia inicial basada solo en probabilidades base")
    print("   -> Alta incertidumbre: no sabemos el estado real del sistema")
    print()

    # Calcular probabilidad posterior (con evidencia)
    p_posterior = posterior_given_alert()
    print("2) PROBABILIDAD POSTERIOR (con evidencia Sensor=Alert):")
    print(f"   P(SafePath=Yes | Sensor=Alert) = {p_posterior:.4f}")
    print("   -> Creencia actualizada después de observar alerta del sensor")
    print("   -> La evidencia reduce la incertidumbre sobre el estado del poder")
    print()

    # Análisis del cambio
    cambio = (p_posterior - p_prior) / p_prior * 100
    print("ANÁLISIS DEL IMPACTO DE LA EVIDENCIA:")
    print(f"   Cambio relativo: {cambio:+.2f}%")
    print()
    
    # Interpretación cualitativa
    if cambio < 0:
        print("INTERPRETACIÓN:")
        print("   La alerta del sensor indica mayor probabilidad de poder defectuoso,")
        print("   lo que aumenta la probabilidad de compuertas cerradas,")
        print("   reduciendo así la confianza en la seguridad del camino.")
        print()
        print("   La evidencia nos hizo MÁS Cautelosos sobre la seguridad.")
    else:
        print("INTERPRETACIÓN:")
        print("   La evidencia aumentó nuestra confianza en la seguridad del camino.")
        print("   La alerta del sensor nos hizo MENOS Cautelosos.")

    print()
    print("CONCLUSIÓN: El razonamiento bayesiano permite actualizar")
    print("creencias de manera sistemática ante nueva evidencia.")

if __name__ == "__main__":
    main()