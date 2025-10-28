# Aprendizaje por Refuerzo Pasivo en TRON
# - Política fija π (determinista y simple)
# - Simulación de episodios en un entorno estocástico
# - Actualización de valores V(s) con TD(0)
# - Sin librerías externas

from typing import Dict, List, Tuple, Optional
import random

# Definición de tipo para mayor claridad
State = str

# ------------------------------------------------------------
# Entorno TRON (pequeño grafo)
# ------------------------------------------------------------
# Grafo que representa el entorno: cada estado tiene una lista de estados vecinos
VECINOS: Dict[State, List[State]] = {
    "Base": ["Sector_Luz", "Portal"],           # Estado inicial
    "Sector_Luz": ["Base", "Arena"],            # Estado intermedio
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],  # Estado intermedio
    "Torre_IO": ["Arena", "Nucleo_Central"],    # Estado cercano al objetivo
    "Portal": ["Base", "Arena"],                # Estado intermedio alternativo
    "Nucleo_Central": [],  # terminal - estado objetivo
}

# Estados terminales (donde termina el episodio)
TERMINALES = {"Nucleo_Central"}

# Sistema de recompensas:
R_PASO = -0.5       # Costo por cada paso dado
R_AVANCE = +2.0     # Recompensa por moverse hacia el objetivo
R_DESVIO = -3.0     # Penalización por desviarse del camino planeado
R_QUEDARSE = -1.0   # Penalización por quedarse en el mismo estado
R_OBJETIVO = +150.0 # Gran recompensa por alcanzar el objetivo

# Dinámica estocástica - el entorno no es completamente determinista:
P_SUCCESS = 0.80   # Probabilidad de ir al vecino elegido (acción exitosa)
P_STAY    = 0.10   # Probabilidad de quedarse en el estado actual
# 1 - P_SUCCESS - P_STAY se reparte entre desvíos (acciones no deseadas)

GAMMA = 0.95  # Factor de descuento para recompensas futuras

# ------------------------------------------------------------
# Política fija π(s): regla simple "acércate al núcleo"
# ------------------------------------------------------------
def politica_fija(s: State) -> Optional[State]:
    """
    Política determinista que siempre intenta acercarse al núcleo central.
    Prioridad: Nucleo_Central > Torre_IO > Arena > primer vecino disponible
    """
    if s in TERMINALES or not VECINOS[s]:
        return None  # No hay acción posible en estados terminales o sin vecinos
    
    vecinos = VECINOS[s]
    
    # Estrategia de búsqueda en profundidad hacia el objetivo
    if "Nucleo_Central" in vecinos:
        return "Nucleo_Central"  # Si el objetivo está directamente accesible
    if "Torre_IO" in vecinos:
        return "Torre_IO"        # Si está disponible el penúltimo estado antes del objetivo
    if "Arena" in vecinos:
        return "Arena"           # Estado que lleva hacia Torre_IO
    
    return vecinos[0]  # Por defecto, elegir el primer vecino disponible

# ------------------------------------------------------------
# Dinámica del entorno
# ------------------------------------------------------------
def transicion(s: State, destino: Optional[State], rng: random.Random) -> Tuple[State, float]:
    """
    Simula la transición estocástica del entorno.
    Dado un estado y una acción, devuelve el próximo estado y la recompensa.
    """
    if s in TERMINALES or destino is None:
        return s, 0.0  # No hay transición en estados terminales

    vecinos = VECINOS[s]
    otros = [v for v in vecinos if v != destino]  # Vecinos alternativos
    
    # Calcular probabilidad de desvío (distribuida entre otros vecinos)
    p_desvio = max(0.0, 1.0 - P_SUCCESS - P_STAY)

    # Construir distribución de probabilidades para los posibles próximos estados
    dist: List[Tuple[State, float]] = []
    dist.append((destino, P_SUCCESS))  # Probabilidad de éxito (ir al destino deseado)
    dist.append((s, P_STAY))           # Probabilidad de quedarse en el mismo estado
    
    if otros:
        # Distribuir la probabilidad de desvío entre los otros vecinos
        p_each = p_desvio / len(otros)
        for v in otros:
            dist.append((v, p_each))
    else:
        # Si no hay otros vecinos, la probabilidad de desvío se suma a quedarse
        dist[-1] = (s, P_STAY + p_desvio)

    # Muestrear el próximo estado según la distribución de probabilidades
    estados, probs = zip(*dist)
    s2 = rng.choices(estados, weights=probs, k=1)[0]

    # Calcular recompensa según el tipo de transición
    if s2 == s:
        # Se quedó en el mismo estado
        r = R_PASO + R_QUEDARSE
    elif s2 == destino:
        # Fue al destino deseado
        r = R_PASO + (R_OBJETIVO if s2 == "Nucleo_Central" else R_AVANCE)
    else:
        # Se desvió a otro estado no deseado
        r = R_PASO + (R_OBJETIVO if s2 == "Nucleo_Central" else R_DESVIO)

    return s2, r

