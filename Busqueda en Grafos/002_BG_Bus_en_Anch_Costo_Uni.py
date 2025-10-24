# Descripción: Encuentra la ruta más eficiente (menor costo energético)
# entre dos programas dentro del sistema digital de TRON.

import heapq  # Cola de prioridad para elegir el camino más barato

# MAPA DIGITAL DEL SISTEMA
# Cada conexión tiene un costo (energía de transmisión)
sistema_tron = {
    "Tron": {"Clu": 2, "Flynn": 4, "Yori": 3},
    "Clu": {"Tron": 2, "Sark": 5},
    "Flynn": {"Tron": 4, "Sark": 1, "Yori": 2},
    "Yori": {"Tron": 3, "Flynn": 2, "Sector7": 6},
    "Sark": {"Clu": 5, "Flynn": 1, "Mcp": 4},
    "Sector7": {"Yori": 6, "Bit": 2},
    "Bit": {"Sector7": 2, "Mcp": 3},
    "Mcp": {"Sark": 4, "Bit": 3}
}


def busqueda_costo_uniforme(grafo, inicio, objetivo):
    """
    Algoritmo de Búsqueda de Costo Uniforme (UCS)
    Encuentra el camino de menor costo energético dentro del sistema TRON.

    Parámetros:
        grafo (dict): Representación del sistema y costos.
        inicio (str): Nodo inicial.
        objetivo (str): Nodo objetivo.

    Retorna:
        (camino, costo_total): Tupla con el mejor camino y su costo.
    """
    # Cola de prioridad con (costo_acumulado, nodo, camino)
    cola = [(0, inicio, [inicio])]
    visitados = set()

    while cola:
        # Selecciona el camino con menor costo
        costo_actual, nodo, camino = heapq.heappop(cola)

        if nodo in visitados:
            continue
        visitados.add(nodo)

        # Si llegamos al objetivo, retornamos el resultado
        if nodo == objetivo:
            return camino, costo_actual

        # Explorar vecinos
        for vecino, costo in grafo.get(nodo, {}).items():
            if vecino not in visitados:
                nuevo_costo = costo_actual + costo
                nuevo_camino = camino + [vecino]
                heapq.heappush(cola, (nuevo_costo, vecino, nuevo_camino))

    return None, float("inf")


# PROGRAMA PRINCIPAL
print("SISTEMA DIGITAL TRON ONLINE")
print("Ruta de costo uniforme entre programas activos...\n")

inicio = input("Ingrese el programa de inicio: ").title()
objetivo = input("Ingrese el programa destino: ").title()

camino, costo = busqueda_costo_uniforme(sistema_tron, inicio, objetivo)

print("\n--- RESULTADOS DE LA RED ---")
if camino:
    print(f"Ruta más eficiente entre {inicio} y {objetivo}:")
    print(" -> ".join(camino))
    print(f"Costo total de energía: {costo} unidades")
    print("\n Tron: 'La ruta más segura ha sido trazada a través de la red.'")
else:
    print("No se encontró una conexión dentro del sistema.")
    print("MCP: 'El acceso ha sido denegado, programa.'")