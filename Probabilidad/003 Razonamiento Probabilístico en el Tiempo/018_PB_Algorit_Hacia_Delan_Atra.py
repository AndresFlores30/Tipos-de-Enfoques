"""
PROGRAMA: ALGORITMO HACIA DELANTE-ATRÁS (FORWARD-BACKWARD)

Este programa implementa el algoritmo Hacia Delante-Atrás (Forward-Backward) para 
procesos estocásticos temporales. El algoritmo calcula probabilidades suavizadas 
de estados ocultos dado una secuencia completa de observaciones.

El algoritmo consta de dos fases:
1. PASO HACIA DELANTE (Forward): Calcula probabilidades de filtrado
   α_t(i) = P(X_t = i, e_{1:t})
   
2. PASO HACIA ATRÁS (Backward): Calcula probabilidades de continuación
   β_t(i) = P(e_{t+1:T} | X_t = i)

Las probabilidades suavizadas se obtienen combinando ambas:
   γ_t(i) = P(X_t = i | e_{1:T}) = α_t(i) * β_t(i) / P(e_{1:T})
"""

import numpy as np

# =============================================================================
# CONFIGURACIÓN DEL MODELO OCULTO DE MARKOV
# =============================================================================
np.random.seed(42)
print("=== ALGORITMO HACIA DELANTE-ATRÁS (FORWARD-BACKWARD) ===\n")

# Estados ocultos del sistema
ESTADOS = ['Soleado', 'Nublado', 'Lluvioso']
print(f"Estados ocultos: {ESTADOS}")

# Observaciones posibles
OBSERVACIONES = ['Seco', 'Humedo', 'Mojado']
print(f"Observaciones: {OBSERVACIONES}")

# =============================================================================
# DEFINICIÓN DEL MODELO HMM
# =============================================================================
def crear_modelo_hmm():
    """
    Crea un modelo oculto de Markov para el clima con 3 estados y 3 observaciones
    """
    # Matriz de transición A: P(X_t | X_{t-1})
    matriz_transicion = np.array([
        # Soleado -> [Soleado, Nublado, Lluvioso]
        [0.6, 0.3, 0.1],  # Soleado
        [0.2, 0.5, 0.3],  # Nublado
        [0.1, 0.2, 0.7]   # Lluvioso
    ])
    
    # Matriz de observación B: P(E_t | X_t)
    matriz_observacion = np.array([
        # Seco, Humedo, Mojado
        [0.7, 0.2, 0.1],  # Soleado
        [0.3, 0.4, 0.3],  # Nublado
        [0.1, 0.3, 0.6]   # Lluvioso
    ])
    
    # Distribución inicial
    distribucion_inicial = np.array([0.5, 0.3, 0.2])  # [Soleado, Nublado, Lluvioso]
    
    return matriz_transicion, matriz_observacion, distribucion_inicial

# Crear el modelo
A, B, pi = crear_modelo_hmm()

print("\n1. PARÁMETROS DEL MODELO HMM:")
print("   Matriz de transición P(X_t | X_t-1):")
print("   " + " " * 10 + "".join([f"{estado:10}" for estado in ESTADOS]))
for i, estado_actual in enumerate(ESTADOS):
    print(f"   {estado_actual:8} " + "".join([f"{A[i,j]:10.3f}" for j in range(len(ESTADOS))]))

print("\n   Matriz de observación P(E_t | X_t):")
print("   " + " " * 10 + "".join([f"{obs:10}" for obs in OBSERVACIONES]))
for i, estado_oculto in enumerate(ESTADOS):
    print(f"   {estado_oculto:8} " + "".join([f"{B[i,j]:10.3f}" for j in range(len(OBSERVACIONES))]))

print(f"\n   Distribución inicial: {pi}")

