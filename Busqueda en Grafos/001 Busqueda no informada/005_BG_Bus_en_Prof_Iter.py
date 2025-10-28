"""
SISTEMA DE BUSQUEDA EN PROFUNDIDAD ITERATIVA (IDDFS) - TRON DIGITAL

Este modulo implementa el algoritmo Iterative Deepening Depth-First Search (IDDFS)
para realizar busquedas progresivas en el sistema digital de TRON, combinando
la completitud de BFS con la eficiencia en memoria de DFS.
"""

# RED DIGITAL DEL SISTEMA TRON
# Diccionario que representa la topologia de la red de TRON
# Cada clave es un programa o sector y su valor es la lista de conexiones directas
red_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],      # Programa principal con multiples conexiones
    "Clu": ["Sark", "Tron"],               # Programa de control con conexiones limitadas
    "Flynn": ["Tron", "Yori", "Sark"],     # Usuario con acceso amplio al sistema
    "Yori": ["Flynn", "Sector7"],          # Programa especializado en sectores perifericos
    "Sark": ["Clu", "Flynn", "Mcp"],       # Programa de seguridad conectado al MCP
    "Sector7": ["Yori", "Bit"],            # Sector periferico del sistema
    "Bit": ["Sector7", "Mcp"],             # Programa de transmision de datos
    "Mcp": ["Sark", "Bit"]                 # Control Principal del sistema
}


def busqueda_profundidad_limitada(grafo, inicio, objetivo, limite, nivel=0, camino=None):
    """
    Realiza una busqueda en profundidad limitada (DLS) dentro del sistema TRON.
    
    Esta funcion es el componente base del algoritmo IDDFS y realiza una
    busqueda en profundidad hasta un limite especifico.

    Parametros:
        grafo (dict): Representacion de la red TRON como diccionario de adyacencia.
        inicio (str): Nodo inicial desde donde comienza la busqueda.
        objetivo (str): Nodo destino que se desea encontrar.
        limite (int): Profundidad maxima permitida para esta iteracion.
        nivel (int): Nivel actual de profundidad en la exploracion (para recursion).
        camino (list): Ruta actual recorrida hasta el momento (para recursion).

    Retorna:
        list or None: Ruta completa hacia el objetivo si se encuentra dentro del limite,
                     None si no se encuentra o se excede el limite.
    """
    # Inicializar el camino si es la primera llamada recursiva
    if camino is None:
        camino = []

    # Agregar el nodo actual al camino de exploracion
    camino.append(inicio)
    
    # Mostrar el progreso de la exploracion para seguimiento
    print(f"Nivel {nivel}: Explorando {inicio}")

    # CASO BASE 1: Objetivo encontrado
    # Si el nodo actual es el objetivo, retornar el camino exitoso
    if inicio == objetivo:
        return camino

    # CASO BASE 2: Limite de profundidad alcanzado
    # Si se alcanza el limite maximo, detener la exploracion en esta rama
    if nivel >= limite:
        return None

    # FASE DE EXPLORACION: Examinar todos los vecinos del nodo actual
    for vecino in grafo.get(inicio, []):
        # Evitar ciclos verificando que el vecino no este en el camino actual
        if vecino not in camino:
            # Llamada recursiva con incremento del nivel de profundidad
            # Se pasa una copia del camino para mantener estados separados
            resultado = busqueda_profundidad_limitada(
                grafo, 
                vecino, 
                objetivo, 
                limite, 
                nivel + 1, 
                list(camino)  # Copia para evitar modificaciones no deseadas
            )
            
            # Si se encontro el objetivo en la rama actual, propagar el resultado
            if resultado is not None:
                return resultado

    # Si no se encontro el objetivo en ninguna rama, retornar None
    return None


