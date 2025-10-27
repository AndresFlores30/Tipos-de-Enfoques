# Tron busca alcanzar el MCP ascendiendo gradualmente en la red,
# avanzando solo hacia nodos que mejoran su valor heurístico (menor costo).
# No hay retrocesos: si no hay mejoras, se detiene.

import random

# --- RED DIGITAL DE TRON ---
grafo = {
    "Tron": ["Clu", "Flynn"],
    "Clu": ["Sark", "Yori"],
    "Flynn": ["Sector7"],
    "Yori": ["Bit"],
    "Sark": ["MCP"],
    "Sector7": ["MCP"],
    "Bit": ["MCP"],
    "MCP": []
}

# --- HEURÍSTICA (energía restante hacia el MCP: menor = mejor) ---
heuristica = {
    "Tron": 6,
    "Clu": 4,
    "Flynn": 5,
    "Yori": 3,
    "Sark": 2,
    "Sector7": 1,
    "Bit": 2,
    "MCP": 0
}

# --- FUNCIÓN PRINCIPAL DE BÚSQUEDA ---
def hill_climbing(inicio, objetivo):
    actual = inicio
    camino = [actual]

    print("INICIO DEL ASCENSO DE COLINAS")
    print(f"Tron ha sido liberado en el nodo: {actual}\n")

    while True:
        print(f"Nodo actual: {actual} | Heurística: {heuristica[actual]}")

        if actual == objetivo:
            print("\nTron ha alcanzado el MCP. ¡La red está liberada!")
            return camino

        vecinos = grafo[actual]
        if not vecinos:
            print("Nodo sin conexiones activas. Tron queda atrapado en la red.")
            return camino

        # Selecciona el mejor vecino (menor heurística)
        mejor_vecino = min(vecinos, key=lambda x: heuristica[x])

        print(f"Vecinos detectados: {vecinos}")
        print(f"Mejor vecino: {mejor_vecino} | Heurística: {heuristica[mejor_vecino]}")

        # Si no hay mejora, detener el ascenso
        if heuristica[mejor_vecino] >= heuristica[actual]:
            print("\nTron detecta un punto alto local.")
            print("'No hay rutas de menor energía... Estoy atrapado en esta colina.'")
            break

        actual = mejor_vecino
        camino.append(actual)
        print(f"Tron avanza hacia: {actual}\n")

    return camino


# --- INTERFAZ DE CONTROL ---
print("SISTEMA DE BÚSQUEDA DE ASCENSIÓN DE COLINAS")
inicio = input("Ingrese el nodo inicial (ej. Tron): ").title()
objetivo = input("Ingrese el nodo objetivo (ej. MCP): ").upper()

camino_encontrado = hill_climbing(inicio, objetivo)

print("\n--- RESULTADO FINAL ---")
print(f"Ruta explorada por Tron: {camino_encontrado}")
print("Estado final:", camino_encontrado[-1])