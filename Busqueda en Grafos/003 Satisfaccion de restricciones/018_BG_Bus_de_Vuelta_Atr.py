# Búsqueda de Vuelta Atrás (Backtracking) en el Grid de TRON
# Objetivo: llegar del nodo Base (S) al Núcleo_Central (G) evitando firewalls.

from typing import List, Tuple, Optional

Pos = Tuple[int, int]

# ------------------------------------------------------------
# Definición del Grid:
#   'S' = Base (origen)
#   'G' = Núcleo_Central (meta)
#   'X' = firewall (bloqueado)
#   ' ' = celda libre
# ------------------------------------------------------------
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
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]
MOVE_NAMES = {(-1, 0): "U", (0, 1): "R", (1, 0): "D", (0, -1): "L"}


def encontrar(G: List[List[str]], ch: str) -> Pos:
    for i, fila in enumerate(G):
        for j, c in enumerate(fila):
            if c == ch:
                return (i, j)
    raise ValueError(f"No se encontró el símbolo {ch} en el grid.")


def dentro(G: List[List[str]], r: int, c: int) -> bool:
    return 0 <= r < len(G) and 0 <= c < len(G[0])


def es_libre(G: List[List[str]], r: int, c: int) -> bool:
    return G[r][c] in (" ", "G")


def render(G: List[List[str]]) -> str:
    return "\n".join("".join(fila) for fila in G)


def marcar_camino(G: List[List[str]], camino: List[Pos], marca: str = ".") -> List[List[str]]:
    copia = [fila[:] for fila in G]
    for (r, c) in camino:
        if copia[r][c] == " ":
            copia[r][c] = marca
    return copia


# ------------------------------------------------------------
# Backtracking: encontrar un camino 
# ------------------------------------------------------------
def backtracking_un_camino(G: List[List[str]], max_pasos: int = 10_000) -> Optional[List[Pos]]:
    start = encontrar(G, "S")
    goal = encontrar(G, "G")
    R, C = len(G), len(G[0])

    visitado = [[False] * C for _ in range(R)]
    camino: List[Pos] = []

    def bt(r: int, c: int, pasos: int) -> bool:
        if pasos > max_pasos:
            return False
        if not dentro(G, r, c) or not es_libre(G, r, c) or visitado[r][c]:
            return False

        camino.append((r, c))
        visitado[r][c] = True

        if (r, c) == goal:
            return True

        for dr, dc in MOVES:
            if bt(r + dr, c + dc, pasos + 1):
                return True

        # Vuelta atrás
        visitado[r][c] = False
        camino.pop()
        return False

    # Iniciamos desde la celda vecina a S (se permite pisar S también)
    sr, sc = start
    visitado[sr][sc] = True
    camino.append((sr, sc))
    for dr, dc in MOVES:
        if bt(sr + dr, sc + dc, 1):
            return camino
    camino.pop()
    visitado[sr][sc] = False
    return None


# Backtracking: encontrar todos los caminos hasta un límite
# Útil para análisis o conteo de soluciones.

def backtracking_todos_los_caminos(G: List[List[str]], max_pasos: int = 200, limite_solutions: int = 20) -> List[List[Pos]]:
    start = encontrar(G, "S")
    goal = encontrar(G, "G")
    R, C = len(G), len(G[0])

    visitado = [[False] * C for _ in range(R)]
    soluciones: List[List[Pos]] = []
    camino: List[Pos] = []

    def bt(r: int, c: int, pasos: int):
        if len(soluciones) >= limite_solutions:
            return
        if pasos > max_pasos:
            return
        if not dentro(G, r, c) or (G[r][c] != " " and G[r][c] != "G") or visitado[r][c]:
            return

        camino.append((r, c))
        visitado[r][c] = True

        if (r, c) == goal:
            soluciones.append(list(camino))
        else:
            for dr, dc in MOVES:
                bt(r + dr, c + dc, pasos + 1)

        # Vuelta atrás
        visitado[r][c] = False
        camino.pop()

    sr, sc = start
    visitado[sr][sc] = True
    camino.append((sr, sc))
    for dr, dc in MOVES:
        bt(sr + dr, sc + dc, 1)
    camino.pop()
    visitado[sr][sc] = False
    return soluciones



# Utilitario: convertir camino a cadena de movimientos
def camino_a_movs(path: List[Pos]) -> str:
    if not path or len(path) < 2:
        return ""
    movs = []
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        dr, dc = r2 - r1, c2 - c1
        movs.append(MOVE_NAMES.get((dr, dc), "?"))
    return "".join(movs)


# Demo
def demo():
    print("Grid original:")
    print(render(GRID))
    print("\nBuscando un camino con Backtracking (DFS con vuelta atrás)...")
    path = backtracking_un_camino(GRID, max_pasos=5000)
    if path is None:
        print("No se encontró un camino.")
    else:
        print(f"Camino encontrado con {len(path)-1} pasos.")
        print("Secuencia de movimientos (U=arriba, R=derecha, D=abajo, L=izquierda):")
        print(camino_a_movs(path))
        print("\nGrid con una ruta marcada:")
        marcado = marcar_camino(GRID, path, marca="·")
        print(render(marcado))

    print("\nBuscando múltiples caminos (hasta 5)...")
    all_paths = backtracking_todos_los_caminos(GRID, max_pasos=200, limite_solutions=5)
    print(f"Se encontraron {len(all_paths)} camino(s).")
    for i, p in enumerate(all_paths, 1):
        print(f" - Camino {i}: longitud={len(p)-1}, movimientos={camino_a_movs(p)}")

if __name__ == "__main__":
    demo()