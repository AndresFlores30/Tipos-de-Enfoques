# Tron ejecuta una búsqueda AO* (And-Or Search) con objetivo definido.
# Evalúa rutas compuestas (AND) o alternativas (OR) hasta alcanzar el núcleo MCP
# o cualquier otro nodo objetivo.

# --- RED DIGITAL DE DECISIONES ---
grafo_ao = {
    "Tron": [["Clu"], ["Flynn", "Yori"]],
    "Clu": [["Sark"]],
    "Flynn": [["Sector7"]],
    "Yori": [["Bit"]],
    "Sector7": [["MCP"]],
    "Bit": [["MCP"]],
    "Sark": [["MCP"]],
    "MCP": []
}

# --- Heurística inicial (estimaciones de complejidad energética) ---
h = {
    "Tron": 6,
    "Clu": 4,
    "Flynn": 3,
    "Yori": 2,
    "Sector7": 1,
    "Bit": 1,
    "Sark": 2,
    "MCP": 0
}

# --- FUNCIONES PRINCIPALES ---

def ao_star(nodo, objetivo, visitados=None):
    """
    Función recursiva AO* con objetivo específico.
    Retorna el costo estimado más bajo desde el nodo hasta el objetivo.
    """
    if visitados is None:
        visitados = set()

    print(f"\n Analizando nodo: {nodo}")

    # Caso base: si ya llegamos al objetivo
    if nodo == objetivo:
        print(f"Nodo objetivo '{objetivo}' alcanzado.")
        return 0

    # Evitar ciclos
    if nodo in visitados:
        print(f"Nodo {nodo} ya fue visitado, evitando ciclo.")
        return float('inf')

    visitados.add(nodo)

    # Si el nodo no tiene expansiones
    if not grafo_ao.get(nodo, []):
        return float('inf')

    costos = []
    rutas = []

    # Evaluar conjuntos AND/OR
    for conjunto in grafo_ao[nodo]:
        print(f"Evaluando subrutas: {conjunto}")
        costo_total = 0
        sub_ruta = []

        for sub in conjunto:
            sub_costo = ao_star(sub, objetivo, visitados.copy())
            costo_total += sub_costo
            sub_ruta.append(sub)

        costos.append(costo_total)
        rutas.append(sub_ruta)

    # Seleccionar el camino con menor costo
    if costos:
        mejor_costo = min(costos) + 1  # +1 por el paso actual
        mejor_ruta = rutas[costos.index(min(costos))]
        print(f"Mejor opción desde {nodo}: {mejor_ruta} | Costo estimado: {mejor_costo}")
        h[nodo] = mejor_costo
        return mejor_costo
    else:
        return float('inf')


# --- INTERFAZ DIGITAL DEL SISTEMA TRON ---
print("SISTEMA DE BÚSQUEDA AO* - RED DE DECISIONES")
inicio = input("Ingrese el nodo inicial (ej. Tron): ").title()
objetivo = input("Ingrese el nodo objetivo (ej. MCP): ").upper()

costo_estimado = ao_star(inicio, objetivo)

print("\n--- RESULTADO FINAL ---")
if costo_estimado < float('inf'):
    print(f"Tron: 'El costo estimado mínimo desde {inicio} hasta {objetivo} es {costo_estimado} unidades de energía.'")
    print("MCP: 'Tus decisiones fueron eficientes, Tron.'")
else:
    print(f"No existe una ruta lógica desde {inicio} hasta {objetivo} dentro de la red.")
    print("MCP: 'Tu búsqueda ha colapsado en el vacío digital.'")