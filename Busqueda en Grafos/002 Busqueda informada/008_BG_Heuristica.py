# Tron recorre la red digital usando una heurística para estimar
# el camino más prometedor hacia el núcleo MCP. Ahora también
# se calcula el costo total de energía en la ruta elegida.

import heapq

# --- RED DIGITAL (GRAFO CON COSTOS DE ENERGÍA) ---
red_tron = {
    "Tron": {"Clu": 3, "Flynn": 2},
    "Clu": {"Sark": 4, "Tron": 3},
    "Flynn": {"Tron": 2, "Yori": 3},
    "Yori": {"Flynn": 3, "Sector7": 5},
    "Sector7": {"Yori": 5, "Bit": 2},
    "Sark": {"Clu": 4, "MCP": 6},
    "Bit": {"Sector7": 2, "MCP": 4},
    "MCP": {}
}

# --- FUNCIÓN HEURÍSTICA ---
# Estima la distancia digital restante al MCP
heuristica = {
    "Tron": 8,
    "Clu": 6,
    "Flynn": 7,
    "Yori": 5,
    "Sector7": 4,
    "Bit": 2,
    "Sark": 3,
    "MCP": 0
}


def busqueda_greedy_con_costos(grafo, inicio, objetivo):
    """
    Búsqueda Greedy con heurística y costo acumulado.
    Tron elige el camino más prometedor según la heurística (h),
    y al final se muestra el costo total de energía.
    """
    frontera = []
    heapq.heappush(frontera, (heuristica[inicio], [inicio], 0))  # (heurística, ruta, costo acumulado)
    visitados = set()

    print("\n INICIANDO BÚSQUEDA INFORMADA EN EL SISTEMA")

    while frontera:
        _, camino, costo = heapq.heappop(frontera)
        nodo_actual = camino[-1]

        print(f"Tron analiza el nodo: {nodo_actual} | Costo acumulado: {costo}")

        if nodo_actual == objetivo:
            print("\n Núcleo MCP localizado.")
            return camino, costo

        if nodo_actual not in visitados:
            visitados.add(nodo_actual)
            for vecino, costo_extra in grafo[nodo_actual].items():
                if vecino not in visitados:
                    nuevo_camino = list(camino)
                    nuevo_camino.append(vecino)
                    nuevo_costo = costo + costo_extra
                    heapq.heappush(frontera, (heuristica[vecino], nuevo_camino, nuevo_costo))

    return None, None


# --- INTERFAZ DEL SISTEMA ---
print("SISTEMA CENTRAL DE BÚSQUEDA - RED TRON")
inicio = input("Ingrese el programa inicial (ej. Tron): ").title()
objetivo = input("Ingrese el programa objetivo (ej. MCP): ").upper()

ruta, costo_total = busqueda_greedy_con_costos(red_tron, inicio, objetivo)

print("\n--- RESULTADO FINAL ---")
if ruta:
    print(" -> ".join(ruta))
    print(f"Costo total de energía: {costo_total} unidades.")
    print("\n Tron: 'He seguido la ruta más prometedora según el análisis heurístico.'")
else:
    print("No se encontró una conexión entre los programas.")
    print("MCP: 'Tu lógica sigue siendo ineficiente, Tron.'")