"""
SISTEMA DE BUSQUEDA TABU - TRON DIGITAL

Este modulo implementa el algoritmo de Busqueda Tabu (Tabu Search),
una metaheuristica que utiliza memoria para evitar ciclos y escapar
de optimos locales. La lista tabu almacena movimientos recientes que
estan temporalmente prohibidos, forzando la exploracion de nuevas areas.

La busqueda tabu es particularmente util en espacios de busqueda complejos
donde los algoritmos voraces pueden quedar atrapados en optimos locales.
"""

import random

# --- RED DIGITAL DE TRON ---
# Diccionario que representa las conexiones entre programas en el sistema
# Cada nodo tiene una lista de nodos vecinos accesibles directamente
red_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],    # Tron tiene multiples opciones iniciales
    "Clu": ["Sark", "Sector5"],          # Clu conduce a dos sectores diferentes
    "Flynn": ["Sector7", "Yori"],        # Flynn tiene rutas alternativas
    "Yori": ["Bit", "Sark"],             # Yori conecta con Bit y Sark
    "Sark": ["MCP"],                     # Sark tiene acceso directo al MCP
    "Sector5": ["MCP"],                  # Sector5 tambien conduce al MCP
    "Sector7": ["Bit"],                  # Sector7 conecta con Bit
    "Bit": ["MCP"],                      # Bit tiene acceso al MCP
    "MCP": []                            # MCP es el objetivo final
}

# --- HEURISTICA: Energia necesaria para alcanzar al MCP (menor valor = mejor) ---
# La heuristica representa la estimacion de dificultad para alcanzar el MCP
# desde cada nodo. Valores mas bajos indican mayor proximidad al objetivo.
heuristica = {
    "Tron": 9,       # Tron esta lejos del MCP
    "Clu": 7,        # Clu esta mas cerca que Tron
    "Flynn": 8,      # Flynn tiene posicion intermedia
    "Yori": 6,       # Yori esta relativamente cerca
    "Sark": 3,       # Sark esta muy cerca del MCP
    "Sector5": 4,    # Sector5 tiene buena proximidad
    "Sector7": 5,    # Sector7 esta a media distancia
    "Bit": 2,        # Bit esta muy cerca del MCP
    "MCP": 0         # El MCP tiene heuristica 0
}