# =============================================================================
# ALGORITMO HACIA DELANTE (FORWARD)
# =============================================================================
def algoritmo_forward(observaciones, A, B, pi):
    """
    Implementa el algoritmo Forward para calcular probabilidades de filtrado
    
    Args:
        observaciones: Lista de observaciones [obs_1, obs_2, ..., obs_T]
        A: Matriz de transición
        B: Matriz de observación
        pi: Distribución inicial
    
    Returns:
        tuple: (alpha, escala) donde:
            alpha: Matriz de probabilidades forward [T x N]
            escala: Factores de escala para normalización [T]
    """
    T = len(observaciones)
    N = len(ESTADOS)
    
    alpha = np.zeros((T, N))
    escala = np.zeros(T)
    
    print(f"\n2. ALGORITMO HACIA DELANTE (FORWARD):")
    print(f"   Calculando α_t(i) = P(X_t = i, e_1:t)")
    print(f"   Observaciones: {observaciones}")
    
    # Paso inicial t=1
    obs_idx = OBSERVACIONES.index(observaciones[0])
    alpha[0] = pi * B[:, obs_idx]
    escala[0] = np.sum(alpha[0])
    alpha[0] = alpha[0] / escala[0]  # Normalizar
    
    print(f"\n   t=1:")
    for i, estado in enumerate(ESTADOS):
        print(f"   α₁({estado}) = {alpha[0,i]:.6f}")
    print(f"   Factor de escala c₁ = {escala[0]:.6f}")
    
    # Pasos recursivos t=2 a T
    for t in range(1, T):
        obs_idx = OBSERVACIONES.index(observaciones[t])
        
        for j in range(N):  # Estado destino
            suma = 0.0
            for i in range(N):  # Estado origen
                suma += alpha[t-1, i] * A[i, j]
            alpha[t, j] = suma * B[j, obs_idx]
        
        escala[t] = np.sum(alpha[t])
        alpha[t] = alpha[t] / escala[t]  # Normalizar
        
        print(f"\n   t={t+1}:")
        for i, estado in enumerate(ESTADOS):
            print(f"   α_{t+1}({estado}) = {alpha[t,i]:.6f}")
        print(f"   Factor de escala c_{t+1} = {escala[t]:.6f}")
    
    return alpha, escala

# =============================================================================
# ALGORITMO HACIA ATRÁS (BACKWARD)
# =============================================================================
def algoritmo_backward(observaciones, A, B, escala):
    """
    Implementa el algoritmo Backward para calcular probabilidades de continuación
    
    Args:
        observaciones: Lista de observaciones
        A: Matriz de transición
        B: Matriz de observación
        escala: Factores de escala del algoritmo forward
    
    Returns:
        numpy.array: Matriz de probabilidades backward [T x N]
    """
    T = len(observaciones)
    N = len(ESTADOS)
    
    beta = np.zeros((T, N))
    
    print(f"\n3. ALGORITMO HACIA ATRÁS (BACKWARD):")
    print(f"   Calculando β_t(i) = P(e_t+1:T | X_t = i)")
    
    # Paso inicial t=T
    beta[T-1] = 1.0 / escala[T-1]  # Inicializar con el factor de escala
    
    print(f"\n   t={T} (inicialización):")
    for i, estado in enumerate(ESTADOS):
        print(f"   β_{T}({estado}) = {beta[T-1,i]:.6f}")
    
    # Pasos recursivos t=T-1 a 1
    for t in range(T-2, -1, -1):
        obs_idx = OBSERVACIONES.index(observaciones[t+1])
        
        for i in range(N):  # Estado origen
            suma = 0.0
            for j in range(N):  # Estado destino
                suma += A[i, j] * B[j, obs_idx] * beta[t+1, j]
            beta[t, i] = suma / escala[t]  # Usar factor de escala para normalizar
        
        print(f"\n   t={t+1}:")
        for i, estado in enumerate(ESTADOS):
            print(f"   β_{t+1}({estado}) = {beta[t,i]:.6f}")
    
    return beta

# =============================================================================
# CÁLCULO DE PROBABILIDADES SUAVIZADAS
# =============================================================================
def calcular_probabilidades_suavizadas(alpha, beta):
    """
    Calcula las probabilidades suavizadas combinando forward y backward
    
    γ_t(i) = P(X_t = i | e_1:T) = α_t(i) * β_t(i)
    
    Args:
        alpha: Probabilidades forward
        beta: Probabilidades backward
    
    Returns:
        numpy.array: Matriz de probabilidades suavizadas [T x N]
    """
    T, N = alpha.shape
    gamma = np.zeros((T, N))
    
    print(f"\n4. PROBABILIDADES SUAVIZADAS:")
    print(f"   Calculando γ_t(i) = P(X_t = i | e_1:T) = α_t(i) * β_t(i)")
    
    for t in range(T):
        for i in range(N):
            gamma[t, i] = alpha[t, i] * beta[t, i]
        
        # Normalizar (aunque teóricamente ya deberían estar normalizadas)
        gamma[t] = gamma[t] / np.sum(gamma[t])
        
        print(f"\n   t={t+1}:")
        for i, estado in enumerate(ESTADOS):
            print(f"   γ_{t+1}({estado}) = P(X_{t+1}={estado} | e_1:T) = {gamma[t,i]:.6f}")
    
    return gamma

