# CSP temático de TRON: Asignación de canales de energía a sectores del Grid
# Estrategias: Backtracking + MRV + Degree Heuristic + LCV + Forward Checking

from typing import Dict, List, Callable, Optional, Tuple, Set
from collections import defaultdict
import copy

# ============================================================
# Definición general de un CSP
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
    ) -> None:
        self.variables = variables
        self.dominios = {v: list(dominios[v]) for v in variables}
        self.vecinos = {v: list(vecinos.get(v, [])) for v in variables}
        self.restriccion_binaria = restriccion_binaria
        self.restriccion_unaria = restriccion_unaria or (lambda var, val: True)
        self.restricciones_globales = restricciones_globales or []
        self.pasos: List[str] = []

    # Comprobación de consistencia local (binaria + unaria)
    def consistente(self, asignacion: Dict[str, str], var: str, val: str) -> bool:
        if not self.restriccion_unaria(var, val):
            return False
        for v2 in self.vecinos[var]:
            if v2 in asignacion:
                if not self.restriccion_binaria(var, v2, val, asignacion[v2]):
                    return False
        # Comprobar restricciones globales con una asignación parcial: solo evalúa
        # las que no fallen por variables no asignadas.
        for rg in self.restricciones_globales:
            if not self._eval_global_parcial(rg, asignacion | {var: val}):
                return False
        return True

    def _eval_global_parcial(self, rg: Callable[[Dict[str, str]], bool], asignacion: Dict[str, str]) -> bool:
        try:
            return rg(asignacion)
        except KeyError:
            # Si la restricción global requiere una variable aún no asignada,
            # la consideramos no restrictiva por ahora.
            return True

    # Forward checking: poda dominios de vecinos con base en la asignación (var=val)
    def forward_checking(
        self,
        var: str,
        val: str,
        dominios_actuales: Dict[str, List[str]],
        asignacion: Dict[str, str]
    ) -> Optional[Dict[str, List[str]]]:
        dominios_podados = copy.deepcopy(dominios_actuales)
        for v2 in self.vecinos[var]:
            if v2 not in asignacion:
                nuevos = []
                for val2 in dominios_podados[v2]:
                    if self.restriccion_binaria(var, v2, val, val2):
                        # También validar restricción unaria del vecino
                        if self.restriccion_unaria(v2, val2):
                            # Comprobar globales con asignación parcial hipotética
                            if all(self._eval_global_parcial(rg, asignacion | {var: val, v2: val2})
                                   for rg in self.restricciones_globales):
                                nuevos.append(val2)
                dominios_podados[v2] = nuevos
                if len(nuevos) == 0:
                    return None
        return dominios_podados

# ============================================================
# Heurísticas
# ============================================================

def seleccionar_variable_MRV_Degree(csp: CSP, asignacion: Dict[str, str], dominios: Dict[str, List[str]]) -> str:
    no_asignadas = [v for v in csp.variables if v not in asignacion]
    # MRV: mínimo dominio restante
    min_dom = min(len(dominios[v]) for v in no_asignadas)
    candidatas = [v for v in no_asignadas if len(dominios[v]) == min_dom]
    if len(candidatas) == 1:
        return candidatas[0]
    # Degree heuristic: mayor cantidad de vecinos no asignados
    def grado_restante(v: str) -> int:
        return sum(1 for u in csp.vecinos[v] if u not in asignacion)
    return max(candidatas, key=grado_restante)

def ordenar_valores_LCV(csp: CSP, var: str, dominios: Dict[str, List[str]], asignacion: Dict[str, str]) -> List[str]:
    # LCV: Least Constraining Value
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
# Backtracking con forward checking
# ============================================================

