# Grafo del sistema digital
# Cada nodo representa un sector o programa dentro del mundo de TRON
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

    Parámetros:
        grafo (dict): Representación del sistema TRON.
        inicio (str): Programa o sector de inicio.
        objetivo (str): Programa o sector destino.

    Retorna:
        list: Camino más corto entre los dos nodos, si existe.
    """
    cola = [[inicio]]      # Cola con caminos posibles
    visitados = set()      # Conjunto de nodos visitados

    while cola:
        camino = cola.pop(0)
        nodo_actual = camino[-1]

        if nodo_actual in visitados:
            continue

        visitados.add(nodo_actual)

        # Si llegamos al objetivo, retornamos el camino
        if nodo_actual == objetivo:
            return camino

        # Explorar vecinos
        for vecino in grafo.get(nodo_actual, []):
            nuevo_camino = list(camino)
            nuevo_camino.append(vecino)
            cola.append(nuevo_camino)

    return None


# PROGRAMA PRINCIPAL
print("BIENVENIDO AL SISTEMA DIGITAL DE TRON ")
print("Encuentra la ruta más corta entre programas dentro de la red.\n")

inicio = input("Ingrese el programa de inicio: ").title()
objetivo = input("Ingrese el programa de destino: ").title()

camino = buscar_camino_bfs(sistema_tron, inicio, objetivo)

print("\n--- RESULTADO DE LA BÚSQUEDA ---")
if camino:
    print(f"Ruta encontrada entre {inicio} y {objetivo}:")
    print(" -> ".join(camino))
    print("\n Tron dice: '¡El camino más eficiente ha sido encontrado!'")
else:
    print(f"No existe conexión entre {inicio} y {objetivo}.")
    print("El MCP bloquea el acceso al sector.")