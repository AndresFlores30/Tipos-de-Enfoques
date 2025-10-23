# RED DIGITAL DEL SISTEMA TRON
red_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],
    "Clu": ["Sark", "Tron"],
    "Flynn": ["Tron", "Yori", "Sark"],
    "Yori": ["Flynn", "Sector7"],
    "Sark": ["Clu", "Flynn", "Mcp"],
    "Sector7": ["Yori", "Bit"],
    "Bit": ["Sector7", "Mcp"],
    "Mcp": ["Sark", "Bit"]
}


def dls(grafo, inicio, objetivo, limite, nivel=0, camino=None):
    """
    Realiza una búsqueda en profundidad limitada (DLS) dentro del sistema TRON.

    Parámetros:
        grafo (dict): Representación de la red TRON.
        inicio (str): Nodo inicial.
        objetivo (str): Nodo destino.
        limite (int): Profundidad máxima para esta iteración.
        nivel (int): Nivel actual de exploración.
        camino (list): Ruta actual recorrida.

    Retorna:
        list: Ruta hacia el objetivo si se encuentra, o None.
    """
    if camino is None:
        camino = []

    camino.append(inicio)
    print(f"Nivel {nivel}: Explorando {inicio}")

    if inicio == objetivo:
        return camino

    if nivel >= limite:
        return None

    for vecino in grafo.get(inicio, []):
        if vecino not in camino:
            resultado = dls(grafo, vecino, objetivo, limite, nivel + 1, list(camino))
            if resultado:
                return resultado

    return None


def iddfs(grafo, inicio, objetivo, limite_max):
    """
    Realiza la Búsqueda en Profundidad Iterativa (IDDFS).
    Incrementa el límite de profundidad en cada iteración hasta encontrar el objetivo.

    Parámetros:
        grafo (dict): Red TRON.
        inicio (str): Nodo inicial.
        objetivo (str): Nodo a encontrar.
        limite_max (int): Profundidad máxima total.

    Retorna:
        list: Camino encontrado, o None si no se localiza el objetivo.
    """
    for limite in range(limite_max + 1):
        print(f"\n Iteración con límite de profundidad: {limite}")
        resultado = dls(grafo, inicio, objetivo, limite)
        if resultado:
            print(f"Objetivo localizado con límite {limite}")
            return resultado
    return None


# --- INTERFAZ DEL SISTEMA ---
print("SISTEMA DIGITAL TRON ONLINE")
print("Protocolo de búsqueda iterativa activado...\n")

inicio = input("Ingrese el programa inicial: ").title()
objetivo = input("Ingrese el programa objetivo: ").title()
limite_max = int(input("Ingrese el límite máximo de profundidad: "))

ruta = iddfs(red_tron, inicio, objetivo, limite_max)

print("\n--- RESULTADO FINAL ---")
if ruta:
    print(" -> ".join(ruta))
    print("\n Tron: 'Objetivo encontrado a través de escaneos iterativos.'")
else:
    print("El objetivo no fue localizado dentro del límite.")
    print("MCP: 'La red ha sido bloqueada antes de la detección final.'")