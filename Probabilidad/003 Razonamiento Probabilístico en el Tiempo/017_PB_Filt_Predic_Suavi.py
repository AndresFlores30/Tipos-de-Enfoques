"""
PROGRAMA: FILTRADO, PREDICCIÓN, SUAVIZADO Y EXPLICACIÓN EN PROCESOS ESTOCÁSTICOS

Este programa implementa las cuatro operaciones fundamentales en el razonamiento probabilístico temporal:

1. FILTRADO: Estimar el estado actual dado observaciones hasta el momento actual
   P(X_t | e_{1:t})

2. PREDICCIÓN: Estimar estados futuros dado observaciones actuales
   P(X_{t+k} | e_{1:t})

3. SUAVIZADO: Estimar estados pasados dado todas las observaciones
   P(X_k | e_{1:t}) donde k < t

4. EXPLICACIÓN: Encontrar la secuencia más probable de estados dado las observaciones
   argmax_{x_{1:t}} P(X_{1:t} | e_{1:t})

Utilizamos un modelo oculto de Markov (HMM) simple para demostrar estos conceptos.
"""

import numpy as np

# =============================================================================
# CONFIGURACIÓN DEL MODELO OCULTO DE MARKOV
# =============================================================================
np.random.seed(42)
print("=== FILTRADO, PREDICCIÓN, SUAVIZADO Y EXPLICACIÓN EN HMM ===\n")

# Estados ocultos posibles (estado del tiempo real)
ESTADOS_OCULTOS = ['Soleado', 'Lluvioso']
print(f"Estados ocultos: {ESTADOS_OCULTOS}")

# Observaciones posibles (lo que podemos medir)
OBSERVACIONES = ['Paraguas', 'SinParaguas']
print(f"Observaciones: {OBSERVACIONES}")

# =============================================================================
# MATRICES DEL MODELO HMM
# =============================================================================
def crear_modelo_hmm():
    """
    Crea un modelo oculto de Markov con:
    - Matriz de transición: probabilidades entre estados ocultos
    - Matriz de observación: probabilidades de observaciones dado estados
    - Distribución inicial: probabilidad inicial de estados
    """
    # Matriz de transición A: P(X_t | X_{t-1})
    # Filas: estado actual, Columnas: estado siguiente
    matriz_transicion = np.array([
        [0.7, 0.3],  # Soleado -> [Soleado, Lluvioso]
        [0.4, 0.6]   # Lluvioso -> [Soleado, Lluvioso]
    ])
    
    # Matriz de observación B: P(E_t | X_t)
    # Filas: estado oculto, Columnas: observación
    matriz_observacion = np.array([
        [0.1, 0.9],  # Soleado -> [Paraguas, SinParaguas]
        [0.8, 0.2]   # Lluvioso -> [Paraguas, SinParaguas]
    ])
    
    # Distribución inicial: P(X_1)
    distribucion_inicial = np.array([0.5, 0.5])  # [Soleado, Lluvioso]
    
    return matriz_transicion, matriz_observacion, distribucion_inicial

# Crear el modelo HMM
A, B, pi = crear_modelo_hmm()

print("\n1. MODELO OCULTO DE MARKOV:")
print("   Matriz de transición P(X_t | X_{t-1}):")
for i, estado_actual in enumerate(ESTADOS_OCULTOS):
    print(f"   {estado_actual:8} -> ", end="")
    for j, estado_siguiente in enumerate(ESTADOS_OCULTOS):
        print(f"P({estado_siguiente:8}) = {A[i,j]:.2f}  ", end="")
    print()

print("\n   Matriz de observación P(E_t | X_t):")
for i, estado_oculto in enumerate(ESTADOS_OCULTOS):
    print(f"   {estado_oculto:8} -> ", end="")
    for j, observacion in enumerate(OBSERVACIONES):
        print(f"P({observacion:11}) = {B[i,j]:.2f}  ", end="")
    print()

print(f"\n   Distribución inicial: P(Soleado) = {pi[0]:.2f}, P(Lluvioso) = {pi[1]:.2f}")

