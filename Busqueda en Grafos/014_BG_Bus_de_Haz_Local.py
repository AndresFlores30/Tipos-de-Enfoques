# Descripción: Búsqueda de haz local que acepta cualquier nodo de inicio/objetivo
# independientemente de mayúsculas/minúsculas.

import time

# RED DIGITAL (nombres "originales")
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

# HEURÍSTICA (valores por nombre original)
energia = {
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


def build_normalized_graph(red, energia_map):
    """
    Devuelve:
      - graph_norm: dict con claves y vecinos en minúsculas
      - energia_norm: dict con energía por clave en minúsculas
      - name_map: dict que mapea clave_minusc -> nombre_original
    """
    name_map = {}
    # incluir todos los nodos (claves y vecinos) para mapear correctamente
    all_nodes = set(red.keys())
    for vecinos in red.values():
        all_nodes.update(vecinos)

    for node in all_nodes:
        key = node.strip().lower()
        name_map[key] = node  # si hay duplicados, queda el último original (no ocurre aquí)

    graph_norm = {k: [] for k in name_map.keys()}
    for orig, vecinos in red.items():
        okey = orig.strip().lower()
        for v in vecinos:
            vkey = v.strip().lower()
            graph_norm[okey].append(vkey)

    energia_norm = {}
    for orig, val in energia_map.items():
        energia_norm[orig.strip().lower()] = val

    return graph_norm, energia_norm, name_map


# Construir versión normalizada
graph_norm, energia_norm, name_map = build_normalized_graph(red_tron, energia)


def busqueda_haz_local(inicio_raw, objetivo_raw, k=3, max_iteraciones=10):
    """
    Local Beam Search usando grafo normalizado internamente.
    Parámetros de entrada (inicio_raw/objetivo_raw) pueden tener cualquier capitalización.
    """
    inicio = inicio_raw.strip().lower()
    objetivo = objetivo_raw.strip().lower()

    # Validaciones
    if inicio not in graph_norm:
        print(f"Error: nodo de inicio '{inicio_raw}' no existe en la red.")
        return None
    if objetivo not in graph_norm:
        print(f"Error: nodo objetivo '{objetivo_raw}' no existe en la red.")
        return None

    # inicializar k haces (todos comienzan en el nodo inicial)
    haces = [[inicio] for _ in range(k)]
    print("INICIO DE LA BÚSQUEDA DE HAZ LOCAL")
    print(f"Lanzando {k} haces desde '{name_map[inicio]}' buscando '{name_map[objetivo]}'\n")

    for iteracion in range(max_iteraciones):
        print(f"--- Iteración {iteracion + 1} ---")
        nuevos_haces = []

        for camino in haces:
            nodo_actual = camino[-1]
            print(f"Haz actual: {[name_map[n] for n in camino]} | Energía: {energia_norm.get(nodo_actual, float('inf'))}")

            # si alcanza objetivo
            if nodo_actual == objetivo:
                print("\nObjetivo alcanzado.")
                return [name_map[n] for n in camino]

            # expandir vecinos
            for vecino in graph_norm.get(nodo_actual, []):
                nuevo_camino = list(camino)
                nuevo_camino.append(vecino)
                nuevos_haces.append(nuevo_camino)

        if not nuevos_haces:
            print("No hay más rutas disponibles. Búsqueda detenida.")
            return None

        # ordenar por energía del último nodo (menor mejor)
        nuevos_haces.sort(key=lambda c: energia_norm.get(c[-1], float('inf')))

        # conservar solo k mejores haces
        haces = nuevos_haces[:k]

        print(f"Se conservan los {k} mejores haces:")
        for h in haces:
            print(f"  {[name_map[n] for n in h]} (Energía: {energia_norm.get(h[-1], float('inf'))})")

        print()
        time.sleep(0.3)

    print("No se alcanzó el nodo objetivo dentro del número máximo de iteraciones.")
    return None


# Programa principal
print("SISTEMA DE BÚSQUEDA DE HAZ LOCAL - UNIVERSO TRON")
inicio_input = input("Ingrese el nodo inicial: ")
objetivo_input = input("Ingrese el nodo objetivo: ")

resultado = busqueda_haz_local(inicio_input, objetivo_input, k=3, max_iteraciones=10)

if resultado:
    print("\n--- RESULTADO FINAL ---")
    print(f"Ruta encontrada: {resultado}")
    print(f"Nodo final: {resultado[-1]}")
else:
    print("\nNo se encontró una ruta hacia el objetivo.")