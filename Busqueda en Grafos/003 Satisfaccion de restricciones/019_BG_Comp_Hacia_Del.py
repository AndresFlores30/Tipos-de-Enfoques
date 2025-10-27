# Comprobación Hacia Delante (Forward Checking) en un CSP temático de TRON

from typing import Dict, List, Callable, Optional, Tuple
import copy

# ==============================
# Definición básica de un CSP
# ==============================

class CSP:
    def __init__(
        self,
        variables: List[str],
        dominios: Dict[str, List[str]],
        vecinos: Dict[str, List[str]],
        restriccion_binaria: Callable[[str, str, str, str], bool],
        restriccion_unaria: Optional[Callable[[str, str], bool]] = None,
        restricciones_globales: Optional[List[Callable[[Dict[str, str]], bool]]] = None,
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
        # Binaria vs vecinos ya asignados
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
                # La restricción requiere variables aún no asignadas: se pospone
                pass
        return True

# ==============================
# Heurísticas: MRV + Degree
# ==============================

def seleccionar_variable_MRV_Degree(
    csp: CSP, asignacion: Dict[str, str], dominios: Dict[str, List[str]]
) -> str:
    no_asignadas = [v for v in csp.variables if v not in asignacion]
    # MRV
    m = min(len(dominios[v]) for v in no_asignadas)
    candidatas = [v for v in no_asignadas if len(dominios[v]) == m]
    if len(candidatas) == 1:
        return candidatas[0]
    # Degree: más vecinos sin asignar
    return max(
        candidatas,
        key=lambda v: sum(1 for u in csp.vecinos[v] if u not in asignacion)
    )

# (Opcional) LCV para ordenar valores: menos restrictivo primero
def ordenar_valores_LCV(
    csp: CSP, var: str, dominios: Dict[str, List[str]], asignacion: Dict[str, str]
) -> List[str]:
    puntajes = []
    for val in dominios[var]:
        impacto = 0
        for v2 in csp.vecinos[var]:
            if v2 not in asignacion:
                # Cuenta cuántos valores del vecino serían incompatibles si tomo val
                impacto += sum(
                    1 for val2 in dominios[v2]
                    if not csp.restriccion_binaria(var, v2, val, val2)
                )
        puntajes.append((val, impacto))
    puntajes.sort(key=lambda t: t[1])
    return [v for v, _ in puntajes]

# ==============================
# Comprobación hacia delante
# ==============================

def forward_checking(
    csp: CSP,
    var: str,
    val: str,
    dominios: Dict[str, List[str]],
    asignacion: Dict[str, str],
) -> Optional[Dict[str, List[str]]]:
    nuevos = copy.deepcopy(dominios)
    # Fijar dominio de var en {val}
    nuevos[var] = [val]

    for v2 in csp.vecinos[var]:
        if v2 in asignacion:
            continue
        permitidos = []
        for val2 in nuevos[v2]:
            # Debe respetar: binaria, unaria y global parcial
            if not csp.restriccion_binaria(var, v2, val, val2):
                continue
            if not csp.restriccion_unaria(v2, val2):
                continue
            ok_global = True
            for rg in csp.restricciones_globales:
                try:
                    if not rg({**asignacion, var: val, v2: val2}):
                        ok_global = False
                        break
                except KeyError:
                    pass
            if ok_global:
                permitidos.append(val2)
        if not permitidos:
            csp.log.append(f"Poda total en {v2} al asignar {var}={val}. Retroceso.")
            return None
        if len(permitidos) < len(nuevos[v2]):
            csp.log.append(
                f"Poda en {v2}: {nuevos[v2]} -> {permitidos} por {var}={val}"
            )
        nuevos[v2] = permitidos
    return nuevos

# ==============================
# Backtracking con Forward Checking
# ==============================

def backtracking_forward_checking(csp: CSP) -> Tuple[Optional[Dict[str, str]], List[str]]:
    asignacion: Dict[str, str] = {}
    dominios = copy.deepcopy(csp.dominios)

    # Poda inicial por restricciones unarias
    for v in csp.variables:
        filtrado = [val for val in dominios[v] if csp.restriccion_unaria(v, val)]
        if not filtrado:
            csp.log.append(f"Dominio vacío inicial por unaria en {v}.")
            return None, csp.log
        if len(filtrado) < len(dominios[v]):
            csp.log.append(f"Poda unaria en {v}: {dominios[v]} -> {filtrado}")
        dominios[v] = filtrado

    def bt(asig: Dict[str, str], dom: Dict[str, List[str]]) -> Optional[Dict[str, str]]:
        if len(asig) == len(csp.variables):
            # Verificación final de restricciones globales
            if all(rg(asig) for rg in csp.restricciones_globales):
                return asig
            return None

        var = seleccionar_variable_MRV_Degree(csp, asig, dom)
        for val in ordenar_valores_LCV(csp, var, dom, asig):
            if csp.consistente_local(asig, var, val):
                csp.log.append(f"Asignar {var} = {val}")
                asig[var] = val
                dom_fc = forward_checking(csp, var, val, dom, asig)
                if dom_fc is not None:
                    res = bt(asig, dom_fc)
                    if res is not None:
                        return res
                csp.log.append(f"Retroceder {var} = {val}")
                del asig[var]
        return None

    sol = bt(asignacion, dominios)
    return sol, csp.log

# ==============================
# Instancia TRON: coloración de sectores
# ==============================

def construir_CSP_TRON() -> CSP:
    # Sectores del Grid
    variables = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]

    # Canales de energía disponibles (colores)
    canales = ["Azul", "Cian", "Blanco", "Ambar"]

    dominios = {v: list(canales) for v in variables}

    # Adyacencias: sectores conectados no pueden compartir canal
    vecinos = {
        "Base": ["Sector_Luz", "Portal"],
        "Sector_Luz": ["Base", "Arena"],
        "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
        "Torre_IO": ["Arena", "Nucleo_Central"],
        "Portal": ["Base", "Arena"],
        "Nucleo_Central": ["Torre_IO"],
    }

    # Restricción binaria: diferentes canales en sectores adyacentes
    def restr_bin(x: str, y: str, vx: str, vy: str) -> bool:
        if y in vecinos.get(x, []):
            return vx != vy
        return True

    # Restricciones unarias temáticas:
    # - Núcleo debe ser Blanco por estabilidad
    # - Torre_IO no puede ser Ambar por interferencia
    # - Sector_Luz prefiere Alta luminosidad: Azul o Cian
    def restr_unaria(var: str, val: str) -> bool:
        if var == "Nucleo_Central":
            return val == "Blanco"
        if var == "Torre_IO":
            return val != "Ambar"
        if var == "Sector_Luz":
            return val in ("Azul", "Cian")
        return True

    # Restricciones globales:
    # 1) Evitar picos: Base y Portal no pueden ser ambos Azul
    def rg_base_portal_no_azul(asig: Dict[str, str]) -> bool:
        if "Base" in asig and "Portal" in asig:
            return not (asig["Base"] == "Azul" and asig["Portal"] == "Azul")
        return True

    # 2) Redundancia mínima: al menos dos sectores deben usar Cian
    def rg_min_cian(asig: Dict[str, str]) -> bool:
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

# ==============================
# Demo
# ==============================

def demo():
    csp = construir_CSP_TRON()
    solucion, log = backtracking_forward_checking(csp)

    print("Registro del proceso:")
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