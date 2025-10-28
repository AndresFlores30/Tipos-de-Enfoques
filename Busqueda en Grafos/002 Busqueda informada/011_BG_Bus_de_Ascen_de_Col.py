"""
SISTEMA DE BUSQUEDA POR ASCENSO DE COLINAS - TRON DIGITAL

Este modulo implementa el algoritmo Hill Climbing (Ascenso de Colinas),
una tecnica de optimizacion local que busca mejorar iterativamente la
solucion actual moviendose hacia vecinos que mejoran el valor heuristico.

El algoritmo es simple y eficiente pero puede quedar atrapado en optimos
locales, sin garantizar encontrar la solucion global optima.
"""

import random

# --- RED DIGITAL DE TRON ---
# Diccionario que representa las conexiones entre programas en el sistema
# Cada nodo tiene una lista de nodos vecinos accesibles directamente
grafo = {
    "Tron": ["Clu", "Flynn"],      # Tron puede acceder a Clu o Flynn
    "Clu": ["Sark", "Yori"],       # Clu tiene dos opciones de expansion
    "Flynn": ["Sector7"],          # Flynn tiene una ruta directa
    "Yori": ["Bit"],               # Yori conduce a Bit
    "Sark": ["MCP"],               # Sark tiene acceso directo al MCP
    "Sector7": ["MCP"],            # Sector7 tambien conduce al MCP
    "Bit": ["MCP"],                # Bit es otra ruta al MCP
    "MCP": []                      # MCP es el objetivo final (nodo terminal)
}

# --- HEURISTICA (energia restante hacia el MCP: menor valor = mejor) ---
# La heuristica representa la estimacion de costo restante hasta el objetivo
# En Hill Climbing, valores mas bajos indican mayor proximidad al objetivo
heuristica = {
    "Tron": 6,      # Tron esta relativamente lejos del MCP
    "Clu": 4,       # Clu esta mas cerca que Tron
    "Flynn": 5,     # Flynn tiene una posicion intermedia
    "Yori": 3,      # Yori esta bastante cerca del MCP
    "Sark": 2,      # Sark esta muy cerca del MCP
    "Sector7": 1,   # Sector7 es el mas cercano al MCP
    "Bit": 2,       # Bit tambien esta muy cerca
    "MCP": 0        # El MCP tiene heuristica 0 (objetivo alcanzado)
}


