"""
SISTEMA DE TEMPLE SIMULADO - TRON DIGITAL

Este modulo implementa el algoritmo de Temple Simulado (Simulated Annealing),
una metaheuristica inspirada en el proceso de recocido en metalurgia. El
algoritmo utiliza una temperatura que disminuye gradualmente, permitiendo
movimientos aleatorios que podrian empeorar la solucion temporalmente
para escapar de optimos locales.

El temple simulado es particularmente efectivo en espacios de busqueda
complejos con multiples optimos locales.
"""

import math
import random
import time

# --- RED DIGITAL DE TRON ---
# Diccionario que representa las conexiones entre programas en el sistema
# Cada nodo tiene una lista de nodos vecinos accesibles directamente
red_tron = {
    "Tron": ["Clu", "Yori", "Flynn"],    # Tron tiene multiples opciones iniciales
    "Clu": ["Sark", "Sector5"],          # Clu conduce a dos rutas diferentes
    "Yori": ["Bit", "Flynn"],            # Yori conecta con Bit y Flynn
    "Flynn": ["Sector7", "Yori"],        # Flynn tiene conexiones reciprocas
    "Sark": ["MCP"],                     # Sark tiene acceso directo al MCP
    "Sector5": ["MCP"],                  # Sector5 tambien conduce al MCP
    "Sector7": ["Bit"],                  # Sector7 conecta con Bit
    "Bit": ["MCP"],                      # Bit tiene acceso al MCP
    "MCP": []                            # MCP es el objetivo final
}

# --- HEURISTICA: Energia (distancia o dificultad hacia el MCP) ---
# La heuristica representa la estimacion de dificultad para alcanzar el MCP
# Valores mas bajos indican mayor proximidad al objetivo
energia_nodo = {
    "Tron": 9,       # Tron esta lejos del MCP
    "Clu": 7,        # Clu esta mas cerca que Tron
    "Yori": 6,       # Yori esta relativamente cerca
    "Flynn": 8,      # Flynn tiene posicion intermedia
    "Sark": 3,       # Sark esta muy cerca del MCP
    "Sector5": 4,    # Sector5 tiene buena proximidad
    "Sector7": 5,    # Sector7 esta a media distancia
    "Bit": 2,        # Bit esta muy cerca del MCP
    "MCP": 0         # El MCP tiene energia 0
}


