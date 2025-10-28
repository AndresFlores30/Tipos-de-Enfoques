"""
SISTEMA DE BUSQUEDA VORAZ PRIMERO EL MEJOR - TRON DIGITAL

Este modulo implementa el algoritmo Greedy Best-First Search que utiliza
exclusivamente una funcion heuristica para guiar la exploracion hacia el objetivo.
El algoritmo siempre expande el nodo que parece mas prometedor segun la heuristica,
sin considerar costos acumulados del camino recorrido.
"""

import heapq

# --- RED DIGITAL DE TRON ---
# Diccionario que representa las conexiones entre programas en el sistema TRON
# Estructura: {nodo: {vecino1, vecino2, ...}} - grafo no ponderado para este algoritmo
red_tron = {
    "Tron": {"Clu", "Flynn"},              # Tron conectado a sus aliados principales
    "Clu": {"Sark", "Tron"},               # Clu con acceso al sistema de seguridad
    "Flynn": {"Tron", "Yori", "Sector7"},  # Flynn con multiples rutas alternativas
    "Yori": {"Flynn", "Sector7"},          # Yori como conexion intermedia
    "Sector7": {"Yori", "Bit"},            # Sector periferico del sistema
    "Bit": {"Sector7", "MCP"},             # Bit con acceso directo al MCP
    "Sark": {"Clu", "MCP"},                # Sark con ruta directa al MCP
    "MCP": set()                           # MCP como objetivo final (sin conexiones salientes)
}

# --- FUNCION HEURISTICA ---
# Estimacion de la distancia desde cada nodo hasta el objetivo MCP
# Valores mas bajos indican mayor proximidad estimada al MCP
# La heuristica guia completamente la decision del algoritmo
heuristica = {
    "Tron": 10,    # Tron esta lejos del MCP segun la estimacion
    "Clu": 8,      # Clu esta mas cerca que Tron
    "Flynn": 7,    # Flynn tiene una posicion intermedia
    "Yori": 5,     # Yori esta relativamente cerca del MCP
    "Sector7": 4,  # Sector7 tiene buena proximidad
    "Bit": 2,      # Bit esta muy cerca del MCP
    "Sark": 3,     # Sark tambien esta muy cerca
    "MCP": 0       # El MCP tiene distancia 0 a si mismo
}


