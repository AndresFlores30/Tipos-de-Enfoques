#   Los programas evolucionan dentro de la red
#   para descifrar una palabra objetivo mediante
#   selección, cruce y mutación.
# ==========================================

import random
import string

# --- CONFIGURACIÓN DEL SISTEMA ---
objetivo = "TRON"
tamaño_poblacion = 20
tasa_mutacion = 0.1
max_generaciones = 1000

# --- FUNCIONES GENÉTICAS ---

def generar_individuo(longitud):
    """Crea un programa (cadena aleatoria) de longitud dada."""
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(longitud))

def calcular_aptitud(individuo):
    """Evalúa la aptitud: cuántas letras coinciden con el objetivo."""
    return sum(1 for i, j in zip(individuo, objetivo) if i == j)

def seleccionar_padres(poblacion):
    """Selecciona dos individuos con mejor desempeño."""
    return random.choices(
        poblacion,
        weights=[calcular_aptitud(i) for i in poblacion],
        k=2
    )

def cruzar(padre1, padre2):
    """Combina dos programas para generar un nuevo descendiente."""
    punto = random.randint(1, len(objetivo) - 1)
    return padre1[:punto] + padre2[punto:]

def mutar(individuo):
    """Aplica mutaciones aleatorias al código."""
    individuo_lista = list(individuo)
    for i in range(len(individuo_lista)):
        if random.random() < tasa_mutacion:
            individuo_lista[i] = random.choice(string.ascii_uppercase)
    return ''.join(individuo_lista)

# --- CICLO EVOLUTIVO ---

def algoritmo_genetico():
    """Ejecución principal del algoritmo genético."""
    poblacion = [generar_individuo(len(objetivo)) for _ in range(tamaño_poblacion)]

    for generacion in range(max_generaciones):
        # Evaluar aptitud
        mejor = max(poblacion, key=calcular_aptitud)
        aptitud_mejor = calcular_aptitud(mejor)

        print(f"Generación {generacion+1} | Mejor programa: {mejor} | Aptitud: {aptitud_mejor}")

        # Si alcanza la solución
        if mejor == objetivo:
            print("\n>>> PROGRAMA ÓPTIMO ENCONTRADO <<<")
            print(f"Solución: {mejor} en {generacion+1} generaciones.")
            return mejor

        # Nueva generación
        nueva_poblacion = []
        for _ in range(tamaño_poblacion):
            padre1, padre2 = seleccionar_padres(poblacion)
            hijo = cruzar(padre1, padre2)
            hijo = mutar(hijo)
            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion

    print("\n>>> LIMITE DE GENERACIONES ALCANZADO <<<")
    print(f"Mejor resultado obtenido: {mejor}")
    return mejor

# --- EJECUCIÓN ---
print("SISTEMA EVOLUTIVO TRON - ALGORITMO GENÉTICO")

algoritmo_genetico()