# =============================================================================
# FILTRADO - ALGORITMO DE AVANCE (FORWARD)
# =============================================================================
def filtrado_forward(observaciones, A, B, pi):
    """
    Implementa el algoritmo de forward para filtrado
    Calcula P(X_t | e_{1:t}) para cada tiempo t
    
    Args:
        observaciones: Lista de observaciones [obs_1, obs_2, ..., obs_t]
        A: Matriz de transición
        B: Matriz de observación
        pi: Distribución inicial
    
    Returns:
        list: Lista de distribuciones de filtrado para cada tiempo
    """
    print(f"\n2. FILTRADO - Algoritmo de Forward:")
    print(f"   Observaciones: {observaciones}")
    print(f"   Calculando P(X_t | e_1:t) para t = 1 a {len(observaciones)}")
    
    T = len(observaciones)
    N = len(ESTADOS_OCULTOS)
    forward = []
    
    # Paso inicial: t = 1
    obs_idx = OBSERVACIONES.index(observaciones[0])
    f1 = pi * B[:, obs_idx]
    f1 = f1 / np.sum(f1)  # Normalizar
    forward.append(f1)
    
    print(f"\n   t=1: P(X1 | e1)")
    for i, estado in enumerate(ESTADOS_OCULTOS):
        print(f"   P(X1={estado} | e1={observaciones[0]}) = {f1[i]:.4f}")
    
    # Pasos siguientes: t = 2 a T
    for t in range(1, T):
        obs_idx = OBSERVACIONES.index(observaciones[t])
        ft = np.zeros(N)
        
        for j in range(N):  # Estado destino
            for i in range(N):  # Estado origen
                ft[j] += forward[t-1][i] * A[i, j]
            ft[j] = ft[j] * B[j, obs_idx]
        
        ft = ft / np.sum(ft)  # Normalizar
        forward.append(ft)
        
        print(f"\n   t={t+1}: P(X{t+1} | e1:{t+1})")
        for i, estado in enumerate(ESTADOS_OCULTOS):
            print(f"   P(X{t+1}={estado} | e1:{t+1}) = {ft[i]:.4f}")
    
    return forward

# =============================================================================
# PREDICCIÓN
# =============================================================================
def prediccion(distribucion_actual, A, k):
    """
    Predice el estado en tiempo t+k dado la distribución en tiempo t
    
    Args:
        distribucion_actual: P(X_t | e_{1:t})
        A: Matriz de transición
        k: Número de pasos a predecir
    
    Returns:
        numpy.array: Distribución predicha P(X_{t+k} | e_{1:t})
    """
    print(f"\n3. PREDICCIÓN - {k} pasos adelante:")
    print(f"   Calculando P(X_t+{k} | e_1:t)")
    
    distribucion_predicha = distribucion_actual.copy()
    
    for paso in range(k):
        distribucion_predicha = distribucion_predicha @ A
        print(f"   Paso {paso+1}: {[f'{p:.4f}' for p in distribucion_predicha]}")
    
    print(f"\n   Distribución predicha para {k} pasos:")
    for i, estado in enumerate(ESTADOS_OCULTOS):
        print(f"   P(X_t+{k}={estado} | e_1:t) = {distribucion_predicha[i]:.4f}")
    
    return distribucion_predicha

# =============================================================================
# SUAVIZADO - ALGORITMO DE AVANCE-RETROCESO
# =============================================================================
def suavizado(observaciones, A, B, pi):
    """
    Implementa suavizado usando el algoritmo forward-backward
    Calcula P(X_k | e_{1:T}) para k < T
    
    Args:
        observaciones: Lista completa de observaciones
        A: Matriz de transición
        B: Matriz de observación
        pi: Distribución inicial
    
    Returns:
        list: Distribuciones suavizadas para cada tiempo
    """
    print(f"\n4. SUAVIZADO - Algoritmo Forward-Backward:")
    print(f"   Calculando P(X_k | e_1:T) para k = 1 a {len(observaciones)}")
    
    T = len(observaciones)
    N = len(ESTADOS_OCULTOS)
    
    # Paso forward (filtrado)
    forward = filtrado_forward(observaciones, A, B, pi)
    
    # Paso backward
    backward = [np.ones(N)]  # Inicializar en tiempo T
    
    for t in range(T-2, -1, -1):
        obs_idx = OBSERVACIONES.index(observaciones[t+1])
        bt = np.zeros(N)
        
        for i in range(N):
            for j in range(N):
                bt[i] += A[i, j] * B[j, obs_idx] * backward[0][j]
        
        backward.insert(0, bt)
    
    # Combinar forward y backward
    suavizado = []
    for t in range(T):
        s = forward[t] * backward[t]
        s = s / np.sum(s)
        suavizado.append(s)
        
        print(f"\n   t={t+1}: P(X{t+1} | e1:T)")
        for i, estado in enumerate(ESTADOS_OCULTOS):
            print(f"   P(X{t+1}={estado} | e1:T) = {s[i]:.4f}")
    
    return suavizado

