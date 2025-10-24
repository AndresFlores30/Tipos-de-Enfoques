# Tron explora la red digital recorriendo todos los nodos conectados
# mediante una Búsqueda en Profundidad (DFS).

from collections import defaultdict

# --- CONSTRUCCIÓN DE LA RED DIGITAL ---
class RedTron:
    """
    Representa la red de conexiones entre programas en el sistema TRON.
    """
    def __init__(self):
        self.red = defaultdict(list)

    def conectar(self, origen, destino):
        """
        Crea una conexión bidireccional entre dos programas.
        """
        self.red[origen].append(destino)
        self.red[destino].append(origen)

    def mostrar_conexiones(self):
        """
        Muestra todas las conexiones en la red.
        """
        print("\n Mapa digital de la red TRON:")
        for nodo, vecinos in self.red.items():
            print(f"{nodo} <-> {', '.join(vecinos)}")

    def busqueda_en_profundidad(self, inicio, visitados=None):
        """
        Realiza una búsqueda en profundidad (DFS) desde un nodo inicial.
        """
        if visitados is None:
            visitados = set()

        visitados.add(inicio)
        print(f" Tron ha accedido al nodo: {inicio}")

        for vecino in self.red[inicio]:
            if vecino not in visitados:
                self.busqueda_en_profundidad(vecino, visitados)

        return visitados


# --- SIMULACIÓN DE LA RED DIGITAL ---
tron_net = RedTron()

# Conectamos los programas (nodos del sistema)
tron_net.conectar("Tron", "Clu")
tron_net.conectar("Tron", "Flynn")
tron_net.conectar("Flynn", "Yori")
tron_net.conectar("Yori", "Sector7")
tron_net.conectar("Clu", "Sark")
tron_net.conectar("Sark", "Mcp")
tron_net.conectar("Sector7", "Bit")
tron_net.conectar("Bit", "Mcp")

# Mostrar mapa de la red
tron_net.mostrar_conexiones()

# --- EJECUTAR BÚSQUEDA ---
inicio = input("\nIngrese el nodo inicial para el escaneo (por ejemplo 'Tron'): ").title()
print("\n INICIANDO BÚSQUEDA EN LA RED DIGITAL \n")

nodos_visitados = tron_net.busqueda_en_profundidad(inicio)

print("\n--- RESULTADO DEL ESCANEO ---")
print("RUTA DE NODOS VISITADOS:", " -> ".join(nodos_visitados))
print("\n Tron: 'El escaneo del sistema ha sido completado con éxito.'")