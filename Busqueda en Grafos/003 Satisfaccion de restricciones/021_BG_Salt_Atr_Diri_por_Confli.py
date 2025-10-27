# Salto Atrás Dirigido por Conflictos (Conflict-Directed Backjumping, CBJ)
# Temática TRON: coloración (canales de energía) de sectores del Grid.

from typing import Dict, List, Tuple, Optional, Set
import copy

# ============================================================
# Definición del problema TRON (CSP de coloración)
# ============================================================

def construir_csp_tron():
    variables = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
    canales = ["Azul", "Cian", "Blanco", "Ambar"]

    dominios: Dict[str, List[str]] = {v: list(canales) for v in variables}

    vecinos: Dict[str, List[str]] = {
        "Base": ["Sector_Luz", "Portal"],
        "Sector_Luz": ["Base", "Arena"],
        "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
        "Torre_IO": ["Arena", "Nucleo_Central"],
        "Portal": ["Base", "Arena"],
        "Nucleo_Central": ["Torre_IO"],
    }

    def restr_unaria(var: str, val: str) -> bool:
        if var == "Nucleo_Central":
            return val == "Blanco"          # Estabilidad del Núcleo
        if var == "Torre_IO":
            return val != "Ambar"           # Interferencia I/O
        if var == "Sector_Luz":
            return val in ("Azul", "Cian")  # Alta luminosidad
        return True

    def restr_binaria(x: str, y: str, vx: str, vy: str) -> bool:
        # Sectores adyacentes no pueden compartir canal
        if y in vecinos.get(x, []):
            return vx != vy
        return True

    # Restricción global simple que podemos comprobar parcialmente:
    # Base y Portal no pueden ser ambos Azul.
    def restr_global_parcial(asig: Dict[str, str]) -> Tuple[bool, Optional[Tuple[str, str]]]:
        if "Base" in asig and "Portal" in asig:
            if asig["Base"] == "Azul" and asig["Portal"] == "Azul":
                return False, ("Base", "Portal")
        return True, None

    return variables, dominios, vecinos, restr_unaria, restr_binaria, restr_global_parcial

# ============================================================
# Utilidades de consistencia y ayuda a CBJ
# ============================================================

def consistente_con(asig: Dict[str, str],
                    var: str, val: str,
                    vecinos: Dict[str, List[str]],
                    restr_unaria,
                    restr_binaria,
                    restr_global_parcial) -> Tuple[bool, Set[str]]:
    """
    Revisa si (var=val) es consistente con la asignación parcial.
    Devuelve (ok, culpables). 'culpables' es el conjunto de variables ya asignadas
    que causan el conflicto. Se usa para actualizar conjuntos de conflicto.
    """
    culpables: Set[str] = set()

    # Unaria
    if not restr_unaria(var, val):
        # No hay culpable asignado específico; lo dejamos vacío.
        return False, culpables

    # Binarias frente a asignadas
    for u in asig:
        if not restr_binaria(var, u, val, asig[u]) or not restr_binaria(u, var, asig[u], val):
            culpables.add(u)

    # Global parcial (puede apuntar a variables concretas)
    ok_global, par = restr_global_parcial({**asig, var: val})
    if not ok_global and par is not None:
        # Añade como culpables a los que participan en la global y ya están asignados
        for w in par:
            if w in asig:
                culpables.add(w)

    return (len(culpables) == 0), culpables

# ============================================================
# CBJ (Conflict-Directed Backjumping) clásico con orden fijo
# ============================================================

