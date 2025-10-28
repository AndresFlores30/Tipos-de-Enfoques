"""
SISTEMA DE BÚSQUEDA EN PROFUNDIDAD LIMITADA (DLS) - TRON DIGITAL

Este módulo implementa el algoritmo de Depth-Limited Search (DLS) para
explorar de manera controlada el sistema digital de TRON, estableciendo
límites de profundidad para prevenir sobrecargas del sistema.
"""

# RED DIGITAL DEL SISTEMA TRON
# Representa la estructura de conexiones entre programas y sectores del sistema
# Cada clave es un nodo y su valor es una lista de nodos vecinos conectados
sistema_tron = {
    "Tron": ["Clu", "Flynn", "Yori"],      # Tron conectado con sus aliados principales
    "Clu": ["Sark", "Tron"],               # Clu conectado con Sark y Tron
    "Flynn": ["Tron", "Yori", "Sark"],     # Flynn con múltiples conexiones
    "Yori": ["Flynn", "Sector7"],          # Yori como puente hacia sectores periféricos
    "Sark": ["Clu", "Flynn", "Mcp"],       # Sark conectado con el MCP
    "Sector7": ["Yori", "Bit"],            # Sector periférico del sistema
    "Bit": ["Sector7", "Mcp"],             # Bit como conexión intermedia
    "Mcp": ["Sark", "Bit"]                 # MCP (Control Principal) con conexiones limitadas
}


def busqueda_profundidad_limitada(grafo, inicio, objetivo, limite, nivel=0, camino=None):
    """
    Realiza una Búsqueda en Profundidad Limitada (DLS) en la red TRON.
    
    DLS es una variante de DFS que establece un límite máximo de profundidad
    para prevenir la exploración infinita y el consumo excesivo de recursos.

    Parámetros:
        grafo (dict): Estructura del sistema digital representada como diccionario de adyacencia.
        inicio (str): Nodo inicial desde donde comienza la búsqueda.
        objetivo (str): Nodo destino que se desea encontrar.
        limite (int): Profundidad máxima permitida para la exploración.
        nivel (int): Nivel actual de profundidad en la búsqueda (para recursión).
        camino (list): Ruta actual recorrida hasta el momento (para recursión).

    Retorna:
        list or None: Camino completo hacia el objetivo si se encuentra dentro del límite,
                     None si no se encuentra o se excede el límite.
    """
    # Validar que los nodos existan en el grafo antes de comenzar la búsqueda
    if inicio not in grafo:
        print(f"ERROR: El nodo '{inicio}' no existe en el sistema TRON")
        return None
    if objetivo not in grafo:
        print(f"ERROR: El nodo '{objetivo}' no existe en el sistema TRON")
        return None
    
    # Inicializar el camino si es la primera llamada recursiva
    if camino is None:
        camino = []

    # Registrar el nodo actual en el camino de exploración
    camino.append(inicio)
    
    # Mostrar progreso de la búsqueda para monitoreo en tiempo real
    indentacion = "  " * nivel  # Sangría para visualizar niveles de profundidad
    print(f"{indentacion}Nivel {nivel}: Explorando nodo [{inicio}]")

    # CASO BASE 1: Objetivo encontrado
    # Si el nodo actual es el objetivo, retornar el camino exitoso
    if inicio == objetivo:
        print(f"{indentacion}¡OBJETIVO ENCONTRADO en el nivel {nivel}!")
        return camino

    # CASO BASE 2: Límite de profundidad alcanzado
    # Si se alcanza el límite máximo, detener la exploración en esta rama
    if nivel >= limite:
        print(f"{indentacion}LÍMITE ALCANZADO en nodo [{inicio}]. Retrocediendo...")
        camino.pop()  # Remover el nodo actual del camino antes de retroceder
        return None

    # FASE DE EXPLORACIÓN: Examinar todos los vecinos del nodo actual
    # Se exploran recursivamente los nodos adyacentes no visitados
    for vecino in grafo.get(inicio, []):
        # Evitar ciclos verificando que el vecino no esté en el camino actual
        if vecino not in camino:
            print(f"{indentacion}-> Explorando vecino: {vecino}")
            
            # Llamada recursiva con incremento del nivel de profundidad
            # Se pasa una copia del camino para evitar modificaciones no deseadas
            resultado = busqueda_profundidad_limitada(
                grafo, 
                vecino, 
                objetivo, 
                limite, 
                nivel + 1, 
                list(camino)  # Copia del camino para mantener estado separado
            )
            
            # Si se encontró el objetivo en la rama actual, propagar el resultado
            if resultado is not None:
                return resultado

    # FASE DE RETROCESO: Ningún vecino llevó al objetivo
    # Si se agotan todas las opciones sin encontrar el objetivo, retroceder
    print(f"{indentacion}Agotadas todas las opciones desde [{inicio}]. Retrocediendo...")
    camino.pop()  # Remover el nodo actual del camino antes de retroceder
    return None


