"""
SISTEMA DE NAVEGACION CON BACKTRACKING - GRID DE TRON

Este modulo implementa algoritmos de backtracking para encontrar rutas
desde la Base hasta el Nucleo Central en el Grid de TRON, evitando firewalls.
Utiliza Depth-First Search (DFS) con vuelta atras para explorar sistematicamente
todas las rutas posibles.
"""

from typing import List, Tuple, Optional

# Tipo de dato para posiciones en el grid (fila, columna)
Pos = Tuple[int, int]

# ============================================================
# CONFIGURACION DEL GRID DE TRON
# ============================================================

# Definicion del Grid:
#   'S' = Base (origen/Start)
#   'G' = Nucleo_Central (meta/Goal)  
#   'X' = firewall (bloqueado)
#   ' ' = celda libre
GRID = [
    list("S   X     "),
    list(" XX   XXX "),
    list("   X      "),
    list(" XXX XXX  "),
    list("    X   X "),
    list(" XX   X   "),
    list("   X   X  "),
    list(" X   XXX  "),
    list("   X    G "),
]

# Movimientos permitidos: arriba, derecha, abajo, izquierda
MOVIMIENTOS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
NOMBRES_MOVIMIENTOS = {(-1, 0): "U", (0, 1): "R", (1, 0): "D", (0, -1): "L"}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def encontrar_posicion(grid: List[List[str]], caracter: str) -> Pos:
    """
    Encuentra la posicion de un caracter en el grid.
    
    Parametros:
        grid: Matriz que representa el grid de TRON
        caracter: Caracter a buscar ('S', 'G', etc.)
        
    Retorna:
        Pos: Tupla (fila, columna) de la posicion encontrada
        
    Lanza:
        ValueError: Si el caracter no se encuentra en el grid
    """
    for fila, lista_caracteres in enumerate(grid):
        for columna, caracter_actual in enumerate(lista_caracteres):
            if caracter_actual == caracter:
                return (fila, columna)
    raise ValueError(f"No se encontro el simbolo '{caracter}' en el grid.")


def esta_dentro_grid(grid: List[List[str]], fila: int, columna: int) -> bool:
    """
    Verifica si una posicion esta dentro de los limites del grid.
    
    Parametros:
        grid: Matriz del grid
        fila: Indice de fila
        columna: Indice de columna
        
    Retorna:
        bool: True si la posicion es valida
    """
    return 0 <= fila < len(grid) and 0 <= columna < len(grid[0])


def es_celda_libre(grid: List[List[str]], fila: int, columna: int) -> bool:
    """
    Verifica si una celda es transitable.
    
    Parametros:
        grid: Matriz del grid
        fila: Indice de fila
        columna: Indice de columna
        
    Retorna:
        bool: True si la celda es libre (' ') o es el objetivo ('G')
    """
    return grid[fila][columna] in (" ", "G")


def renderizar_grid(grid: List[List[str]]) -> str:
    """
    Convierte el grid a una cadena de texto para visualizacion.
    
    Parametros:
        grid: Matriz a visualizar
        
    Retorna:
        str: Representacion en texto del grid
    """
    return "\n".join("".join(fila) for fila in grid)


def marcar_camino_en_grid(grid: List[List[str]], camino: List[Pos], marca: str = ".") -> List[List[str]]:
    """
    Crea una copia del grid marcando las posiciones del camino.
    
    Parametros:
        grid: Grid original
        camino: Lista de posiciones a marcar
        marca: Caracter para marcar las celdas del camino
        
    Retorna:
        List[List[str]]: Nueva matriz con el camino marcado
    """
    copia_grid = [fila.copy() for fila in grid]
    for (fila, columna) in camino:
        if copia_grid[fila][columna] == " ":
            copia_grid[fila][columna] = marca
    return copia_grid


# ============================================================
# ALGORITMOS DE BACKTRACKING
# ============================================================

