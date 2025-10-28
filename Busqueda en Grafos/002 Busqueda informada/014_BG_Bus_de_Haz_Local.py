"""
SISTEMA DE BUSQUEDA DE HAZ LOCAL - TRON DIGITAL

Este modulo implementa el algoritmo de Busqueda de Haz Local (Local Beam Search)
que mantiene k estados o caminos simultaneos en cada iteracion. A diferencia de
la busqueda en anchura que explora nivel por nivel, el haz local selecciona
los k mejores caminos basados en una funcion heuristica.

El algoritmo es particularmente util cuando se necesita explorar multiples
rutas prometedoras simultaneamente sin el costo computacional completo de BFS.
"""

import time

# --- RED DIGITAL (nombres originales) ---
# Diccionario que representa las conexiones entre programas en el sistema
# Cada nodo tiene una lista de nodos vecinos accesibles directamente
red_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],    # Tron tiene multiples opciones iniciales
    "Clu": ["Sark", "Sector5"],          # Clu conduce a dos rutas diferentes
    "Flynn": ["Sector7", "Yori"],        # Flynn tiene conexiones reciprocas
    "Yori": ["Bit", "Sark"],             # Yori conecta con Bit y Sark
    "Sark": ["MCP"],                     # Sark tiene acceso directo al MCP
    "Sector5": ["MCP"],                  # Sector5 tambien conduce al MCP
    "Sector7": ["Bit"],                  # Sector7 conecta con Bit
    "Bit": ["MCP"],                      # Bit tiene acceso al MCP
    "MCP": []                            # MCP es el objetivo final
}

# --- HEURISTICA (valores por nombre original) ---
# La heuristica representa la estimacion de dificultad para alcanzar el MCP
# Valores mas bajos indican mayor proximidad al objetivo
energia = {
    "Tron": 9,       # Tron esta lejos del MCP
    "Clu": 7,        # Clu esta mas cerca que Tron
    "Flynn": 8,      # Flynn tiene posicion intermedia
    "Yori": 6,       # Yori esta relativamente cerca
    "Sark": 3,       # Sark esta muy cerca del MCP
    "Sector5": 4,    # Sector5 tiene buena proximidad
    "Sector7": 5,    # Sector7 esta a media distancia
    "Bit": 2,        # Bit esta muy cerca del MCP
    "MCP": 0         # El MCP tiene energia 0
}


def construir_grafo_normalizado(red, mapa_energia):
    """
    Construye versiones normalizadas (minusculas) del grafo y heuristicas
    para permitir entradas case-insensitive del usuario.
    
    Parametros:
        red (dict): Grafo original con nombres en formato estandar
        mapa_energia (dict): Valores heuristicos originales
        
    Retorna:
        tuple: (grafo_norm, energia_norm, mapa_nombres) donde:
            - grafo_norm: Grafo con claves y vecinos en minusculas
            - energia_norm: Heuristicas con claves en minusculas
            - mapa_nombres: Diccionario que mapea clave_minuscula -> nombre_original
    """
    mapa_nombres = {}
    
    # Recopilar todos los nodos del sistema (tanto claves como vecinos)
    todos_nodos = set(red.keys())
    for vecinos in red.values():
        todos_nodos.update(vecinos)

    # Construir mapeo de nombres normalizados
    for nodo in todos_nodos:
        clave_normalizada = nodo.strip().lower()
        mapa_nombres[clave_normalizada] = nodo

    # Construir grafo normalizado
    grafo_norm = {clave: [] for clave in mapa_nombres.keys()}
    for origen, vecinos in red.items():
        clave_origen = origen.strip().lower()
        for vecino in vecinos:
            clave_vecino = vecino.strip().lower()
            grafo_norm[clave_origen].append(clave_vecino)

    # Construir heuristicas normalizadas
    energia_norm = {}
    for origen, valor in mapa_energia.items():
        clave_normalizada = origen.strip().lower()
        energia_norm[clave_normalizada] = valor

    return grafo_norm, energia_norm, mapa_nombres


# Construir version normalizada del sistema
grafo_norm, energia_norm, mapa_nombres = construir_grafo_normalizado(red_tron, energia)