def busqueda_voraz_primero_mejor(grafo, inicio, objetivo):
    """
    Busqueda voraz guiada por heuristica (Greedy Best-First Search).
    
    Este algoritmo expande siempre el nodo con menor valor heuristico,
    ignorando completamente los costos reales del camino. Es eficiente
    en memoria y tiempo pero no garantiza optimalidad ni completitud.
    
    Parametros:
        grafo (dict): Red TRON representada como diccionario de adyacencia.
        inicio (str): Nodo inicial desde donde comenzar la busqueda.
        objetivo (str): Nodo objetivo que se desea alcanzar.
        
    Retorna:
        list or None: Camino desde inicio hasta objetivo si existe,
                     None si no se encuentra conexion.
    """
    # Validar que los nodos existan en el grafo y heuristica
    if inicio not in grafo or inicio not in heuristica:
        print(f"Error: El nodo inicial '{inicio}' no existe en el sistema")
        return None
    if objetivo not in grafo or objetivo not in heuristica:
        print(f"Error: El nodo objetivo '{objetivo}' no existe en el sistema")
        return None
    
    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio]

    # Frontera: cola de prioridad que almacena (valor_heuristico, camino)
    # Se utiliza heapq para mantener siempre el nodo mas prometedor al frente
    frontera = []
    heapq.heappush(frontera, (heuristica[inicio], [inicio]))
    
    # Conjunto para registrar nodos ya expandidos (evita ciclos infinitos)
    visitados = set()

    print("\nINICIANDO BUSQUEDA VORAZ EN EL SISTEMA")
    print("=" * 50)

    # Bucle principal de busqueda
    while frontera:
        # Extraer el nodo mas prometedor segun la heuristica
        valor_heuristico_actual, camino_actual = heapq.heappop(frontera)
        nodo_actual = camino_actual[-1]

        # Mostrar el progreso de la exploracion
        print(f"Tron analiza el nodo: {nodo_actual} | h(n) = {heuristica[nodo_actual]}")

        # Verificar si hemos alcanzado el objetivo
        if nodo_actual == objetivo:
            print("\nNucleo MCP localizado.")
            return camino_actual

        # Si el nodo no ha sido visitado, expandirlo
        if nodo_actual not in visitados:
            # Marcar como visitado para evitar re-expansion
            visitados.add(nodo_actual)
            
            # Explorar todos los vecinos del nodo actual
            for vecino in grafo.get(nodo_actual, set()):
                # Solo considerar vecinos no visitados
                if vecino not in visitados:
                    # Construir nuevo camino extendiendo el actual
                    nuevo_camino = list(camino_actual)
                    nuevo_camino.append(vecino)
                    
                    # Obtener valor heuristico del vecino
                    heuristica_vecino = heuristica.get(vecino, float('inf'))
                    
                    # Agregar a la frontera para futura expansion
                    heapq.heappush(frontera, (heuristica_vecino, nuevo_camino))

    # Si la frontera se vacia sin encontrar el objetivo
    return None


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con conexiones y heuristicas.
    
    Proporciona una vision general de la red y los valores heuristicos
    para entender el comportamiento del algoritmo.
    """
    print("\n" + "="*60)
    print("MAPA DEL SISTEMA TRON (Conexiones y Valores Heuristicos)")
    print("="*60)
    for nodo, conexiones in sorted(red_tron.items()):
        # Mostrar nodo con su valor heuristico y conexiones
        print(f"{nodo:10} [h={heuristica.get(nodo, 'N/A'):2}] -> {', '.join(sorted(conexiones))}")
    print("="*60)


def validar_entrada_nodo(entrada, grafo, heuristica_dict):
    """
    Valida que la entrada del usuario corresponda a un nodo existente.
    
    Parametros:
        entrada (str): Texto ingresado por el usuario.
        grafo (dict): Grafo del sistema para validar existencia.
        heuristica_dict (dict): Diccionario de heuristicas para validar.
        
    Retorna:
        bool: True si el nodo existe en ambos diccionarios, False en caso contrario.
    """
    entrada_normalizada = entrada.strip()
    # Manejar caso especial para MCP (case insensitive)
    if entrada_normalizada.upper() == "MCP":
        entrada_normalizada = "MCP"
    else:
        entrada_normalizada = entrada_normalizada.title()
    
    return entrada_normalizada in grafo and entrada_normalizada in heuristica_dict


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
    y ejecuta el algoritmo de busqueda voraz primero el mejor.
    """
    print("SISTEMA DE NAVEGACION VORAZ - RED TRON")
    print("Algoritmo Greedy Best-First Search con Heuristica Pura")
    
    # Mostrar el mapa del sistema para referencia
    mostrar_mapa_sistema()
    
    # Captura y validacion del nodo inicial
    while True:
        inicio = input("\nIngrese el programa inicial (ej. Tron): ").strip()
        if validar_entrada_nodo(inicio, red_tron, heuristica):
            # Normalizar el formato del nodo inicial
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
        objetivo = input("Ingrese el programa objetivo (ej. MCP): ").strip()
        if validar_entrada_nodo(objetivo, red_tron, heuristica):
            # Normalizar el formato del nodo objetivo
            if objetivo.upper() == "MCP":
                objetivo = "MCP"
            else:
                objetivo = objetivo.title()
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))
    
    # Ejecutar busqueda voraz primero el mejor
    ruta = busqueda_voraz_primero_mejor(red_tron, inicio, objetivo)
    
    # Mostrar resultados finales
    print("\n--- RESULTADO FINAL ---")
    if ruta:
        print("Ruta encontrada:")
        print(" -> ".join(ruta))
        print(f"Longitud del camino: {len(ruta)-1} saltos")
        print(f"Valor heuristico inicial: {heuristica[inicio]}")
        print(f"Valor heuristico final: {heuristica[objetivo]}")
        print("\nTron: 'He seguido la señal mas prometedora hacia el nodo.'")
    else:
        print("No se encontro conexion entre los programas.")
        print("MCP: 'Tu heuristica carece de eficiencia, Tron.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()