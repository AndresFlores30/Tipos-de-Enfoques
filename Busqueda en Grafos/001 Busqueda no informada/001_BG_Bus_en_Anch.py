"""
SISTEMA DE NAVEGACION TRON - BUSQUEDA DE CAMINOS

Este programa implementa un sistema de búsqueda de rutas en el mundo digital de TRON
utilizando el algoritmo de Búsqueda en Anchura (BFS) para encontrar el camino más corto
entre diferentes programas y sectores del sistema.
"""

# Grafo del sistema digital de TRON
# Cada nodo representa un sector o programa dentro del mundo de TRON
# Las conexiones representan enlaces de comunicación o rutas de acceso
sistema_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],
    "Clu": ["Tron", "Sark"],
    "Flynn": ["Tron", "Yori", "Sark"],
    "Yori": ["Tron", "Flynn", "Grid Sector 7"],
    "Sark": ["Clu", "Flynn", "Mcp"],
    "Grid Sector 7": ["Yori", "Bit"],
    "Bit": ["Grid Sector 7", "Mcp"],
    "Mcp": ["Sark", "Bit"]
}

def buscar_camino_bfs(grafo, inicio, objetivo):
    """
    Realiza una búsqueda en anchura (BFS) en el sistema TRON.
    Encuentra el camino más corto entre dos programas o sectores.

    BFS garantiza encontrar el camino más corto en un grafo no ponderado
    explorando todos los vecinos en el nivel actual antes de pasar al siguiente.

    Parámetros:
        grafo (dict): Representación del sistema TRON como diccionario de adyacencia
        inicio (str): Programa o sector de inicio de la búsqueda
        objetivo (str): Programa o sector destino de la búsqueda

    Retorna:
        list or None: Lista con el camino más corto si existe, None si no hay camino
    """
    # Verificar que los nodos de inicio y objetivo existan en el grafo
    if inicio not in grafo:
        print(f"Error: El nodo '{inicio}' no existe en el sistema TRON")
        return None
    if objetivo not in grafo:
        print(f"Error: El nodo '{objetivo}' no existe en el sistema TRON")
        return None
    
    # Caso especial: si inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio]
    
    # Cola para almacenar los caminos a explorar
    # Cada elemento de la cola es una lista que representa un camino posible
    cola = [[inicio]]
    
    # Conjunto para mantener registro de nodos ya visitados
    # Esto evita ciclos infinitos y procesamiento redundante
    visitados = set([inicio])

    while cola:
        # Extraer el primer camino de la cola (FIFO - First In First Out)
        camino_actual = cola.pop(0)
        nodo_actual = camino_actual[-1]

        # Si llegamos al nodo objetivo, retornar el camino encontrado
        if nodo_actual == objetivo:
            return camino_actual

        # Explorar todos los vecinos del nodo actual
        for vecino in grafo.get(nodo_actual, []):
            # Solo procesar vecinos no visitados
            if vecino not in visitados:
                visitados.add(vecino)  # Marcar como visitado
                
                # Crear nuevo camino extendiendo el camino actual con el vecino
                nuevo_camino = list(camino_actual)  # Copiar el camino actual
                nuevo_camino.append(vecino)         # Añadir el vecino
                cola.append(nuevo_camino)           # Añadir a la cola para explorar

    # Si la cola se vacía sin encontrar el objetivo, no existe camino
    return None

def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON para referencia del usuario.
    """
    print("\n--- MAPA DEL SISTEMA TRON ---")
    for nodo, vecinos in sistema_tron.items():
        print(f"{nodo}: conectado con {', '.join(vecinos)}")
    print("-----------------------------")

def validar_entrada_usuario(entrada, grafo):
    """
    Valida que la entrada del usuario exista en el sistema TRON.

    Parámetros:
        entrada (str): Texto ingresado por el usuario
        grafo (dict): Grafo del sistema para validar existencia

    Retorna:
        bool: True si la entrada es válida, False en caso contrario
    """
    entrada_normalizada = entrada.strip().title()
    return entrada_normalizada in grafo

# PROGRAMA PRINCIPAL
def main():
    """
    Función principal que coordina la interacción con el usuario
    y la ejecución del algoritmo de búsqueda.
    """
    print("BIENVENIDO AL SISTEMA DIGITAL DE TRON")
    print("Encuentra la ruta más corta entre programas dentro de la red.\n")
    
    # Mostrar mapa del sistema para ayudar al usuario
    mostrar_mapa_sistema()
    
    # Solicitar nodo de inicio con validación
    while True:
        inicio = input("\nIngrese el programa de inicio: ").strip().title()
        if validar_entrada_usuario(inicio, sistema_tron):
            break
        else:
            print(f"Error: '{inicio}' no existe en el sistema. Por favor ingrese un nodo válido.")
            print("Nodos disponibles:", ", ".join(sistema_tron.keys()))
    
    # Solicitar nodo objetivo con validación
    while True:
        objetivo = input("Ingrese el programa de destino: ").strip().title()
        if validar_entrada_usuario(objetivo, sistema_tron):
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema. Por favor ingrese un nodo válido.")
            print("Nodos disponibles:", ", ".join(sistema_tron.keys()))
    
    # Ejecutar búsqueda del camino más corto
    print(f"\nBuscando ruta entre {inicio} y {objetivo}...")
    camino = buscar_camino_bfs(sistema_tron, inicio, objetivo)
    
    # Mostrar resultados de la búsqueda
    print("\n--- RESULTADO DE LA BÚSQUEDA ---")
    if camino:
        print(f"Ruta encontrada entre {inicio} y {objetivo}:")
        print(" -> ".join(camino))
        print(f"Longitud del camino: {len(camino)-1} saltos")
        print("\nTron dice: '¡El camino más eficiente ha sido encontrado!'")
    else:
        print(f"No existe conexión entre {inicio} y {objetivo}.")
        print("El MCP bloquea el acceso al sector.")

# Punto de entrada del programa
if __name__ == "__main__":
    main()