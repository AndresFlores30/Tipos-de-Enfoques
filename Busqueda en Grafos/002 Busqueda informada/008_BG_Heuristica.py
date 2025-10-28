"""
SISTEMA DE BUSQUEDA GREEDY CON HEURISTICA Y COSTOS - TRON DIGITAL

Este modulo implementa el algoritmo de Busqueda Greedy que utiliza una
funcion heuristica para guiar la exploracion hacia el objetivo MCP.
El algoritmo selecciona siempre el nodo mas prometedor segun la heuristica
y calcula el costo total de energia consumida en la ruta.
"""

import heapq

# --- RED DIGITAL (GRAFO CON COSTOS DE ENERGIA) ---
# Diccionario que representa la red TRON con costos de transmision energetica
# Estructura: {nodo: {vecino: costo_energia, ...}}
red_tron = {
    "Tron": {"Clu": 3, "Flynn": 2},       # Tron conectado con costos diferentes
    "Clu": {"Sark": 4, "Tron": 3},        # Conexiones bidireccionales con costos
    "Flynn": {"Tron": 2, "Yori": 3},      # Flynn con acceso a Yori
    "Yori": {"Flynn": 3, "Sector7": 5},   # Yori conectado al Sector7 con alto costo
    "Sector7": {"Yori": 5, "Bit": 2},     # Sector7 con conexion economica a Bit
    "Sark": {"Clu": 4, "MCP": 6},         # Sark tiene acceso directo al MCP
    "Bit": {"Sector7": 2, "MCP": 4},      # Bit con conexion eficiente al MCP
    "MCP": {}                             # MCP es el objetivo final
}

# --- FUNCION HEURISTICA ---
# Estima la distancia digital restante desde cada nodo hasta el MCP
# Valores mas bajos indican mayor proximidad estimada al objetivo
heuristica = {
    "Tron": 8,      # Estimacion de distancia desde Tron al MCP
    "Clu": 6,       # Clu esta mas cerca del MCP que Tron
    "Flynn": 7,     # Flynn tiene distancia media estimada
    "Yori": 5,      # Yori esta relativamente cerca del MCP
    "Sector7": 4,   # Sector7 tiene buena proximidad estimada
    "Bit": 2,       # Bit esta muy cerca del MCP
    "Sark": 3,      # Sark tiene acceso directo al MCP
    "MCP": 0        # El MCP tiene distancia 0 a si mismo
}


def busqueda_greedy_con_costos(grafo, inicio, objetivo):
    """
    Busqueda Greedy con heuristica y costo acumulado.
    
    Este algoritmo selecciona siempre el nodo con mejor valor heuristico
    (mas prometedor) para expandir, sin considerar costos acumulados.
    Es eficiente pero no garantiza optimalidad.
    
    Parametros:
        grafo (dict): Red TRON con costos de energia entre conexiones.
        inicio (str): Nodo inicial desde donde comenzar la busqueda.
        objetivo (str): Nodo objetivo que se desea alcanzar.
        
    Retorna:
        tuple: (camino, costo_total) donde:
            - camino: lista de nodos del camino encontrado
            - costo_total: suma de costos de energia del camino
        Retorna (None, None) si no se encuentra camino.
    """
    # Validar que los nodos existan en el grafo y heuristica
    if inicio not in grafo or inicio not in heuristica:
        print(f"Error: El nodo inicial '{inicio}' no existe en el sistema")
        return None, None
    if objetivo not in grafo or objetivo not in heuristica:
        print(f"Error: El nodo objetivo '{objetivo}' no existe en el sistema")
        return None, None
    
    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio], 0

    # Frontera: cola de prioridad que almacena (valor_heuristico, camino, costo_acumulado)
    # Se utiliza heapq para mantener siempre el nodo mas prometedor al frente
    frontera = []
    heapq.heappush(frontera, (heuristica[inicio], [inicio], 0))
    
    # Conjunto para registrar nodos ya expandidos (evita ciclos)
    visitados = set()

    print("\nINICIANDO BUSQUEDA INFORMADA EN EL SISTEMA")
    print("=" * 50)

    while frontera:
        # Extraer el nodo mas prometedor segun la heuristica
        valor_heuristico, camino, costo_acumulado = heapq.heappop(frontera)
        nodo_actual = camino[-1]

        # Mostrar progreso de la exploracion
        print(f"Tron analiza el nodo: {nodo_actual} | Heuristica: {valor_heuristico} | Costo acumulado: {costo_acumulado}")

        # Verificar si hemos alcanzado el objetivo
        if nodo_actual == objetivo:
            print("\nNucleo MCP localizado.")
            return camino, costo_acumulado

        # Si el nodo no ha sido visitado, expandirlo
        if nodo_actual not in visitados:
            visitados.add(nodo_actual)
            
            # Explorar todos los vecinos del nodo actual
            for vecino, costo_arista in grafo.get(nodo_actual, {}).items():
                if vecino not in visitados:
                    # Construir nuevo camino extendiendo el actual
                    nuevo_camino = list(camino)
                    nuevo_camino.append(vecino)
                    
                    # Calcular nuevo costo acumulado
                    nuevo_costo = costo_acumulado + costo_arista
                    
                    # Obtener valor heuristico del vecino
                    heuristica_vecino = heuristica.get(vecino, float('inf'))
                    
                    # Agregar a la frontera para futura expansion
                    heapq.heappush(frontera, (heuristica_vecino, nuevo_camino, nuevo_costo))

    # Si la frontera se vacia sin encontrar el objetivo
    return None, None


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con costos y heuristicas.
    
    Proporciona una vision completa de la red para entender las
    decisiones del algoritmo greedy.
    """
    print("\n" + "="*60)
    print("MAPA DEL SISTEMA TRON (Conexiones y Heuristicas)")
    print("="*60)
    for nodo, conexiones in red_tron.items():
        conexiones_str = [f"{destino}(costo:{costo})" for destino, costo in conexiones.items()]
        print(f"{nodo:10} [h={heuristica.get(nodo, 'N/A'):2}] -> {', '.join(conexiones_str)}")
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
    # Para el objetivo, permitir tanto title case como uppercase
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
    y ejecuta el algoritmo de busqueda greedy con heuristicas.
    """
    print("SISTEMA CENTRAL DE BUSQUEDA - RED TRON")
    print("Algoritmo Greedy con Heuristica y Control de Costos")
    
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
    
    # Ejecutar busqueda greedy con costos
    ruta, costo_total = busqueda_greedy_con_costos(red_tron, inicio, objetivo)
    
    # Mostrar resultados finales
    print("\n--- RESULTADO FINAL ---")
    if ruta:
        print("Ruta encontrada:")
        print(" -> ".join(ruta))
        print(f"Costo total de energia: {costo_total} unidades.")
        print(f"Longitud del camino: {len(ruta)-1} saltos")
        print(f"Eficiencia energetica: {costo_total/(len(ruta)-1) if len(ruta)>1 else 0:.2f} unidades/salto")
        print("\nTron: 'He seguido la ruta mas prometedora segun el analisis heuristico.'")
    else:
        print("No se encontro una conexion entre los programas.")
        print("MCP: 'Tu logica sigue siendo ineficiente, Tron.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()