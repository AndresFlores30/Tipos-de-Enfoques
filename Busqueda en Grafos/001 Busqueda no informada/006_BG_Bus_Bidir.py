"""
SISTEMA DE BUSQUEDA BIDIRECCIONAL - TRON DIGITAL

Este modulo implementa el algoritmo de Busqueda Bidireccional que ejecuta
dos busquedas BFS simultaneas desde ambos extremos del grafo, encontrandose
en un punto intermedio para formar el camino completo.
"""

from collections import deque

# --- RED DIGITAL DEL SISTEMA TRON ---
# Diccionario que representa la topologia de conexiones del sistema TRON
# Cada programa/sector tiene una lista de conexiones directas
red_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],      # Programa principal con multiples aliados
    "Clu": ["Tron", "Sark"],               # Programa de control con conexiones estrategicas
    "Flynn": ["Tron", "Yori", "Sark"],     # Usuario con acceso amplio al sistema
    "Yori": ["Flynn", "Sector7"],          # Especialista en sectores perifericos
    "Sark": ["Clu", "Flynn", "Mcp"],       # Programa de seguridad del MCP
    "Sector7": ["Yori", "Bit"],            # Sector de almacenamiento periferico
    "Bit": ["Sector7", "Mcp"],             # Programa de transmision de datos
    "Mcp": ["Sark", "Bit"]                 # Control Principal del sistema
}


