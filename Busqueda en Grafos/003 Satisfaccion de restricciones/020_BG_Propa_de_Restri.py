# Propagación de Restricciones en un CSP temático de TRON
# - AC-3 (consistencia de arcos) como propagación previa
# - MAC (Maintaining Arc Consistency) durante backtracking
# - MRV + Degree y orden LCV

from typing import Dict, List, Callable, Optional, Tuple
from collections import deque
import copy

# ============================================================
# Definición general del CSP
# ============================================================

class CSP:
    def __init__(
        self,
        variables: List[str],
        dominios: Dict[str, List[str]],
        vecinos: Dict[str, List[str]],
        restriccion_binaria: Callable[[str, str, str, str], bool],
        restriccion_unaria: Optional[Callable[[str, str], bool]] = None,
        restricciones_globales: Optional[List[Callable[[Dict[str, str]], bool]]] = None
    ):
        self.variables = variables
        self.dominios = {v: list(dominios[v]) for v in variables}
        self.vecinos = {v: list(vecinos.get(v, [])) for v in variables}
        self.restriccion_binaria = restriccion_binaria
        self.restriccion_unaria = restriccion_unaria or (lambda var, val: True)
        self.restricciones_globales = restricciones_globales or []
        self.log: List[str] = []

    def consistente_local(self, asignacion: Dict[str, str], var: str, val: str) -> bool:
        # Unaria
        if not self.restriccion_unaria(var, val):
            return False
        # Binaria con vecinos asignados
        for v2 in self.vecinos[var]:
            if v2 in asignacion:
                if not self.restriccion_binaria(var, v2, val, asignacion[v2]):
                    return False
        # Globales con asignación parcial
        for rg in self.restricciones_globales:
            try:
                if not rg({**asignacion, var: val}):
                    return False
            except KeyError:
                pass
        return True

# ============================================================
# Utilidades
# ============================================================

def pretty_domains(doms: Dict[str, List[str]]) -> str:
    ancho = max(len(v) for v in doms)
    lineas = []
    for v in sorted(doms.keys()):
        lineas.append(f"{v:<15s}: {doms[v]}")
    return "\n".join(lineas)

# ============================================================
# Propagación de restricciones: AC-3
# ============================================================

