"""
PROGRAMA: ANÁLISIS BÁSICO DE PROCESOS ESTACIONARIOS

Este programa simula y analiza un proceso estacionario simple (proceso de media móvil MA(1)).
Un proceso estacionario mantiene propiedades estadísticas constantes en el tiempo:
- Media constante
- Varianza constante
- Autocovarianza que depende solo del retraso, no del tiempo absoluto

El proceso MA(1) se define como:
X_t = μ + ε_t + θ*ε_{t-1}
Donde ε_t es ruido blanco (distribución normal)
"""

import numpy as np

# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================
np.random.seed(42)  # Para resultados reproducibles
print("=== ANÁLISIS DE PROCESO ESTACIONARIO MA(1) ===\n")

# Parámetros del proceso
MEDIA = 2.0        # Media del proceso (μ)
THETA = 0.6        # Parámetro MA(1) 
DESVIACION = 1.0   # Desviación estándar del ruido
N_PUNTOS = 100     # Número de puntos temporales

print(f"Parámetros del proceso:")
print(f"- Media (μ): {MEDIA}")
print(f"- Theta (θ): {THETA}")
print(f"- Desviación estándar: {DESVIACION}")
print(f"- Puntos temporales: {N_PUNTOS}")

# =============================================================================
# SIMULACIÓN DEL PROCESO MA(1)
# =============================================================================
def simular_proceso_ma1(n_puntos, media=MEDIA, theta=THETA, sigma=DESVIACION):
    """
    Simula un proceso de media móvil de orden 1 (MA(1))
    
    Args:
        n_puntos: Cantidad de puntos temporales
        media: Media del proceso
        theta: Parámetro MA(1)
        sigma: Desviación estándar del ruido
    
    Returns:
        list: Serie temporal del proceso MA(1)
    """
    # Generar ruido blanco (errores con distribución normal)
    ruido = np.random.normal(0, sigma, n_puntos + 1)
    
    # Inicializar lista para el proceso
    proceso = []
    
    # Calcular cada punto del proceso MA(1)
    for t in range(n_puntos):
        x_t = media + ruido[t + 1] + theta * ruido[t]
        proceso.append(x_t)
    
    return proceso

# Simular el proceso
proceso_simulado = simular_proceso_ma1(N_PUNTOS)
print(f"\n* Proceso MA(1) simulado con {len(proceso_simulado)} puntos")

# =============================================================================
# ANÁLISIS DE ESTACIONARIEDAD
# =============================================================================
def analizar_estacionariedad(serie_temporal):
    """
    Analiza si una serie temporal muestra propiedades de estacionariedad
    
    Args:
        serie_temporal: Lista con los valores del proceso
    
    Returns:
        dict: Diccionario con métricas de estacionariedad
    """
    # Convertir a array de numpy para cálculos
    serie = np.array(serie_temporal)
    
    # Dividir la serie en 4 segmentos para comparar
    segmento_len = len(serie) // 4
    segmentos = [
        serie[0:segmento_len],
        serie[segmento_len:2*segmento_len],
        serie[2*segmento_len:3*segmento_len],
        serie[3*segmento_len:4*segmento_len]
    ]
    
    # Calcular media y varianza para cada segmento
    medias_segmentos = [np.mean(seg) for seg in segmentos]
    varianzas_segmentos = [np.var(seg) for seg in segmentos]
    
    # Calcular estadísticas globales
    media_global = np.mean(serie)
    varianza_global = np.var(serie)
    
    # Calcular autocorrelación simple (lag 1)
    if len(serie) > 1:
        autocorr_lag1 = np.corrcoef(serie[:-1], serie[1:])[0, 1]
    else:
        autocorr_lag1 = 0
    
    return {
        'media_global': media_global,
        'varianza_global': varianza_global,
        'medias_segmentos': medias_segmentos,
        'varianzas_segmentos': varianzas_segmentos,
        'autocorrelacion_lag1': autocorr_lag1
    }

# Realizar análisis
analisis = analizar_estacionariedad(proceso_simulado)

