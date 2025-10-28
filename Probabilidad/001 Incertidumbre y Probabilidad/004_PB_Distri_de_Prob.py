# Distribución de Probabilidad — Ejemplo simple con temática TRON
# Este programa define y analiza una distribución discreta de probabilidad
# para el estado energético del sistema TRON.

from typing import Dict

# -------------------------------------------------------
# Definición de una distribución de probabilidad discreta
# -------------------------------------------------------
# Variable aleatoria: Power
# Valores posibles: Good (energía estable), Bad (energía inestable)

P_Power: Dict[str, float] = {
    "Good": 0.8,
    "Bad": 0.2
}

# -------------------------------------------------------
# Funciones de utilidad
# -------------------------------------------------------

def verificar_normalizacion(distribucion: Dict[str, float]) -> bool:
    """Verifica si las probabilidades suman aproximadamente 1."""
    total = sum(distribucion.values())
    return abs(total - 1.0) < 1e-6

def valor_esperado(distribucion: Dict[str, float], valores: Dict[str, float]) -> float:
    """Calcula el valor esperado (media ponderada)."""
    return sum(distribucion[estado] * valores[estado] for estado in distribucion)

# -------------------------------------------------------
# Ejemplo demostrativo
# -------------------------------------------------------

def demo():
    print("Distribución de Probabilidad — Sistema TRON")
    print("-------------------------------------------")
    print("Variable aleatoria: Power (estado energético del sistema)\n")

    for estado, prob in P_Power.items():
        print(f"P(Power={estado}) = {prob:.2f}")

    # Comprobación de normalización
    if verificar_normalizacion(P_Power):
        print("\nVerificación: La distribución está normalizada (suma ≈ 1).")
    else:
        print("\nAdvertencia: La distribución NO está normalizada.")

    # Asignamos valores numéricos simbólicos a los estados
    valores_numericos = {"Good": 100, "Bad": 20}
    ve = valor_esperado(P_Power, valores_numericos)
    print(f"\nValor esperado de energía = {ve:.2f} unidades.")

    print("\nInterpretación:")
    print("La variable Power tiene dos posibles estados con sus probabilidades.")
    print("El valor esperado representa la 'energía promedio' del sistema TRON\n"
          "teniendo en cuenta la incertidumbre sobre su estado.")

if __name__ == "__main__":
    demo()