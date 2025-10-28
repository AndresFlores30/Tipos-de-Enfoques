"""
DISTRIBUCIÓN DE PROBABILIDAD DISCRETA - SISTEMA ENERGÉTICO TRON

Este código introduce los conceptos fundamentales de las distribuciones de probabilidad
discretas usando como ejemplo el sistema energético del mundo TRON.

Conceptos cubiertos:
- Distribución de probabilidad discreta
- Normalización (suma de probabilidades = 1)
- Valor esperado (media ponderada)
- Interpretación de variables aleatorias

En el contexto TRON: Modelamos la incertidumbre sobre el estado del sistema de poder.
"""

from typing import Dict

# -------------------------------------------------------
# DISTRIBUCIÓN DE PROBABILIDAD DEL SISTEMA ENERGÉTICO TRON
# -------------------------------------------------------
# Variable aleatoria: Power (Estado del sistema de poder)
# Espacio muestral: {"Good", "Bad"} - Estados posibles del sistema
# Función de masa de probabilidad: Asigna probabilidades a cada estado

P_Power: Dict[str, float] = {
    "Good": 0.8,  # 80% de probabilidad - Sistema estable y confiable
    "Bad": 0.2    # 20% de probabilidad - Sistema inestable o defectuoso
}

# -------------------------------------------------------
# FUNCIONES PARA ANÁLISIS DE DISTRIBUCIONES DE PROBABILIDAD
# -------------------------------------------------------

def verificar_normalizacion(distribucion: Dict[str, float]) -> bool:
    """
    Verifica si una distribución de probabilidad está normalizada.
    
    Propiedad fundamental: La suma de todas las probabilidades debe ser 1.
    Esto asegura que la distribución cubre todos los posibles resultados.
    
    Args:
        distribucion: Diccionario {estado: probabilidad}
    
    Returns:
        bool: True si la suma es aproximadamente 1.0
    
    Ejemplo:
        >>> verificar_normalizacion({"A": 0.6, "B": 0.4})
        True
    """
    total = sum(distribucion.values())
    # Usamos tolerancia numérica para comparaciones de punto flotante
    return abs(total - 1.0) < 1e-6

def valor_esperado(distribucion: Dict[str, float], valores: Dict[str, float]) -> float:
    """
    Calcula el valor esperado (esperanza matemática) de una variable aleatoria.
    
    Fórmula: E[X] = Σ x_i × P(x_i)
    Representa el promedio ponderado de los valores posibles.
    
    Args:
        distribucion: Probabilidades P(x_i)
        valores: Valores numéricos x_i asociados a cada estado
    
    Returns:
        float: Valor esperado de la variable aleatoria
    
    Ejemplo:
        >>> valor_esperado({"A": 0.6, "B": 0.4}, {"A": 100, "B": 20})
        68.0
    """
    return sum(distribucion[estado] * valores[estado] for estado in distribucion)

def varianza(distribucion: Dict[str, float], valores: Dict[str, float]) -> float:
    """
    Calcula la varianza de una distribución discreta.
    
    La varianza mide la dispersión de los valores alrededor de la media.
    Fórmula: Var(X) = E[X²] - (E[X])²
    
    Args:
        distribucion: Probabilidades P(x_i)
        valores: Valores numéricos x_i
    
    Returns:
        float: Varianza de la distribución
    """
    esperanza = valor_esperado(distribucion, valores)
    # E[X²] = Σ x_i² × P(x_i)
    esperanza_cuadrados = sum(distribucion[estado] * (valores[estado] ** 2) 
                             for estado in distribucion)
    return esperanza_cuadrados - (esperanza ** 2)

def desviacion_estandar(distribucion: Dict[str, float], valores: Dict[str, float]) -> float:
    """
    Calcula la desviación estándar (raíz cuadrada de la varianza).
    
    Mide la dispersión en las mismas unidades que los datos originales.
    """
    return varianza(distribucion, valores) ** 0.5

# -------------------------------------------------------
# DEMOSTRACIÓN COMPLETA - ANÁLISIS DE LA DISTRIBUCIÓN
# -------------------------------------------------------

