# Regla de la Cadena (Chain Rule) — Ejemplo simple con temática TRON
#
# P(Power, Gate, Sensor, SafePath)
# = P(Power) * P(Gate|Power) * P(Sensor|Power) * P(SafePath|Gate)
#
# Este código ilustra cómo descomponer una probabilidad conjunta en factores condicionales.

from typing import Dict

# ----------------------------------
# Definición de las probabilidades
# ----------------------------------

P = {
    "Power": {"Good": 0.8, "Bad": 0.2},
    "Gate|Power": {
        ("Good",): {"Open": 0.9, "Closed": 0.1},
        ("Bad",):  {"Open": 0.3, "Closed": 0.7},
    },
    "Sensor|Power": {
        ("Good",): {"OK": 0.85, "Alert": 0.15},
        ("Bad",):  {"OK": 0.3, "Alert": 0.7},
    },
    "SafePath|Gate": {
        ("Open",):   {"Yes": 0.95, "No": 0.05},
        ("Closed",): {"Yes": 0.20, "No": 0.80},
    }
}

# ----------------------------------------------------
# Función para calcular una probabilidad conjunta
# usando la Regla de la Cadena
# ----------------------------------------------------
def joint_probability(power: str, gate: str, sensor: str, safepath: str) -> float:
    """
    Aplica la regla de la cadena:
    P(Power, Gate, Sensor, SafePath) =
        P(Power) * P(Gate|Power) * P(Sensor|Power) * P(SafePath|Gate)
    """
    p1 = P["Power"][power]
    p2 = P["Gate|Power"][(power,)][gate]
    p3 = P["Sensor|Power"][(power,)][sensor]
    p4 = P["SafePath|Gate"][(gate,)][safepath]
    return p1 * p2 * p3 * p4

# ----------------------------------------------------
# Ejemplo práctico: cálculo manual y comparación
# ----------------------------------------------------
def demo():
    print("Ejemplo de Regla de la Cadena en TRON")
    print("Queremos P(Power=Good, Gate=Open, Sensor=OK, SafePath=Yes)")
    
    p = joint_probability("Good", "Open", "OK", "Yes")
    print(f"Resultado: {p:.6f}")

    print("\nOtro ejemplo: P(Power=Bad, Gate=Closed, Sensor=Alert, SafePath=No)")
    p2 = joint_probability("Bad", "Closed", "Alert", "No")
    print(f"Resultado: {p2:.6f}")

    # Podemos comparar ambas
    ratio = p / (p2 + 1e-12)
    print(f"\nLa primera configuración es aproximadamente {ratio:.1f} veces más probable que la segunda.")

if __name__ == "__main__":
    demo()