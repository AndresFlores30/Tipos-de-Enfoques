# Descripción: Simula cómo un programa recorre los niveles más profundos
# del sistema digital de TRON buscando una conexión entre programas.

# Cada nodo es un programa o sector dentro del sistema
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


def dfs(grafo, inicio, objetivo, visitados=None, camino=None):
    """
    Realiza una búsqueda en profundidad (DFS) dentro del sistema TRON.
    
    Parámetros:
        grafo (dict): Estructura de conexiones de la red TRON.
        inicio (str): Nodo de partida.
        objetivo (str): Nodo que se desea encontrar.
        visitados (set): Nodos ya explorados.
        camino (list): Camino actual recorrido.

    Retorna:
        list: Camino completo si se encuentra el objetivo, o None.
    """
    if visitados is None:
        visitados = set()
    if camino is None:
        camino = []

    # Marcar nodo actual como visitado
    visitados.add(inicio)
    camino.append(inicio)

    # Si encontramos el objetivo, retornamos el camino
    if inicio == objetivo:
        return camino

    # Explorar los vecinos no visitados
    for vecino in grafo.get(inicio, []):
        if vecino not in visitados:
            resultado = dfs(grafo, vecino, objetivo, visitados, list(camino))
            if resultado:
                return resultado

    # Si no se encuentra el objetivo, retornar None
    return None


# PROGRAMA PRINCIPAL
print("SISTEMA DIGITAL TRON ONLINE")
print("Búsqueda profunda entre programas dentro de la red...\n")

inicio = input("Ingrese el programa de inicio: ").title()
objetivo = input("Ingrese el programa destino: ").title()

resultado = dfs(sistema_tron, inicio, objetivo)

print("\n--- RESULTADOS DE LA RED ---")
if resultado:
    print(f"Ruta encontrada entre {inicio} y {objetivo}:")
    print(" -> ".join(resultado))
    print("\n Tron: 'El programa ha descendido a las capas más profundas del sistema.'")
else:
    print("No se encontró conexión entre los programas.")
    print("MCP: 'Tu búsqueda ha fallado, usuario.'")