def main():
    """
    Ejecuta un análisis completo de la distribución de probabilidad del sistema TRON.
    """
    print("DISTRIBUCIÓN DE PROBABILIDAD - SISTEMA ENERGÉTICO TRON")
    print("=" * 65)
    print("Variable aleatoria: Power (Estado del sistema de poder)")
    print("Espacio muestral: {Good, Bad}")
    print()
    
    # Mostrar la distribución de probabilidad
    print("DISTRIBUCIÓN DE PROBABILIDAD P(Power):")
    print("-" * 40)
    for estado, prob in P_Power.items():
        print(f"  P(Power = {estado:4s}) = {prob:.2f} ({prob*100:.0f}%)")
    
    # Verificación de propiedades fundamentales
    print("\nPROPIEDADES DE LA DISTRIBUCIÓN:")
    print("-" * 40)
    
    # 1. Normalización
    if verificar_normalizacion(P_Power):
        print("✓ Normalización: La distribución es válida (suma = 1.00)")
    else:
        total = sum(P_Power.values())
        print(f"✗ Normalización: Problema - la suma es {total:.2f}")
    
    # 2. Probabilidades no negativas
    prob_negativas = any(p < 0 for p in P_Power.values())
    if not prob_negativas:
        print("✓ No negatividad: Todas las probabilidades son ≥ 0")
    else:
        print("✗ No negatividad: Hay probabilidades negativas")
    
    # Análisis del valor esperado
    print("\nANÁLISIS DEL VALOR ESPERADO:")
    print("-" * 40)
    
    # Definir valores numéricos para el nivel de energía
    # Good: 100 unidades (sistema operando óptimamente)
    # Bad:  20 unidades (sistema con fallas críticas)
    niveles_energia = {"Good": 100, "Bad": 20}
    
    print("Niveles de energía asociados a cada estado:")
    for estado, nivel in niveles_energia.items():
        print(f"  {estado}: {nivel:3d} unidades de energía")
    
    # Calcular valor esperado
    ve = valor_esperado(P_Power, niveles_energia)
    print(f"\nCálculo del valor esperado:")
    print("E[Energía] = Σ (Energía × Probabilidad)")
    for estado in P_Power:
        print(f"  + ({niveles_energia[estado]:3d} × {P_Power[estado]:.2f})", end="")
    print(f" = {ve:.1f} unidades")
    
    print(f"\nValor esperado de energía = {ve:.1f} unidades")
    
    # Análisis de dispersión
    print("\nANÁLISIS DE DISPERSIÓN:")
    print("-" * 40)
    
    var = varianza(P_Power, niveles_energia)
    desv_std = desviacion_estandar(P_Power, niveles_energia)
    
    print(f"Varianza:  {var:.1f} unidades²")
    print(f"Desviación estándar: {desv_std:.1f} unidades")
    
    # Interpretación cualitativa
    print("\nINTERPRETACIÓN PRÁCTICA:")
    print("-" * 40)
    print("* Con 80% de probabilidad, el sistema opera a 100 unidades (óptimo)")
    print("* Con 20% de probabilidad, el sistema cae a 20 unidades (crítico)")
    print(f"* En promedio, esperamos {ve:.1f} unidades de energía")
    print(f"* La dispersión ({desv_std:.1f} unidades) indica el riesgo de variación")
    
    print("\nIMPLICANCIAS PARA TRON:")
    print("-" * 40)
    if ve >= 80:
        print("* Sistema generalmente confiable - operación normal")
    elif ve >= 50:
        print("Sistema moderadamente confiable - monitoreo requerido")
    else:
        print("X Sistema de alto riesgo - protocolos de emergencia")
    
    print(f"\nRecomendación: {'Continuar operación normal' if ve >= 80 else 'Activar verificaciones adicionales'}")

def ejemplo_alternativo():
    """
    Muestra una distribución alternativa para comparación.
    """
    print("\n" + "="*65)
    print("EJEMPLO ALTERNATIVO - SISTEMA DEGRADADO")
    print("="*65)
    
    # Distribución con mayor incertidumbre
    P_Power_alternativo: Dict[str, float] = {
        "Good": 0.5,
        "Bad": 0.5
    }
    
    niveles_energia = {"Good": 100, "Bad": 20}
    ve_alt = valor_esperado(P_Power_alternativo, niveles_energia)
    
    print("Distribución alternativa (sistema degradado):")
    for estado, prob in P_Power_alternativo.items():
        print(f"  P({estado}) = {prob:.2f}")
    
    print(f"Valor esperado: {ve_alt:.1f} unidades")
    print("-> Mayor incertidumbre, menor confiabilidad promedio")

if __name__ == "__main__":
    main()
    ejemplo_alternativo()