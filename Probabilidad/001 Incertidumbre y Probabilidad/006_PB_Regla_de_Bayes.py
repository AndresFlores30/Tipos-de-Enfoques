"""
REGLA DE BAYES EN ENTORNO TRON - ACTUALIZACIÓN DE CREENCIAS CON EVIDENCIA

Este código implementa la Regla de Bayes para actualizar probabilidades 
cuando se obtiene nueva evidencia. Demuestra cómo incorporar observaciones
del sensor para refinar nuestra comprensión del estado del sistema.

Conceptos clave:
- Probabilidad previa (prior): Creencia inicial antes de la evidencia
- Verosimilitud (likelihood): Probabilidad de la evidencia dada cada hipótesis  
- Evidencia (evidence): Probabilidad total de observar los datos
- Probabilidad posterior: Creencia actualizada después de la evidencia

Fórmula de Bayes: P(H|E) = [P(E|H) x P(H)] / P(E)
"""

from typing import Dict, Tuple

# -------------------------------------------------------
# PROBABILIDADES BASE - CONOCIMIENTO PREVIO DEL SISTEMA
# -------------------------------------------------------

# P(Power) - PROBABILIDADES PREVIAS
# Representa nuestro conocimiento inicial sobre el estado del sistema de poder
P_Power: Dict[str, float] = {
    "Good": 0.8,  # 80% de probabilidad de que el sistema esté en buen estado
    "Bad": 0.2    # 20% de probabilidad de que el sistema esté en mal estado
}

# P(Sensor | Power) - VEROSIMILITUDES  
# Describe el comportamiento del sensor bajo diferentes estados del sistema
P_Sensor_given_Power: Dict[tuple, Dict[str, float]] = {
    ("Good",): {"OK": 0.9, "Alert": 0.1},  # Con buen poder: 90% OK, 10% Alertas
    ("Bad",):  {"OK": 0.3, "Alert": 0.7}   # Con mal poder: 30% OK, 70% Alertas
}

# -------------------------------------------------------
# IMPLEMENTACIÓN DE LA REGLA DE BAYES PASO A PASO
# -------------------------------------------------------

def bayes_rule(sensor_value: str) -> Tuple[Dict[str, float], float]:
    """
    Aplica la Regla de Bayes para calcular P(Power | Sensor=sensor_value).
    
    Fórmula: P(Power | Sensor) = [P(Sensor | Power) × P(Power)] / P(Sensor)
    
    Args:
        sensor_value: Valor observado del sensor ("OK" o "Alert")
    
    Returns:
        Tuple: (probabilidades_posteriores, probabilidad_evidencia)
    
    Pasos:
    1. Calcular numeradores no normalizados: P(Sensor|Power) × P(Power)
    2. Calcular denominador (evidencia): P(Sensor) = Σ numeradores
    3. Normalizar dividiendo cada numerador por la evidencia
    """
    print("PASO 1: Calcular numeradores no normalizados")
    print("=" * 50)
    
    # PASO 1: Calcular numeradores P(Sensor|Power) × P(Power) para cada estado
    unnormalized = {}
    for power in P_Power:
        prior = P_Power[power]                    # P(Power) - probabilidad previa
        likelihood = P_Sensor_given_Power[(power,)][sensor_value]  # P(Sensor|Power) - verosimilitud
        unnormalized[power] = prior * likelihood  # Producto: P(Sensor|Power) × P(Power)
        
        print(f"P(Sensor={sensor_value} | {power}) × P({power}) = {likelihood:.2f} × {prior:.2f} = {unnormalized[power]:.3f}")
    
    # PASO 2: Calcular probabilidad de la evidencia P(Sensor)
    print("\nPASO 2: Calcular probabilidad de la evidencia P(Sensor)")
    print("=" * 50)
    
    evidence = sum(unnormalized.values())  # P(Sensor) = Σ [P(Sensor|Power) × P(Power)]
    print(f"P(Sensor={sensor_value}) = Σ [P(Sensor|Power) × P(Power)]")
    print(f"P(Sensor={sensor_value}) = {sum(unnormalized.values()):.3f}")
    
    # PASO 3: Normalizar para obtener probabilidades posteriores
    print("\nPASO 3: Normalizar para obtener probabilidades posteriores")
    print("=" * 50)
    
    posterior = {}
    for power, numerador in unnormalized.items():
        posterior[power] = numerador / evidence  # P(Power|Sensor) = numerador / P(Sensor)
        print(f"P({power} | Sensor={sensor_value}) = {numerador:.3f} / {evidence:.3f} = {posterior[power]:.3f}")
    
    return posterior, evidence