def cbj_buscar(variables: List[str],
               dominios_iniciales: Dict[str, List[str]],
               vecinos: Dict[str, List[str]],
               restr_unaria,
               restr_binaria,
               restr_global_parcial):
    """
    Implementación educativa de CBJ con:
      - Orden fijo de variables (en el orden de 'variables').
      - Conjuntos de conflicto C(var).
      - Salto atrás al índice más alto en C(var) cuando var se queda sin valores.
    """
    # Copias de trabajo
    dominios = {v: list(dominios_iniciales[v]) for v in variables}
    asignacion: Dict[str, str] = {}
    log: List[str] = []

    # Pre-poda unaria
    for v in variables:
        d0 = list(dominios[v])
        dominios[v] = [x for x in d0 if restr_unaria(v, x)]
        if not dominios[v]:
            log.append(f"Dominio vacío inicial por unaria en {v}.")
            return None, log

    # Conjunto de conflicto por variable
    C: Dict[str, Set[str]] = {v: set() for v in variables}

    # Índices y cursores de valores
    n = len(variables)
    i = 0
    valor_idx: Dict[str, int] = {v: 0 for v in variables}
    orden_valores: Dict[str, List[str]] = {v: list(dominios[v]) for v in variables}

    # Función para reiniciar una variable cuando retrocedemos por encima de ella
    def reset_var(v: str):
        if v in asignacion:
            del asignacion[v]
        C[v].clear()
        valor_idx[v] = 0
        orden_valores[v] = list(dominios[v])

    while 0 <= i < n:
        var = variables[i]
        asignada_previa = var in asignacion

        # Si llegamos aquí tras un salto, continuamos donde íbamos; si no, iniciamos
        if not asignada_previa and valor_idx[var] >= len(orden_valores[var]):
            # Sin más valores: dead-end en var
            if not C[var]:
                log.append(f"Fallo en {var} sin culpables: inconsistencia global.")
                return None, log
            # Saltar al responsable de mayor índice
            jump_to_var, jump_to_idx = None, -1
            for u in C[var]:
                idx_u = variables.index(u)
                if idx_u > jump_to_idx:
                    jump_to_var, jump_to_idx = u, idx_u

            log.append(f"Dead-end en {var}. Conflicto con {sorted(C[var])}. Saltando a {jump_to_var}.")

            # Fusionar causas: C(jump) = C(jump) U (C(var) - {jump_to_var})
            C[jump_to_var].update(C[var] - {jump_to_var})
            # Resetear variables entre jump_to_idx+1 y i (exclusivo)
            for k in range(jump_to_idx + 1, i + 1):
                v = variables[k]
                reset_var(v)
            # Reanudar en la variable a la que saltamos, descartando el valor usado
            i = jump_to_idx
            # Avanzar el cursor de jump_to_var para intentar otro valor
            valor_idx[jump_to_var] += 1
            continue

        # Si la variable no está asignada aún, intenta valores desde valor_idx
        asigno_algo = False
        while valor_idx[var] < len(orden_valores[var]):
            val = orden_valores[var][valor_idx[var]]
            ok, culpables = consistente_con(asignacion, var, val,
                                            vecinos, restr_unaria, restr_binaria,
                                            restr_global_parcial)
            if ok:
                asignacion[var] = val
                log.append(f"Asignar {var} = {val}")
                asigno_algo = True
                i += 1
                break
            else:
                # Registrar culpables del fallo en el conjunto de conflicto de var
                C[var].update(culpables)
                log.append(f"Rechazar {var} = {val} por conflicto con {sorted(culpables)}")
                valor_idx[var] += 1

        if not asigno_algo:
            # No quedaban valores para var: proceder al manejo de dead-end al inicio del bucle
            continue

        # Si avanzamos, preparar la siguiente variable: limpiar su estado si estaba sucia
        if i < n:
            nxt = variables[i]
            if nxt in asignacion:
                del asignacion[nxt]
            C[nxt].clear()
            valor_idx[nxt] = 0
            orden_valores[nxt] = list(dominios[nxt])

    # Asignación completa
    return asignacion, log

# ============================================================
# Demo
# ============================================================

def demo():
    variables, dominios, vecinos, ru, rb, rg = construir_csp_tron()

    # Orden fijo de ejemplo (puedes cambiarlo para ver saltos distintos)
    # variables = ["Sector_Luz", "Base", "Portal", "Arena", "Torre_IO", "Nucleo_Central"]

    solucion, log = cbj_buscar(variables, dominios, vecinos, ru, rb, rg)

    print("Registro del proceso (CBJ):")
    for linea in log:
        print(" -", linea)

    if solucion is None:
        print("\nNo se encontró solución.")
    else:
        print("\nSolución encontrada:")
        for v in variables:
            print(f"  {v:15s} = {solucion[v]}")

if __name__ == "__main__":
    demo()