def backtracking_buscar(csp: CSP) -> Tuple[Optional[Dict[str, str]], List[str]]:
    asignacion: Dict[str, str] = {}
    dominios_actuales = copy.deepcopy(csp.dominios)

    # Poda inicial por restricciones unarias
    for v in csp.variables:
        dominios_actuales[v] = [val for val in dominios_actuales[v] if csp.restriccion_unaria(v, val)]
        if not dominios_actuales[v]:
            csp.pasos.append(f"Fallo temprano: dominio vacío en {v} por restricción unaria.")
            return None, csp.pasos

    def bt_rec(asig: Dict[str, str], dom: Dict[str, List[str]]) -> Optional[Dict[str, str]]:
        if len(asig) == len(csp.variables):
            # Validar restricciones globales finales
            if all(rg(asig) for rg in csp.restricciones_globales):
                return asig
            return None

        var = seleccionar_variable_MRV_Degree(csp, asig, dom)
        for val in ordenar_valores_LCV(csp, var, dom, asig):
            if csp.consistente(asig, var, val):
                csp.pasos.append(f"Asignar {var} = {val}")
                asig[var] = val
                nuevos_dom = csp.forward_checking(var, val, dom, asig)
                if nuevos_dom is not None:
                    res = bt_rec(asig, nuevos_dom)
                    if res is not None:
                        return res
                csp.pasos.append(f"Retroceder {var} = {val}")
                del asig[var]
        return None

    solucion = bt_rec(asignacion, dominios_actuales)
    return solucion, csp.pasos

# ============================================================
# Instancia TRON del CSP
# ============================================================

def construir_CSP_TRON() -> CSP:
    # Sectores del Grid
    variables = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]

    # Canales de energía disponibles
    canales = ["Azul", "Cian", "Blanco", "Ambar"]

    dominios = {
        "Base": canales[:],
        "Sector_Luz": canales[:],
        "Arena": canales[:],
        "Torre_IO": canales[:],
        "Portal": canales[:],
        "Nucleo_Central": canales[:],
    }

    # Grafo de adyacencias: sectores conectados no pueden usar el mismo canal
    vecinos = {
        "Base": ["Sector_Luz", "Portal"],
        "Sector_Luz": ["Base", "Arena"],
        "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
        "Torre_IO": ["Arena", "Nucleo_Central"],
        "Portal": ["Base", "Arena"],
        "Nucleo_Central": ["Torre_IO"]
    }

    # Restricción binaria: adyacentes con canal distinto
    def restr_binaria(x: str, y: str, vx: str, vy: str) -> bool:
        if y in vecinos.get(x, []):
            return vx != vy
        return True

    # Restricciones unarias temáticas
    def restr_unaria(var: str, val: str) -> bool:
        # El Núcleo debe ser Blanco por estabilidad del sistema.
        if var == "Nucleo_Central":
            return val == "Blanco"
        # La Torre IO no puede ser Ámbar por interferencia con I/O.
        if var == "Torre_IO":
            return val != "Ambar"
        # Sector de Luz prefiere canales de alta luminosidad (Azul o Cian).
        if var == "Sector_Luz":
            return val in ("Azul", "Cian")
        return True

    # Restricción global opcional:
    # Evitar que Base y Portal sean simultáneamente Azul (control de picos de entrada/salida).
    def rg_base_portal_no_azul(asig: Dict[str, str]) -> bool:
        if "Base" in asig and "Portal" in asig:
            return not (asig["Base"] == "Azul" and asig["Portal"] == "Azul")
        return True

    # Otra restricción global: al menos dos sectores deben usar Cian para redundancia
    # Nota: se verifica al final cuando todas las variables estén asignadas.
    def rg_min_cian(asig: Dict[str, str]) -> bool:
        if len(asig) < 6:
            return True  # se evalúa al final
        conteo = sum(1 for v in asig.values() if v == "Cian")
        return conteo >= 2

    csp = CSP(
        variables=variables,
        dominios=dominios,
        vecinos=vecinos,
        restriccion_binaria=restr_binaria,
        restriccion_unaria=restr_unaria,
        restricciones_globales=[rg_base_portal_no_azul, rg_min_cian],
    )
    return csp

# ============================================================
# Ejecución de demostración
# ============================================================

def demo_tron_csp():
    csp = construir_CSP_TRON()
    solucion, pasos = backtracking_buscar(csp)

    print("Registro del proceso:")
    for p in pasos:
        print(" -", p)

    if solucion is None:
        print("\nNo se encontró solución.")
    else:
        print("\nSolución encontrada:")
        for var in csp.variables:
            print(f"  {var:15s} = {solucion[var]}")

if __name__ == "__main__":
    demo_tron_csp()