def busqueda_profundidad_iterativa(grafo, inicio, objetivo, limite_max):
    """
    Realiza la Busqueda en Profundidad Iterativa (IDDFS).
    
    IDDFS ejecuta multiples iteraciones de DLS, incrementando progresivamente
    el limite de profundidad en cada iteracion. Esto combina la completitud
    de BFS con la eficiencia en memoria de DFS.

    Parametros:
        grafo (dict): Red TRON representada como diccionario de adyacencia.
        inicio (str): Nodo inicial de la busqueda.
        objetivo (str): Nodo objetivo que se desea encontrar.
        limite_max (int): Profundidad maxima total permitida para la busqueda.

    Retorna:
        list or None: Camino encontrado hacia el objetivo si existe,
                     None si no se localiza dentro del limite maximo.
    """
    # Validar que los nodos existan en el grafo
    if inicio not in grafo:
        print(f"Error: El nodo '{inicio}' no existe en el sistema TRON")
        return None
    if objetivo not in grafo:
        print(f"Error: El nodo '{objetivo}' no existe en el sistema TRON")
        return None
    
    # Caso especial: inicio y objetivo son el mismo nodo
    if inicio == objetivo:
        return [inicio]
    
    # Ejecutar iteraciones progresivas incrementando el limite de profundidad
    for limite_actual in range(limite_max + 1):
        print(f"\n--- Iteracion con limite de profundidad: {limite_actual} ---")
        
        # Ejecutar busqueda en profundidad con el limite actual
        resultado = busqueda_profundidad_limitada(grafo, inicio, objetivo, limite_actual)
        
        # Si se encontro el objetivo en esta iteracion, retornar el resultado
        if resultado is not None:
            print(f"Objetivo localizado con limite {limite_actual}")
            return resultado
            
        # Si no se encontro, continuar con la siguiente iteracion con limite mayor
    
    # Si ninguna iteracion encontro el objetivo, retornar None
    return None


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con todas las conexiones.
    
    Proporciona al usuario una vision general de la estructura de la red
    antes de iniciar la busqueda.
    """
    print("\n" + "="*50)
    print("MAPA DEL SISTEMA TRON")
    print("="*50)
    for nodo, conexiones in red_tron.items():
        print(f"{nodo}: conectado con {', '.join(conexiones)}")
    print("="*50)


def validar_entrada_nodo(entrada, grafo):
    """
    Valida que la entrada del usuario corresponda a un nodo existente.
    
    Parametros:
        entrada (str): Texto ingresado por el usuario.
        grafo (dict): Grafo del sistema para validar existencia.
        
    Retorna:
        bool: True si el nodo existe, False en caso contrario.
    """
    entrada_normalizada = entrada.strip().title()
    return entrada_normalizada in grafo


def validar_limite_maximo(limite_str):
    """
    Valida que el limite maximo sea un numero entero positivo.
    
    Parametros:
        limite_str (str): Cadena ingresada por el usuario.
        
    Retorna:
        int or None: Limite validado como entero, o None si es invalido.
    """
    try:
        limite = int(limite_str)
        if limite < 0:
            print("Error: El limite debe ser un numero no negativo")
            return None
        return limite
    except ValueError:
        print("Error: El limite debe ser un numero entero valido")
        return None


# PROGRAMA PRINCIPAL
def main():
    """
    Funcion principal que coordina la interaccion con el usuario
    y ejecuta el algoritmo de busqueda en profundidad iterativa.
    """
    print("SISTEMA DIGITAL TRON ONLINE")
    print("Protocolo de busqueda iterativa activado...")
    
    # Mostrar el mapa del sistema para referencia del usuario
    mostrar_mapa_sistema()
    
    # FASE 1: Captura y validacion del nodo de inicio
    while True:
        inicio = input("\nIngrese el programa inicial: ").strip().title()
        if validar_entrada_nodo(inicio, red_tron):
            break
        else:
            print(f"Error: '{inicio}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(red_tron.keys()))
    
    # FASE 2: Captura y validacion del nodo objetivo
    while True:
        objetivo = input("Ingrese el programa objetivo: ").strip().title()
        if validar_entrada_nodo(objetivo, red_tron):
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(red_tron.keys()))
    
    # FASE 3: Captura y validacion del limite maximo
    while True:
        limite_str = input("Ingrese el limite maximo de profundidad: ").strip()
        limite_max = validar_limite_maximo(limite_str)
        if limite_max is not None:
            break
    
    # FASE 4: Ejecutar busqueda en profundidad iterativa
    print(f"\nIniciando busqueda iterativa desde '{inicio}' hacia '{objetivo}'")
    print(f"Limite maximo establecido: {limite_max} niveles")
    
    ruta = busqueda_profundidad_iterativa(red_tron, inicio, objetivo, limite_max)
    
    # FASE 5: Mostrar resultados finales
    print("\n--- RESULTADO FINAL ---")
    if ruta:
        print("Ruta encontrada:")
        print(" -> ".join(ruta))
        print(f"Profundidad requerida: {len(ruta)-1} niveles")
        print("\nTron: 'Objetivo encontrado a traves de escaneos iterativos.'")
    else:
        print("El objetivo no fue localizado dentro del limite establecido.")
        print("MCP: 'La red ha sido bloqueada antes de la deteccion final.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()