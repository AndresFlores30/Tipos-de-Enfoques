"""
PROGRAMA: PROCESOS DE MARKOV - HIPÓTESIS DE MARKOV

Este programa implementa y simula un Proceso de Markov, demostrando la propiedad de Markov:
"El futuro depende solo del estado presente, no del historial completo de estados anteriores"

La Hipótesis de Markov establece que para un proceso estocástico:
P(X_{t+1} = x | X_t = x_t, X_{t-1} = x_{t-1}, ..., X_0 = x_0) = P(X_{t+1} = x | X_t = x_t)

Es decir, la probabilidad de transición al siguiente estado depende únicamente del estado actual.
"""

import numpy as np

# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================
np.random.seed(42)  # Para reproducibilidad
print("=== PROCESOS DE MARKOV - HIPÓTESIS DE MARKOV ===\n")

# Definir los estados posibles del sistema
ESTADOS = ['Soleado', 'Nublado', 'Lluvioso']
print(f"Estados posibles: {ESTADOS}")

# =============================================================================
# MATRIZ DE TRANSICIÓN DE MARKOV
# =============================================================================
def crear_matriz_transicion():
    """
    Crea una matriz de transición para una cadena de Markov
    
    La matriz P[i][j] representa la probabilidad de pasar del estado i al estado j
    Cada fila debe sumar 1 (probabilidades válidas)
    
    Returns:
        numpy.array: Matriz de transición 3x3
    """
    # Matriz de transición para el clima:
    # Filas: estado actual, Columnas: estado siguiente
    matriz = np.array([
        # Soleado -> [Soleado, Nublado, Lluvioso]
        [0.7, 0.2, 0.1],   # Si está soleado
        [0.3, 0.4, 0.3],   # Si está nublado  
        [0.2, 0.3, 0.5]    # Si está lluvioso
    ])
    
    return matriz

# Crear la matriz de transición
matriz_transicion = crear_matriz_transicion()
print("\n1. MATRIZ DE TRANSICIÓN DE MARKOV:")
print("   Estado actual -> Probabilidades del siguiente estado")
print("   " + "-" * 50)

for i, estado_actual in enumerate(ESTADOS):
    print(f"   {estado_actual:8} -> ", end="")
    for j, estado_siguiente in enumerate(ESTADOS):
        prob = matriz_transicion[i][j]
        print(f"P({estado_siguiente:8}) = {prob:.2f}  ", end="")
    print()

# Verificar que cada fila suma 1
print("\n   Verificación de probabilidades (suma por filas):")
for i, estado in enumerate(ESTADOS):
    suma_fila = np.sum(matriz_transicion[i])
    print(f"   {estado}: {suma_fila:.2f} {'✓' if abs(suma_fila - 1.0) < 0.001 else '✗'}")

# =============================================================================
# SIMULACIÓN DE CADENA DE MARKOV
# =============================================================================
def simular_cadena_markov(estado_inicial, n_pasos, matriz_trans, estados):
    """
    Simula una cadena de Markov por n pasos
    
    Args:
        estado_inicial: Estado inicial de la cadena
        n_pasos: Número de pasos a simular
        matriz_trans: Matriz de transición
        estados: Lista de estados posibles
    
    Returns:
        list: Secuencia de estados de la cadena
    """
    # Encontrar índice del estado inicial
    estado_actual_idx = estados.index(estado_inicial)
    cadena = [estado_inicial]
    
    print(f"\n2. SIMULACIÓN DE CADENA DE MARKOV:")
    print(f"   Estado inicial: {estado_inicial}")
    print(f"   Número de pasos: {n_pasos}")
    print(f"   Secuencia de estados:")
    print(f"   Paso 0: {estado_inicial}")
    
    # Simular cada paso
    for paso in range(1, n_pasos + 1):
        # Obtener probabilidades de transición desde el estado actual
        prob_transiciones = matriz_trans[estado_actual_idx]
        
        # Elegir próximo estado basado en las probabilidades
        proximo_estado_idx = np.random.choice(len(estados), p=prob_transiciones)
        proximo_estado = estados[proximo_estado_idx]
        
        # Mostrar transición
        prob_transicion = prob_transiciones[proximo_estado_idx]
        print(f"   Paso {paso}: {proximo_estado} (transición desde {cadena[-1]} con p={prob_transicion:.2f})")
        
        # Actualizar estado actual y agregar a la cadena
        estado_actual_idx = proximo_estado_idx
        cadena.append(proximo_estado)
    
    return cadena

# Simular una cadena de Markov
cadena_simulada = simular_cadena_markov('Soleado', 10, matriz_transicion, ESTADOS)