# -------------------------------------------------------
# DEMOSTRACIÓN COMPLETA CON ANÁLISIS
# -------------------------------------------------------

def main():
    """
    Ejecuta una demostración completa de la Regla de Bayes aplicada al escenario TRON.
    """
    print("REGLA DE BAYES EN SISTEMA TRON - ACTUALIZACIÓN DE CREENCIAS")
    print("=" * 70)
    print("Problema: Determinar el estado real del sistema dado una alerta del sensor")
    print()
    
    # Mostrar el conocimiento inicial del sistema
    print("CONOCIMIENTO INICIAL (ANTES DE LA EVIDENCIA):")
    print("-" * 50)
    print("PROBABILIDADES PREVIAS P(Power):")
    for power, prob in P_Power.items():
        print(f"  P({power}) = {prob:.2f} ({prob*100:.0f}% de confianza inicial)")
    
    print("\nCOMPORTAMIENTO DEL SENSOR P(Sensor | Power):")
    for power, distribucion in P_Sensor_given_Power.items():
        print(f"  Cuando Power = {power[0]}:")
        for sensor, prob in distribucion.items():
            print(f"    P(Sensor={sensor} | {power[0]}) = {prob:.2f}")
    
    # Evidencia observada
    evidencia_observada = "Alert"
    print(f"\n{'='*70}")
    print(f"EVIDENCIA OBSERVADA: Sensor = {evidencia_observada}")
    print(f"{'='*70}")
    
    # Aplicar Regla de Bayes
    posterior, p_evidencia = bayes_rule(evidencia_observada)
    
    # Mostrar resultados
    print(f"\nRESULTADOS - PROBABILIDADES ACTUALIZADAS:")
    print("-" * 50)
    for estado, prob in posterior.items():
        print(f"P(Power={estado} | Sensor={evidencia_observada}) = {prob:.3f} ({prob*100:.1f}%)")
    
    print(f"\nProbabilidad de observar esta evidencia: P(Sensor={evidencia_observada}) = {p_evidencia:.3f}")
    
    # Análisis del impacto de la evidencia
    print(f"\nANÁLISIS DEL IMPACTO:")
    print("-" * 50)
    
    for estado in P_Power:
        cambio = posterior[estado] - P_Power[estado]
        direccion = "AUMENTÓ" if cambio > 0 else "DISMINUYÓ"
        print(f"Power={estado}: {P_Power[estado]:.3f} → {posterior[estado]:.3f} ({direccion} {abs(cambio):.3f})")
    
    # Interpretación cualitativa
    print(f"\nINTERPRETACIÓN EN CONTEXTO TRON:")
    print("-" * 50)
    print("* INICIALMENTE: Alta confianza (80%) en sistema estable")
    print("* TRAS ALERTA: La confianza en 'Good' cae a {:.1f}%".format(posterior["Good"]*100))
    print("* La evidencia del sensor cambió significativamente nuestra creencia")
    print("* La alerta hace mucho más probable que el sistema esté en mal estado")
    
    print(f"\nRECOMENDACIÓN DE ACCIÓN:")
    print("-" * 50)
    if posterior["Bad"] > 0.5:
        print(" ACTIVAR PROTOCOLOS DE EMERGENCIA - Alto riesgo de fallo del sistema")
        print("   - Buscar rutas alternativas inmediatamente")
        print("   - Preparar sistemas de respaldo")
    else:
        print(" MONITOREAR SITUACIÓN - Riesgo moderado")
        print("   - Continuar operación con precaución")
        print("   - Verificar otros sensores")

def demostracion_comparativa():
    """
    Muestra cómo diferentes evidencias producen diferentes actualizaciones.
    """
    print(f"\n{'='*70}")
    print("COMPARACIÓN CON DIFERENTES EVIDENCIAS")
    print(f"{'='*70}")
    
    # Probar con ambas posibles evidencias
    evidencias = ["OK", "Alert"]
    
    print(f"\n{'Evidencia':<10} {'P(Good|E)':<10} {'P(Bad|E)':<10} {'Cambio Good':<15} {'Interpretación':<20}")
    print("-" * 70)
    
    for evidencia in evidencias:
        posterior, _ = bayes_rule(evidencia)
        cambio_good = posterior["Good"] - P_Power["Good"]
        
        if cambio_good > 0:
            interpretacion = "Refuerza confianza"
        else:
            interpretacion = "Reduce confianza"
        
        print(f"{evidencia:<10} {posterior['Good']:<10.3f} {posterior['Bad']:<10.3f} {cambio_good:+.3f}         {interpretacion:<20}")

if __name__ == "__main__":
    main()
    demostracion_comparativa()