# =============================================================================
# EXPLICACIÓN - ALGORITMO DE VITERBI
# =============================================================================
def explicacion_viterbi(observaciones, A, B, pi):
    """
    Implementa el algoritmo de Viterbi para encontrar la secuencia
    más probable de estados ocultos dado las observaciones
    
    Args:
        observaciones: Secuencia de observaciones
        A: Matriz de transición
        B: Matriz de observación
        pi: Distribución inicial
    
    Returns:
        list: Secuencia más probable de estados ocultos
    """
    print(f"\n5. EXPLICACIÓN - Algoritmo de Viterbi:")
    print(f"   Encontrando la secuencia más probable de estados dado las observaciones")
    
    T = len(observaciones)
    N = len(ESTADOS_OCULTOS)
    
    # Inicializar matrices
    delta = np.zeros((T, N))
    psi = np.zeros((T, N), dtype=int)
    
    # Paso inicial
    obs_idx = OBSERVACIONES.index(observaciones[0])
    delta[0] = pi * B[:, obs_idx]
    
    # Pasos recursivos
    for t in range(1, T):
        obs_idx = OBSERVACIONES.index(observaciones[t])
        for j in range(N):
            prob_transiciones = delta[t-1] * A[:, j]
            psi[t, j] = np.argmax(prob_transiciones)
            delta[t, j] = prob_transiciones[psi[t, j]] * B[j, obs_idx]
    
    # Backtracking
    secuencia_estados = [np.argmax(delta[T-1])]
    for t in range(T-2, -1, -1):
        secuencia_estados.insert(0, psi[t+1, secuencia_estados[0]])
    
    # Convertir índices a nombres de estados
    secuencia_nombres = [ESTADOS_OCULTOS[i] for i in secuencia_estados]
    
    print(f"\n   Secuencia más probable de estados ocultos:")
    for t, estado in enumerate(secuencia_nombres):
        prob = delta[t, secuencia_estados[t]]
        print(f"   t={t+1}: {estado} (probabilidad: {prob:.6f})")
    
    return secuencia_nombres

# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================
def main():
    # Secuencia de observaciones de ejemplo
    observaciones_ejemplo = ['SinParaguas', 'SinParaguas', 'Paraguas', 'Paraguas', 'SinParaguas']
    
    print("=" * 70)
    print("SECUENCIA DE OBSERVACIONES:", observaciones_ejemplo)
    print("=" * 70)
    
    # 1. FILTRADO
    distribuciones_filtrado = filtrado_forward(observaciones_ejemplo, A, B, pi)
    
    # 2. PREDICCIÓN
    distribucion_actual = distribuciones_filtrado[-1]  # Última distribución de filtrado
    prediccion(distribucion_actual, A, k=3)
    
    # 3. SUAVIZADO
    distribuciones_suavizado = suavizado(observaciones_ejemplo, A, B, pi)
    
    # 4. EXPLICACIÓN
    secuencia_explicacion = explicacion_viterbi(observaciones_ejemplo, A, B, pi)
    
    # =============================================================================
    # COMPARACIÓN Y CONCLUSIÓN
    # =============================================================================
    print(f"\n6. COMPARACIÓN DE RESULTADOS:")
    print(f"   Tiempo | Filtrado      | Suavizado     | Explicación")
    print(f"   " + "-" * 55)
    
    for t in range(len(observaciones_ejemplo)):
        filt = distribuciones_filtrado[t]
        suav = distribuciones_suavizado[t]
        expl = secuencia_explicacion[t]
        
        filt_str = f"[{filt[0]:.3f}, {filt[1]:.3f}]"
        suav_str = f"[{suav[0]:.3f}, {suav[1]:.3f}]"
        
        print(f"   {t+1:6} | {filt_str} | {suav_str} | {expl:8}")
    
    print(f"\n7. CONCLUSIÓN:")
    print(f"   - FILTRADO: Estima el estado actual usando observaciones hasta el presente")
    print(f"   - PREDICCIÓN: Proyecta estados futuros basado en el estado actual")
    print(f"   - SUAVIZADO: Mejora estimaciones pasadas usando información completa")
    print(f"   - EXPLICACIÓN: Encuentra la secuencia globalmente más consistente")
    
    print(f"\n=== ANÁLISIS COMPLETADO ===")

# Ejecutar el programa principal
if __name__ == "__main__":
    main()