# Descripción: Simula cómo un programa recorre los niveles más profundos
# del sistema digital de TRON buscando una conexión entre programas.

# Cada nodo es un programa o sector dentro del sistema
# Estructura: {nodo: [vecino1, vecino2, ...]}
sistema_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],
    "Clu": ["Sark", "Tron"],
    "Flynn": ["Tron", "Yori", "Sark"],
    "Yori": ["Flynn", "Sector7"],
    "Sark": ["Clu", "Flynn", "Mcp"],
    "Sector7": ["Yori", "Bit"],
    "Bit": ["Sector7", "Mcp"],
    "Mcp": ["Sark", "Bit"]
}


def busqueda_profundidad(grafo, inicio, objetivo, visitados=None, camino=None):
    """
    Realiza una búsqueda en profundidad (DFS) dentro del sistema TRON.
    
    DFS explora recursivamente cada rama del grafo hasta encontrar el objetivo
    o agotar todas las posibilidades en esa dirección.

    Parámetros:
        grafo (dict): Estructura de conexiones de la red TRON como diccionario de adyacencia.
        inicio (str): Nodo de partida de la búsqueda.
        objetivo (str): Nodo que se desea encontrar.
        visitados (set): Conjunto de nodos ya explorados (para recursión).
        camino (list): Camino actual recorrido (para recursión).

    Retorna:
        list or None: Camino completo si se encuentra el objetivo, None en caso contrario.
    """
    # Inicializar estructuras en la primera llamada (no recursiva)
    if visitados is None:
        visitados = set()
    if camino is None:
        camino = []

    # Verificar que los nodos existan en el grafo
    if inicio not in grafo:
        print(f"Error: El nodo '{inicio}' no existe en el sistema TRON")
        return None
    if objetivo not in grafo:
        print(f"Error: El nodo '{objetivo}' no existe en el sistema TRON")
        return None
    
    # Caso base: si inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio]

    # Marcar nodo actual como visitado para evitar ciclos
    visitados.add(inicio)
    
    # Agregar nodo actual al camino
    camino.append(inicio)

    # Explorar recursivamente todos los vecinos no visitados
    for vecino in grafo.get(inicio, []):
        if vecino not in visitados:
            # Llamada recursiva con nuevo estado
            resultado = busqueda_profundidad(grafo, vecino, objetivo, visitados, list(camino))
            
            # Si se encontró el objetivo en la rama actual, propagar el resultado
            if resultado is not None:
                return resultado

    # Si ninguna rama llevó al objetivo, retornar None
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
        entrada (str): Texto ingresado por el usuario.
        grafo (dict): Grafo del sistema para validar existencia.

    Retorna:
        bool: True si la entrada es válida, False en caso contrario.
    """
    entrada_normalizada = entrada.strip().title()
    return entrada_normalizada in grafo


# PROGRAMA PRINCIPAL
def main():
    """
    Función principal que coordina la interacción con el usuario
    y la ejecución del algoritmo de búsqueda en profundidad.
    """
    print("SISTEMA DIGITAL TRON ONLINE")
    print("Búsqueda profunda entre programas dentro de la red...\n")
    
    # Mostrar mapa del sistema para ayudar al usuario
    mostrar_mapa_sistema()
    
    # Solicitar nodo de inicio con validación
    while True:
        inicio = input("\nIngrese el programa de inicio: ").strip().title()
        if validar_entrada_usuario(inicio, sistema_tron):
            break
        else:
            print(f"Error: '{inicio}' no existe en el sistema.")
            print("Nodos disponibles:", ", ".join(sistema_tron.keys()))
    
    # Solicitar nodo objetivo con validación
    while True:
        objetivo = input("Ingrese el programa destino: ").strip().title()
        if validar_entrada_usuario(objetivo, sistema_tron):
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema.")
            print("Nodos disponibles:", ", ".join(sistema_tron.keys()))
    
    # Ejecutar búsqueda en profundidad
    print(f"\nExplorando rutas profundas entre {inicio} y {objetivo}...")
    resultado = busqueda_profundidad(sistema_tron, inicio, objetivo)
    
    # Mostrar resultados de la búsqueda
    print("\n--- RESULTADOS DE LA RED ---")
    if resultado:
        print(f"Ruta encontrada entre {inicio} y {objetivo}:")
        print(" -> ".join(resultado))
        print(f"Longitud del camino: {len(resultado)-1} saltos")
        print("\nTron: 'El programa ha descendido a las capas más profundas del sistema.'")
    else:
        print("No se encontró conexión entre los programas.")
        print("MCP: 'Tu búsqueda ha fallado, usuario.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()