"""
TEOREMA DE BAYES Y NORMALIZACIÓN EN ENTORNO TRON - ACTUALIZACIÓN DE CREENCIAS

Este código demuestra la aplicación práctica del teorema de Bayes para 
actualizar probabilidades condicionadas cuando se obtiene nueva evidencia.

Conceptos fundamentales:
- Probabilidad previa (prior): Creencia inicial antes de la evidencia
- Verosimilitud (likelihood): Cómo se relaciona la evidencia con las hipótesis
- Probabilidad posterior: Creencia actualizada después de la evidencia
- Normalización: Asegurar que las probabilidades sumen 1

Escenario: Determinar el estado del sistema de poder en TRON basándose
en lecturas del sensor.
"""

from typing import Dict

# -------------------------------------------------------
# PROBABILIDADES BASE - CONOCIMIENTO PREVIO DEL SISTEMA
# -------------------------------------------------------

# P(Power) - PROBABILIDADES PREVIAS
# Representa nuestro conocimiento inicial sobre el estado del sistema
P_Power: Dict[str, float] = {
    "Good": 0.8,  # 80% de probabilidad de que el sistema esté en buen estado
    "Bad": 0.2    # 20% de probabilidad de que el sistema esté en mal estado
}

# P(Sensor | Power) - VEROSIMILITUDES
# Describe cómo se comporta el sensor bajo diferentes estados del sistema
P_Sensor_given_Power: Dict[tuple, Dict[str, float]] = {
    ("Good",): {"OK": 0.9, "Alert": 0.1},  # Con buen poder: 90% OK, 10% Alertas
    ("Bad",):  {"OK": 0.3, "Alert": 0.7}   # Con mal poder: 30% OK, 70% Alertas
}

# -------------------------------------------------------
# INFERENCIA BAYESIANA - TEOREMA DE BAYES APLICADO
# -------------------------------------------------------

def posterior_power_given_sensor(sensor: str) -> Dict[str, float]:
    """
    Calcula P(Power | Sensor) usando el teorema de Bayes.
    
    Fórmula: P(Power | Sensor) = α × P(Power) × P(Sensor | Power)
    donde α = 1 / P(Sensor) es el factor de normalización.
    
    Args:
        sensor: Evidencia observada ("OK" o "Alert")
    
    Returns:
        Dict[str, float]: Probabilidades posteriores normalizadas para cada estado de Power
    
    Proceso:
    1. Calcular probabilidades no normalizadas (prior × likelihood)
    2. Calcular factor de normalización (suma de todas las probabilidades no normalizadas)
    3. Normalizar dividiendo cada probabilidad por la suma total
    """
    # PASO 1: Calcular probabilidades no normalizadas
    # P_no_normalizada(Power) = P(Power) × P(Sensor | Power)
    unnormalized = {}
    for power in P_Power:
        prior = P_Power[power]                    # P(Power) - probabilidad previa
        likelihood = P_Sensor_given_Power[(power,)][sensor]  # P(Sensor | Power) - verosimilitud
        unnormalized[power] = prior * likelihood  # Producto no normalizado
    
    print("CÁLCULOS INTERMEDIOS:")
    print("-" * 40)
    for power, valor in unnormalized.items():
        prior = P_Power[power]
        likelihood = P_Sensor_given_Power[(power,)][sensor]
        print(f"P({power}) × P(Sensor={sensor} | {power}) = {prior:.2f} × {likelihood:.2f} = {valor:.3f}")
    
    # PASO 2: Calcular factor de normalización (P(Sensor))
    # P(Sensor) = Σ_{Power} P(Power) × P(Sensor | Power)
    total = sum(unnormalized.values())
    print(f"\nFactor de normalización α = 1 / P(Sensor={sensor})")
    print(f"P(Sensor={sensor}) = {total:.3f}")
    print(f"α = 1 / {total:.3f} = {1/total:.3f}")
    
    # PASO 3: Normalizar las probabilidades
    # P(Power | Sensor) = [P(Power) × P(Sensor | Power)] / P(Sensor)
    normalized = {k: v / total for k, v in unnormalized.items()}
    
    return normalized

