# Búsqueda Local: Mínimos-Conflictos (Min-Conflicts) en un CSP temático de TRON
# - Variables: sectores del Grid
# - Valores: canales de energía (colores)
# - Restricciones: unarias, binarias (adyacencia distinta) y globales
# - Estrategia: Min-Conflicts con reinicios y caminata aleatoria opcional

from typing import Dict, List, Tuple, Callable, Optional
import random

Variables = List[str]
Dominios = Dict[str, List[str]]
Vecinos = Dict[str, List[str]]
Asignacion = Dict[str, str]

# ------------------------------------------------------------
# Definición del problema TRON
# ------------------------------------------------------------

def construir_problema_tron() -> Tuple[Variables, Dominios, Vecinos,
                                        Callable[[str, str], bool],
                                        Callable[[str, str, str, str], bool],
                                        List[Callable[[Asignacion], int]]]:
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

    # Restricciones unarias temáticas (devuelven True si es válido)
    def restr_unaria(var: str, val: str) -> bool:
        if var == "Nucleo_Central":
            return val == "Blanco"            # Núcleo estable en Blanco
        if var == "Torre_IO":
            return val != "Ambar"             # Interferencia I/O
        if var == "Sector_Luz":
            return val in ("Azul", "Cian")    # Alta luminosidad
        return True

    # Restricción binaria: sectores adyacentes no comparten canal
    def restr_binaria(x: str, y: str, vx: str, vy: str) -> bool:
        if y in vecinos.get(x, []):
            return vx != vy
        return True

    # Restricciones globales como funciones de penalización (0 si cumple, >0 si viola)
    def rg_base_portal_no_ambos_azul(asig: Asignacion) -> int:
        if "Base" in asig and "Portal" in asig:
            return 1 if (asig["Base"] == "Azul" and asig["Portal"] == "Azul") else 0
        return 0  # no penaliza parcialmente

    def rg_minimo_cian(asig: Asignacion) -> int:
        # Penaliza si, estando completa, hay menos de 2 sectores en Cian
        if len(asig) == len(variables):
            cnt = sum(1 for v in asig.values() if v == "Cian")
            return 0 if cnt >= 2 else (2 - cnt)
        return 0

    restricciones_globales = [rg_base_portal_no_ambos_azul, rg_minimo_cian]

    return variables, dominios, vecinos, restr_unaria, restr_binaria, restricciones_globales

# ------------------------------------------------------------
# Utilidades de evaluación de conflictos
# ------------------------------------------------------------

def contar_conflictos_var(
    var: str,
    val: str,
    asig: Asignacion,
    vecinos: Vecinos,
    restr_unaria: Callable[[str, str], bool],
    restr_binaria: Callable[[str, str, str, str], bool],
    restricciones_globales: List[Callable[[Asignacion], int]]
) -> int:
    """
    Cuántos conflictos habría si var=val manteniendo el resto de la asignación igual.
    Suma:
      - 0/1 por violar unaria en var
      - cantidad de vecinos asignados que violan binaria
      - penalizaciones globales resultantes
    """
    conflictos = 0

    if not restr_unaria(var, val):
        return 10**6  # gran penalización para valores unariamente inválidos

    # Conflictos binarios con vecinos ya asignados
    for u in vecinos[var]:
        if u in asig:
            if not restr_binaria(var, u, val, asig[u]):
                conflictos += 1

    # Globales: evaluar asignación hipotética
    hipotetica = dict(asig)
    hipotetica[var] = val
    for rg in restricciones_globales:
        conflictos += rg(hipotetica)

    return conflictos

def variables_en_conflicto(
    variables: Variables,
    asig: Asignacion,
    vecinos: Vecinos,
    restr_unaria: Callable[[str, str], bool],
    restr_binaria: Callable[[str, str, str, str], bool],
    restricciones_globales: List[Callable[[Asignacion], int]]
) -> List[str]:
    conflicted = []
    for v in variables:
        if v not in asig:
            conflicted.append(v)
            continue
        c = contar_conflictos_var(v, asig[v], {k: asig[k] for k in asig if k != v},
                                  vecinos, restr_unaria, restr_binaria, restricciones_globales)
        if c > 0:
            conflicted.append(v)
    return conflicted