def busqueda_haz_local(inicio_sin_procesar, objetivo_sin_procesar, k=3, max_iteraciones=10):
    """
    Implementacion del algoritmo de Busqueda de Haz Local.
    
    Mantiene k caminos simultaneos (haces) que se expanden en paralelo.
    En cada iteracion, selecciona los k mejores caminos basados en la
    heuristica del nodo final de cada camino.
    
    Parametros:
        inicio_sin_procesar (str): Nodo inicial (acepta cualquier capitalizacion)
        objetivo_sin_procesar (str): Nodo objetivo (acepta cualquier capitalizacion)
        k (int): Numero de haces (caminos paralelos) a mantener
        max_iteraciones (int): Numero maximo de iteraciones permitidas
        
    Retorna:
        list or None: Camino encontrado (en nombres originales) o None si no se encuentra
    """
    # Normalizar entradas del usuario
    inicio = inicio_sin_procesar.strip().lower()
    objetivo = objetivo_sin_procesar.strip().lower()

    # Validaciones de existencia de nodos
    if inicio not in grafo_norm:
        print(f"Error: Nodo de inicio '{inicio_sin_procesar}' no existe en la red.")
        return None
    if objetivo not in grafo_norm:
        print(f"Error: Nodo objetivo '{objetivo_sin_procesar}' no existe en la red.")
        return None

    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [mapa_nombres[inicio]]

    # Inicializar k haces (todos comienzan en el nodo inicial)
    haces = [[inicio] for _ in range(k)]
    
    print("INICIO DE LA BUSQUEDA DE HAZ LOCAL")
    print(f"Lanzando {k} haces desde '{mapa_nombres[inicio]}' buscando '{mapa_nombres[objetivo]}'")
    print(f"Energia inicial: {energia_norm.get(inicio, 'N/A')}")
    print("=" * 60)

    # Bucle principal de busqueda
    for iteracion in range(max_iteraciones):
        print(f"\n--- Iteracion {iteracion + 1} ---")
        nuevos_haces = []

        # Expandir cada haz actual
        for camino in haces:
            nodo_actual = camino[-1]
            energia_actual = energia_norm.get(nodo_actual, float('inf'))
            
            print(f"Haz actual: {[mapa_nombres[n] for n in camino]} | Energia: {energia_actual}")

            # CASO DE EXITO: Objetivo alcanzado
            if nodo_actual == objetivo:
                print("\nEXITO: Objetivo alcanzado por uno de los haces.")
                camino_original = [mapa_nombres[nodo] for nodo in camino]
                return camino_original

            # EXPANSION: Generar nuevos caminos desde los vecinos
            vecinos = grafo_norm.get(nodo_actual, [])
            for vecino in vecinos:
                nuevo_camino = list(camino)  # Copiar camino actual
                nuevo_camino.append(vecino)  # Agregar vecino
                nuevos_haces.append(nuevo_camino)

        # CASO DE BLOQUEO: No hay nuevos caminos disponibles
        if not nuevos_haces:
            print("BLOQUEO: No hay mas rutas disponibles. Busqueda detenida.")
            return None

        # SELECCION: Ordenar todos los nuevos caminos por energia del ultimo nodo
        # (menor energia = mejor, mas cerca del MCP)
        nuevos_haces.sort(key=lambda camino: energia_norm.get(camino[-1], float('inf')))

        # PODA: Conservar solo los k mejores haces
        haces = nuevos_haces[:k]

        print(f"Se conservan los {k} mejores haces:")
        for i, haz in enumerate(haces):
            energia_final = energia_norm.get(haz[-1], float('inf'))
            nombres_haz = [mapa_nombres[nodo] for nodo in haz]
            print(f"  Haz {i+1}: {nombres_haz} (Energia final: {energia_final})")

        # Pausa para visualizacion
        time.sleep(0.3)

    # Terminacion por limite de iteraciones
    print(f"\nTERMINACION: No se alcanzo el objetivo en {max_iteraciones} iteraciones.")
    
    # Retornar el mejor camino encontrado (primero de los haces actuales)
    if haces:
        mejor_camino = [mapa_nombres[nodo] for nodo in haces[0]]
        print(f"Mejor camino encontrado: {mejor_camino}")
        return mejor_camino
    
    return None


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con conexiones y energias.
    
    Proporciona una vision general de la topologia y los valores de energia
    para entender el comportamiento del algoritmo.
    """
    print("\n" + "="*70)
    print("MAPA DEL SISTEMA TRON (Busqueda de Haz Local)")
    print("="*70)
    print("Energia: menor valor = mas cerca del MCP")
    print("-" * 70)
    for nodo, vecinos in sorted(red_tron.items()):
        if vecinos:
            vecinos_info = [f"{v}(e:{energia[v]})" for v in vecinos]
            print(f"{nodo:10} [e={energia[nodo]:2}] -> {', '.join(vecinos_info)}")
        else:
            print(f"{nodo:10} [e={energia[nodo]:2}] -> NODO TERMINAL")
    print("="*70)


def obtener_nodos_disponibles():
    """
    Retorna una lista de todos los nodos disponibles en el sistema.
    
    Retorna:
        list: Lista ordenada de nodos disponibles (nombres originales).
    """
    return sorted(red_tron.keys())


# PROGRAMA PRINCIPAL
def main():
    """
    Funcion principal que coordina la interaccion con el usuario
    y ejecuta el algoritmo de busqueda de haz local.
    """
    print("SISTEMA DE BUSQUEDA DE HAZ LOCAL - UNIVERSO TRON")
    print("Algoritmo Local Beam Search - Exploracion Paralela")
    
    # Mostrar el mapa del sistema para referencia
    mostrar_mapa_sistema()
    
    # Captura de nodo inicial (case-insensitive)
    while True:
        inicio_input = input("\nIngrese el nodo inicial: ").strip()
        if not inicio_input:
            print("Error: Debe ingresar un nodo inicial")
            continue
            
        inicio_normalizado = inicio_input.lower()
        if inicio_normalizado in grafo_norm:
            break
        else:
            print(f"Error: '{inicio_input}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))

    # Captura de nodo objetivo (case-insensitive)
    while True:
        objetivo_input = input("Ingrese el nodo objetivo: ").strip()
        if not objetivo_input:
            print("Error: Debe ingresar un nodo objetivo")
            continue
            
        objetivo_normalizado = objetivo_input.lower()
        if objetivo_normalizado in grafo_norm:
            break
        else:
            print(f"Error: '{objetivo_input}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))

    # Parametros configurables del algoritmo
    try:
        k_haces = int(input("Numero de haces paralelos (default 3): ") or "3")
        max_iter = int(input("Iteraciones maximas (default 10): ") or "10")
    except ValueError:
        print("Usando valores por defecto: k=3, iteraciones=10")
        k_haces = 3
        max_iter = 10

    # Ejecutar algoritmo de busqueda de haz local
    resultado = busqueda_haz_local(inicio_input, objetivo_input, k=k_haces, max_iteraciones=max_iter)

    # Mostrar resultados finales
    print("\n" + "="*50)
    print("RESULTADO FINAL DE LA BUSQUEDA DE HAZ LOCAL")
    print("="*50)
    
    if resultado:
        print(f"Ruta encontrada: {' -> '.join(resultado)}")
        print(f"Nodo final: {resultado[-1]}")
        print(f"Longitud del camino: {len(resultado)} nodos")
        print(f"Energia final: {energia.get(resultado[-1], 'N/A')}")
        
        if resultado[-1] == mapa_nombres[objetivo_input.lower()]:
            print("\nEXITO: El algoritmo alcanzo el objetivo")
            print("Tron: 'Los multiples haces encontraron eficientemente el MCP'")
        else:
            print(f"\MEJOR SOLUCION: El algoritmo encontro un camino hacia {resultado[-1]}")
            print("Tron: 'La exploracion paralela encontro una buena ruta'")
    else:
        print("No se encontro una ruta hacia el objetivo.")
        print("MCP: 'Tu estrategia de haz local ha fallado, Tron.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()