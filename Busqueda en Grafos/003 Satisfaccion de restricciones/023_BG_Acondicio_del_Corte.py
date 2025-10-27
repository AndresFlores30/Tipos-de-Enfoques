# Acondicionamiento del Corte (Cutset Conditioning) en un CSP temático de TRON
# - Selección automática de un conjunto de corte aproximado por "deshojado" de hojas
# - Enumeración inteligente de asignaciones del corte con poda (unarias + AC-3 incremental)
# - Propagación de restricciones (AC-3)
# - Resolución del resto (bosque) con backtracking ligero (MRV + LCV) tras fijar el corte

from typing import Dict, List, Tuple, Callable, Optional, Set
from collections import deque
import copy
import itertools

Variables = List[str]
Dominios = Dict[str, List[str]]
Vecinos = Dict[str, List[str]]
Asignacion = Dict[str, str]

# ============================================================
# Definición del problema TRON (coloración de sectores)
# ============================================================

def construir_problema_tron() -> Tuple[Variables, Dominios, Vecinos,
                                        Callable[[str, str], bool],
                                        Callable[[str, str, str, str], bool],
                                        List[Callable[[Asignacion], bool]]]:
    variables = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    canales = ["Azul", "Cian", "Blanco", "Ambar"]

    dominios: Dominios = {v: list(canales) for v in variables}

    vecinos: Vecinos = {
        "Base": ["Sector_Luz", "Portal"],
        "Sector_Luz": ["Base", "Arena"],
        "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
        "Torre_IO": ["Arena", "Nucleo_Central"],
        "Portal": ["Base", "Arena"],
        "Nucleo_Central": ["Torre_IO"],
    }

    # Restricciones unarias temáticas
    def restr_unaria(var: str, val: str) -> bool:
        if var == "Nucleo_Central":
            return val == "Blanco"          # Núcleo estable
        if var == "Torre_IO":
            return val != "Ambar"           # Interferencia I/O
        if var == "Sector_Luz":
            return val in ("Azul", "Cian")  # Alta luminosidad
        return True

    # Restricción binaria: adyacentes con canal distinto
    def restr_binaria(x: str, y: str, vx: str, vy: str) -> bool:
        if y in vecinos.get(x, []):
            return vx != vy
        return True

    # Restricciones globales binarias simples (opcionales)
    def rg_base_portal_no_azul(asig: Asignacion) -> bool:
        if "Base" in asig and "Portal" in asig:
            return not (asig["Base"] == "Azul" and asig["Portal"] == "Azul")
        return True

    # Al finalizar, debe haber al menos dos sectores en Cian (redundancia)
    def rg_min_cian_final(asig: Asignacion) -> bool:
        # Solo evaluar cuando esté completa
        if len(asig) < len(variables):
            return True
        return sum(1 for v in asig.values() if v == "Cian") >= 2

    restricciones_globales: List[Callable[[Asignacion], bool]] = [
        rg_base_portal_no_azul,
        rg_min_cian_final
    ]

    return variables, dominios, vecinos, restr_unaria, restr_binaria, restricciones_globales

# ============================================================
# Utilidades de grafo y corte
# ============================================================

def core_por_deshojado(variables: Variables, vecinos: Vecinos) -> Set[str]:
    """
    Aproximación a un conjunto de corte:
    quitar iterativamente hojas (grado <= 1). Lo que queda (core) tiene grado >= 2,
    y sirve como conjunto con el que romper ciclos.
    """
    grados = {v: len(vecinos[v]) for v in variables}
    eliminado = set()
    cola = deque([v for v in variables if grados[v] <= 1])

    while cola:
        v = cola.popleft()
        if v in eliminado:
            continue
        eliminado.add(v)
        for u in vecinos[v]:
            if u in eliminado:
                continue
            grados[u] -= 1
            if grados[u] == 1:
                cola.append(u)

    core = set(v for v in variables if v not in eliminado)
    return core

# ============================================================
# AC-3 (consistencia de arcos)
# ============================================================

def ac3(variables: Variables,
        dominios: Dominios,
        vecinos: Vecinos,
        restr_unaria: Callable[[str, str], bool],
        restr_binaria: Callable[[str, str, str, str], bool],
        cola_inicial: Optional[List[Tuple[str, str]]] = None) -> bool:
    cola = deque()
    if cola_inicial is None:
        for xi in variables:
            for xj in vecinos[xi]:
                cola.append((xi, xj))
    else:
        for arc in cola_inicial:
            cola.append(arc)

    def revisar(xi: str, xj: str) -> bool:
        eliminado = False
        vx = list(dominios[xi])
        for vi in vx:
            if not restr_unaria(xi, vi):
                dominios[xi].remove(vi)
                eliminado = True
                continue
            soportado = any(
                restr_binaria(xi, xj, vi, vj) and restr_unaria(xj, vj)
                for vj in dominios[xj]
            )
            if not soportado:
                dominios[xi].remove(vi)
                eliminado = True
        return eliminado

    while cola:
        xi, xj = cola.popleft()
        if revisar(xi, xj):
            if not dominios[xi]:
                return False
            for xk in vecinos[xi]:
                if xk != xj:
                    cola.append((xk, xi))
    return True

# ============================================================
# Backtracking ligero (para el bosque restante): MRV + LCV
# ============================================================

def seleccionar_MRV(variables: Variables, asignacion: Asignacion, dominios: Dominios) -> str:
    cand = [v for v in variables if v not in asignacion]
    return min(cand, key=lambda v: len(dominios[v]))