def busqueda_tabu(inicio, objetivo, tamano_tabu=3, iteraciones_max=10):
    """
    Implementacion del algoritmo de Busqueda Tabu.
    
    El algoritmo mantiene una lista tabu de nodos recientemente visitados
    para evitar ciclos y forzar la exploracion de nuevas areas. En cada
    iteracion, selecciona el mejor vecino no tabu disponible.
    
    Parametros:
        inicio (str): Nodo inicial desde donde comenzar la busqueda.
        objetivo (str): Nodo objetivo que se desea alcanzar.
        tamano_tabu (int): Tamano maximo de la lista tabu (memoria a corto plazo).
        iteraciones_max (int): Numero maximo de iteraciones permitidas.
        
    Retorna:
        list: Camino recorrido durante la busqueda.
    """
    # Validar que los nodos existan en el grafo y heuristica
    if inicio not in red_tron or inicio not in heuristica:
        print(f"Error: El nodo inicial '{inicio}' no existe en el sistema")
        return [inicio]
    if objetivo not in red_tron or objetivo not in heuristica:
        print(f"Error: El nodo objetivo '{objetivo}' no existe en el sistema")
        return [inicio]
    
    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio]

    # Inicializacion del algoritmo
    nodo_actual = inicio
    mejor_nodo_global = nodo_actual
    mejor_valor_global = heuristica[nodo_actual]
    lista_tabu = []  # Lista tabu: almacena nodos temporalmente prohibidos
    camino_recorrido = [nodo_actual]

    print("INICIO DE LA BUSQUEDA TABU")
    print(f"Tron inicia en el nodo: {nodo_actual}")
    print(f"Tamano de lista tabu: {tamano_tabu}")
    print(f"Iteraciones maximas: {iteraciones_max}")
    print("=" * 50)

    # Bucle principal de busqueda
    for iteracion in range(iteraciones_max):
        print(f"\n--- Iteracion {iteracion + 1} ---")
        print(f"Nodo actual: {nodo_actual} | Heuristica: {heuristica[nodo_actual]}")
        print(f"Lista Tabu actual: {lista_tabu}")

        # CASO DE EXITO: Objetivo alcanzado
        if nodo_actual == objetivo:
            print("\nEXITO: Tron ha alcanzado el MCP. ¡Sistema liberado!")
            return camino_recorrido

        # Obtener vecinos del nodo actual
        vecinos = red_tron.get(nodo_actual, [])
        
        # Filtrar vecinos: excluir los que estan en la lista tabu
        candidatos_validos = []
        for vecino in vecinos:
            if vecino not in lista_tabu:
                valor_heuristico = heuristica.get(vecino, float('inf'))
                candidatos_validos.append((vecino, valor_heuristico))
        
        # CASO DE BLOQUEO: No hay vecinos validos disponibles
        if not candidatos_validos:
            print("BLOQUEO: No hay vecinos validos fuera de la lista tabu.")
            print("Tron esta temporalmente bloqueado.")
            break

        # Mostrar informacion de candidatos
        print(f"Vecinos disponibles: {[v for v, _ in candidatos_validos]}")
        print(f"Evaluacion heuristica: {dict(candidatos_validos)}")

        # Seleccionar el mejor candidato (menor valor heuristico)
        mejor_vecino, mejor_valor = min(candidatos_validos, key=lambda x: x[1])
        print(f"Mejor vecino seleccionado: {mejor_vecino} | Heuristica: {mejor_valor}")

        # ACTUALIZACION DE MEMORIA TABU
        # Agregar el nodo actual a la lista tabu
        lista_tabu.append(nodo_actual)
        
        # Mantener el tamano de la lista tabu (eliminar el mas antiguo si es necesario)
        if len(lista_tabu) > tamano_tabu:
            nodo_eliminado = lista_tabu.pop(0)
            print(f"Nodo '{nodo_eliminado}' eliminado de la lista tabu")

        # MOVIMIENTO: Avanzar al mejor vecino seleccionado
        nodo_actual = mejor_vecino
        camino_recorrido.append(nodo_actual)

        # ACTUALIZACION DE MEJOR SOLUCION GLOBAL
        if mejor_valor < mejor_valor_global:
            mejor_valor_global = mejor_valor
            mejor_nodo_global = nodo_actual
            print(f"¡Nueva mejor solucion global! Nodo: {mejor_nodo_global}, Heuristica: {mejor_valor_global}")

        print(f"Tron avanza hacia: {nodo_actual}")

    # Fin de las iteraciones maximas
    print(f"\nFIN: Se alcanzo el limite de {iteraciones_max} iteraciones.")
    print(f"Mejor solucion encontrada: {mejor_nodo_global} | Heuristica: {mejor_valor_global}")
    return camino_recorrido


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con conexiones y heuristicas.
    
    Proporciona una vision general de la topologia y los valores heuristicos
    para entender el comportamiento del algoritmo tabu.
    """
    print("\n" + "="*70)
    print("MAPA DEL SISTEMA TRON (Busqueda Tabu)")
    print("="*70)
    print("Heuristica: menor valor = mas cerca del MCP")
    print("-" * 70)
    for nodo, vecinos in sorted(red_tron.items()):
        if vecinos:
            vecinos_info = [f"{v}(h:{heuristica[v]})" for v in vecinos]
            print(f"{nodo:10} [h={heuristica[nodo]:2}] -> {', '.join(vecinos_info)}")
        else:
            print(f"{nodo:10} [h={heuristica[nodo]:2}] -> NODO TERMINAL")
    print("="*70)


def validar_entrada_nodo(entrada, grafo_dict, heuristica_dict):
    """
    Valida que la entrada del usuario corresponda a un nodo existente.
    
    Parametros:
        entrada (str): Texto ingresado por el usuario.
        grafo_dict (dict): Grafo del sistema para validar existencia.
        heuristica_dict (dict): Diccionario de heuristicas para validar.
        
    Retorna:
        bool: True si el nodo existe en ambos diccionarios, False en caso contrario.
    """
    entrada_normalizada = entrada.strip()
    if entrada_normalizada.upper() == "MCP":
        entrada_normalizada = "MCP"
    else:
        entrada_normalizada = entrada_normalizada.title()
    
    return entrada_normalizada in grafo_dict and entrada_normalizada in heuristica_dict


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
    y ejecuta el algoritmo de busqueda tabu.
    """
    print("SISTEMA DE BUSQUEDA TABU")
    print("Algoritmo Tabu Search - Exploracion con Memoria")
    
    # Mostrar el mapa del sistema para referencia
    mostrar_mapa_sistema()
    
    # Captura y validacion del nodo inicial
    while True:
        inicio = input("\nIngrese el nodo inicial (ej. Tron): ").strip()
        if validar_entrada_nodo(inicio, red_tron, heuristica):
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
        if validar_entrada_nodo(objetivo, red_tron, heuristica):
            if objetivo.upper() == "MCP":
                objetivo = "MCP"
            else:
                objetivo = objetivo.title()
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))
    
    # Parametros configurables del algoritmo tabu
    try:
        tamano_tabu = int(input("Tamano de lista tabu (default 3): ") or "3")
        iteraciones_max = int(input("Iteraciones maximas (default 10): ") or "10")
    except ValueError:
        print("Usando valores por defecto: tamano_tabu=3, iteraciones_max=10")
        tamano_tabu = 3
        iteraciones_max = 10
    
    # Ejecutar algoritmo de busqueda tabu
    camino_encontrado = busqueda_tabu(inicio, objetivo, tamano_tabu, iteraciones_max)
    
    # Mostrar resultados finales
    print("\n" + "="*50)
    print("RESULTADO FINAL DE LA BUSQUEDA TABU")
    print("="*50)
    print(f"Ruta explorada por Tron: {' -> '.join(camino_encontrado)}")
    print(f"Nodo final alcanzado: {camino_encontrado[-1]}")
    print(f"Longitud del camino: {len(camino_encontrado)} nodos")
    print(f"Heuristica final: {heuristica.get(camino_encontrado[-1], 'N/A')}")
    
    # Analisis del resultado
    if camino_encontrado[-1] == objetivo:
        print("\nEXITO: El algoritmo alcanzo el objetivo MCP")
        print("Tron: 'La memoria tabu me permitio evitar ciclos y encontrar el MCP.'")
    else:
        print(f"\nTERMINACION: El algoritmo se detuvo en {camino_encontrado[-1]}")
        print("Tron: 'La busqueda tabu me ayudo a explorar areas nuevas,'")
        print("      'pero se necesitarian mas iteraciones para alcanzar el MCP.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()