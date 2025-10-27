# RED DIGITAL DEL SISTEMA TRON
sistema_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],
    "Clu": ["Sark", "Tron"],
    "Flynn": ["Tron", "Yori", "Sark"],
    "Yori": ["Flynn", "Sector7"],
    "Sark": ["Clu", "Flynn", "Mcp"],
    "Sector7": ["Yori", "Bit"],
    "Bit": ["Sector7", "Mcp"],
    "Mcp": ["Sark", "Bit"]
}


def dls(grafo, inicio, objetivo, limite, nivel=0, camino=None):
    """
    Realiza una Búsqueda en Profundidad Limitada (DLS) en la red TRON.

    Parámetros:
        grafo (dict): Estructura del sistema digital.
        inicio (str): Nodo inicial.
        objetivo (str): Nodo que se desea encontrar.
        limite (int): Profundidad máxima permitida.
        nivel (int): Nivel actual de profundidad.
        camino (list): Ruta actual recorrida.

    Retorna:
        list: Camino hacia el objetivo si se encuentra dentro del límite, o None.
    """
    if camino is None:
        camino = []

    # Registrar el nodo actual en el camino
    camino.append(inicio)
    print(f"Nivel {nivel}: Ingresando al nodo {inicio}")

    # Si encontramos el objetivo, retornamos el camino
    if inicio == objetivo:
        return camino

    # Si alcanzamos el límite de profundidad, regresamos sin seguir descendiendo
    if nivel >= limite:
        print(f"Límite alcanzado en el nodo {inicio}. Regresando...")
        return None

    # Explorar los vecinos dentro del límite
    for vecino in grafo.get(inicio, []):
        if vecino not in camino:
            resultado = dls(grafo, vecino, objetivo, limite, nivel + 1, list(camino))
            if resultado:
                return resultado

    # Si no se encuentra el objetivo dentro del límite
    return None


print("SISTEMA DIGITAL TRON ONLINE")
print("Búsqueda profunda con límite de seguridad activado...\n")

inicio = input("Ingrese el programa de inicio: ").title()
objetivo = input("Ingrese el programa destino: ").title()
limite = int(input("Ingrese el límite de profundidad (nivel máximo permitido): "))

resultado = dls(sistema_tron, inicio, objetivo, limite)

print("\n--- RESULTADOS DE LA RED ---")
if resultado:
    print(f"Ruta encontrada dentro del límite de {limite} niveles:")
    print(" -> ".join(resultado))
    print("\n Tron: 'El objetivo fue localizado antes de sobrecargar la red.'")
else:
    print("No se encontró el objetivo dentro del límite establecido.")
    print("MCP: 'El acceso fue restringido por seguridad del sistema.'")