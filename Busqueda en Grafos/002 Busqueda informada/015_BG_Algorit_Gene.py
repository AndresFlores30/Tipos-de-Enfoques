import math
import random
from typing import List, Tuple

#  Algoritmo Genético para maximizar f(x) = x*sin(10πx)+1
#  - Genoma: 16 bits que codifican un real x in [0, 1]
#  - Selección: torneo
#  - Cruza: 1 punto
#  - Mutación: bit-flip
#  - Elitismo: conservar los mejores k

# ---------- Configuración ----------
SEED = 42                 # Fija semilla para reproducibilidad
BITS = 16                 # Longitud del genoma binario
POP_SIZE = 80             # Tamaño de población
GENERATIONS = 120         # Número de generaciones
TOURNEY_SIZE = 3          # Participantes en torneo
CROSSOVER_RATE = 0.9      # Probabilidad de cruza
MUTATION_RATE = 1.0 / BITS  # Probabilidad de mutación por bit
ELITISM_K = 2             # Número de élites que pasan directos

random.seed(SEED)


# ---------- Utilidades GA ----------
def random_genome(bits: int = BITS) -> List[int]:
    """Crea un genoma binario aleatorio."""
    return [random.randint(0, 1) for _ in range(bits)]


def decode(genome: List[int]) -> float:
    """
    Decodifica un binario de 16 bits a un real en [0, 1].
    Int: v in [0, 2^BITS - 1]  ->  x = v / (2^BITS - 1)
    """
    v = 0
    for b in genome:
        v = (v << 1) | b
    return v / ((1 << BITS) - 1)


def fitness(x: float) -> float:
    """Función objetivo a maximizar: f(x) = x * sin(10πx) + 1."""
    return x * math.sin(10 * math.pi * x) + 1.0


def evaluate_population(pop: List[List[int]]) -> List[Tuple[float, float, List[int]]]:
    """
    Evalúa la población.
    Retorna lista de tuplas: (fitness, x_decodificado, genome)
    """
    scored = []
    for g in pop:
        x = decode(g)
        f = fitness(x)
        scored.append((f, x, g))
    # Ordena de mayor a menor aptitud
    scored.sort(key=lambda t: t[0], reverse=True)
    return scored


def tournament_selection(scored_pop: List[Tuple[float, float, List[int]]],
                         k: int = TOURNEY_SIZE) -> List[int]:
    """Selecciona un individuo por torneo (mayor fitness gana)."""
    participants = random.sample(scored_pop, k)
    winner = max(participants, key=lambda t: t[0])
    return winner[2][:]  # genome copy


def one_point_crossover(p1: List[int], p2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Cruza de un punto. Con prob. CROSSOVER_RATE cruza, si no, devuelve copia.
    """
    if random.random() > CROSSOVER_RATE or len(p1) != len(p2):
        return p1[:], p2[:]
    point = random.randint(1, len(p1) - 1)  # punto de corte entre [1, BITS-1]
    c1 = p1[:point] + p2[point:]
    c2 = p2[:point] + p1[point:]
    return c1, c2


def mutate(genome: List[int], pmut: float = MUTATION_RATE) -> None:
    """Mutación bit-flip independiente por bit con probabilidad pmut."""
    for i in range(len(genome)):
        if random.random() < pmut:
            genome[i] ^= 1  # flip 0<->1


# ---------- Bucle principal ----------
def genetic_algorithm() -> Tuple[float, float, List[int]]:
    # 1) Población inicial
    population = [random_genome() for _ in range(POP_SIZE)]

    best_overall = None  # (fitness, x, genome)

    for gen in range(1, GENERATIONS + 1):
        # 2) Evaluación
        scored = evaluate_population(population)
        if best_overall is None or scored[0][0] > best_overall[0]:
            best_overall = scored[0]

        # Logging de progreso
        f_best, x_best, _ = scored[0]
        f_mean = sum(s[0] for s in scored) / len(scored)
        f_worst = scored[-1][0]
        if gen % 10 == 0 or gen == 1 or gen == GENERATIONS:
            print(f"Gen {gen:3d} | Best: {f_best:.6f} @ x={x_best:.6f} | "
                  f"Mean: {f_mean:.6f} | Worst: {f_worst:.6f}")

        # 3) Elitismo: conserva los mejores ELITISM_K
        elites = [ind[2][:] for ind in scored[:ELITISM_K]]

        # 4) Selección + Cruza + Mutación para llenar el resto
        new_population: List[List[int]] = []
        while len(new_population) < POP_SIZE - ELITISM_K:
            # Selección por torneo
            p1 = tournament_selection(scored, TOURNEY_SIZE)
            p2 = tournament_selection(scored, TOURNEY_SIZE)

            # Cruza
            c1, c2 = one_point_crossover(p1, p2)

            # Mutación
            mutate(c1, MUTATION_RATE)
            mutate(c2, MUTATION_RATE)

            new_population.append(c1)
            if len(new_population) < POP_SIZE - ELITISM_K:
                new_population.append(c2)

        # 5) Nueva población = élites + descendencia
        population = elites + new_population

    # Evaluación final y mejor global
    scored = evaluate_population(population)
    if scored[0][0] > best_overall[0]:
        best_overall = scored[0]

    return best_overall  # (fitness, x, genome)


if __name__ == "__main__":
    best_f, best_x, best_g = genetic_algorithm()
    print("\n=== Resultado final ===")
    print(f"Mejor fitness: {best_f:.8f}")
    print(f"Mejor x en [0,1]: {best_x:.8f}")
    # Muestra el genoma en binario como string
    print("Genoma (bits):", "".join(str(b) for b in best_g))