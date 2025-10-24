# Tron busca llegar al MCP dentro de la red digital.
# Usa una temperatura inicial alta para explorar ampliamente, y luego enfría gradualmente.
# Esto permite escapar de mínimos locales mientras se busca la mejor ruta.

import math
import random
import time

# --- RED DIGITAL DE TRON ---
red_tron = {
    "Tron": ["Clu", "Yori", "Flynn"],
    "Clu": ["Sark", "Sector5"],
    "Yori": ["Bit", "Flynn"],
    "Flynn": ["Sector7", "Yori"],
    "Sark": ["MCP"],
    "Sector5": ["MCP"],
    "Sector7": ["Bit"],
    "Bit": ["MCP"],
    "MCP": []
}

# --- HEURÍSTICA: Energía (distancia o dificultad hacia el MCP) ---
energia_nodo = {
    "Tron": 9,
    "Clu": 7,
    "Yori": 6,
    "Flynn": 8,
    "Sark": 3,
    "Sector5": 4,
    "Sector7": 5,
    "Bit": 2,
    "MCP": 0
}

# --- FUNCIÓN DE TEMPLE SIMULADO ---
def temple_simulado(inicio, objetivo, temperatura_inicial=100, tasa_enfriamiento=0.9, iteraciones=100):
    actual = inicio
    mejor = actual
    mejor_energia = energia_nodo[actual]
    temperatura = temperatura_inicial
    camino = [actual]

    print("INICIO DE BÚSQUEDA POR TEMPLE SIMULADO")
    print(f"Tron inicia en el nodo: {inicio} con energía {mejor_energia}\n")

    for paso in range(iteraciones):
        if actual == objetivo:
            print("\n Tron ha alcanzado el MCP. ¡Red liberada!")
            break

        vecinos = red_tron[actual]
        if not vecinos:
            print("Tron se ha quedado sin rutas disponibles.")
            break

        # Elegimos un vecino al azar (exploración)
        vecino = random.choice(vecinos)
        energia_actual = energia_nodo[actual]
        energia_vecino = energia_nodo[vecino]

        # Diferencia de energía (costo)
        delta = energia_vecino - energia_actual

        # Criterio de aceptación
        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            actual = vecino
            camino.append(actual)
            print(f"Tron avanza hacia {actual} | Energía: {energia_vecino} | Temp: {temperatura:.2f}")
            
            # Actualizamos mejor solución si mejora
            if energia_vecino < mejor_energia:
                mejor = actual
                mejor_energia = energia_vecino
        else:
            print(f"Tron rechaza moverse hacia {vecino} | Energía: {energia_vecino}")

        # Enfriamiento de la temperatura
        temperatura *= tasa_enfriamiento

        # Pausa estética (simula exploración digital)
        time.sleep(0.1)

        # Si la temperatura llega muy baja, detenemos
        if temperatura < 0.1:
            print("\n💤 Temperatura demasiado baja. Tron detiene la exploración.")
            break

    print("\n--- RESULTADO FINAL ---")
    print(f"Camino explorado: {camino}")
    print(f"Mejor nodo alcanzado: {mejor} | Energía: {mejor_energia}")
    print(f"Temperatura final: {temperatura:.2f}")
    return camino


# --- INTERFAZ DE CONTROL ---
print("SISTEMA DE TEMPLE SIMULADO")
inicio = input("Ingrese el nodo inicial (ej. Tron): ").title()
objetivo = input("Ingrese el nodo objetivo (ej. MCP): ").upper()

camino_final = temple_simulado(inicio, objetivo)