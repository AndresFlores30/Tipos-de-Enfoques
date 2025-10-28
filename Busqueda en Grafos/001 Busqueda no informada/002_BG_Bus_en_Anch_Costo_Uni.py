# Descripción: Encuentra la ruta más eficiente (menor costo energético)
# entre dos programas dentro del sistema digital de TRON.

import heapq  # Cola de prioridad para elegir el camino más barato

# MAPA DIGITAL DEL SISTEMA
# Cada conexión tiene un costo (energía de transmisión)
# Estructura: {nodo_origen: {nodo_destino: costo_energia, ...}, ...}
sistema_tron = {
    "Tron": {"Clu": 2, "Flynn": 4, "Yori": 3},
    "Clu": {"Tron": 2, "Sark": 5},
    "Flynn": {"Tron": 4, "Sark": 1, "Yori": 2},
    "Yori": {"Tron": 3, "Flynn": 2, "Sector7": 6},
    "Sark": {"Clu": 5, "Flynn": 1, "Mcp": 4},
    "Sector7": {"Yori": 6, "Bit": 2},
    "Bit": {"Sector7": 2, "Mcp": 3},
    "Mcp": {"Sark": 4, "Bit": 3}
}


def busqueda_costo_uniforme(grafo, inicio, objetivo):
    """
    Algoritmo de Búsqueda de Costo Uniforme (UCS)
    Encuentra el camino de menor costo energético dentro del sistema TRON.
    
    UCS es óptimo para grafos con costos no negativos y garantiza encontrar
    el camino de menor costo total.

    Parámetros:
        grafo (dict): Representación del sistema y costos como diccionario anidado.
        inicio (str): Nodo inicial de la búsqueda.
        objetivo (str): Nodo objetivo de la búsqueda.

    Retorna:
        tuple: (camino, costo_total) donde:
            - camino: lista de nodos del camino óptimo
            - costo_total: suma de costos del camino
        Si no hay camino, retorna (None, infinito)
    """
    # Verificar que los nodos existan en el grafo
    if inicio not in grafo:
        print(f"Error: El nodo '{inicio}' no existe en el sistema TRON")
        return None, float("inf")
    if objetivo not in grafo:
        print(f"Error: El nodo '{objetivo}' no existe en el sistema TRON")
        return None, float("inf")
    
    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio], 0
    
    # Cola de prioridad: almacena tuplas (costo_acumulado, nodo_actual, camino_recorrido)
    # heapq mantiene el orden por el primer elemento (costo_acumulado)
    cola = [(0, inicio, [inicio])]
    
    # Conjunto para registrar nodos ya expandidos (evita procesamiento redundante)
    visitados = set()

    while cola:
        # Extraer el camino con menor costo acumulado (propiedad de la cola de prioridad)
        costo_actual, nodo_actual, camino_actual = heapq.heappop(cola)

        # Si el nodo ya fue visitado, ignorar esta entrada (puede haber duplicados en la cola)
        if nodo_actual in visitados:
            continue
            
        # Marcar nodo como visitado
        visitados.add(nodo_actual)

        # Verificar si llegamos al objetivo
        if nodo_actual == objetivo:
            return camino_actual, costo_actual

        # Explorar todos los vecinos del nodo actual
        for vecino, costo_arista in grafo.get(nodo_actual, {}).items():
            # Solo procesar vecinos no visitados
            if vecino not in visitados:
                # Calcular nuevo costo acumulado
                nuevo_costo = costo_actual + costo_arista
                # Construir nuevo camino extendiendo el actual
                nuevo_camino = camino_actual + [vecino]
                # Agregar a la cola de prioridad para futura exploración
                heapq.heappush(cola, (nuevo_costo, vecino, nuevo_camino))

    # Si la cola se vacía sin encontrar el objetivo, no existe camino
    return None, float("inf")


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con costos de conexión.
    """
    print("\n--- MAPA DEL SISTEMA TRON (con costos de energía) ---")
    for nodo, conexiones in sistema_tron.items():
        conexiones_str = [f"{destino}({costo})" for destino, costo in conexiones.items()]
        print(f"{nodo}: conectado con {', '.join(conexiones_str)}")
    print("-----------------------------------------------------")


def validar_entrada_usuario(entrada, grafo):
    """
    Valida que la entrada del usuario exista en el sistema TRON.

    Parámetros:
        entrada (str): Texto ingresado por el usuario.
        grafo (dict): Grafo del sistema para validar existencia.

    Retorna:
        bool: True si la entrada es válida, False en caso contrario.
    """
    entrada_normalizada = entrada.strip().title()
    return entrada_normalizada in grafo


# PROGRAMA PRINCIPAL
def main():
    """
    Función principal que coordina la interacción con el usuario
    y la ejecución del algoritmo de búsqueda de costo uniforme.
    """
    print("SISTEMA DIGITAL TRON ONLINE")
    print("Ruta de costo uniforme entre programas activos...\n")
    
    # Mostrar mapa del sistema para referencia del usuario
    mostrar_mapa_sistema()
    
    # Solicitar nodo de inicio con validación
    while True:
        inicio = input("\nIngrese el programa de inicio: ").strip().title()
        if validar_entrada_usuario(inicio, sistema_tron):
            break
        else:
            print(f"Error: '{inicio}' no existe en el sistema.")
            print("Nodos disponibles:", ", ".join(sistema_tron.keys()))
    
    # Solicitar nodo objetivo con validación
    while True:
        objetivo = input("Ingrese el programa destino: ").strip().title()
        if validar_entrada_usuario(objetivo, sistema_tron):
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema.")
            print("Nodos disponibles:", ", ".join(sistema_tron.keys()))
    
    # Ejecutar búsqueda del camino de menor costo
    print(f"\nBuscando ruta óptima entre {inicio} y {objetivo}...")
    camino, costo = busqueda_costo_uniforme(sistema_tron, inicio, objetivo)
    
    # Mostrar resultados de la búsqueda
    print("\n--- RESULTADOS DE LA RED ---")
    if camino:
        print(f"Ruta más eficiente entre {inicio} y {objetivo}:")
        print(" -> ".join(camino))
        print(f"Costo total de energía: {costo} unidades")
        print("\nTron: 'La ruta más segura ha sido trazada a través de la red.'")
    else:
        print("No se encontró una conexión dentro del sistema.")
        print("MCP: 'El acceso ha sido denegado, programa.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()