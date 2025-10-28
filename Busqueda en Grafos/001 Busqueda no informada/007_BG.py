"""
SISTEMA DE EXPLORACION COMPLETA CON BUSQUEDA EN PROFUNDIDAD - TRON DIGITAL

Este modulo implementa una busqueda en profundidad (DFS) que recorre
completamente la red digital de TRON, visitando todos los nodos conectados
desde un punto de inicio especifico.
"""

from collections import defaultdict


class RedTron:
    """
    Representa la red de conexiones entre programas en el sistema TRON.
    
    Esta clase modela la topologia de la red digital utilizando un grafo
    no dirigido y proporciona metodos para realizar busquedas exhaustivas.
    """
    
    def __init__(self):
        """
        Inicializa una nueva red TRON vacia.
        
        Utiliza defaultdict para automaticamente crear listas vacias
        cuando se accede a nodos que no existen previamente.
        """
        self.red = defaultdict(list)  # Diccionario que mapea nodos a sus vecinos

    def conectar(self, origen, destino):
        """
        Crea una conexion bidireccional entre dos programas.
        
        En el sistema TRON, las conexiones son simetricas - si un programa
        puede comunicarse con otro, la conexion funciona en ambos sentidos.
        
        Parametros:
            origen (str): Primer programa a conectar.
            destino (str): Segundo programa a conectar.
        """
        # Agregar destino como vecino de origen
        self.red[origen].append(destino)
        # Agregar origen como vecino de destino (conexion bidireccional)
        self.red[destino].append(origen)

    def mostrar_conexiones(self):
        """
        Muestra todas las conexiones en la red de forma organizada.
        
        Proporciona una vision completa de la topologia del sistema
        para ayudar en la planificacion de exploraciones.
        """
        print("\n" + "="*50)
        print("MAPA DIGITAL DE LA RED TRON")
        print("="*50)
        for nodo, vecinos in sorted(self.red.items()):
            print(f"{nodo}: conectado con {', '.join(sorted(vecinos))}")
        print("="*50)

    def busqueda_en_profundidad(self, inicio, visitados=None):
        """
        Realiza una busqueda en profundidad (DFS) desde un nodo inicial.
        
        Este algoritmo recorre recursivamente todos los nodos conectados
        al nodo inicial, explorando cada rama completamente antes de
        retroceder (backtracking).
        
        Parametros:
            inicio (str): Nodo desde donde comenzar la exploracion.
            visitados (set): Conjunto de nodos ya visitados (uso interno recursivo).
            
        Retorna:
            set: Conjunto de todos los nodos visitados durante la exploracion.
        """
        # Validar que el nodo inicial exista en la red
        if inicio not in self.red:
            print(f"Error: El nodo '{inicio}' no existe en la red TRON")
            return set()
        
        # Inicializar conjunto de visitados en la primera llamada recursiva
        if visitados is None:
            visitados = set()

        # Marcar el nodo actual como visitado
        visitados.add(inicio)
        
        # Mostrar el progreso de la exploracion
        print(f"Tron ha accedido al nodo: {inicio}")

        # Explorar recursivamente todos los vecinos no visitados
        for vecino in self.red[inicio]:
            if vecino not in visitados:
                # Llamada recursiva para explorar el vecino
                self.busqueda_en_profundidad(vecino, visitados)

        # Retornar el conjunto completo de nodos visitados
        return visitados

    def obtener_nodos_disponibles(self):
        """
        Retorna una lista de todos los nodos existentes en la red.
        
        Util para validar entradas del usuario y mostrar opciones disponibles.
        
        Retorna:
            list: Lista ordenada de todos los nodos en la red.
        """
        return sorted(self.red.keys())


def inicializar_red_tron():
    """
    Inicializa y configura la red TRON con las conexiones predeterminadas.
    
    Retorna:
        RedTron: Instancia de la red configurada con todas las conexiones.
    """
    red = RedTron()
    
    # Establecer todas las conexiones del sistema TRON
    # Conexiones principales del programa Tron
    red.conectar("Tron", "Clu")
    red.conectar("Tron", "Flynn")
    
    # Conexiones de Flynn hacia otros programas
    red.conectar("Flynn", "Yori")
    
    # Expansion hacia sectores perifericos
    red.conectar("Yori", "Sector7")
    
    # Conexiones del sistema de control
    red.conectar("Clu", "Sark")
    red.conectar("Sark", "Mcp")
    
    # Conexiones del sector periferico
    red.conectar("Sector7", "Bit")
    red.conectar("Bit", "Mcp")
    
    return red


def validar_entrada_usuario(entrada, red):
    """
    Valida que la entrada del usuario corresponda a un nodo existente.
    
    Parametros:
        entrada (str): Texto ingresado por el usuario.
        red (RedTron): Instancia de la red para validar existencia.
        
    Retorna:
        bool: True si el nodo existe, False en caso contrario.
    """
    entrada_normalizada = entrada.strip().title()
    return entrada_normalizada in red.obtener_nodos_disponibles()


# PROGRAMA PRINCIPAL
def main():
    """
    Funcion principal que coordina la inicializacion del sistema,
    la interaccion con el usuario y la ejecucion de la exploracion DFS.
    """
    print("SISTEMA DIGITAL TRON ONLINE")
    print("Protocolo de exploracion completa activado...")
    
    # Inicializar la red TRON con las conexiones predeterminadas
    tron_net = inicializar_red_tron()
    
    # Mostrar el mapa completo de la red
    tron_net.mostrar_conexiones()
    
    # Captura y validacion del nodo inicial
    while True:
        inicio = input("\nIngrese el nodo inicial para el escaneo (por ejemplo 'Tron'): ").strip().title()
        if validar_entrada_usuario(inicio, tron_net):
            break
        else:
            print(f"Error: El nodo '{inicio}' no existe en el sistema TRON")
            print("Nodos disponibles:", ", ".join(tron_net.obtener_nodos_disponibles()))
    
    # Ejecutar busqueda en profundidad
    print("\nINICIANDO BUSQUEDA EN LA RED DIGITAL")
    print("="*40)
    
    nodos_visitados = tron_net.busqueda_en_profundidad(inicio)
    
    # Mostrar resultados finales de la exploracion
    print("\n" + "="*50)
    print("RESULTADO DEL ESCANEO COMPLETO")
    print("="*50)
    
    if nodos_visitados:
        # Convertir el conjunto a lista ordenada para mejor presentacion
        nodos_ordenados = sorted(nodos_visitados)
        print("RUTA DE NODOS VISITADOS:", " -> ".join(nodos_ordenados))
        print(f"Total de nodos explorados: {len(nodos_visitados)}")
        print(f"Porcentaje de red cubierta: {(len(nodos_visitados)/len(tron_net.red))*100:.1f}%")
        
        # Verificar si se exploró toda la red
        if len(nodos_visitados) == len(tron_net.red):
            print("\nTron: 'Exploracion completa del sistema finalizada con exito.'")
        else:
            print("\nTron: 'Se han identificado componentes desconectados en el sistema.'")
    else:
        print("No se pudo realizar la exploracion.")
        print("MCP: 'El acceso al sistema ha sido denegado.'")


# Punto de entrada del programa
if __name__ == "__main__":
    main()