# -------------------------------------------------------
# DEMOSTRACIÓN DETALLADA
# -------------------------------------------------------

def main():
    """
    Ejecuta una demostración completa del teorema de Bayes aplicado al escenario TRON.
    """
    print("TEOREMA DE BAYES EN TRON: ACTUALIZACIÓN DE CREENCIAS")
    print("=" * 65)
    print("Problema: Determinar el estado del sistema de poder dado una lectura del sensor")
    print()
    
    # Mostrar probabilidades iniciales
    print("CONOCIMIENTO INICIAL DEL SISTEMA:")
    print("-" * 40)
    print("PROBABILIDADES PREVIAS P(Power):")
    for power, prob in P_Power.items():
        print(f"  P({power}) = {prob:.2f}")
    
    print("\nVEROSIMILITUDES P(Sensor | Power):")
    for power, distribucion in P_Sensor_given_Power.items():
        print(f"  P(Sensor | Power={power[0]}):")
        for sensor, prob in distribucion.items():
            print(f"    P(Sensor={sensor} | {power[0]}) = {prob:.2f}")
    
    # Evidencia observada
    evidencia = "Alert"
    print(f"\nEVIDENCIA OBSERVADA: Sensor = {evidencia}")
    print("=" * 50)
    
    # Calcular probabilidades posteriores
    posterior = posterior_power_given_sensor(evidencia)
    
    print(f"\nRESULTADOS - PROBABILIDADES POSTERIORES:")
    print("-" * 40)
    for estado, prob in posterior.items():
        print(f"P(Power={estado} | Sensor={evidencia}) = {prob:.3f}")
    
    # Verificación de normalización
    print(f"\nVERIFICACIÓN: Suma de probabilidades = {sum(posterior.values()):.2f}")
    
    # Análisis e interpretación
    print("\nANÁLISIS E INTERPRETACIÓN:")
    print("-" * 40)
    cambio_good = posterior["Good"] - P_Power["Good"]
    cambio_bad = posterior["Bad"] - P_Power["Bad"]
    
    print(f"Estado 'Good': {P_Power['Good']:.2f} → {posterior['Good']:.2f} " +
          f"(cambio: {cambio_good:+.2f})")
    print(f"Estado 'Bad':  {P_Power['Bad']:.2f} → {posterior['Bad']:.2f} " +
          f"(cambio: {cambio_bad:+.2f})")
    
    print(f"\nINTERPRETACIÓN:")
    print(f"• La alerta del sensor hace que sea MÁS probable que el poder esté 'Bad'")
    print(f"• Nuestra confianza en 'Good' disminuye de {P_Power['Good']:.0f}% a {posterior['Good']*100:.0f}%")
    print(f"• La evidencia redujo significativamente nuestra incertidumbre")
    
    print(f"\nIMPLICANCIAS PARA TRON:")
    print(f"• Con {posterior['Bad']*100:.1f}% de probabilidad de mal funcionamiento,")
    print(f"  deberíamos activar protocolos de seguridad y buscar rutas alternativas.")

def demostracion_extra():
    """
    Demostración adicional mostrando el contraste con evidencia diferente.
    """
    print("\n" + "="*65)
    print("COMPARACIÓN CON DIFERENTE EVIDENCIA")
    print("="*65)
    
    # Calcular para Sensor="OK" también
    posterior_ok = posterior_power_given_sensor("OK")
    
    print(f"\nCOMPARACIÓN P(Power | Sensor):")
    print("-" * 50)
    print(f"{'Estado':<10} {'P(Power)':<10} {'P(|OK)':<10} {'P(|Alert)':<10}")
    print("-" * 50)
    for power in P_Power:
        print(f"{power:<10} {P_Power[power]:<10.3f} {posterior_ok[power]:<10.3f} {posterior_power_given_sensor('Alert')[power]:<10.3f}")
    
    print(f"\nCONCLUSIÓN GENERAL:")
    print("• Sensor='OK' refuerza la creencia en 'Good'")
    print("• Sensor='Alert' refuerza la creencia en 'Bad'")
    print("• La normalización asegura coherencia probabilística")

if __name__ == "__main__":
    main()
    demostracion_extra()