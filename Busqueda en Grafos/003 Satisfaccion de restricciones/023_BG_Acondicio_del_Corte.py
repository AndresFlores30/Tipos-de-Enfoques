# Cutset Conditioning (versión simple) en un CSP de TRON

from collections import deque
from itertools import product

# --------------------------
# CSP TRON (coloración)
# --------------------------
VARS = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]
COLORES = ["Azul", "Cian", "Blanco", "Ambar"]

DOM = {v: COLORES[:] for v in VARS}

NEIGH = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": ["Torre_IO"],
}

def unaria(var, val):
    if var == "Nucleo_Central": return val == "Blanco"
    if var == "Torre_IO":       return val != "Ambar"
    if var == "Sector_Luz":     return val in ("Azul", "Cian")
    return True

def binaria(x, y, vx, vy):
    if y in NEIGH.get(x, []): return vx != vy
    return True

# --------------------------
# Utilidades
# --------------------------
def podar_unarias(dom):
    for v in VARS:
        dom[v] = [x for x in dom[v] if unaria(v, x)]
        if not dom[v]: return False
    return True

def core_por_deshojado():
    deg = {v: len(NEIGH[v]) for v in VARS}
    elim = set()
    q = deque([v for v in VARS if deg[v] <= 1])
    while q:
        v = q.popleft()
        if v in elim: continue
        elim.add(v)
        for u in NEIGH[v]:
            if u in elim: continue
            deg[u] -= 1
            if deg[u] == 1: q.append(u)
    return sorted([v for v in VARS if v not in elim])

def ac3(dom):
    q = deque()
    for xi in VARS:
        for xj in NEIGH[xi]:
            q.append((xi, xj))

    def revisar(xi, xj):
        changed = False
        vals = dom[xi][:]
        for vi in vals:
            # ¿existe soporte en xj?
            ok = False
            for vj in dom[xj]:
                if binaria(xi, xj, vi, vj) and unaria(xj, vj):
                    ok = True; break
            if not ok:
                dom[xi].remove(vi); changed = True
        return changed

    while q:
        xi, xj = q.popleft()
        if revisar(xi, xj):
            if not dom[xi]: return False
            for xk in NEIGH[xi]:
                if xk != xj:
                    q.append((xk, xi))
    return True

def mrv(dom, asign):
    candidatos = [v for v in VARS if v not in asign]
    return min(candidatos, key=lambda v: len(dom[v]))

def consistente_local(var, val, asign):
    if not unaria(var, val): return False
    for u, vu in asign.items():
        if not binaria(var, u, val, vu): return False
    return True

def backtracking_bosque(dom, asign):
    if len(asign) == len(VARS):
        return dict(asign)
    var = mrv(dom, asign)
    for val in dom[var]:
        if consistente_local(var, val, asign):
            asign[var] = val
            res = backtracking_bosque(dom, asign)
            if res: return res
            del asign[var]
    return None

# --------------------------
# Cutset Conditioning simple
# --------------------------
def cutset_conditioning_simple():
    dom0 = {v: DOM[v][:] for v in VARS}
    if not podar_unarias(dom0):
        print("Inconsistente tras unarias."); return None

    cutset = core_por_deshojado()   # si vacío, el grafo ya es bosque
    resto = [v for v in VARS if v not in cutset]
    print("Cutset aproximado:", cutset if cutset else "(vacío)")

    if not cutset:
        dom = {v: dom0[v][:] for v in VARS}
        if not ac3(dom): print("Sin solución."); return None
        sol = backtracking_bosque(dom, {})
        imprimir_sol(sol); return sol

    # Enumeración sencilla del corte
    dominios_corte = [dom0[v] for v in cutset]
    for valores in product(*dominios_corte):
        asign_corte = dict(zip(cutset, valores))
        # Chequeo rápido binario dentro del corte
        ok = True
        for i, vi in asign_corte.items():
            for j, vj in asign_corte.items():
                if i == j: continue
                if j in NEIGH[i] and vi == vj:
                    ok = False; break
            if not ok: break
        if not ok: continue

        dom = {v: dom0[v][:] for v in VARS}
        for v, val in asign_corte.items():
            dom[v] = [val]

        if not ac3(dom):  # poda antes de resolver el bosque
            continue

        sol = backtracking_bosque(dom, dict(asign_corte))
        if sol:
            imprimir_sol(sol); return sol

    print("No se encontró solución.")
    return None

def imprimir_sol(sol):
    if not sol:
        print("Sin solución."); return
    print("Solución:")
    for v in VARS:
        print(f"  {v:15s} = {sol[v]}")

# --------------------------
# Demo
# --------------------------
if __name__ == "__main__":
    cutset_conditioning_simple()