def temple_simulado(inicio, objetivo, temperatura_inicial=100, tasa_enfriamiento=0.9, iteraciones=100):
    """
    Implementacion del algoritmo de Temple Simulado (Simulated Annealing).
    
    El algoritmo comienza con alta temperatura que permite movimientos
    aleatorios (incluso hacia soluciones peores) y gradualmente reduce
    la temperatura para converger hacia una solucion optima.
    
    Parametros:
        inicio (str): Nodo inicial desde donde comenzar la busqueda.
        objetivo (str): Nodo objetivo que se desea alcanzar.
        temperatura_inicial (float): Temperatura inicial para controlar la exploracion.
        tasa_enfriamiento (float): Factor de reduccion de temperatura en cada paso.
        iteraciones (int): Numero maximo de iteraciones permitidas.
        
    Retorna:
        list: Camino recorrido durante la busqueda.
    """
    # Validar que los nodos existan en el grafo y heuristica
    if inicio not in red_tron or inicio not in energia_nodo:
        print(f"Error: El nodo inicial '{inicio}' no existe en el sistema")
        return [inicio]
    if objetivo not in red_tron or objetivo not in energia_nodo:
        print(f"Error: El nodo objetivo '{objetivo}' no existe en el sistema")
        return [inicio]
    
    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio]

    # Inicializacion del algoritmo
    nodo_actual = inicio
    mejor_nodo = nodo_actual
    mejor_energia = energia_nodo[nodo_actual]
    temperatura = temperatura_inicial
    camino_recorrido = [nodo_actual]

    print("INICIO DE BUSQUEDA POR TEMPLE SIMULADO")
    print(f"Tron inicia en el nodo: {inicio} con energia {mejor_energia}")
    print(f"Temperatura inicial: {temperatura_inicial}")
    print(f"Tasa de enfriamiento: {tasa_enfriamiento}")
    print(f"Iteraciones maximas: {iteraciones}")
    print("=" * 60)

    # Bucle principal de busqueda
    for paso in range(iteraciones):
        print(f"\n--- Iteracion {paso + 1} ---")
        print(f"Nodo actual: {nodo_actual} | Energia: {energia_nodo[nodo_actual]}")
        print(f"Temperatura actual: {temperatura:.2f}")

        # CASO DE EXITO: Objetivo alcanzado
        if nodo_actual == objetivo:
            print("\nEXITO: Tron ha alcanzado el MCP. ¡Red liberada!")
            break

        # Obtener vecinos del nodo actual
        vecinos = red_tron.get(nodo_actual, [])
        
        # CASO DE BLOQUEO: Sin vecinos disponibles
        if not vecinos:
            print("BLOQUEO: Tron se ha quedado sin rutas disponibles.")
            break

        # SELECCION ESTOCASTICA: Elegir un vecino al azar (exploracion)
        vecino_seleccionado = random.choice(vecinos)
        energia_actual = energia_nodo[nodo_actual]
        energia_vecino = energia_nodo[vecino_seleccionado]
        
        # Calcular diferencia de energia (costo del movimiento)
        delta_energia = energia_vecino - energia_actual
        
        print(f"Vecino seleccionado: {vecino_seleccionado} | Energia: {energia_vecino}")
        print(f"Delta energia: {delta_energia}")

        # CRITERIO DE ACEPTACION DE MOVIMIENTO
        # Se acepta el movimiento si:
        # 1. Mejora la energia (delta < 0), O
        # 2. Con probabilidad exp(-delta/temperatura) si empeora (delta >= 0)
        movimiento_aceptado = False
        
        if delta_energia < 0:
            # Movimiento que mejora: siempre aceptado
            movimiento_aceptado = True
            print("ACEPTADO: Movimiento mejora la energia")
        else:
            # Movimiento que empeora: aceptado con probabilidad basada en temperatura
            probabilidad_aceptacion = math.exp(-delta_energia / temperatura)
            umbral_aleatorio = random.random()
            
            print(f"Probabilidad de aceptacion: {probabilidad_aceptacion:.4f}")
            print(f"Umbral aleatorio: {umbral_aleatorio:.4f}")
            
            if umbral_aleatorio < probabilidad_aceptacion:
                movimiento_aceptado = True
                print("ACEPTADO: Movimiento peor aceptado probabilisticamente")
            else:
                print("RECHAZADO: Movimiento peor rechazado")

        # EJECUCION DEL MOVIMIENTO
        if movimiento_aceptado:
            nodo_actual = vecino_seleccionado
            camino_recorrido.append(nodo_actual)
            
            # ACTUALIZACION DE MEJOR SOLUCION
            if energia_vecino < mejor_energia:
                mejor_nodo = nodo_actual
                mejor_energia = energia_vecino
                print(f"¡NUEVO OPTIMO! Nodo: {mejor_nodo}, Energia: {mejor_energia}")

        # ENFRIAMIENTO: Reducir la temperatura gradualmente
        temperatura_anterior = temperatura
        temperatura *= tasa_enfriamiento
        print(f"Enfriamiento: {temperatura_anterior:.2f} -> {temperatura:.2f}")

        # CRITERIO DE TERMINACION POR TEMPERATURA
        if temperatura < 0.1:
            print("\nTERMINACION: Temperatura demasiado baja. Tron detiene la exploracion.")
            break

        # Pausa para visualizacion (simula procesamiento digital)
        time.sleep(0.1)

    # Resultados finales del algoritmo
    print("\n" + "=" * 60)
    print("RESULTADO FINAL DEL TEMPLE SIMULADO")
    print("=" * 60)
    print(f"Camino explorado: {' -> '.join(camino_recorrido)}")
    print(f"Mejor nodo alcanzado: {mejor_nodo} | Energia: {mejor_energia}")
    print(f"Temperatura final: {temperatura:.2f}")
    print(f"Longitud del camino: {len(camino_recorrido)} nodos")
    
    return camino_recorrido


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con conexiones y energias.
    
    Proporciona una vision general de la topologia y los valores de energia
    para entender el comportamiento del algoritmo.
    """
    print("\n" + "="*70)
    print("MAPA DEL SISTEMA TRON (Temple Simulado)")
    print("="*70)
    print("Energia: menor valor = mas cerca del MCP")
    print("-" * 70)
    for nodo, vecinos in sorted(red_tron.items()):
        if vecinos:
            vecinos_info = [f"{v}(e:{energia_nodo[v]})" for v in vecinos]
            print(f"{nodo:10} [e={energia_nodo[nodo]:2}] -> {', '.join(vecinos_info)}")
        else:
            print(f"{nodo:10} [e={energia_nodo[nodo]:2}] -> NODO TERMINAL")
    print("="*70)


def validar_entrada_nodo(entrada, grafo_dict, energia_dict):
    """
    Valida que la entrada del usuario corresponda a un nodo existente.
    
    Parametros:
        entrada (str): Texto ingresado por el usuario.
        grafo_dict (dict): Grafo del sistema para validar existencia.
        energia_dict (dict): Diccionario de energias para validar.
        
    Retorna:
        bool: True si el nodo existe en ambos diccionarios, False en caso contrario.
    """
    entrada_normalizada = entrada.strip()
    if entrada_normalizada.upper() == "MCP":
        entrada_normalizada = "MCP"
    else:
        entrada_normalizada = entrada_normalizada.title()
    
    return entrada_normalizada in grafo_dict and entrada_normalizada in energia_dict


def obtener_nodos_disponibles():
    """
    Retorna una lista de todos los nodos disponibles en el sistema.
    
    Retorna:
        list: Lista ordenada de nodos disponibles.
    """
    return sorted(red_tron.keys())


# PROGRAMA PRINCIPAL
def main():
    """
    Funcion principal que coordina la interaccion con el usuario
    y ejecuta el algoritmo de temple simulado.
    """
    print("SISTEMA DE TEMPLE SIMULADO")
    print("Algoritmo Simulated Annealing - Optimizacion Estocastica")
    
    # Mostrar el mapa del sistema para referencia
    mostrar_mapa_sistema()
    
    # Captura y validacion del nodo inicial
    while True:
        inicio = input("\nIngrese el nodo inicial (ej. Tron): ").strip()
        if validar_entrada_nodo(inicio, red_tron, energia_nodo):
            if inicio.upper() == "MCP":
                inicio = "MCP"
            else:
                inicio = inicio.title()
            break
        else:
            print(f"Error: '{inicio}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))
    
    # Captura y validacion del nodo objetivo
    while True:
        objetivo = input("Ingrese el nodo objetivo (ej. MCP): ").strip()
        if validar_entrada_nodo(objetivo, red_tron, energia_nodo):
            if objetivo.upper() == "MCP":
                objetivo = "MCP"
            else:
                objetivo = objetivo.title()
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))
    
    # Parametros configurables del algoritmo
    try:
        temperatura = float(input("Temperatura inicial (default 100): ") or "100")
        tasa_enfriamiento = float(input("Tasa de enfriamiento (default 0.9): ") or "0.9")
        iteraciones = int(input("Iteraciones maximas (default 100): ") or "100")
    except ValueError:
        print("Usando valores por defecto: temp=100, tasa=0.9, iter=100")
        temperatura = 100
        tasa_enfriamiento = 0.9
        iteraciones = 100
    
    # Ejecutar algoritmo de temple simulado
    camino_final = temple_simulado(inicio, objetivo, temperatura, tasa_enfriamiento, iteraciones)
    
    # Analisis final del resultado
    print("\n" + "="*50)
    print("ANALISIS FINAL")
    print("="*50)
    if camino_final[-1] == objetivo:
        print("EXITO: El algoritmo alcanzo el objetivo MCP")
        print("Tron: 'El temple simulado me permitio escapar de optimos locales'")
        print("      'y encontrar la ruta al MCP.'")
    else:
        print(f"TERMINACION: El algoritmo se detuvo en {camino_final[-1]}")
        print("Tron: 'La exploracion estocastica encontro buenas rutas,'")
        print("      'pero se necesitarian mas iteraciones para el MCP.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()