# =============================================================================
# MOSTRAR RESULTADOS
# =============================================================================
print("\n=== RESULTADOS DEL ANÁLISIS ===")

# Mostrar estadísticas globales
print(f"\n1. ESTADÍSTICAS GLOBALES:")
print(f"   Media global: {analisis['media_global']:.4f}")
print(f"   Varianza global: {analisis['varianza_global']:.4f}")
print(f"   Autocorrelación (lag 1): {analisis['autocorrelacion_lag1']:.4f}")

# Mostrar comparación por segmentos
print(f"\n2. ANÁLISIS POR SEGMENTOS TEMPORALES:")
print("   Segmento |   Media   | Varianza")
print("   " + "-" * 35)

for i, (media, varianza) in enumerate(zip(analisis['medias_segmentos'], 
                                        analisis['varianzas_segmentos'])):
    print(f"   {i+1}        | {media:8.4f} | {varianza:8.4f}")

# Calcular variaciones en medias y varianzas
variacion_media = np.std(analisis['medias_segmentos'])
variacion_varianza = np.std(analisis['varianzas_segmentos'])

print(f"\n3. VARIACIÓN ENTRE SEGMENTOS:")
print(f"   Desviación estándar de las medias: {variacion_media:.4f}")
print(f"   Desviación estándar de las varianzas: {variacion_varianza:.4f}")

# =============================================================================
# VERIFICACIÓN DE ESTACIONARIEDAD
# =============================================================================
def verificar_estacionariedad(analisis, umbral=0.1):
    """
    Verifica si el proceso muestra características de estacionariedad
    
    Args:
        analisis: Diccionario con el análisis del proceso
        umbral: Umbral para considerar constante
    
    Returns:
        bool: True si es estacionario, False si no
    """
    medias = analisis['medias_segmentos']
    varianzas = analisis['varianzas_segmentos']
    
    # Calcular variaciones relativas
    variacion_rel_media = np.std(medias) / np.abs(np.mean(medias))
    variacion_rel_varianza = np.std(varianzas) / np.mean(varianzas)
    
    print(f"\n4. VERIFICACIÓN DE ESTACIONARIEDAD:")
    print(f"   Variación relativa de medias: {variacion_rel_media:.4f}")
    print(f"   Variación relativa de varianzas: {variacion_rel_varianza:.4f}")
    print(f"   Umbral utilizado: {umbral}")
    
    # Verificar criterios
    media_constante = variacion_rel_media < umbral
    varianza_constante = variacion_rel_varianza < umbral
    
    print(f"\n   ¿Media constante? {'SÍ' if media_constante else 'NO'}")
    print(f"   ¿Varianza constante? {'SÍ' if varianza_constante else 'NO'}")
    
    return media_constante and varianza_constante

# Realizar verificación
es_estacionario = verificar_estacionariedad(analisis)

# =============================================================================
# CONCLUSIÓN
# =============================================================================
print(f"\n5. CONCLUSIÓN:")
if es_estacionario:
    print("   * EL PROCESO MUESTRA CARACTERÍSTICAS DE ESTACIONARIEDAD")
    print("   - La media se mantiene aproximadamente constante")
    print("   - La varianza se mantiene aproximadamente constante")
else:
    print("   X EL PROCESO PODRÍA NO SER ESTACIONARIO")
    print("   - Se detectaron variaciones significativas en el tiempo")

# Mostrar valores teóricos esperados
print(f"\n6. VALORES TEÓRICOS ESPERADOS PARA MA(1):")
varianza_teorica = DESVIACION**2 * (1 + THETA**2)
print(f"   Media teórica: {MEDIA}")
print(f"   Varianza teórica: σ²(1 + θ²) = {varianza_teorica:.4f}")

# Comparar con valores observados
print(f"\n7. COMPARACIÓN CON VALORES OBSERVADOS:")
print(f"   Diferencia en media: {abs(analisis['media_global'] - MEDIA):.4f}")
print(f"   Diferencia en varianza: {abs(analisis['varianza_global'] - varianza_teorica):.4f}")

print(f"\n=== ANÁLISIS COMPLETADO ===")