def ac3(csp: CSP, dominios: Dict[str, List[str]], cola_inicial: Optional[List[Tuple[str, str]]] = None) -> bool:
    """
    Enforce Arc Consistency sobre 'dominios'.
    Retorna False si algún dominio queda vacío (inconsistencia).
    """
    cola = deque()
    if cola_inicial is None:
        for xi in csp.variables:
            for xj in csp.vecinos[xi]:
                cola.append((xi, xj))
    else:
        for arc in cola_inicial:
            cola.append(arc)

    def revisar(xi: str, xj: str) -> bool:
        eliminado = False
        vals_xi = list(dominios[xi])
        for vi in vals_xi:
            # vi es soportado si existe al menos un vj en Dj consistente con vi
            soportado = any(
                csp.restriccion_binaria(xi, xj, vi, vj) and csp.restriccion_unaria(xj, vj)
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
            for xk in csp.vecinos[xi]:
                if xk != xj:
                    cola.append((xk, xi))
    return True

# ============================================================
# Heurísticas: MRV + Degree y orden LCV
# ============================================================

def seleccionar_variable_MRV_Degree(
    csp: CSP, asignacion: Dict[str, str], dominios: Dict[str, List[str]]
) -> str:
    no_asignadas = [v for v in csp.variables if v not in asignacion]
    m = min(len(dominios[v]) for v in no_asignadas)
    candidatas = [v for v in no_asignadas if len(dominios[v]) == m]
    if len(candidatas) == 1:
        return candidatas[0]
    # Degree: mayor cantidad de vecinos sin asignar
    return max(candidatas, key=lambda v: sum(1 for u in csp.vecinos[v] if u not in asignacion))

def ordenar_valores_LCV(
    csp: CSP, var: str, dominios: Dict[str, List[str]], asignacion: Dict[str, str]
) -> List[str]:
    puntajes = []
    for val in dominios[var]:
        impacto = 0
        for v2 in csp.vecinos[var]:
            if v2 not in asignacion:
                impacto += sum(
                    1 for val2 in dominios[v2]
                    if not csp.restriccion_binaria(var, v2, val, val2)
                )
        puntajes.append((val, impacto))
    puntajes.sort(key=lambda t: t[1])  # menor impacto primero
    return [v for v, _ in puntajes]

# ============================================================
# Backtracking con MAC (propagación AC-3 tras cada asignación)
# ============================================================

def backtracking_mac(csp: CSP) -> Tuple[Optional[Dict[str, str]], List[str]]:
    asignacion: Dict[str, str] = {}
    dominios = copy.deepcopy(csp.dominios)

    # Poda inicial por restricciones unarias
    for v in csp.variables:
        filtrado = [val for val in dominios[v] if csp.restriccion_unaria(v, val)]
        if not filtrado:
            csp.log.append(f"Dominio vacío inicial por restricción unaria en {v}.")
            return None, csp.log
        if len(filtrado) < len(dominios[v]):
            csp.log.append(f"Poda unaria en {v}: {dominios[v]} -> {filtrado}")
        dominios[v] = filtrado

    # Propagación inicial (AC-3 completa)
    csp.log.append("AC-3 inicial:")
    dom_ini = copy.deepcopy(dominios)
    ok = ac3(csp, dominios)
    csp.log.append(pretty_domains(dominios))
    if not ok:
        csp.log.append("Inconsistencia detectada por AC-3 inicial.")
        return None, csp.log

    def bt(asig: Dict[str, str], dom: Dict[str, List[str]]) -> Optional[Dict[str, str]]:
        if len(asig) == len(csp.variables):
            # Verificación global final
            if all(rg(asig) for rg in csp.restricciones_globales):
                return asig
            return None

        var = seleccionar_variable_MRV_Degree(csp, asig, dom)
        for val in ordenar_valores_LCV(csp, var, dom, asig):
            if csp.consistente_local(asig, var, val):
                csp.log.append(f"Probar {var} = {val}")
                asig[var] = val

                # Mantener consistencia de arcos: AC-3 incremental
                dom_copia = copy.deepcopy(dom)
                dom_copia[var] = [val]  # fija el dominio de var
                # Inicializa la cola con los arcos (vecino, var) para propagar
                cola_inicial = [(v2, var) for v2 in csp.vecinos[var]]
                if ac3(csp, dom_copia, cola_inicial):
                    res = bt(asig, dom_copia)
                    if res is not None:
                        return res

                csp.log.append(f"Retroceso {var} = {val}")
                del asig[var]
        return None

    sol = bt(asignacion, dominios)
    return sol, csp.log

# ============================================================
# Instancia TRON: coloración de sectores del Grid
# ============================================================

def construir_CSP_TRON() -> CSP:
    variables = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    canales = ["Azul", "Cian", "Blanco", "Ambar"]

    dominios = {v: list(canales) for v in variables}

    vecinos = {
        "Base": ["Sector_Luz", "Portal"],
        "Sector_Luz": ["Base", "Arena"],
        "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
        "Torre_IO": ["Arena", "Nucleo_Central"],
        "Portal": ["Base", "Arena"],
        "Nucleo_Central": ["Torre_IO"],
    }

    # Restricción binaria: sectores adyacentes no deben compartir canal
    def restr_bin(x: str, y: str, vx: str, vy: str) -> bool:
        if y in vecinos.get(x, []):
            return vx != vy
        return True

    # Restricciones unarias temáticas
    def restr_unaria(var: str, val: str) -> bool:
        # Núcleo debe ser Blanco por estabilidad de la Red
        if var == "Nucleo_Central":
            return val == "Blanco"
        # Torre_IO no puede ser Ambar por interferencia I/O
        if var == "Torre_IO":
            return val != "Ambar"
        # Sector_Luz usa canales de alta luminosidad
        if var == "Sector_Luz":
            return val in ("Azul", "Cian")
        return True

    # Restricciones globales opcionales
    def rg_base_portal_no_azul(asig: Dict[str, str]) -> bool:
        if "Base" in asig and "Portal" in asig:
            return not (asig["Base"] == "Azul" and asig["Portal"] == "Azul")
        return True

    def rg_min_cian(asig: Dict[str, str]) -> bool:
        # Al menos dos sectores en Cian al finalizar
        if len(asig) < len(variables):
            return True
        return sum(1 for v in asig.values() if v == "Cian") >= 2

    return CSP(
        variables=variables,
        dominios=dominios,
        vecinos=vecinos,
        restriccion_binaria=restr_bin,
        restriccion_unaria=restr_unaria,
        restricciones_globales=[rg_base_portal_no_azul, rg_min_cian],
    )

# ============================================================
# Demo
# ============================================================

def demo():
    csp = construir_CSP_TRON()
    print("Dominios iniciales:")
    print(pretty_domains(csp.dominios))
    print("\nEjecutando backtracking con propagación (MAC)...\n")

    solucion, log = backtracking_mac(csp)

    print("Registro de propagación y búsqueda:")
    for linea in log:
        print(" -", linea)

    if solucion is None:
        print("\nNo se encontró solución.")
    else:
        print("\nSolución encontrada:")
        for var in csp.variables:
            print(f"  {var:15s} = {solucion[var]}")

if __name__ == "__main__":
    demo()