# =============================================================================
# PROBABILIDADES DE TRANSICIÓN SUAVIZADAS
# =============================================================================
def calcular_probabilidades_transicion_suavizadas(observaciones, alpha, beta, A, B, escala):
    """
    Calcula probabilidades de transición suavizadas
    
    ξ_t(i,j) = P(X_t = i, X_t+1 = j | e_1:T)
    
    Args:
        observaciones: Secuencia de observaciones
        alpha: Probabilidades forward
        beta: Probabilidades backward
        A: Matriz de transición
        B: Matriz de observación
        escala: Factores de escala
    
    Returns:
        numpy.array: Tensor de probabilidades de transición [T-1 x N x N]
    """
    T = len(observaciones)
    N = len(ESTADOS)
    
    xi = np.zeros((T-1, N, N))
    
    print(f"\n5. PROBABILIDADES DE TRANSICIÓN SUAVIZADAS:")
    print(f"   Calculando ξ_t(i,j) = P(X_t = i, X_t+1 = j | e_1:T)")
    
    for t in range(T-1):
        obs_idx = OBSERVACIONES.index(observaciones[t+1])
        denominador = 0.0
        
        for i in range(N):
            for j in range(N):
                xi[t, i, j] = alpha[t, i] * A[i, j] * B[j, obs_idx] * beta[t+1, j]
                denominador += xi[t, i, j]
        
        # Normalizar
        if denominador > 0:
            xi[t] = xi[t] / denominador
        
        print(f"\n   t={t+1}:")
        for i, estado_i in enumerate(ESTADOS):
            for j, estado_j in enumerate(ESTADOS):
                if xi[t, i, j] > 0.001:  # Mostrar solo valores significativos
                    print(f"   ξ_{t+1}({estado_i},{estado_j}) = {xi[t,i,j]:.6f}")
    
    return xi

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    # Secuencia de observaciones de ejemplo
    observaciones = ['Seco', 'Humedo', 'Mojado', 'Mojado', 'Humedo', 'Seco']
    
    print("=" * 70)
    print("SECUENCIA DE OBSERVACIONES:", observaciones)
    print("=" * 70)
    
    # Ejecutar algoritmo Forward
    alpha, escala = algoritmo_forward(observaciones, A, B, pi)
    
    # Ejecutar algoritmo Backward
    beta = algoritmo_backward(observaciones, A, B, escala)
    
    # Calcular probabilidades suavizadas
    gamma = calcular_probabilidades_suavizadas(alpha, beta)
    
    # Calcular probabilidades de transición suavizadas
    xi = calcular_probabilidades_transicion_suavizadas(observaciones, alpha, beta, A, B, escala)
    
    # =============================================================================
    # RESULTADOS FINALES Y ANÁLISIS
    # =============================================================================
    print(f"\n6. RESUMEN FINAL - SECUENCIA MÁS PROBABLE:")
    print(f"   Tiempo | Observación | " + " | ".join([f"P({estado})" for estado in ESTADOS]) + " | Estado Más Probable")
    print(f"   " + "-" * 85)
    
    for t in range(len(observaciones)):
        obs = observaciones[t]
        probs = [f"{gamma[t,i]:.3f}" for i in range(len(ESTADOS))]
        estado_max = ESTADOS[np.argmax(gamma[t])]
        
        print(f"   {t+1:6} | {obs:11} | " + " | ".join(probs) + f" | {estado_max:13}")
    
    # Calcular la probabilidad de la secuencia de observaciones
    log_probabilidad = np.sum(np.log(escala))
    probabilidad = np.exp(log_probabilidad)
    
    print(f"\n7. PROBABILIDAD DE LA SECUENCIA OBSERVADA:")
    print(f"   P(e_1:T) = ∏ c_t = {probabilidad:.8f}")
    print(f"   Log P(e_1:T) = ∑ log(c_t) = {log_probabilidad:.8f}")
    
    # Comparación entre filtrado y suavizado
    print(f"\n8. COMPARACIÓN FILTRADO vs SUAVIZADO:")
    print(f"   Tiempo | " + " | ".join([f"Filtrado({estado})" for estado in ESTADOS]) + " | " + 
          " | ".join([f"Suavizado({estado})" for estado in ESTADOS]))
    print(f"   " + "-" * 100)
    
    for t in range(len(observaciones)):
        filtrado = [f"{alpha[t,i]:.3f}" for i in range(len(ESTADOS))]
        suavizado = [f"{gamma[t,i]:.3f}" for i in range(len(ESTADOS))]
        
        print(f"   {t+1:6} | " + " | ".join(filtrado) + " | " + " | ".join(suavizado))
    
    print(f"\n9. INTERPRETACIÓN:")
    print(f"   - El algoritmo Forward-Backward permite estimar estados pasados")
    print(f"     usando información completa (suavizado)")
    print(f"   - Las probabilidades suavizadas son más precisas que las de filtrado")
    print(f"   - El algoritmo es fundamental para el aprendizaje de parámetros en HMMs")
    
    print(f"\n=== ALGORITMO HACIA DELANTE-ATRÁS COMPLETADO ===")

# Ejecutar el programa
if __name__ == "__main__":
    main()