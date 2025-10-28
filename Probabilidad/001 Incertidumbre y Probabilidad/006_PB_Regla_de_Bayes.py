# Regla de Bayes — Ejemplo simple con temática TRON
#
# Calcula la probabilidad posterior P(Power | Sensor=Alert)
# usando la Regla de Bayes paso a paso.

from typing import Dict

# -------------------------------------------------------
# Probabilidades base
# -------------------------------------------------------

# P(Power)
P_Power: Dict[str, float] = {
    "Good": 0.8,
    "Bad": 0.2
}

# P(Sensor | Power)
P_Sensor_given_Power: Dict[tuple, Dict[str, float]] = {
    ("Good",): {"OK": 0.9, "Alert": 0.1},
    ("Bad",):  {"OK": 0.3, "Alert": 0.7}
}

# -------------------------------------------------------
# Regla de Bayes: cálculo paso a paso
# -------------------------------------------------------

def bayes_rule(sensor_value: str) -> Dict[str, float]:
    """
    Aplica la Regla de Bayes:
    P(Power | Sensor=s) = [ P(Sensor=s | Power) * P(Power) ] / P(Sensor=s)
    """
    # Numerador sin normalizar
    unnormalized = {}
    for power in P_Power:
        prior = P_Power[power]
        likelihood = P_Sensor_given_Power[(power,)][sensor_value]
        unnormalized[power] = prior * likelihood

    # Denominador: P(Sensor=s) = suma de numeradores
    evidence = sum(unnormalized.values())

    # Normalización
    posterior = {k: v / evidence for k, v in unnormalized.items()}
    return posterior, evidence

# -------------------------------------------------------
# Ejemplo demostrativo
# -------------------------------------------------------

def demo():
    print("Regla de Bayes en TRON")
    print("----------------------")
    print("Queremos calcular la probabilidad de que el sistema tenga energía buena o mala")
    print("dado que el sensor ha enviado una alerta (Sensor=Alert).\n")

    posterior, evidence = bayes_rule("Alert")

    for estado, prob in posterior.items():
        print(f"P(Power={estado} | Sensor=Alert) = {prob:.3f}")

    print(f"\nProbabilidad total de observar una alerta: P(Sensor=Alert) = {evidence:.3f}")

    print("\nInterpretación:")
    print("Inicialmente (a priori), se creía que el sistema estaba en buen estado con 0.8 de probabilidad.")
    print("Pero al observar una alerta, esa creencia cambia:")
    print("Ahora la probabilidad de que el sistema esté en mal estado aumenta significativamente.")

if __name__ == "__main__":
    demo()