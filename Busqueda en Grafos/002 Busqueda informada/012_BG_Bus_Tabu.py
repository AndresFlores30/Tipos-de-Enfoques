# Tron explora la red digital usando una búsqueda heurística con memoria.
# Guarda en una lista tabú los nodos ya visitados para evitar bucles.
# El objetivo es llegar al MCP minimizando la heurística y sin repetir nodos prohibidos.

import random

# --- RED DIGITAL DE TRON ---
red_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],
    "Clu": ["Sark", "Sector5"],
    "Flynn": ["Sector7", "Yori"],
    "Yori": ["Bit", "Sark"],
    "Sark": ["MCP"],
    "Sector5": ["MCP"],
    "Sector7": ["Bit"],
    "Bit": ["MCP"],
    "MCP": []
}

# --- HEURÍSTICA: Energía necesaria para alcanzar al MCP (menor = mejor) ---
heuristica = {
    "Tron": 9,
    "Clu": 7,
    "Flynn": 8,
    "Yori": 6,
    "Sark": 3,
    "Sector5": 4,
    "Sector7": 5,
    "Bit": 2,
    "MCP": 0
}

# --- FUNCIÓN PRINCIPAL DE BÚSQUEDA TABÚ ---
def busqueda_tabu(inicio, objetivo, tamano_tabu=3, iteraciones_max=10):
    actual = inicio
    mejor_nodo = actual
    mejor_valor = heuristica[actual]
    tabu = []  # lista tabú (memoria de nodos visitados)
    camino = [actual]

    print("💠 INICIO DE LA BÚSQUEDA TABÚ 💠")
    print(f"Tron inicia en el nodo: {actual}\n")

    for paso in range(iteraciones_max):
        print(f"--- Iteración {paso + 1} ---")
        print(f"Nodo actual: {actual} | Heurística: {heuristica[actual]}")
        print(f"Lista Tabú: {tabu}")

        if actual == objetivo:
            print("\n Tron ha alcanzado el MCP. ¡Sistema liberado!")
            return camino

        vecinos = red_tron[actual]
        candidatos = [(n, heuristica[n]) for n in vecinos if n not in tabu]

        if not candidatos:
            print("No hay vecinos válidos fuera de la lista tabú. Tron está bloqueado.")
            break

        # Selecciona el vecino con mejor heurística (menor valor)
        mejor_vecino, valor = min(candidatos, key=lambda x: x[1])
        print(f"Vecinos disponibles: {candidatos}")
        print(f"Mejor vecino elegido: {mejor_vecino} | Heurística: {valor}")

        # Actualiza memoria tabú
        tabu.append(actual)
        if len(tabu) > tamano_tabu:
            tabu.pop(0)  # elimina el más antiguo

        actual = mejor_vecino
        camino.append(actual)

        # Actualiza mejor solución encontrada
        if valor < mejor_valor:
            mejor_valor = valor
            mejor_nodo = actual

        print(f"Tron avanza hacia: {actual}\n")

    print("\n Tron detiene la búsqueda.")
    print(f"Mejor nodo alcanzado: {mejor_nodo} | Heurística: {mejor_valor}")
    return camino


# --- INTERFAZ DE CONTROL ---
print("SISTEMA DE BÚSQUEDA TABÚ")
inicio = input("Ingrese el nodo inicial (ej. Tron): ").title()
objetivo = input("Ingrese el nodo objetivo (ej. MCP): ").upper()

camino_encontrado = busqueda_tabu(inicio, objetivo)

print("\n--- RESULTADO FINAL ---")
print(f"Ruta explorada por Tron: {camino_encontrado}")
print(f"Nodo final alcanzado: {camino_encontrado[-1]}")