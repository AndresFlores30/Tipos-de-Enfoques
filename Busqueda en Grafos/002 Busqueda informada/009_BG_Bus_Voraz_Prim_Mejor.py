# Tron intenta alcanzar el núcleo MCP siguiendo el camino
# que parece más prometedor, guiado únicamente por la heurística (h).

import heapq

red_tron = {
    "Tron": {"Clu": 3, "Flynn": 2},
    "Clu": {"Sark": 4, "Tron": 3},
    "Flynn": {"Tron": 2, "Yori": 3, "Sector7": 6},
    "Yori": {"Flynn": 3, "Sector7": 5},
    "Sector7": {"Yori": 5, "Bit": 2},
    "Bit": {"Sector7": 2, "MCP": 4},
    "Sark": {"Clu": 4, "MCP": 6},
    "MCP": {}
}

# --- FUNCIÓN HEURÍSTICA ---
# Valores más bajos significan "más cerca" del MCP.
heuristica = {
    "Tron": 10,
    "Clu": 8,
    "Flynn": 7,
    "Yori": 5,
    "Sector7": 4,
    "Bit": 2,
    "Sark": 3,
    "MCP": 0
}


def busqueda_voraz_primero_mejor(grafo, inicio, objetivo):
    """
    Búsqueda voraz guiada por heurística (Greedy Best-First Search).
    Tron elige siempre el nodo con menor valor heurístico h(n).
    """
    frontera = []
    heapq.heappush(frontera, (heuristica[inicio], [inicio]))  # (heurística, camino)
    visitados = set()

    print("\n INICIANDO BÚSQUEDA VORAZ EN EL SISTEMA")

    while frontera:
        _, camino = heapq.heappop(frontera)
        nodo_actual = camino[-1]

        print(f"Tron analiza el nodo: {nodo_actual} | h(n) = {heuristica[nodo_actual]}")

        if nodo_actual == objetivo:
            print("\n Núcleo MCP localizado.")
            return camino

        if nodo_actual not in visitados:
            visitados.add(nodo_actual)
            for vecino in grafo[nodo_actual]:
                if vecino not in visitados:
                    nuevo_camino = list(camino)
                    nuevo_camino.append(vecino)
                    heapq.heappush(frontera, (heuristica[vecino], nuevo_camino))

    return None


# --- INTERFAZ DIGITAL ---
print("SISTEMA DE NAVEGACIÓN VORAZ - RED TRON")
inicio = input("Ingrese el programa inicial (ej. Tron): ").title()
objetivo = input("Ingrese el programa objetivo (ej. MCP): ").upper()

ruta = busqueda_voraz_primero_mejor(red_tron, inicio, objetivo)

print("\n--- RESULTADO FINAL ---")
if ruta:
    print(" -> ".join(ruta))
    print("\n Tron: 'He seguido la señal más prometedora hacia el MCP.'")
else:
    print("No se encontró conexión entre los programas.")
    print("MCP: 'Tu heurística carece de eficiencia, Tron.'")