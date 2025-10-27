# TRON - Búsqueda Online en la Red (Online Search)
# Un programa de defensa intenta llegar al Núcleo Central,
# reaccionando en tiempo real a fallos y nuevas conexiones.

from typing import Dict, List

# Mapa digital de la Red
red: Dict[str, List[str]] = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Núcleo_Central"],
    "Portal": ["Base", "Arena"],
    "Núcleo_Central": ["Torre_IO"]
}

# Heuristica: costo estimado de energía hacia el Nucleo 
h: Dict[str, int] = {
    "Base": 8,
    "Sector_Luz": 6,
    "Arena": 4,
    "Torre_IO": 2,
    "Portal": 5,
    "Núcleo_Central": 0
}

# Evento inesperado: un túnel de datos colapsa
TUNEL_CAIDO = ("Arena", "Torre_IO")


def online_search_TRON(origen: str, destino: str, max_pasos: int = 10):
    """
    Simula una búsqueda online en la Red:
    El programa avanza nodo por nodo, reaccionando a fallos en rutas de datos
    y descubriendo nuevas conexiones emergentes.
    """
    actual = origen
    camino = [actual]
    print(f"Iniciando transmisión desde: {actual}")

    for paso in range(max_pasos):
        conexiones = red.get(actual, [])

        # Detectar si hay un túnel de datos colapsado
        if TUNEL_CAIDO[0] == actual and TUNEL_CAIDO[1] in conexiones:
            conexiones.remove(TUNEL_CAIDO[1])
            print(f"ALERTA: Túnel de datos colapsado: {actual} -> {TUNEL_CAIDO[1]}")

        if not conexiones:
            print("Sin rutas de energía disponibles. Proceso detenido.")
            break

        # Elegir la conexión más prometedora según la heurística (energía mínima)
        siguiente = min(conexiones, key=lambda n: h[n])

        print(f"Paso {paso+1}: {actual} -> {siguiente} (energía estimada: {h[siguiente]})")
        actual = siguiente
        camino.append(actual)

        # Verificar si llegó al destino
        if actual == destino:
            print("Conexión establecida con el Núcleo Central. Misión completada.")
            break

        # Simular que el programa descubre una nueva conexión emergente
        if actual == "Sector_Luz" and "Torre_IO" not in red["Sector_Luz"]:
            red["Sector_Luz"].append("Torre_IO")
            print("Nueva ruta emergente detectada: Sector_Luz ↔ Torre_IO")

    return camino


def demo_TRON():
    origen, destino = "Base", "Núcleo_Central"
    ruta = online_search_TRON(origen, destino)

    print("\n Ruta seguida dentro del Grid:")
    print("  " + " -> ".join(ruta))


if __name__ == "__main__":
    demo_TRON()