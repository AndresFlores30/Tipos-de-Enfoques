"""
SISTEMA DE BUSQUEDA AO* (AND-OR SEARCH) - TRON DIGITAL

Este modulo implementa el algoritmo de busqueda AO* para resolver problemas
de decision en grafos AND-OR. Los nodos OR representan elecciones alternativas,
mientras los nodos AND representan conjuntos de requisitos que deben cumplirse
simultaneamente.

AO* es particularmente util para problemas de planificacion y toma de decisiones
con dependencias complejas.
"""

# --- RED DIGITAL DE DECISIONES ---
# Estructura AND-OR: cada nodo contiene una lista de conjuntos alternativos (OR)
# Cada conjunto contiene nodos que deben alcanzarse simultaneamente (AND)
# Ejemplo: [["Clu"], ["Flynn", "Yori"]] significa:
# - OPCION 1: Solo Clu (OR)
# - OPCION 2: Flynn Y Yori (ambos deben cumplirse - AND)
grafo_ao = {
    "Tron": [["Clu"], ["Flynn", "Yori"]],  # Tron puede: O ir solo por Clu, O ir por Flynn Y Yori
    "Clu": [["Sark"]],                     # Clu debe ir por Sark
    "Flynn": [["Sector7"]],                # Flynn debe ir por Sector7
    "Yori": [["Bit"]],                     # Yori debe ir por Bit
    "Sector7": [["MCP"]],                  # Sector7 lleva directo al MCP
    "Bit": [["MCP"]],                      # Bit lleva directo al MCP
    "Sark": [["MCP"]],                     # Sark lleva directo al MCP
    "MCP": []                              # MCP es el objetivo final (nodo terminal)
}

# --- HEURISTICA INICIAL (estimaciones de complejidad energetica) ---
# Valores que representan el costo estimado desde cada nodo hasta el objetivo
# Estos valores se actualizan dinamicamente durante la busqueda
h = {
    "Tron": 6,      # Costo estimado desde Tron al MCP
    "Clu": 4,       # Costo estimado desde Clu al MCP
    "Flynn": 3,     # Costo estimado desde Flynn al MCP
    "Yori": 2,      # Costo estimado desde Yori al MCP
    "Sector7": 1,   # Costo estimado desde Sector7 al MCP
    "Bit": 1,       # Costo estimado desde Bit al MCP
    "Sark": 2,      # Costo estimado desde Sark al MCP
    "MCP": 0        # El MCP tiene costo 0 a si mismo
}


def ao_estrella(nodo, objetivo, visitados=None):
    """
    Funcion recursiva AO* con objetivo especifico.
    
    AO* evalua recursivamente todas las opciones AND-OR desde un nodo
    hasta alcanzar el objetivo, actualizando los valores heuristicos
    con la mejor estimacion encontrada.
    
    Parametros:
        nodo (str): Nodo actual que se esta evaluando.
        objetivo (str): Nodo objetivo que se desea alcanzar.
        visitados (set): Conjunto de nodos ya visitados en el camino actual.
        
    Retorna:
        float: Costo estimado minimo desde el nodo actual hasta el objetivo.
               Retorna infinito si no existe camino.
    """
    # Validar que el nodo actual exista en el grafo
    if nodo not in grafo_ao:
        print(f"Error: El nodo '{nodo}' no existe en el sistema")
        return float('inf')
    
    # Inicializar conjunto de visitados en la primera llamada recursiva
    if visitados is None:
        visitados = set()

    print(f"\nAnalizando nodo: {nodo}")

    # CASO BASE: Si ya llegamos al objetivo
    if nodo == objetivo:
        print(f"Nodo objetivo '{objetivo}' alcanzado.")
        return 0  # Costo 0 desde el objetivo a si mismo

    # Evitar ciclos infinitos: si el nodo ya fue visitado en este camino
    if nodo in visitados:
        print(f"Nodo {nodo} ya fue visitado, evitando ciclo.")
        return float('inf')

    # Marcar nodo como visitado en el camino actual
    visitados.add(nodo)

    # Si el nodo no tiene expansiones (es un nodo terminal sin solucion)
    if not grafo_ao.get(nodo, []):
        print(f"Nodo {nodo} no tiene expansiones validas.")
        return float('inf')

    # Listas para almacenar costos y rutas de todas las opciones
    costos_opciones = []  # Costo total de cada opcion OR
    rutas_opciones = []   # Ruta correspondiente a cada opcion

    # Evaluar todos los conjuntos AND-OR disponibles desde el nodo actual
    for indice, conjunto in enumerate(grafo_ao[nodo]):
        print(f"  Opcion {indice + 1}: Evaluando subrutas AND: {conjunto}")
        
        costo_total_conjunto = 0
        sub_ruta = []
        conjunto_valido = True

        # Para conjuntos AND, todos los nodos deben ser alcanzables
        for sub_nodo in conjunto:
            # Llamada recursiva para evaluar el sub-nodo
            # Se pasa una copia del conjunto de visitados para evitar ciclos
            costo_sub = ao_estrella(sub_nodo, objetivo, visitados.copy())
            
            # Si algun sub-nodo del conjunto AND es inalcanzable, toda la opcion es invalida
            if costo_sub == float('inf'):
                conjunto_valido = False
                print(f"    Sub-nodo {sub_nodo} es inalcanzable - descartando opcion AND")
                break
            
            costo_total_conjunto += costo_sub
            sub_ruta.append(sub_nodo)

        # Solo considerar opciones AND donde todos los sub-nodos son alcanzables
        if conjunto_valido:
            costos_opciones.append(costo_total_conjunto)
            rutas_opciones.append(sub_ruta)
            print(f"    Opcion AND valida: {sub_ruta} | Costo total: {costo_total_conjunto}")

    # Seleccionar la mejor opcion OR (la de menor costo)
    if costos_opciones:
        mejor_costo = min(costos_opciones) + 1  # +1 por el paso actual desde el nodo padre
        mejor_ruta = rutas_opciones[costos_opciones.index(min(costos_opciones))]
        
        print(f"Mejor opcion desde {nodo}: {mejor_ruta} | Costo estimado: {mejor_costo}")
        
        # Actualizar la heuristica con el mejor costo encontrado
        h[nodo] = mejor_costo
        return mejor_costo
    else:
        # Ninguna opcion OR es viable desde este nodo
        print(f"Todas las opciones desde {nodo} son inviables.")
        return float('inf')


