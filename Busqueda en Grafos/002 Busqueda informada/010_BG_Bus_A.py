"""
SISTEMA DE BUSQUEDA A* (A ESTRELLA) - TRON DIGITAL

Este modulo implementa el algoritmo de busqueda A* que combina el costo real
del camino recorrido (g(n)) con una estimacion heuristica del costo restante
(h(n)) para encontrar la ruta optima hacia el objetivo MCP.

A* es completo y optimo cuando la heuristica es admisible (no sobreestima
el costo real) y consistente.
"""

import heapq

# --- RED DIGITAL DE TRON ---
# Diccionario que representa las conexiones con costos de energia
# Estructura: {nodo: {vecino: costo_energia, ...}}
red_tron = {
    "Tron": {"Clu": 3, "Flynn": 2},           # Tron con conexiones a diferentes costos
    "Clu": {"Sark": 4, "Tron": 3},            # Conexiones bidireccionales con costos
    "Flynn": {"Tron": 2, "Yori": 3, "Sector7": 6},  # Flynn con multiples rutas
    "Yori": {"Flynn": 3, "Sector7": 5, "Bit": 2},   # Yori como nodo intermedio clave
    "Sector7": {"Yori": 5, "Bit": 2},         # Sector periferico
    "Bit": {"Sector7": 2, "MCP": 4},          # Bit con acceso directo al MCP
    "Sark": {"Clu": 4, "MCP": 6},             # Sark con ruta alternativa al MCP
    "MCP": {}                                 # MCP como objetivo final
}

# --- FUNCION HEURISTICA (estimacion de distancia hacia MCP) ---
# La heuristica debe ser admisible (no sobreestimar el costo real)
# y preferiblemente consistente para garantizar optimalidad
heuristica = {
    "Tron": 10,    # Estimacion del costo minimo desde Tron al MCP
    "Clu": 8,      # Clu esta mas cerca del MCP que Tron
    "Flynn": 7,    # Posicion intermedia en el sistema
    "Yori": 5,     # Relativamente cerca del MCP
    "Sector7": 4,  # Buena proximidad al MCP
    "Bit": 2,      # Muy cerca del MCP
    "Sark": 3,     # Cercano al MCP por ruta directa
    "MCP": 0       # El MCP tiene costo 0 a si mismo
}