# ------------------------------------------------------------
# Inicialización aleatoria respetando unarias
# ------------------------------------------------------------

def inicializacion_aleatoria_valida(
    variables: Variables,
    dominios: Dominios,
    restr_unaria: Callable[[str, str], bool],
    seed: Optional[int] = None
) -> Asignacion:
    rnd = random.Random(seed)
    asig: Asignacion = {}
    for v in variables:
        vals_validos = [x for x in dominios[v] if restr_unaria(v, x)]
        if not vals_validos:
            raise ValueError(f"Dominio vacío por unaria en {v}")
        asig[v] = rnd.choice(vals_validos)
    return asig

# ------------------------------------------------------------
# Min-Conflicts con reinicios y caminata aleatoria
# ------------------------------------------------------------

def min_conflicts(
    variables: Variables,
    dominios: Dominios,
    vecinos: Vecinos,
    restr_unaria: Callable[[str, str], bool],
    restr_binaria: Callable[[str, str, str, str], bool],
    restricciones_globales: List[Callable[[Asignacion], int]],
    max_pasos: int = 5000,
    prob_caminata: float = 0.05,
    reinicios: int = 10,
    seed: Optional[int] = 42,
    verbose: bool = True
) -> Optional[Asignacion]:
    rnd = random.Random(seed)

    for r in range(reinicios):
        asig = inicializacion_aleatoria_valida(variables, dominios, restr_unaria, seed=rnd.randint(0, 10**9))

        if verbose:
            print(f"Reinicio {r+1}/{reinicios}")

        for paso in range(1, max_pasos + 1):
            conflicted = variables_en_conflicto(variables, asig, vecinos,
                                                restr_unaria, restr_binaria, restricciones_globales)
            if not conflicted:
                if verbose:
                    print(f"Solución encontrada en {paso} pasos del reinicio {r+1}.")
                return asig

            var = rnd.choice(conflicted)

            # Caminata aleatoria: explora sin mirar conflictos
            if rnd.random() < prob_caminata:
                candidatos = [v for v in dominios[var] if restr_unaria(var, v)]
                if candidatos:
                    asig[var] = rnd.choice(candidatos)
                continue

            # Elegir valor que minimiza conflictos (empates al azar)
            mejor_val = None
            mejor_conf = 10**9
            candidatos = []
            for val in dominios[var]:
                conf = contar_conflictos_var(var, val, {k: asig[k] for k in asig if k != var},
                                             vecinos, restr_unaria, restr_binaria, restricciones_globales)
                if conf < mejor_conf:
                    mejor_conf = conf
                    candidatos = [val]
                elif conf == mejor_conf:
                    candidatos.append(val)

            if candidatos:
                asig[var] = rnd.choice(candidatos)

            if verbose and paso % 200 == 0:
                print(f"  Paso {paso}: {len(conflicted)} variables en conflicto.")

    if verbose:
        print("No se encontró solución con los parámetros dados.")
    return None

# ------------------------------------------------------------
# Demo
# ------------------------------------------------------------

def demo():
    variables, dominios, vecinos, ru, rb, rgs = construir_problema_tron()
    solucion = min_conflicts(
        variables, dominios, vecinos, ru, rb, rgs,
        max_pasos=5000,
        prob_caminata=0.10,   # algo de exploración
        reinicios=20,         # varios reinicios por si hay estancamiento
        seed=1234,
        verbose=True
    )

    if solucion is None:
        print("\nNo se encontró solución.")
    else:
        print("\nSolución:")
        for v in variables:
            print(f"  {v:15s} = {solucion[v]}")

if __name__ == "__main__":
    demo()