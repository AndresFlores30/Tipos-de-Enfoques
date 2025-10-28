"""
Q-LEARNING EN ENTORNO TRON - APRENDIZAJE POR REFUERZO ACTIVO

Este código implementa el algoritmo Q-Learning para aprender una política óptima
en un entorno estocástico temático de TRON. A diferencia del aprendizaje pasivo
que solo evalúa una política fija, Q-Learning aprende activamente la mejor política
mediante exploración y explotación.

Características principales:
- Entorno estocástico con transiciones probabilísticas
- Sistema de recompensas complejo
- Exploración ε-greedy con decaimiento
- Aprendizaje de función Q(s,a) para política óptima
"""

import random

# --------------------------
# CONFIGURACIÓN DEL ENTORNO TRON
# --------------------------
# Grafo de estados que representa el mundo de TRON
# Cada estado tiene estados vecinos accesibles
VECINOS = {
    "Base": ["Sector_Luz", "Portal"],           # Estado inicial
    "Sector_Luz": ["Base", "Arena"],            # Zona de transición
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],  # Área central de decisiones
    "Torre_IO": ["Arena", "Nucleo_Central"],    # Último estado antes del objetivo
    "Portal": ["Base", "Arena"],                # Camino alternativo
    "Nucleo_Central": [],  # Estado terminal - objetivo del juego
}

TERMINAL = "Nucleo_Central"  # Estado objetivo donde termina el episodio

# SISTEMA DE RECOMPENSAS - Motiva al agente a tomar buenas decisiones
R_PASO = -0.5       # Costo por moverse (incentiva eficiencia)
R_AVANCE = +2.0     # Recompensa por avanzar hacia el objetivo
R_DESVIO = -3.0     # Penalización por desviarse del camino
R_QUEDARSE = -1.0   # Penalización por no moverse
R_OBJETIVO = +150.0 # Gran recompensa por alcanzar el objetivo

# DINÁMICA ESTOCÁSTICA - El entorno es incierto
P_SUCCESS = 0.80   # Probabilidad de éxito en la acción elegida
P_STAY    = 0.10   # Probabilidad de quedarse en el estado actual
# El resto (10%) se distribuye como desvíos a otros vecinos

GAMMA = 0.95  # Factor de descuento para recompensas futuras

# --------------------------
# FUNCIONES DEL ENTORNO
# --------------------------

def acciones(s):
    """Devuelve las acciones disponibles desde el estado s."""
    return VECINOS[s]

def step(s, a, rng):
    """
    Simula un paso en el entorno TRON.
    
    Args:
        s: Estado actual
        a: Acción elegida (vecino destino)
        rng: Generador de números aleatorios
    
    Returns:
        tuple: (siguiente_estado, recompensa)
    """
    if s == TERMINAL or a is None:
        return s, 0.0

    vecinos = VECINOS[s]
    dest = a
    otros = [v for v in vecinos if v != dest]  # Vecinos alternativos
    p_desvio = max(0.0, 1.0 - P_SUCCESS - P_STAY)

    # Construir distribución de probabilidades
    dist = [(dest, P_SUCCESS), (s, P_STAY)]
    if otros:
        p_each = p_desvio / len(otros)
        for v in otros:
            dist.append((v, p_each))
    else:
        dist[-1] = (s, P_STAY + p_desvio)

    # Muestrear próximo estado según distribución
    estados, probs = zip(*dist)
    s2 = rng.choices(estados, weights=probs, k=1)[0]

    # Calcular recompensa según resultado de la transición
    if s2 == s:
        r = R_PASO + R_QUEDARSE  # Se quedó en el mismo lugar
    elif s2 == dest:
        r = R_PASO + (R_OBJETIVO if s2 == TERMINAL else R_AVANCE)  # Éxito
    else:
        r = R_PASO + (R_OBJETIVO if s2 == TERMINAL else R_DESVIO)  # Desvío

    return s2, r

# --------------------------
# ALGORITMO Q-LEARNING
# --------------------------

def elegir_accion(Q, s, eps, rng):
    """
    Selección de acción usando estrategia ε-greedy.
    
    Con probabilidad ε: explora (acción aleatoria)
    Con probabilidad 1-ε: explota (mejor acción según Q)
    """
    acts = acciones(s)
    if not acts:
        return None
    
    # Exploración: acción aleatoria
    if rng.random() < eps:
        return rng.choice(acts)
    
    # Explotación: mejor acción según valores Q
    mejor_val = float("-inf")
    mejores = []
    for a in acts:
        q = Q.get((s, a), 0.0)  # Valor por defecto 0.0 para estados no visitados
        if q > mejor_val + 1e-12:  # Comparación con tolerancia numérica
            mejor_val, mejores = q, [a]
        elif abs(q - mejor_val) <= 1e-12:
            mejores.append(a)
    
    # Si hay empate, elegir aleatoriamente entre las mejores
    return rng.choice(mejores)

