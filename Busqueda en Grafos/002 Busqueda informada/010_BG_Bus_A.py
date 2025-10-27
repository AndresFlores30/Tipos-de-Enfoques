# Tron calcula el camino más eficiente hasta el MCP combinando
# el costo real (g) y la heurística (h).

import heapq

# --- RED DIGITAL DE TRON ---
red_tron = {
    "Tron": {"Clu": 3, "Flynn": 2},
    "Clu": {"Sark": 4, "Tron": 3},
    "Flynn": {"Tron": 2, "Yori": 3, "Sector7": 6},
    "Yori": {"Flynn": 3, "Sector7": 5, "Bit": 2},
    "Sector7": {"Yori": 5, "Bit": 2},
    "Bit": {"Sector7": 2, "MCP": 4},
    "Sark": {"Clu": 4, "MCP": 6},
    "MCP": {}
}

# --- FUNCIÓN HEURÍSTICA (estimación de distancia hacia MCP) ---
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

def busqueda_a_estrella(grafo, inicio, objetivo):
    frontera = []
    heapq.heappush(frontera, (0 + heuristica[inicio], 0, [inicio]))  # (f, g, camino)
    visitados = {}

    print("\n INICIANDO BÚSQUEDA A* EN EL SISTEMA")

    while frontera:
        f, g, camino = heapq.heappop(frontera)
        nodo_actual = camino[-1]

        print(f"Nodo actual: {nodo_actual} | g={g} | h={heuristica[nodo_actual]} | f={f}")

        if nodo_actual == objetivo:
            print("\n Núcleo MCP alcanzado.")
            return camino, g

        if nodo_actual in visitados and visitados[nodo_actual] <= g:
            continue

        visitados[nodo_actual] = g

        for vecino, costo in grafo[nodo_actual].items():
            nuevo_g = g + costo
            nuevo_f = nuevo_g + heuristica[vecino]
            nuevo_camino = list(camino)
            nuevo_camino.append(vecino)
            heapq.heappush(frontera, (nuevo_f, nuevo_g, nuevo_camino))

    return None, float("inf")


# --- INTERFAZ DIGITAL ---
print("SISTEMA DE BÚSQUEDA A* - RED TRON")
inicio = input("Ingrese el programa inicial (ej. Tron): ").title()
objetivo = input("Ingrese el programa objetivo (ej. MCP): ").upper()

ruta, costo = busqueda_a_estrella(red_tron, inicio, objetivo)

print("\n--- RESULTADO FINAL ---")
if ruta:
    print(" -> ".join(ruta))
    print(f"Costo total del trayecto: {costo}")
    print("\n Tron: 'He encontrado la ruta óptima a través del sistema.'")
else:
    print("No se pudo establecer conexión con el MCP.")