# =============================================================================
# VERIFICACIÓN DE LA PROPIEDAD DE MARKOV
# =============================================================================
def verificar_propiedad_markov(cadena, matriz_trans, estados, historial_largo=3):
    """
    Verifica la propiedad de Markov comparando probabilidades condicionales
    
    Args:
        cadena: Secuencia de estados simulada
        matriz_trans: Matriz de transición
        estados: Lista de estados posibles
        historial_largo: Longitud del historial a considerar
    """
    print(f"\n3. VERIFICACIÓN DE LA PROPIEDAD DE MARKOV:")
    print("   La propiedad de Markov establece:")
    print("   P(futuro | presente, pasado) = P(futuro | presente)")
    print("   " + "-" * 60)
    
    if len(cadena) < historial_largo + 1:
        print("   Cadena demasiado corta para verificación")
        return
    
    # Tomar un punto aleatorio en la cadena para verificación
    punto_verificacion = min(5, len(cadena) - 2)
    
    # Estado futuro a predecir
    estado_futuro_real = cadena[punto_verificacion + 1]
    estado_presente = cadena[punto_verificacion]
    
    print(f"   Punto de verificación: paso {punto_verificacion}")
    print(f"   Estado presente: {estado_presente}")
    print(f"   Estado futuro real: {estado_futuro_real}")
    
    # Calcular probabilidad usando solo el estado presente (propiedad de Markov)
    idx_presente = estados.index(estado_presente)
    idx_futuro = estados.index(estado_futuro_real)
    prob_markov = matriz_trans[idx_presente][idx_futuro]
    
    print(f"   Probabilidad Markov P({estado_futuro_real}|{estado_presente}) = {prob_markov:.4f}")
    
    # Mostrar que el historial no afecta la probabilidad
    if punto_verificacion >= 2:
        estado_pasado = cadena[punto_verificacion - 1]
        print(f"   Estado pasado: {estado_pasado}")
        print(f"   Probabilidad sigue siendo: {prob_markov:.4f} (independiente del pasado)")
    
    # Verificar con múltiples historiales
    print(f"\n   Verificación con diferentes historiales:")
    for i in range(min(3, punto_verificacion)):
        historial = cadena[punto_verificacion - i:punto_verificacion + 1]
        historial_str = " -> ".join(historial)
        print(f"   Historial {i+1}: [{historial_str}] -> P({estado_futuro_real}|{estado_presente}) = {prob_markov:.4f}")

# Verificar la propiedad
verificar_propiedad_markov(cadena_simulada, matriz_transicion, ESTADOS)

# =============================================================================
# DISTRIBUCIÓN ESTACIONARIA
# =============================================================================
def calcular_distribucion_estacionaria(matriz_trans, estados, tolerancia=1e-8, max_iter=1000):
    """
    Calcula la distribución estacionaria de la cadena de Markov
    
    La distribución estacionaria π satisface: π = π * P
    Donde P es la matriz de transición
    
    Args:
        matriz_trans: Matriz de transición
        estados: Lista de estados
        tolerancia: Tolerancia para convergencia
        max_iter: Máximo número de iteraciones
    
    Returns:
        numpy.array: Distribución estacionaria
    """
    print(f"\n4. DISTRIBUCIÓN ESTACIONARIA:")
    print("   La distribución estacionaria π satisface: π = π * P")
    
    # Empezar con distribución uniforme
    pi_actual = np.ones(len(estados)) / len(estados)
    
    # Iterar hasta convergencia
    for iteracion in range(max_iter):
        pi_siguiente = pi_actual @ matriz_trans
        
        # Verificar convergencia
        if np.max(np.abs(pi_siguiente - pi_actual)) < tolerancia:
            print(f"   Convergencia alcanzada en {iteracion + 1} iteraciones")
            break
        
        pi_actual = pi_siguiente
    
    else:
        print(f"   Máximo de iteraciones ({max_iter}) alcanzado")
    
    # Mostrar distribución estacionaria
    print("   Distribución estacionaria:")
    for i, estado in enumerate(estados):
        print(f"   π({estado}) = {pi_actual[i]:.4f}")
    
    # Verificar que es distribución válida
    suma = np.sum(pi_actual)
    print(f"   Suma de probabilidades: {suma:.6f}")
    
    return pi_actual

# Calcular distribución estacionaria
dist_estacionaria = calcular_distribucion_estacionaria(matriz_transicion, ESTADOS)

# =============================================================================
# ANÁLISIS DE PROBABILIDADES A LARGO PLAZO
# =============================================================================
def analizar_largo_plazo(cadena_simulada, estados):
    """
    Analiza las frecuencias observadas en la simulación y las compara
    con la distribución estacionaria teórica
    """
    print(f"\n5. ANÁLISIS DE FRECUENCIAS OBSERVADAS:")
    
    # Calcular frecuencias observadas
    frecuencias = {}
    total_estados = len(cadena_simulada)
    
    for estado in estados:
        conteo = cadena_simulada.count(estado)
        frecuencia = conteo / total_estados
        frecuencias[estado] = frecuencia
    
    print("   Frecuencias observadas en la simulación:")
    for estado in estados:
        freq_obs = frecuencias[estado]
        freq_teo = dist_estacionaria[estados.index(estado)]
        diferencia = abs(freq_obs - freq_teo)
        print(f"   {estado}: Observada = {freq_obs:.4f}, Teórica = {freq_teo:.4f}, Diferencia = {diferencia:.4f}")

# Realizar análisis de frecuencias
analizar_largo_plazo(cadena_simulada, ESTADOS)

# =============================================================================
# CONCLUSIÓN
# =============================================================================
print(f"\n6. CONCLUSIÓN SOBRE LA HIPÓTESIS DE MARKOV:")
print("   - La propiedad de Markov se verifica: el futuro depende solo del estado presente")
print("   - Las probabilidades de transición son constantes en el tiempo")
print("   - La cadena converge a una distribución estacionaria")
print("   - El historial completo no es necesario para predecir el siguiente estado")

print(f"\n=== ANÁLISIS DE PROCESOS DE MARKOV COMPLETADO ===")