def ordenar_LCV(var: str,
                dominios: Dominios,
                vecinos: Vecinos,
                asignacion: Asignacion,
                restr_binaria: Callable[[str, str, str, str], bool]) -> List[str]:
    vals = dominios[var]
    punt = []
    for val in vals:
        impacto = 0
        for u in vecinos[var]:
            if u in asignacion:
                continue
            impacto += sum(
                1 for vu in dominios[u]
                if not restr_binaria(var, u, val, vu)
            )
        punt.append((val, impacto))
    punt.sort(key=lambda t: t[1])
    return [v for v, _ in punt]

def backtracking_bosque(variables: Variables,
                        dominios: Dominios,
                        vecinos: Vecinos,
                        restr_unaria: Callable[[str, str], bool],
                        restr_binaria: Callable[[str, str, str, str], bool],
                        restricciones_globales: List[Callable[[Asignacion], bool]],
                        asignacion_inicial: Asignacion) -> Optional[Asignacion]:
    asignacion = dict(asignacion_inicial)

    def consistente_local(var: str, val: str) -> bool:
        if not restr_unaria(var, val):
            return False
        for u in vecinos[var]:
            if u in asignacion and not restr_binaria(var, u, val, asignacion[u]):
                return False
        for rg in restricciones_globales:
            if not rg({**asignacion, var: val}):
                return False
        return True

    def bt() -> Optional[Asignacion]:
        if len(asignacion) == len(variables):
            # Verificación final de globales (ya se valida en consistente_local)
            return dict(asignacion)

        var = seleccionar_MRV(variables, asignacion, dominios)
        for val in ordenar_LCV(var, dominios, vecinos, asignacion, restr_binaria):
            if val not in dominios[var]:
                continue
            if consistente_local(var, val):
                asignacion[var] = val
                # Forward trivial: no modificamos dominios aquí; AC-3 ya podó bastante
                res = bt()
                if res is not None:
                    return res
                del asignacion[var]
        return None

    return bt()

# ============================================================
# Acondicionamiento del Corte
# ============================================================

def cutset_conditioning():
    variables, dominios0, vecinos, ru, rb, rgs = construir_problema_tron()

    # Pre-poda unaria
    dominios = {v: [x for x in dominios0[v] if ru(v, x)] for v in variables}
    if any(len(dominios[v]) == 0 for v in variables):
        print("Dominio vacío tras restricciones unarias.")
        return None

    # Encontrar core por deshojado (conjunto de corte aproximado)
    core = core_por_deshojado(variables, vecinos)
    cutset = sorted(core) if core else []  # si ya es bosque, cutset vacío

    print("Variables:", variables)
    print("Conjunto de corte aproximado:", cutset if cutset else "(vacío: el grafo ya es un bosque)")
    print()

    # Variables restantes (bosque) al quitar cutset
    resto = [v for v in variables if v not in cutset]

    # Orden de enumeración del corte: MRV sobre dominios actuales
    cutset_orden = sorted(cutset, key=lambda v: len(dominios[v]))

    intentos = 0
    soluciones = 0

    # Backtracking sobre el corte con AC-3 incremental para podar temprano
    asig_corte: Asignacion = {}

    def bt_corte(i: int, dom_actual: Dominios) -> Optional[Asignacion]:
        nonlocal intentos, soluciones

        if i == len(cutset_orden):
            # Con el corte fijado, resolver el bosque
            dom_bosque = copy.deepcopy(dom_actual)
            # Propagación final antes del bosque (no hace daño)
            if not ac3(variables, dom_bosque, vecinos, ru, rb):
                return None
            sol = backtracking_bosque(variables, dom_bosque, vecinos, ru, rb, rgs, asig_corte)
            if sol is not None:
                soluciones += 1
                return sol
            return None

        var = cutset_orden[i]
        # Ordenar valores por LCV respecto de sus vecinos
        vals_ordenados = ordenar_LCV(var, dom_actual, vecinos, asig_corte, rb)
        for val in vals_ordenados:
            intentos += 1
            # Chequeo local rápido
            ok_unaria = ru(var, val)
            if not ok_unaria:
                continue
            ok_binaria = all(
                (u not in asig_corte) or rb(var, u, val, asig_corte[u])
                for u in vecinos[var]
            )
            if not ok_binaria:
                continue
            # Chequeo global parcial
            if not all(rg({**asig_corte, var: val}) for rg in rgs):
                continue

            # Fijar y propagar con AC-3 incremental
            dom_new = copy.deepcopy(dom_actual)
            dom_new[var] = [val]
            cola_inicial = [(u, var) for u in vecinos[var]]
            if not ac3(variables, dom_new, vecinos, ru, rb, cola_inicial):
                continue

            asig_corte[var] = val
            sol = bt_corte(i + 1, dom_new)
            if sol is not None:
                return sol
            del asig_corte[var]

        return None

    # AC-3 inicial para podar antes de arrancar
    dom_inicial = copy.deepcopy(dominios)
    ac3(variables, dom_inicial, vecinos, ru, rb)

    solucion = bt_corte(0, dom_inicial)

    print(f"Intentos sobre el corte: {intentos}")
    if solucion is None:
        print("No se encontró solución.")
    else:
        print("Solución:")
        for v in variables:
            print(f"  {v:15s} = {solucion[v]}")

    return solucion

# ============================================================
# Demo
# ============================================================

if __name__ == "__main__":
    cutset_conditioning()