def busqueda_a_estrella(grafo, inicio, objetivo):
    """
    Implementacion del algoritmo de busqueda A* (A Estrella).
    
    A* utiliza la funcion de evaluacion f(n) = g(n) + h(n), donde:
    - g(n): costo real desde el inicio hasta el nodo n
    - h(n): estimacion heuristica desde el nodo n hasta el objetivo
    
    El algoritmo es completo y optimo cuando la heuristica es admisible
    y el grafo es finito.

    Parametros:
        grafo (dict): Red TRON con costos de energia entre conexiones.
        inicio (str): Nodo inicial desde donde comenzar la busqueda.
        objetivo (str): Nodo objetivo que se desea alcanzar.
        
    Retorna:
        tuple: (camino, costo_total) donde:
            - camino: lista de nodos del camino optimo encontrado
            - costo_total: suma de costos de energia del camino
        Retorna (None, infinito) si no se encuentra camino.
    """
    # Validar que los nodos existan en el grafo y heuristica
    if inicio not in grafo or inicio not in heuristica:
        print(f"Error: El nodo inicial '{inicio}' no existe en el sistema")
        return None, float("inf")
    if objetivo not in grafo or objetivo not in heuristica:
        print(f"Error: El nodo objetivo '{objetivo}' no existe en el sistema")
        return None, float("inf")
    
    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio], 0

    # Frontera: cola de prioridad que almacena (f(n), g(n), camino)
    # donde f(n) = g(n) + h(n) es la funcion de evaluacion de A*
    frontera = []
    
    # Inicializar con el nodo inicial: f(inicio) = g(inicio) + h(inicio) = 0 + h(inicio)
    heapq.heappush(frontera, (0 + heuristica[inicio], 0, [inicio]))
    
    # Diccionario para registrar el mejor costo conocido hasta cada nodo
    # Esto permite podar caminos suboptimos que llegan a nodos ya visitados
    mejores_costos = {}

    print("\nINICIANDO BUSQUEDA A* EN EL SISTEMA")
    print("=" * 60)
    print("f(n) = g(n) + h(n) | g: costo real | h: heuristica")
    print("=" * 60)

    # Bucle principal de busqueda
    while frontera:
        # Extraer el nodo con menor valor f(n) de la frontera
        f_actual, g_actual, camino_actual = heapq.heappop(frontera)
        nodo_actual = camino_actual[-1]

        # Mostrar informacion del nodo actual en expansion
        h_actual = heuristica[nodo_actual]
        print(f"Nodo actual: {nodo_actual:8} | g={g_actual:2} | h={h_actual:2} | f={f_actual:2}")

        # Verificar si hemos alcanzado el objetivo
        if nodo_actual == objetivo:
            print("\nNucleo MCP alcanzado.")
            return camino_actual, g_actual

        # Si ya visitamos este nodo con un costo igual o menor, ignorar esta expansion
        # Esto evita procesar caminos suboptimos que llegan a nodos ya explorados
        if nodo_actual in mejores_costos and mejores_costos[nodo_actual] <= g_actual:
            continue

        # Registrar el mejor costo conocido para este nodo
        mejores_costos[nodo_actual] = g_actual

        # Expandir el nodo actual: explorar todos sus vecinos
        for vecino, costo_arista in grafo.get(nodo_actual, {}).items():
            # Calcular nuevo costo real g(n) para el vecino
            nuevo_g = g_actual + costo_arista
            
            # Calcular nueva funcion de evaluacion f(n) = g(n) + h(n)
            nuevo_f = nuevo_g + heuristica.get(vecino, float('inf'))
            
            # Construir nuevo camino extendiendo el actual
            nuevo_camino = list(camino_actual)
            nuevo_camino.append(vecino)
            
            # Agregar a la frontera para futura expansion
            heapq.heappush(frontera, (nuevo_f, nuevo_g, nuevo_camino))

    # Si la frontera se vacia sin encontrar el objetivo
    return None, float("inf")


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con costos y heuristicas.
    
    Proporciona una vision detallada de la red para entender las
    decisiones del algoritmo A*.
    """
    print("\n" + "="*70)
    print("MAPA DEL SISTEMA TRON (Conexiones, Costos y Heuristicas)")
    print("="*70)
    for nodo, conexiones in sorted(red_tron.items()):
        if conexiones:
            conexiones_str = [f"{destino}(c:{costo})" for destino, costo in conexiones.items()]
            print(f"{nodo:10} [h={heuristica.get(nodo, 'N/A'):2}] -> {', '.join(conexiones_str)}")
        else:
            print(f"{nodo:10} [h={heuristica.get(nodo, 'N/A'):2}] -> SIN CONEXIONES SALIENTES")
    print("="*70)


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
    y ejecuta el algoritmo de busqueda A*.
    """
    print("SISTEMA DE BUSQUEDA A* - RED TRON")
    print("Algoritmo A* (A Estrella) - Busqueda Optima Informada")
    
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
    
    # Ejecutar busqueda A*
    ruta, costo_total = busqueda_a_estrella(red_tron, inicio, objetivo)
    
    # Mostrar resultados finales
    print("\n--- RESULTADO FINAL ---")
    if ruta:
        print("Ruta optima encontrada:")
        print(" -> ".join(ruta))
        print(f"Costo total de energia: {costo_total} unidades")
        print(f"Longitud del camino: {len(ruta)-1} saltos")
        print(f"Eficiencia promedio: {costo_total/(len(ruta)-1) if len(ruta)>1 else 0:.2f} unidades/salto")
        
        # Analisis de optimalidad
        print("\nTron: 'He encontrado la ruta optima a traves del sistema.'")
        print("      Algoritmo A* garantiza el camino de menor costo")
        print("      con heuristica admisible y consistente.")
    else:
        print("No se pudo establecer conexion con el MCP.")
        print("MCP: 'El sistema ha rechazado tu intrusion, Tron.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()