def mostrar_grafo_ao():
    """
    Muestra el grafo AND-OR de forma legible.
    
    Explica la estructura de decisiones del sistema para ayudar
    a entender el comportamiento del algoritmo AO*.
    """
    print("\n" + "="*60)
    print("GRAFO AND-OR DEL SISTEMA TRON")
    print("="*60)
    print("Estructura: [opcion1], [opcion2] donde:")
    print("  - Opciones separadas por comas son OR (alternativas)")
    print("  - Nodos dentro de corchetes son AND (requieren todos)")
    print("="*60)
    
    for nodo, opciones in sorted(grafo_ao.items()):
        if opciones:
            opciones_str = []
            for conjunto in opciones:
                if len(conjunto) == 1:
                    opciones_str.append(f"SOLO {conjunto[0]}")  # OR simple
                else:
                    opciones_str.append(f"{' Y '.join(conjunto)}")  # AND multiple
            print(f"{nodo:10} -> O {' O '.join(opciones_str)}")
        else:
            print(f"{nodo:10} -> NODO TERMINAL")
    print("="*60)


def validar_nodo_entrada(entrada, grafo):
    """
    Valida que la entrada del usuario corresponda a un nodo existente.
    
    Parametros:
        entrada (str): Texto ingresado por el usuario.
        grafo (dict): Grafo del sistema para validar existencia.
        
    Retorna:
        bool: True si el nodo existe, False en caso contrario.
    """
    entrada_normalizada = entrada.strip()
    if entrada_normalizada.upper() == "MCP":
        entrada_normalizada = "MCP"
    else:
        entrada_normalizada = entrada_normalizada.title()
    
    return entrada_normalizada in grafo


def obtener_nodos_disponibles():
    """
    Retorna una lista de todos los nodos disponibles en el sistema.
    
    Retorna:
        list: Lista ordenada de nodos disponibles.
    """
    return sorted(grafo_ao.keys())


# PROGRAMA PRINCIPAL
def main():
    """
    Funcion principal que coordina la interaccion con el usuario
    y ejecuta el algoritmo de busqueda AO*.
    """
    print("SISTEMA DE BUSQUEDA AO* - RED DE DECISIONES")
    print("Algoritmo AND-OR Search para Planificacion Estrategica")
    
    # Mostrar la estructura del grafo AND-OR
    mostrar_grafo_ao()
    
    # Mostrar heuristicas iniciales
    print("\nHEURISTICAS INICIALES (estimaciones de costo):")
    for nodo, valor in sorted(h.items()):
        print(f"  {nodo}: {valor}")
    
    # Captura y validacion del nodo inicial
    while True:
        inicio = input("\nIngrese el nodo inicial (ej. Tron): ").strip()
        if validar_nodo_entrada(inicio, grafo_ao):
            if inicio.upper() == "MCP":
                inicio = "MCP"
            else:
                inicio = inicio.title()
            break
        else:
            print(f"Error: '{inicio}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))
    
    # Captura y validacion del nodo objetivo
    while True:
        objetivo = input("Ingrese el nodo objetivo (ej. MCP): ").strip()
        if validar_nodo_entrada(objetivo, grafo_ao):
            if objetivo.upper() == "MCP":
                objetivo = "MCP"
            else:
                objetivo = objetivo.title()
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(obtener_nodos_disponibles()))
    
    # Ejecutar busqueda AO*
    print(f"\nINICIANDO BUSQUEDA AO* DESDE '{inicio}' HACIA '{objetivo}'")
    print("=" * 50)
    
    costo_estimado = ao_estrella(inicio, objetivo)
    
    # Mostrar resultados finales
    print("\n" + "="*50)
    print("RESULTADO FINAL DE BUSQUEDA AO*")
    print("="*50)
    
    if costo_estimado < float('inf'):
        print(f"Costo estimado minimo desde {inicio} hasta {objetivo}: {costo_estimado} unidades")
        
        # Mostrar heuristicas actualizadas
        print("\nHeuristicas actualizadas despues de la busqueda:")
        for nodo, valor in sorted(h.items()):
            print(f"  {nodo}: {valor}")
        
        print("\nTron: 'El costo estimado minimo desde {inicio} hasta {objetivo} es {costo_estimado} unidades de energia.'")
        print("MCP: 'Tus decisiones fueron eficientes, Tron.'")
    else:
        print(f"No existe una ruta logica desde {inicio} hasta {objetivo} dentro de la red.")
        print("MCP: 'Tu busqueda ha colapsado en el vacio digital.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()