def mostrar_mapa_sistema():
    """
    Muestra el mapa completo del sistema TRON con todas las conexiones disponibles.
    
    Esta función ayuda al usuario a entender la estructura de la red
    antes de realizar una búsqueda.
    """
    print("\n" + "="*50)
    print("MAPA COMPLETO DEL SISTEMA TRON")
    print("="*50)
    for nodo, conexiones in sistema_tron.items():
        print(f"* {nodo}: conectado con {', '.join(conexiones)}")
    print("="*50)


def validar_entrada_nodo(entrada, grafo):
    """
    Valida que la entrada del usuario corresponda a un nodo existente en el sistema.
    
    Parámetros:
        entrada (str): Texto ingresado por el usuario.
        grafo (dict): Grafo del sistema para validar existencia.
        
    Retorna:
        bool: True si el nodo existe, False en caso contrario.
    """
    entrada_normalizada = entrada.strip().title()
    return entrada_normalizada in grafo


def validar_limite_profundidad(limite_str):
    """
    Valida que el límite de profundidad sea un número entero positivo.
    
    Parámetros:
        limite_str (str): Cadena ingresada por el usuario.
        
    Retorna:
        int or None: Límite validado como entero, o None si es inválido.
    """
    try:
        limite = int(limite_str)
        if limite < 1:
            print("Error: El límite debe ser un número positivo mayor a 0")
            return None
        return limite
    except ValueError:
        print("Error: El límite debe ser un número entero válido")
        return None


# PROGRAMA PRINCIPAL
def main():
    """
    Función principal que coordina la interacción con el usuario
    y ejecuta el algoritmo de búsqueda en profundidad limitada.
    """
    print("SISTEMA DIGITAL TRON ONLINE")
    print("Búsqueda profunda con límite de seguridad activado...\n")
    
    # Mostrar el mapa del sistema para referencia del usuario
    mostrar_mapa_sistema()
    
    # FASE 1: Captura y validación del nodo de inicio
    while True:
        inicio = input("\n Ingrese el programa de inicio: ").strip().title()
        if validar_entrada_nodo(inicio, sistema_tron):
            break
        else:
            print(f"Error: '{inicio}' no existe en el sistema TRON")
            print("   Nodos disponibles:", ", ".join(sistema_tron.keys()))
    
    # FASE 2: Captura y validación del nodo objetivo
    while True:
        objetivo = input(" Ingrese el programa destino: ").strip().title()
        if validar_entrada_nodo(objetivo, sistema_tron):
            break
        else:
            print(f"Error: '{objetivo}' no existe en el sistema TRON")
            print("   Nodos disponibles:", ", ".join(sistema_tron.keys()))
    
    # FASE 3: Captura y validación del límite de profundidad
    while True:
        limite_str = input(" Ingrese el límite de profundidad (nivel máximo permitido): ").strip()
        limite = validar_limite_profundidad(limite_str)
        if limite is not None:
            break
    
    # FASE 4: Ejecutar la búsqueda en profundidad limitada
    print(f"\n Iniciando búsqueda desde '{inicio}' hacia '{objetivo}'")
    print(f"   Límite de profundidad establecido: {limite} niveles")
    print("\n" + "="*50)
    print("PROGRESO DE LA BÚSQUEDA:")
    print("="*50)
    
    resultado = busqueda_profundidad_limitada(sistema_tron, inicio, objetivo, limite)
    
    # FASE 5: Mostrar resultados de la búsqueda
    print("\n" + "="*50)
    print("RESULTADOS FINALES DE LA BÚSQUEDA")
    print("="*50)
    
    if resultado:
        print(f" RUTA ENCONTRADA dentro del límite de {limite} niveles:")
        print("   " + " -> ".join(resultado))
        print(f"   Longitud del camino: {len(resultado)-1} saltos")
        print(f"   Profundidad alcanzada: {len(resultado)-1} niveles")
        print("\n Tron: 'El objetivo fue localizado antes de sobrecargar la red.'")
    else:
        print(f" No se encontró el objetivo dentro del límite de {limite} niveles.")
        print("   Posibles causas:")
        print("   • El objetivo está más profundo que el límite establecido")
        print("   • No existe conexión entre los nodos seleccionados")
        print("   • El camino requiere más recursos de los permitidos")
        print("\n  MCP: 'El acceso fue restringido por seguridad del sistema.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()