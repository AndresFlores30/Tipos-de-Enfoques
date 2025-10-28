# Probabilidad Condicionada y Normalización — Ejemplo simple (TRON)
# Demuestra cómo usar el teorema de Bayes para calcular P(Power | Sensor)
# y cómo normalizar los resultados para que las probabilidades sumen 1.

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
# El sensor tiende a indicar "OK" cuando la energía es buena.
P_Sensor_given_Power: Dict[tuple, Dict[str, float]] = {
    ("Good",): {"OK": 0.9, "Alert": 0.1},
    ("Bad",):  {"OK": 0.3, "Alert": 0.7}
}

# -------------------------------------------------------
# Cálculo de P(Power | Sensor=Alert)
# -------------------------------------------------------

def posterior_power_given_sensor(sensor: str) -> Dict[str, float]:
    """
    Usa la fórmula de Bayes:
    P(Power | Sensor) = α * P(Power) * P(Sensor | Power)
    donde α = 1 / P(Sensor) es el factor de normalización.
    """
    unnormalized = {}
    for power in P_Power:
        prior = P_Power[power]
        likelihood = P_Sensor_given_Power[(power,)][sensor]
        unnormalized[power] = prior * likelihood

    # Normalización
    total = sum(unnormalized.values())
    normalized = {k: v / total for k, v in unnormalized.items()}
    return normalized

# -------------------------------------------------------
# Ejemplo demostrativo
# -------------------------------------------------------

def demo():
    print("Probabilidad Condicionada y Normalización en TRON")
    print("-------------------------------------------------")
    print("Queremos saber: ¿Cuál es la probabilidad de que el sistema esté 'Good' o 'Bad'")
    print("dado que el sensor envió una alerta (Sensor=Alert)?\n")

    posterior = posterior_power_given_sensor("Alert")
    for estado, prob in posterior.items():
        print(f"P(Power={estado} | Sensor=Alert) = {prob:.3f}")

    print("\nInterpretación:")
    print("Aunque inicialmente creíamos que el sistema estaba estable (Good=0.8),")
    print("la evidencia del sensor cambia esa creencia.")
    print("El factor de normalización asegura que las nuevas probabilidades sumen 1.")

    print(f"\nVerificación de normalización: {sum(posterior.values()):.2f}")

if __name__ == "__main__":
    demo()