def busqueda_bidireccional(grafo, inicio, objetivo):
    """
    Realiza una busqueda bidireccional en la red TRON.
    
    Este algoritmo ejecuta dos busquedas BFS simultaneas: una desde el nodo inicial
    y otra desde el nodo objetivo. Cuando ambos frentes se encuentran en un nodo
    comun, se reconstruye el camino completo.

    Parametros:
        grafo (dict): Representacion de la red digital como diccionario de adyacencia.
        inicio (str): Nodo inicial desde donde comienza la primera busqueda.
        objetivo (str): Nodo objetivo desde donde comienza la segunda busqueda.

    Retorna:
        list or None: Ruta completa entre inicio y objetivo si existe, 
                     None si no hay conexion.
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

    # --- INICIALIZACION DE ESTRUCTURAS DE DATOS ---
    
    # Colas para almacenar los caminos en exploracion
    # Cada elemento en la cola es una lista que representa un camino parcial
    frente_inicio = deque([[inicio]])      # Cola de caminos desde el nodo inicial
    frente_objetivo = deque([[objetivo]])  # Cola de caminos desde el nodo objetivo

    # Conjuntos para registrar nodos visitados por cada frente
    # Esto evita ciclos y permite detectar cuando los frentes se encuentran
    visitados_inicio = {inicio}      # Nodos visitados desde el inicio
    visitados_objetivo = {objetivo}  # Nodos visitados desde el objetivo

    print("\nPROTOCOLO DE BUSQUEDA BIDIRECCIONAL ACTIVADO")

    # --- BUCLE PRINCIPAL DE BUSQUEDA ---
    # Continua mientras ambas colas tengan caminos por explorar
    while frente_inicio and frente_objetivo:
        
        # --- EXPANSION DESDE EL FRENTE DEL INICIO ---
        camino_inicio = frente_inicio.popleft()          # Extraer el siguiente camino a expandir
        nodo_actual_inicio = camino_inicio[-1]          # Ultimo nodo del camino actual
        print(f"Explorando desde inicio: {nodo_actual_inicio}")

        # Explorar todos los vecinos del nodo actual
        for vecino in grafo.get(nodo_actual_inicio, []):
            if vecino not in visitados_inicio:
                # Construir nuevo camino extendiendo el actual
                nuevo_camino_inicio = list(camino_inicio) + [vecino]
                frente_inicio.append(nuevo_camino_inicio)
                visitados_inicio.add(vecino)

                # Verificar si este vecino ha sido visitado por el frente opuesto
                if vecino in visitados_objetivo:
                    print(f"Conexion detectada en nodo: {vecino}")
                    # Se encontro conexion, reconstruir camino completo
                    return construir_camino_completo(nuevo_camino_inicio, frente_objetivo, vecino)

        # --- EXPANSION DESDE EL FRENTE DEL OBJETIVO ---
        camino_objetivo = frente_objetivo.popleft()      # Extraer el siguiente camino a expandir
        nodo_actual_objetivo = camino_objetivo[-1]      # Ultimo nodo del camino actual
        print(f"Explorando desde objetivo: {nodo_actual_objetivo}")

        # Explorar todos los vecinos del nodo actual
        for vecino in grafo.get(nodo_actual_objetivo, []):
            if vecino not in visitados_objetivo:
                # Construir nuevo camino extendiendo el actual
                nuevo_camino_objetivo = list(camino_objetivo) + [vecino]
                frente_objetivo.append(nuevo_camino_objetivo)
                visitados_objetivo.add(vecino)

                # Verificar si este vecino ha sido visitado por el frente opuesto
                if vecino in visitados_inicio:
                    print(f"Conexion detectada en nodo: {vecino}")
                    # Se encontro conexion, reconstruir camino completo
                    return construir_camino_completo(frente_inicio, nuevo_camino_objetivo, vecino)

    # Si alguna cola se vacia sin encontrar conexion, no existe camino
    return None


def construir_camino_completo(camino_inicio, frente_opuesto, punto_encuentro):
    """
    Combina los caminos desde ambos frentes en el punto de encuentro.
    
    Toma el camino desde un frente y busca el camino correspondiente en el
    frente opuesto que termina en el mismo nodo de encuentro, luego los
    combina para formar el camino completo.

    Parametros:
        camino_inicio (list or deque): Camino desde el frente inicial o cola de caminos.
        frente_opuesto (deque or list): Cola de caminos o camino individual del frente opuesto.
        punto_encuentro (str): Nodo donde ambos frentes se encontraron.

    Retorna:
        list: Camino completo desde inicio hasta objetivo.
    """
    # Determinar cual parametro es el camino y cual es la cola
    if isinstance(camino_inicio, deque):
        # camino_inicio es realmente la cola, buscar el camino que termina en punto_encuentro
        camino_desde_inicio = None
        for ruta in camino_inicio:
            if ruta[-1] == punto_encuentro:
                camino_desde_inicio = ruta
                break
        camino_desde_objetivo = frente_opuesto
    else:
        # camino_inicio es el camino correcto
        camino_desde_inicio = camino_inicio
        camino_desde_objetivo = None
        # Buscar en la cola del frente opuesto el camino que termina en punto_encuentro
        for ruta in frente_opuesto:
            if ruta[-1] == punto_encuentro:
                camino_desde_objetivo = ruta
                break

    # Si no se encuentra el camino correspondiente, retornar solo uno de los caminos
    if not camino_desde_objetivo:
        return camino_desde_inicio

    # Combinar ambos caminos: desde inicio (sin duplicar punto_encuentro) + 
    # camino desde objetivo invertido
    # Ejemplo: [A, B, C] + [E, D, C].invertido() = [A, B, C, D, E]
    camino_final = camino_desde_inicio[:-1] + camino_desde_objetivo[::-1]
    return camino_final


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con todas las conexiones.
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


# PROGRAMA PRINCIPAL
def main():
    """
    Funcion principal que coordina la interaccion con el usuario
    y ejecuta el algoritmo de busqueda bidireccional.
    """
    print("SISTEMA DIGITAL TRON ONLINE")
    
    # Mostrar el mapa del sistema para referencia del usuario
    mostrar_mapa_sistema()
    
    # Captura y validacion del nodo de inicio
    while True:
        inicio = input("\nIngrese el programa inicial: ").strip().title()
        if validar_entrada_nodo(inicio, red_tron):
            break
        else:
            print(f"Error: '{inicio}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(red_tron.keys()))
    
    # Captura y validacion del nodo objetivo
    while True:
        objetivo = input("Ingrese el programa objetivo: ").strip().title()
        if validar_entrada_nodo(objetivo, red_tron):
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(red_tron.keys()))
    
    # Ejecutar busqueda bidireccional
    ruta = busqueda_bidireccional(red_tron, inicio, objetivo)
    
    # Mostrar resultados finales
    print("\n--- RESULTADO FINAL ---")
    if ruta:
        print("Ruta encontrada:")
        print(" -> ".join(ruta))
        print(f"Longitud del camino: {len(ruta)-1} saltos")
        print("\nTron: 'Conexion establecida entre ambos extremos de la red.'")
    else:
        print("No se encontro conexion entre los programas.")
        print("MCP: 'Tus intentos de interceptar mi red han fallado, Tron.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()