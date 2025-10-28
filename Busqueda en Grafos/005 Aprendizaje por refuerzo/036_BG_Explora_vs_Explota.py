"""
EXPLORACIÓN VS EXPLOTACIÓN EN ENTORNO BANDIT MULTI-ARMADO TEMÁTICO TRON

Este código implementa y compara dos estrategias clásicas para el problema
bandit multi-armado (multi-armed bandit) en un contexto temático de TRON.

El problema bandit representa el dilema fundamental en aprendizaje por refuerzo:
¿Cuándo explorar nuevas acciones para obtener información vs. explotar acciones
que ya sabemos que son buenas?

Estrategias implementadas:
1. ε-greedy con decaimiento (balance explícito exploración/explotación)
2. UCB1 (Upper Confidence Bound) - balance basado en incertidumbre

Cada "brazo" bandit representa una ruta diferente en el mundo TRON.
"""

import math
import random
from typing import Dict, List, Tuple

# ------------------------------------------------------------
# CONFIGURACIÓN DEL ENTORNO BANDIT TRON
# ------------------------------------------------------------
# Tres rutas disponibles en TRON (tres "brazos" del bandit)
ACTIONS = ["Sector_Luz", "Portal", "Arena"]

# Probabilidades de éxito reales de cada ruta (desconocidas para el agente)
# Estas probabilidades representan qué tan confiable es cada ruta para el éxito
P_SUCCESS = {
    "Sector_Luz": 0.55,   # Ruta media - decente pero no óptima
    "Portal":     0.40,   # Ruta débil - baja probabilidad de éxito
    "Arena":      0.70,   # Mejor ruta - óptima (pero el agente no lo sabe inicialmente)
}

def pull(action: str, rng: random.Random) -> int:
    """
    Simula usar un "brazo" bandit - devuelve recompensa Bernoulli.
    
    Args:
        action: La ruta elegida en TRON
        rng: Generador de números aleatorios
    
    Returns:
        int: 1 si hay éxito, 0 si falla (distribución Bernoulli)
    """
    return 1 if rng.random() < P_SUCCESS[action] else 0

# ------------------------------------------------------------
# FUNCIONES UTILITARIAS
# ------------------------------------------------------------
def argmax_ties_random(items: List[Tuple[str, float]], rng: random.Random) -> str:
    """
    Encuentra la acción con máximo valor, rompiendo empates aleatoriamente.
    
    Args:
        items: Lista de (acción, valor)
        rng: Generador para romper empates
    
    Returns:
        str: Acción con valor máximo (elegida aleatoriamente si hay empate)
    """
    best_val = max(v for _, v in items)
    candidates = [k for k, v in items if abs(v - best_val) <= 1e-12]
    return rng.choice(candidates)

def summary(name: str, Q: Dict[str, float], N: Dict[str, int], rewards: List[float]):
    """
    Genera un resumen estadístico del desempeño de una estrategia.
    
    Args:
        name: Nombre de la estrategia
        Q: Estimaciones de valor para cada acción
        N: Conteo de selecciones por acción
        rewards: Historial de recompensas obtenidas
    """
    print(f"\n=== {name} ===")
    print("Estimaciones Q(a) y conteos N(a):")
    for a in ACTIONS:
        print(f"  {a:12s}  Q={Q[a]:6.3f}  N={N[a]}")
    
    # Métricas de desempeño
    avg_reward = sum(rewards) / len(rewards)
    opt = "Arena"  # La acción óptima por definición
    opt_rate = sum(1 for r in selected_actions if r == opt) / len(selected_actions)
    
    print(f"Recompensa media: {avg_reward:.3f}")
    print(f"Frecuencia de acción óptima ({opt}): {opt_rate*100:.1f}%")

# ------------------------------------------------------------
# ESTRATEGIA ε-GREEDY CON DECAIMIENTO LINEAL
# ------------------------------------------------------------
def run_eps_greedy(steps: int, eps_ini: float, eps_fin: float, seed: int) -> Tuple[Dict[str, float], Dict[str, int], List[float], List[str]]:
    """
    Implementa la estrategia ε-greedy con decaimiento lineal de ε.
    
    Características:
    - Con probabilidad ε: explora (acción aleatoria)
    - Con probabilidad 1-ε: explota (mejor acción según Q)
    - ε decae linealmente de eps_ini a eps_fin
    
    Args:
        steps: Número total de pasos/episodios
        eps_ini: Valor inicial de ε (alta exploración)
        eps_fin: Valor final de ε (baja exploración)
        seed: Semilla para reproducibilidad
    
    Returns:
        tuple: (Q, N, rewards, actions_taken)
    """
    rng = random.Random(seed)
    
    # Inicialización
    Q = {a: 0.0 for a in ACTIONS}   # Estimación de valor para cada acción
    N = {a: 0   for a in ACTIONS}   # Veces que cada acción fue seleccionada
    rewards: List[float] = []        # Historial de recompensas
    actions_taken: List[str] = []    # Historial de acciones tomadas

    for t in range(1, steps + 1):
        # Decaimiento lineal de ε: más exploración al inicio, más explotación al final
        eps = eps_fin + (eps_ini - eps_fin) * max(0.0, (steps - t) / max(1, steps - 1))
        
        # Selección de acción: ε-greedy
        if rng.random() < eps:
            # Exploración: acción aleatoria
            a = rng.choice(ACTIONS)
        else:
            # Explotación: mejor acción según estimaciones actuales
            a = argmax_ties_random([(k, Q[k]) for k in ACTIONS], rng)

        # Ejecutar acción y observar recompensa
        r = pull(a, rng)
        
        # Actualizar estadísticas
        N[a] += 1
        # Actualización incremental: nuevo_promedio = promedio_antiguo + (nueva_muestra - promedio_antiguo) / n
        Q[a] += (r - Q[a]) / N[a]
        
        rewards.append(r)
        actions_taken.append(a)

    return Q, N, rewards, actions_taken

