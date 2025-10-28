# Probabilidad e Incertidumbre — Ejemplo simple con temática TRON
# Muestra cómo la incertidumbre disminuye al incorporar evidencia.

from typing import Dict

# -----------------------------------------------------
# Conjunto base de probabilidades (Red Bayesiana parcial)
# -----------------------------------------------------

# P(Power)
P_Power = {"Good": 0.8, "Bad": 0.2}

# P(Gate | Power)
P_Gate_given_Power = {
    ("Good",): {"Open": 0.9, "Closed": 0.1},
    ("Bad",):  {"Open": 0.3, "Closed": 0.7},
}

# P(Sensor | Power)
P_Sensor_given_Power = {
    ("Good",): {"OK": 0.85, "Alert": 0.15},
    ("Bad",):  {"OK": 0.3, "Alert": 0.7},
}

# P(SafePath | Gate)
P_SafePath_given_Gate = {
    ("Open",):   {"Yes": 0.95, "No": 0.05},
    ("Closed",): {"Yes": 0.2,  "No": 0.8},
}

# -----------------------------------------------------
# Inferencia manual básica
# -----------------------------------------------------

def prior_probability_safe_path() -> float:
    """
    Calcula P(SafePath=Yes) sin evidencia.
    Se basa en la incertidumbre de Power y Gate.
    """
    total = 0.0
    for power, p_power in P_Power.items():
        for gate, p_gate in P_Gate_given_Power[(power,)].items():
            p_safe = P_SafePath_given_Gate[(gate,)]['Yes']
            total += p_power * p_gate * p_safe
    return total

def posterior_given_alert() -> float:
    """
    Calcula P(SafePath=Yes | Sensor=Alert) aplicando el teorema de Bayes.
    La evidencia (Sensor=Alert) reduce la incertidumbre sobre Power.
    """
    # 1. Obtener P(Power | Sensor=Alert) con Bayes
    # P(Power) * P(Sensor=Alert | Power)
    unnormalized = {}
    for power in P_Power:
        unnormalized[power] = P_Power[power] * P_Sensor_given_Power[(power,)]['Alert']
    norm = sum(unnormalized.values())
    P_Power_given_Alert = {k: v / norm for k, v in unnormalized.items()}

    # 2. Propagar incertidumbre restante a SafePath
    total = 0.0
    for power, p_power in P_Power_given_Alert.items():
        for gate, p_gate in P_Gate_given_Power[(power,)].items():
            p_safe = P_SafePath_given_Gate[(gate,)]['Yes']
            total += p_power * p_gate * p_safe
    return total

# -----------------------------------------------------
# Ejemplo demostrativo
# -----------------------------------------------------

def demo():
    print("Incertidumbre en TRON: predicción del camino seguro (SafePath)")
    print("--------------------------------------------------------------")

    p_prior = prior_probability_safe_path()
    print(f"1) P(SafePath=Yes) sin evidencia: {p_prior:.4f}")

    p_posterior = posterior_given_alert()
    print(f"2) P(SafePath=Yes | Sensor=Alert): {p_posterior:.4f}")

    cambio = (p_posterior - p_prior) / p_prior * 100
    print(f"\nCambio relativo en la creencia: {cambio:+.2f}%")
    print("La evidencia 'Sensor=Alert' aumenta la incertidumbre y reduce la confianza en el camino seguro.")

if __name__ == "__main__":
    demo()