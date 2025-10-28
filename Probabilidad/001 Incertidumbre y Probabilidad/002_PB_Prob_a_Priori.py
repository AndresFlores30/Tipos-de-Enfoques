# La probabilidad a priori representa nuestro conocimiento inicial
# sobre el estado del sistema antes de observar evidencia.

from typing import Dict

# -------------------------------------------------------
# Probabilidades a priori del estado del sistema TRON
# -------------------------------------------------------
# Supongamos que el sistema puede estar en dos estados de energía:
# - Good: energía estable
# - Bad: energía inestable

P_Power: Dict[str, float] = {
    "Good": 0.8,  # 80% de confianza inicial en energía estable
    "Bad":  0.2   # 20% de confianza inicial en energía inestable
}

# -------------------------------------------------------
# Cálculo y demostración de uso
# -------------------------------------------------------

def demo():
    print("Probabilidad a Priori en TRON")
    print("-----------------------------")
    print("Estados posibles del sistema de energía:")
    for estado, prob in P_Power.items():
        print(f"  P(Power={estado}) = {prob:.2f}")

    print("\nInterpretación:")
    print("Antes de recibir señales del sensor, se asume que el sistema TRON")
    print("tiene una probabilidad del 80% de estar estable (Good) y 20% de estar inestable (Bad).")
    print("Esta es la creencia a priori: se basa en conocimiento previo o experiencia histórica.")

    # Ejemplo: si queremos saber la probabilidad de que el sistema esté estable o inestable
    p_total = sum(P_Power.values())
    print(f"\nVerificación de normalización: P(Good)+P(Bad) = {p_total:.2f}")

    # Ejemplo de uso: predicción antes de evidencia
    print("\nPredicción sin evidencia:")
    if P_Power["Good"] > P_Power["Bad"]:
        print("  -> Se predice que el sistema TRON probablemente esté en estado 'Good' (energía estable).")
    else:
        print("  -> Se predice que el sistema TRON probablemente esté en estado 'Bad' (energía inestable).")

if __name__ == "__main__":
    demo()