# ------------------------------------------------------------
# ESTRATEGIA UCB1 (UPPER CONFIDENCE BOUND)
# ------------------------------------------------------------
def run_ucb1(steps: int, c: float, seed: int) -> Tuple[Dict[str, float], Dict[str, int], List[float], List[str]]:
    """
    Implementa la estrategia UCB1 (Upper Confidence Bound).
    
    Características:
    - Balance exploración/explotación usando intervalos de confianza
    - Selecciona acciones con mayor límite superior de confianza
    - Exploración optimista: asume que acciones menos exploradas podrían ser mejores
    
    Args:
        steps: Número total de pasos
        c: Parámetro que controla el nivel de exploración
        seed: Semilla para reproducibilidad
    
    Returns:
        tuple: (Q, N, rewards, actions_taken)
    """
    rng = random.Random(seed)
    
    # Inicialización
    Q = {a: 0.0 for a in ACTIONS}   # Estimaciones de valor
    N = {a: 0   for a in ACTIONS}   # Conteos de selección
    rewards: List[float] = []        # Historial de recompensas
    actions_taken: List[str] = []    # Historial de acciones

    # Fase de inicialización: probar cada brazo al menos una vez
    t = 0
    for a in ACTIONS:
        r = pull(a, rng)
        N[a] += 1
        Q[a] = r * 1.0  # Inicializar con primera observación
        rewards.append(r)
        actions_taken.append(a)
        t += 1
        if t >= steps:
            return Q, N, rewards, actions_taken

    # Fase principal: selección UCB1
    for t in range(t + 1, steps + 1):
        total_pulls = sum(N.values())  # Total de selecciones hasta ahora
        
        scores = []
        for a in ACTIONS:
            # Término de exploración: mayor para acciones menos probadas
            bonus = c * math.sqrt(math.log(total_pulls) / N[a])
            # Score UCB = estimación actual + bonus de exploración
            scores.append((a, Q[a] + bonus))
        
        # Seleccionar acción con mayor score UCB
        a = argmax_ties_random(scores, rng)
        
        r = pull(a, rng)
        N[a] += 1
        # Actualizar estimación de valor
        Q[a] += (r - Q[a]) / N[a]
        
        rewards.append(r)
        actions_taken.append(a)

    return Q, N, rewards, actions_taken

# ------------------------------------------------------------
# DEMOSTRACIÓN Y COMPARACIÓN
# ------------------------------------------------------------
if __name__ == "__main__":
    STEPS = 2000  # Número de episodios/pasos de simulación
    
    print("PROBLEMA BANDIT MULTI-ARMADO EN ENTORNO TRON")
    print("=" * 50)
    print("Tres rutas disponibles con diferentes probabilidades de éxito:")
    print("(El agente NO conoce estas probabilidades inicialmente)")
    
    # Mostrar probabilidades reales (información que el agente no tiene)
    print("\nProbabilidades reales de éxito de cada ruta:")
    for a in ACTIONS:
        print(f"  {a:12s}: p={P_SUCCESS[a]:.2f}")

    # Ejecutar y evaluar estrategia ε-greedy
    print("\n" + "="*50)
    Q_eps, N_eps, R_eps, selected_actions = run_eps_greedy(
        steps=STEPS, eps_ini=0.6, eps_fin=0.02, seed=7
    )
    summary("ε-GREEDY (ε decae 0.60 → 0.02)", Q_eps, N_eps, R_eps)

    # Ejecutar y evaluar estrategia UCB1
    print("\n" + "="*50)
    Q_ucb, N_ucb, R_ucb, selected_actions = run_ucb1(
        steps=STEPS, c=2.0, seed=7
    )
    summary("UCB1 (c=2.0)", Q_ucb, N_ucb, R_ucb)

    # Análisis comparativo
    print("\n" + "="*50)
    print("ANÁLISIS COMPARATIVO:")
    print("- ε-greedy: Simple, control explícito de exploración vs explotación")
    print("- UCB1: Exploración optimista, balance automático basado en incertidumbre")
    print("- Ambas estrategias deberían aprender que 'Arena' es la mejor ruta")