def maxQ(Q, s):
    """
    Calcula el máximo valor Q para un estado s sobre todas las acciones.
    Usado en la actualización de Q-Learning.
    """
    acts = acciones(s)
    return 0.0 if not acts else max(Q.get((s, a), 0.0) for a in acts)

def entrenar_qlearning(alpha=0.2, gamma=GAMMA,
                       eps_ini=0.6, eps_fin=0.05,
                       episodios=1200, max_pasos=60, semilla=7):
    """
    Entrena un agente usando Q-Learning.
    
    Args:
        alpha: Tasa de aprendizaje (cuánto peso dar a nuevas experiencias)
        gamma: Factor de descuento para recompensas futuras
        eps_ini: ε inicial para exploración
        eps_fin: ε final para exploración
        episodios: Número de episodios de entrenamiento
        max_pasos: Límite de pasos por episodio
        semilla: Semilla para reproducibilidad
    
    Returns:
        dict: Función Q(s,a) aprendida
    """
    rng = random.Random(semilla)
    Q = {}  # Tabla Q: (estado, acción) -> valor
    
    for ep in range(episodios):
        s = "Base"  # Estado inicial de cada episodio
        
        # Decaimiento lineal de ε: más exploración al inicio, más explotación al final
        eps = eps_fin + (eps_ini - eps_fin) * (1 - ep / max(1, episodios - 1))
        
        pasos = 0
        # Ejecutar episodio hasta estado terminal o máximo de pasos
        while s != TERMINAL and pasos < max_pasos:
            # 1. Elegir acción (ε-greedy)
            a = elegir_accion(Q, s, eps, rng)
            
            # 2. Ejecutar acción y observar resultado
            s2, r = step(s, a, rng)
            
            # 3. Actualización Q-Learning: Q(s,a) ← Q(s,a) + α[r + γ·maxₐ'Q(s',a') - Q(s,a)]
            target = r + (0.0 if s2 == TERMINAL else gamma * maxQ(Q, s2))
            Q[(s, a)] = Q.get((s, a), 0.0) + alpha * (target - Q.get((s, a), 0.0))
            
            s = s2  # Avanzar al siguiente estado
            pasos += 1
            
    return Q

def politica_greedy(Q):
    """
    Deriva la política greedy a partir de la función Q aprendida.
    
    Para cada estado, selecciona la acción con mayor valor Q.
    """
    pi = {}
    for s in VECINOS.keys():
        acts = acciones(s)
        if not acts:
            pi[s] = None
        else:
            # Seleccionar acción con máximo valor Q
            pi[s] = max(acts, key=lambda a: Q.get((s, a), 0.0))
    return pi

# --------------------------
# VISUALIZACIÓN Y DEMOSTRACIÓN
# --------------------------

def imprimir_politica(pi):
    """Muestra la política aprendida en un formato legible."""
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    print("Política aprendida (greedy sobre Q):")
    for s in orden:
        print(f"  {s:15s} -> {pi.get(s)}")

def simular(pi, pasos=25, semilla=11):
    """
    Simula la ejecución de la política aprendida en el entorno.
    
    Muestra paso a paso la trayectoria y calcula el retorno descontado.
    """
    rng = random.Random(semilla)
    s = "Base"
    G = 0.0  # Retorno descontado acumulado
    t = 0
    
    print("\nSimulación con la política aprendida:")
    while s != TERMINAL and t < pasos:
        a = pi.get(s)
        s2, r = step(s, a, rng)
        print(f"t={t:2d}  s={s:12s}  a={str(a):12s}  s'={s2:12s}  r={r:6.1f}")
        G += (GAMMA ** t) * r  # Acumular retorno descontado
        s = s2
        t += 1
        
    print(f"Retorno descontado aproximado: {G:.2f}")

def main():
    """Función principal que ejecuta el entrenamiento y demostración."""
    print("Q-LEARNING EN ENTORNO TRON - APRENDIZAJE ACTIVO")
    print("=" * 50)
    
    # Fase de entrenamiento: aprender la función Q
    print("Entrenando agente con Q-Learning...")
    Q = entrenar_qlearning(alpha=0.2, eps_ini=0.6, eps_fin=0.05,
                           episodios=1200, max_pasos=60, semilla=42)
    
    # Derivar política óptima a partir de Q
    pi = politica_greedy(Q)
    
    # Mostrar resultados
    imprimir_politica(pi)
    simular(pi, pasos=25, semilla=13)

if __name__ == "__main__":
    main()