# Descripción: Tron ejecuta una búsqueda doble desde ambos extremos de la red digital
# para localizar una ruta óptima hacia el objetivo MCP.

from collections import deque

# --- RED DIGITAL DEL SISTEMA TRON ---
red_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],
    "Clu": ["Tron", "Sark"],
    "Flynn": ["Tron", "Yori", "Sark"],
    "Yori": ["Flynn", "Sector7"],
    "Sark": ["Clu", "Flynn", "Mcp"],
    "Sector7": ["Yori", "Bit"],
    "Bit": ["Sector7", "Mcp"],
    "Mcp": ["Sark", "Bit"]
}


def bidirectional_search(grafo, inicio, objetivo):
    """
    Realiza una búsqueda bidireccional en la red TRON.

    Parámetros:
        grafo (dict): Representación de la red digital.
        inicio (str): Nodo inicial (Tron).
        objetivo (str): Nodo objetivo (Mcp).

    Retorna:
        list: Ruta completa si se encuentran, None en caso contrario.
    """
    if inicio == objetivo:
        return [inicio]

    # --- Colas de exploración ---
    frente_inicio = deque([[inicio]])
    frente_objetivo = deque([[objetivo]])

    # --- Conjuntos de nodos visitados ---
    visitados_inicio = {inicio}
    visitados_objetivo = {objetivo}

    print("\n💠 PROTOCOLO DE BÚSQUEDA BIDIRECCIONAL ACTIVADO 💠")

    while frente_inicio and frente_objetivo:
        # --- Expansión desde el inicio (Tron) ---
        camino_inicio = frente_inicio.popleft()
        nodo_actual_inicio = camino_inicio[-1]
        print(f"Explorando desde Tron: {nodo_actual_inicio}")

        for vecino in grafo.get(nodo_actual_inicio, []):
            if vecino not in visitados_inicio:
                nuevo_camino_inicio = list(camino_inicio) + [vecino]
                frente_inicio.append(nuevo_camino_inicio)
                visitados_inicio.add(vecino)

                if vecino in visitados_objetivo:
                    print(f"\n Conexión detectada en nodo: {vecino}")
                    # Encontramos la conexión, reconstruimos camino
                    return construir_camino(nuevo_camino_inicio, frente_objetivo, vecino)

        # --- Expansión desde el objetivo (MCP) ---
        camino_objetivo = frente_objetivo.popleft()
        nodo_actual_objetivo = camino_objetivo[-1]
        print(f"Explorando desde MCP: {nodo_actual_objetivo}")

        for vecino in grafo.get(nodo_actual_objetivo, []):
            if vecino not in visitados_objetivo:
                nuevo_camino_objetivo = list(camino_objetivo) + [vecino]
                frente_objetivo.append(nuevo_camino_objetivo)
                visitados_objetivo.add(vecino)

                if vecino in visitados_inicio:
                    print(f"\n🔗 Conexión detectada en nodo: {vecino}")
                    return construir_camino(frente_inicio, nuevo_camino_objetivo, vecino)

    return None


def construir_camino(camino_inicio, frente_opuesto, punto_encuentro):
    """
    Combina los caminos desde Tron y MCP en el punto de encuentro.

    Parámetros:
        camino_inicio (list): Ruta desde Tron.
        frente_opuesto (deque o list): Rutas desde MCP.
        punto_encuentro (str): Nodo de conexión.

    Retorna:
        list: Camino completo entre ambos extremos.
    """
    # Buscar en la cola del lado opuesto el camino que termina en el punto de encuentro
    camino_objetivo = None
    for ruta in frente_opuesto:
        if ruta[-1] == punto_encuentro:
            camino_objetivo = ruta
            break

    if not camino_objetivo:
        return camino_inicio

    # Invertimos la ruta del objetivo y unimos ambas
    camino_final = camino_inicio[:-1] + camino_objetivo[::-1]
    return camino_final


# INTERFAZ DEL SISTEMA
print("SISTEMA DIGITAL TRON ONLINE")
inicio = input("Ingrese el programa inicial: ").title()
objetivo = input("Ingrese el programa objetivo: ").title()

ruta = bidirectional_search(red_tron, inicio, objetivo)

print("\n--- RESULTADO FINAL ---")
if ruta:
    print(" -> ".join(ruta))
    print("\n Tron: 'Conexión establecida entre ambos extremos de la red.'")
else:
    print("No se encontró conexión entre los programas.")
    print("MCP: 'Tus intentos de interceptar mi red han fallado, Tron.'")