def backtracking_un_camino(grid: List[List[str]], max_pasos: int = 10000) -> Optional[List[Pos]]:
    """
    Encuentra un camino desde la Base (S) hasta el Nucleo Central (G) usando backtracking.
    
    Este algoritmo realiza una busqueda en profundidad (DFS) con vuelta atras
    para encontrar el primer camino valido que conecte el inicio con el objetivo.
    
    Parametros:
        grid: Grid de TRON
        max_pasos: Numero maximo de pasos para evitar bucles infinitos
        
    Retorna:
        Optional[List[Pos]]: Lista de posiciones del camino encontrado, o None si no hay camino
    """
    inicio = encontrar_posicion(grid, "S")
    objetivo = encontrar_posicion(grid, "G")
    total_filas, total_columnas = len(grid), len(grid[0])
    
    # Matriz para evitar visitar celdas repetidas
    visitado = [[False] * total_columnas for _ in range(total_filas)]
    camino_actual: List[Pos] = []
    
    def backtracking_recursivo(fila: int, columna: int, pasos_realizados: int) -> bool:
        """
        Funcion recursiva interna para backtracking.
        
        Parametros:
            fila: Fila actual
            columna: Columna actual
            pasos_realizados: Contador de pasos para evitar bucles
            
        Retorna:
            bool: True si se encontro el objetivo desde esta posicion
        """
        # Condicion de seguridad: limite de pasos
        if pasos_realizados > max_pasos:
            return False
            
        # Verificar si la posicion es valida y no visitada
        if not esta_dentro_grid(grid, fila, columna) or not es_celda_libre(grid, fila, columna) or visitado[fila][columna]:
            return False

        # Agregar posicion actual al camino
        camino_actual.append((fila, columna))
        visitado[fila][columna] = True

        # Verificar si llegamos al objetivo
        if (fila, columna) == objetivo:
            return True

        # Explorar todos los movimientos posibles
        for movimiento_fila, movimiento_columna in MOVIMIENTOS:
            nueva_fila = fila + movimiento_fila
            nueva_columna = columna + movimiento_columna
            
            if backtracking_recursivo(nueva_fila, nueva_columna, pasos_realizados + 1):
                return True

        # VUELTA ATRAS: si ningun movimiento llevo al objetivo
        visitado[fila][columna] = False
        camino_actual.pop()
        return False

    # Iniciar busqueda desde la posicion inicial
    fila_inicio, columna_inicio = inicio
    visitado[fila_inicio][columna_inicio] = True
    camino_actual.append((fila_inicio, columna_inicio))
    
    # Explorar desde los vecinos de la posicion inicial
    for movimiento_fila, movimiento_columna in MOVIMIENTOS:
        nueva_fila = fila_inicio + movimiento_fila
        nueva_columna = columna_inicio + movimiento_columna
        
        if backtracking_recursivo(nueva_fila, nueva_columna, 1):
            return camino_actual
            
    # Limpiar si no se encontro camino
    camino_actual.pop()
    visitado[fila_inicio][columna_inicio] = False
    return None


def backtracking_todos_los_caminos(grid: List[List[str]], max_pasos: int = 200, limite_soluciones: int = 20) -> List[List[Pos]]:
    """
    Encuentra todos los caminos posibles desde la Base hasta el Nucleo Central.
    
    Este algoritmo explora exhaustivamente el espacio de busqueda para encontrar
    todas las rutas validas, hasta un limite especificado.
    
    Parametros:
        grid: Grid de TRON
        max_pasos: Numero maximo de pasos por camino
        limite_soluciones: Numero maximo de soluciones a encontrar
        
    Retorna:
        List[List[Pos]]: Lista de todos los caminos encontrados
    """
    inicio = encontrar_posicion(grid, "S")
    objetivo = encontrar_posicion(grid, "G")
    total_filas, total_columnas = len(grid), len(grid[0])
    
    visitado = [[False] * total_columnas for _ in range(total_filas)]
    soluciones: List[List[Pos]] = []
    camino_actual: List[Pos] = []
    
    def backtracking_recursivo(fila: int, columna: int, pasos_realizados: int):
        """
        Funcion recursiva para encontrar todos los caminos.
        """
        # Condiciones de terminacion
        if len(soluciones) >= limite_soluciones:
            return
        if pasos_realizados > max_pasos:
            return
            
        # Verificar validez de la posicion
        if not esta_dentro_grid(grid, fila, columna) or (grid[fila][columna] != " " and grid[fila][columna] != "G") or visitado[fila][columna]:
            return

        # Agregar posicion actual al camino
        camino_actual.append((fila, columna))
        visitado[fila][columna] = True

        # Verificar si es solucion
        if (fila, columna) == objetivo:
            soluciones.append(camino_actual.copy())
        else:
            # Explorar movimientos
            for movimiento_fila, movimiento_columna in MOVIMIENTOS:
                nueva_fila = fila + movimiento_fila
                nueva_columna = columna + movimiento_columna
                backtracking_recursivo(nueva_fila, nueva_columna, pasos_realizados + 1)

        # Vuelta atras
        visitado[fila][columna] = False
        camino_actual.pop()

    # Iniciar busqueda
    fila_inicio, columna_inicio = inicio
    visitado[fila_inicio][columna_inicio] = True
    camino_actual.append((fila_inicio, columna_inicio))
    
    for movimiento_fila, movimiento_columna in MOVIMIENTOS:
        nueva_fila = fila_inicio + movimiento_fila
        nueva_columna = columna_inicio + movimiento_columna
        backtracking_recursivo(nueva_fila, nueva_columna, 1)
        
    # Limpiar
    camino_actual.pop()
    visitado[fila_inicio][columna_inicio] = False
    
    return soluciones


