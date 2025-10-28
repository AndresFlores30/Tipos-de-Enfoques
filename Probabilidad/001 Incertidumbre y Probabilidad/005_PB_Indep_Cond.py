# Independencia Condicional — Ejemplo simple con temática TRON
#
# Muestra cómo dos variables pueden ser independientes
# al conocer el estado de una tercera variable.

from typing import Dict

# -------------------------------------------------------
# Probabilidades base (ejemplo pequeño)
# -------------------------------------------------------
# Gate -> Sensor
# Gate -> SafePath
# Sensor y SafePath comparten la causa común "Gate".

P_Gate = {"Open": 0.6, "Closed": 0.4}

# P(Sensor | Gate)
P_Sensor_given_Gate = {
    ("Open",):   {"OK": 0.9, "Alert": 0.1},
    ("Closed",): {"OK": 0.4, "Alert": 0.6},
}

# P(SafePath | Gate)
P_SafePath_given_Gate = {
    ("Open",):   {"Yes": 0.95, "No": 0.05},
    ("Closed",): {"Yes": 0.2,  "No": 0.8},
}

# -------------------------------------------------------
# Funciones de cálculo
# -------------------------------------------------------

def joint(sensor: str, safepath: str) -> float:
    """
    Calcula P(Sensor, SafePath) marginalizando sobre Gate:
    P(Sensor, SafePath) = Σ_gate P(Gate) * P(Sensor|Gate) * P(SafePath|Gate)
    """
    total = 0.0
    for gate, p_gate in P_Gate.items():
        p_sensor = P_Sensor_given_Gate[(gate,)][sensor]
        p_safe = P_SafePath_given_Gate[(gate,)][safepath]
        total += p_gate * p_sensor * p_safe
    return total

def conditional(sensor: str, safepath: str, gate: str) -> float:
    """
    Calcula P(Sensor, SafePath | Gate)
    Si las variables son independientes dadas Gate, entonces:
    P(Sensor, SafePath | Gate) = P(Sensor|Gate) * P(SafePath|Gate)
    """
    p_sensor = P_Sensor_given_Gate[(gate,)][sensor]
    p_safe = P_SafePath_given_Gate[(gate,)][safepath]
    return p_sensor * p_safe

# -------------------------------------------------------
# Ejemplo demostrativo
# -------------------------------------------------------

def demo():
    print("Independencia Condicional en TRON")
    print("---------------------------------")

    # Dependencia general (sin condicionar)
    p_joint = joint("OK", "Yes")
    print(f"P(Sensor=OK, SafePath=Yes) = {p_joint:.4f}")

    # Condicional: dado Gate=Open
    p_cond = conditional("OK", "Yes", "Open")
    print(f"P(Sensor=OK, SafePath=Yes | Gate=Open) = {p_cond:.4f}")

    # Comprobamos independencia condicional
    print("\nInterpretación:")
    print("Sin conocer Gate, Sensor y SafePath están correlacionados, porque dependen de la misma causa (Gate).")
    print("Pero al conocer Gate, las variables se vuelven independientes:")
    print("  P(Sensor, SafePath | Gate) = P(Sensor|Gate) * P(SafePath|Gate)")

if __name__ == "__main__":
    demo()