def ascenso_colinas(inicio, objetivo):
    """
    Implementacion del algoritmo Hill Climbing (Ascenso de Colinas).
    
    El algoritmo comienza en el nodo inicial y en cada iteracion se mueve
    al vecino con mejor valor heuristico. Se detiene cuando:
    1. Alcanza el objetivo
    2. No hay vecinos disponibles
    3. Ningun vecino ofrece mejora (optimo local)
    
    Parametros:
        inicio (str): Nodo inicial desde donde comenzar la busqueda.
        objetivo (str): Nodo objetivo que se desea alcanzar.
        
    Retorna:
        list: Camino recorrido desde el inicio hasta el punto de detencion.
    """
    # Validar que los nodos existan en el grafo y heuristica
    if inicio not in grafo or inicio not in heuristica:
        print(f"Error: El nodo inicial '{inicio}' no existe en el sistema")
        return [inicio]
    if objetivo not in grafo or objetivo not in heuristica:
        print(f"Error: El nodo objetivo '{objetivo}' no existe en el sistema")
        return [inicio]
    
    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio]

    # Inicializar el estado actual y el camino recorrido
    nodo_actual = inicio
    camino_recorrido = [nodo_actual]

    print("INICIO DEL ASCENSO DE COLINAS")
    print(f"Tron ha sido liberado en el nodo: {nodo_actual}")
    print(f"Heuristica inicial: {heuristica[nodo_actual]}")
    print("=" * 50)

    # Bucle principal de busqueda
    while True:
        # Mostrar estado actual
        print(f"\nNodo actual: {nodo_actual} | Heuristica: {heuristica[nodo_actual]}")

        # CASO 1: Objetivo alcanzado
        if nodo_actual == objetivo:
            print("\n" + "=" * 50)
            print("EXITO: Tron ha alcanzado el MCP. ¡La red esta liberada!")
            print("=" * 50)
            return camino_recorrido

        # Obtener vecinos del nodo actual
        vecinos = grafo.get(nodo_actual, [])
        
        # CASO 2: Sin vecinos disponibles (callejon sin salida)
        if not vecinos:
            print("\n" + "=" * 50)
            print("BLOQUEO: Nodo sin conexiones activas.")
            print("Tron queda atrapado en la red sin opciones de avance.")
            print("=" * 50)
            return camino_recorrido

        # Mostrar informacion de los vecinos
        print(f"Vecinos detectados: {vecinos}")
        print("Heuristicas de vecinos:", {v: heuristica[v] for v in vecinos})

        # Seleccionar el mejor vecino (menor valor heuristico)
        mejor_vecino = min(vecinos, key=lambda x: heuristica.get(x, float('inf')))
        heuristica_mejor_vecino = heuristica.get(mejor_vecino, float('inf'))
        
        print(f"Mejor vecino seleccionado: {mejor_vecino} | Heuristica: {heuristica_mejor_vecino}")

        # CASO 3: Optimo local alcanzado (ningun vecino ofrece mejora)
        if heuristica_mejor_vecino >= heuristica[nodo_actual]:
            print("\n" + "=" * 50)
            print("OPTIMO LOCAL: Tron detecta un punto alto local.")
            print(f"No hay rutas de menor energia desde {nodo_actual}.")
            print("Heuristica actual:", heuristica[nodo_actual])
            print("Mejor heuristica vecina:", heuristica_mejor_vecino)
            print("Tron: 'Estoy atrapado en esta colina...'")
            print("=" * 50)
            return camino_recorrido

        # MOVIMIENTO: Avanzar al mejor vecino
        nodo_actual = mejor_vecino
        camino_recorrido.append(nodo_actual)
        print(f"AVANCE: Tron se mueve hacia: {nodo_actual}")
        print(f"Heuristica mejorada: {heuristica[camino_recorrido[-2]]} -> {heuristica[nodo_actual]}")


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con conexiones y heuristicas.
    
    Proporciona una vision general de la topologia y los valores heuristicos
    para entender el comportamiento del algoritmo.
    """
    print("\n" + "="*60)
    print("MAPA DEL SISTEMA TRON (Ascenso de Colinas)")
    print("="*60)
    print("Heuristica: menor valor = mas cerca del MCP")
    print("-" * 60)
    for nodo, vecinos in sorted(grafo.items()):
        if vecinos:
            vecinos_info = [f"{v}(h:{heuristica[v]})" for v in vecinos]
            print(f"{nodo:10} [h={heuristica[nodo]:2}] -> {', '.join(vecinos_info)}")
        else:
            print(f"{nodo:10} [h={heuristica[nodo]:2}] -> NODO TERMINAL")
    print("="*60)


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
    return sorted(grafo.keys())


# PROGRAMA PRINCIPAL
def main():
    """
    Funcion principal que coordina la interaccion con el usuario
    y ejecuta el algoritmo de ascenso de colinas.
    """
    print("SISTEMA DE BUSQUEDA DE ASCENSION DE COLINAS")
    print("Algoritmo Hill Climbing - Optimizacion Local Voraz")
    
    # Mostrar el mapa del sistema para referencia
    mostrar_mapa_sistema()
    
    # Captura y validacion del nodo inicial
    while True:
        inicio = input("\nIngrese el nodo inicial (ej. Tron): ").strip()
        if validar_entrada_nodo(inicio, grafo, heuristica):
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
        if validar_entrada_nodo(objetivo, grafo, heuristica):
            if objetivo.upper() == "MCP":
                objetivo = "MCP"
            else:
                objetivo = objetivo.title()
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))
    
    # Ejecutar algoritmo de ascenso de colinas
    camino_encontrado = ascenso_colinas(inicio, objetivo)
    
    # Mostrar resultados finales
    print("\n" + "="*50)
    print("RESULTADO FINAL DEL ASCENSO DE COLINAS")
    print("="*50)
    print(f"Ruta explorada por Tron: {' -> '.join(camino_encontrado)}")
    print(f"Estado final: {camino_encontrado[-1]}")
    print(f"Longitud del camino: {len(camino_encontrado)} nodos")
    print(f"Heuristica final: {heuristica[camino_encontrado[-1]]}")
    
    # Analisis del resultado
    if camino_encontrado[-1] == objetivo:
        print("\nEXITO: El algoritmo alcanzo el objetivo MCP")
        print("Tron: 'He encontrado el camino mas directo al MCP.'")
    else:
        print(f"\nOPTIMO LOCAL: El algoritmo se detuvo en {camino_encontrado[-1]}")
        print("Tron: 'La ruta optima requiere estrategias mas avanzadas...'")
        print("MCP: 'Tu enfoque voraz te ha fallado, Tron.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()