def convertir_camino_a_movimientos(camino: List[Pos]) -> str:
    """
    Convierte una secuencia de posiciones a una cadena de movimientos.
    
    Parametros:
        camino: Lista de posiciones consecutivas
        
    Retorna:
        str: Cadena de movimientos (U=arriba, R=derecha, D=abajo, L=izquierda)
    """
    if not camino or len(camino) < 2:
        return ""
    
    movimientos = []
    for (fila_actual, columna_actual), (fila_siguiente, columna_siguiente) in zip(camino, camino[1:]):
        diferencia_fila = fila_siguiente - fila_actual
        diferencia_columna = columna_siguiente - columna_actual
        movimiento = NOMBRES_MOVIMIENTOS.get((diferencia_fila, diferencia_columna), "?")
        movimientos.append(movimiento)
        
    return "".join(movimientos)


# ============================================================
# DEMOSTRACION PRINCIPAL
# ============================================================

def demostrar_backtracking():
    """
    Funcion principal que demuestra el funcionamiento del backtracking.
    """
    print("SISTEMA DE NAVEGACION CON BACKTRACKING - GRID DE TRON")
    print("=" * 50)
    
    # Mostrar grid original
    print("Grid original:")
    print(renderizar_grid(GRID))
    print("\nLeyenda: S=Base, G=Nucleo Central, X=Firewall, ' '=Libre")
    
    # Buscar un camino
    print("\n" + "=" * 50)
    print("BUSCANDO UN CAMINO CON BACKTRACKING...")
    print("(DFS con vuelta atras)")
    
    camino_encontrado = backtracking_un_camino(GRID, max_pasos=5000)
    
    if camino_encontrado is None:
        print("NO SE ENCONTRO UN CAMINO VALIDO.")
        print("El Nucleo Central esta inaccesible desde la Base.")
    else:
        print(f"✓ CAMINO ENCONTRADO con {len(camino_encontrado)-1} pasos")
        print("\nSecuencia de movimientos:")
        movimientos = convertir_camino_a_movimientos(camino_encontrado)
        print(f"  {movimientos}")
        print("\n  (U=Arriba, R=Derecha, D=Abajo, L=Izquierda)")
        
        print("\nGrid con la ruta marcada:")
        grid_marcado = marcar_camino_en_grid(GRID, camino_encontrado, marca="·")
        print(renderizar_grid(grid_marcado))

    # Buscar multiples caminos
    print("\n" + "=" * 50)
    print("BUSCANDO MULTIPLES CAMINOS...")
    print("(Hasta 5 soluciones)")
    
    todos_los_caminos = backtracking_todos_los_caminos(GRID, max_pasos=200, limite_soluciones=5)
    
    print(f"Se encontraron {len(todos_los_caminos)} camino(s) alternativo(s):")
    
    for indice, camino in enumerate(todos_los_caminos, 1):
        movimientos = convertir_camino_a_movimientos(camino)
        print(f"\nCamino {indice}:")
        print(f"  - Longitud: {len(camino)-1} pasos")
        print(f"  - Movimientos: {movimientos}")
        
        # Mostrar solo el primer camino en el grid para no saturar
        if indice == 1 and camino_encontrado is None:
            grid_alternativo = marcar_camino_en_grid(GRID, camino, marca="·")
            print(f"  - Ruta:")
            print(renderizar_grid(grid_alternativo))


if __name__ == "__main__":
    demostrar_backtracking()