# ------------------------------------------------------------
# Aprendizaje pasivo TD(0) sobre V(s)
# ------------------------------------------------------------
def aprender_td0(
    alpha: float = 0.1,      # Tasa de aprendizaje
    episodios: int = 500,    # Número de episodios de entrenamiento
    max_pasos: int = 60,     # Máximo de pasos por episodio
    semilla: int = 7         # Semilla para reproducibilidad
) -> Dict[State, float]:
    """
    Implementa el algoritmo TD(0) para aprender la función valor V(s) 
    bajo una política fija (aprendizaje pasivo).
    """
    rng = random.Random(semilla)
    
    # Inicializar función valor V(s) = 0 para todos los estados
    V: Dict[State, float] = {s: 0.0 for s in VECINOS}

    # Bucle principal de entrenamiento por episodios
    for _ in range(episodios):
        s = "Base"  # Estado inicial de cada episodio
        pasos = 0
        
        # Ejecutar episodio hasta estado terminal o máximo de pasos
        while s not in TERMINALES and pasos < max_pasos:
            a = politica_fija(s)           # Seleccionar acción según política fija
            s2, r = transicion(s, a, rng)  # Observar transición y recompensa
            
            # Actualización TD(0): V(s) <- V(s) + alpha * [r + gamma V(s') - V(s)]
            objetivo = r + (0.0 if s2 in TERMINALES else GAMMA * V[s2])
            V[s] += alpha * (objetivo - V[s])
            
            s = s2  # Avanzar al siguiente estado
            pasos += 1
            
    return V  # Devolver función valor aprendida

# ------------------------------------------------------------
# Utilidades de impresión y demo
# ------------------------------------------------------------
def imprimir_valores(V: Dict[State, float]):
    """Imprime los valores V(s) en un orden específico para mejor legibilidad."""
    orden = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    for s in orden:
        print(f"{s:15s}: V(s) = {V[s]:8.3f}")

def simular_politica(pasos: int = 20, semilla: int = 17):
    """Simula y muestra la ejecución de la política fija paso a paso."""
    rng = random.Random(semilla)
    s = "Base"
    G = 0.0  # Retorno descontado acumulado
    t = 0
    
    print("\nSimulación siguiendo la política fija:")
    while s not in TERMINALES and t < pasos:
        a = politica_fija(s)
        s2, r = transicion(s, a, rng)
        print(f"t={t:2d}  s={s:12s}  a-> {str(a):12s}  s'={s2:12s}  r={r:6.1f}")
        
        # Acumular retorno descontado: G = Σ γ^t * r_t
        G += (GAMMA ** t) * r
        s = s2
        t += 1
        
    print(f"Retorno descontado aproximado: {G:.2f}")

def demo():
    """Función de demostración que ejecuta el aprendizaje y muestra resultados."""
    print("Aprendizaje por Refuerzo Pasivo (TD(0)) en TRON")
    
    # Aprender la función valor V(s)
    V = aprender_td0(alpha=0.15, episodios=800, max_pasos=50, semilla=42)
    
    print("\nValores aprendidos V(s) bajo la política fija:")
    imprimir_valores(V)
    
    # Simular la política para verla en acción
    simular_politica(pasos=25, semilla=11)

if __name__ == "__main__":
    demo()