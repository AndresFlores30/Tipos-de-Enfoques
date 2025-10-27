# Teoría de la Utilidad en temática TRON
# - Funciones de utilidad: CARA y CRRA
# - Loterías (resultados con probabilidades)
# - Utilidad esperada, equivalente cierto y prima de riesgo
# - Demo con rutas del Grid de TRON (recompensas energéticas y riesgos)

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Callable
import math
import random

# ---------------------------------------------------------------------
# Funciones de utilidad
# ---------------------------------------------------------------------

class Utility:
    """
    Base para funciones de utilidad u(x).
    x representa recursos/energía/ingreso (x > 0 para CRRA).
    """

    def u(self, x: float) -> float:
        raise NotImplementedError

    def inverse_u(self, uval: float) -> float:
        """
        Inversa de la utilidad, necesaria para equivalentes ciertos.
        Debe implementarse acorde a la forma funcional.
        """
        raise NotImplementedError


class CARA(Utility):
    """
    CARA: u(x) = -exp(-a x)
    - a > 0: aversión absoluta al riesgo constante
    - Dominio x en R
    """
    def __init__(self, a: float = 0.01):
        assert a > 0, "El parámetro a debe ser > 0"
        self.a = a

    def u(self, x: float) -> float:
        return -math.exp(-self.a * x)

    def inverse_u(self, uval: float) -> float:
        # u = -exp(-a x) -> -u = exp(-a x) -> ln(-u) = -a x -> x = -ln(-u)/a
        if uval >= 0:
            raise ValueError("Para CARA, u(x) < 0 siempre; no existe inversa para u >= 0.")
        return -math.log(-uval) / self.a


class CRRA(Utility):
    """
    CRRA: u(x) = x^(1 - r)/(1 - r), si r != 1
          u(x) = ln(x), si r = 1
    - r: coeficiente de aversión relativa al riesgo
    - Dominio x > 0
    """
    def __init__(self, r: float = 0.5):
        assert r >= 0, "El parámetro r debe ser >= 0"
        self.r = r

    def u(self, x: float) -> float:
        if x <= 0:
            return float("-inf")
        if self.r == 1.0:
            return math.log(x)
        return x ** (1.0 - self.r) / (1.0 - self.r)

    def inverse_u(self, uval: float) -> float:
        if self.r == 1.0:
            # u = ln(x) -> x = e^u
            return math.exp(uval)
        # u = x^(1-r)/(1-r) -> (1-r)u = x^(1-r) -> x = [(1-r)u]^(1/(1-r))
        base = (1.0 - self.r) * uval
        if base <= 0:
            return 0.0
        return base ** (1.0 / (1.0 - self.r))


# ---------------------------------------------------------------------
# Loterías y métricas de decisión
# ---------------------------------------------------------------------

@dataclass
class Outcome:
    energia: float     # recompensa en energía/recursos
    etiqueta: str      # descripción (p.ej. "Cruzar Arena", "Firewall leve")


@dataclass
class Lottery:
    """
    Lotería: lista de (probabilidad, Outcome)
    Las probabilidades deben sumar 1.
    """
    eventos: List[Tuple[float, Outcome]]

    def normalizada(self) -> "Lottery":
        s = sum(p for p, _ in self.eventos)
        if s <= 0:
            raise ValueError("Suma de probabilidades no positiva.")
        if abs(s - 1.0) < 1e-9:
            return self
        return Lottery([(p / s, o) for p, o in self.eventos])

    def expected_utility(self, u: Utility) -> float:
        ev = 0.0
        for p, out in self.eventos:
            ev += p * u.u(out.energia)
        return ev

    def certainty_equivalent(self, u: Utility) -> float:
        ue = self.expected_utility(u)
        return u.inverse_u(ue)

    def risk_premium(self, u: Utility) -> float:
        """
        Prima de riesgo = Valor esperado monetario - Equivalente cierto.
        Si es positiva, el decisor pagaría por eliminar el riesgo.
        """
        valor_esperado = sum(p * out.energia for p, out in self.eventos)
        ce = self.certainty_equivalent(u)
        return valor_esperado - ce


def elegir_mejor(loterias: Dict[str, Lottery], u: Utility) -> Tuple[str, Dict[str, Dict[str, float]]]:
    """
    Devuelve la mejor opción por utilidad esperada y un reporte con:
    - EU
    - valor esperado monetario
    - equivalente cierto (CE)
    - prima de riesgo (RP)
    """
    reporte: Dict[str, Dict[str, float]] = {}
    mejor, mejor_eu = None, float("-inf")
    for nombre, L in loterias.items():
        L = L.normalizada()
        eu = L.expected_utility(u)
        ce = L.certainty_equivalent(u)
        ve = sum(p * out.energia for p, out in L.eventos)
        rp = ve - ce
        reporte[nombre] = {"EU": eu, "VE": ve, "CE": ce, "RP": rp}
        if eu > mejor_eu:
            mejor_eu = eu
            mejor = nombre
    return mejor, reporte


# ---------------------------------------------------------------------
# Escenario TRON: rutas del Grid con recompensas y riesgos
# ---------------------------------------------------------------------

def construir_escenario_tron() -> Dict[str, Lottery]:
    """
    Tres rutas del Grid con distinta distribución de resultados energéticos.
    Las unidades pueden interpretarse como puntos de energía estabilizada.
    """
    random.seed(7)

    # Ruta A: Sector_Luz -> Torre_IO (estable pero modesta)
    ruta_A = Lottery([
        (0.90, Outcome(energia=80, etiqueta="Transmisión limpia por Sector_Luz")),
        (0.10, Outcome(energia=40, etiqueta="Interferencia menor en Torre_IO")),
    ])

    # Ruta B: Portal -> Arena (alta varianza, gran premio posible)
    ruta_B = Lottery([
        (0.60, Outcome(energia=50, etiqueta="Retraso por colisiones en Arena")),
        (0.35, Outcome(energia=120, etiqueta="Aceleración a través de Portal optimizado")),
        (0.05, Outcome(energia=5, etiqueta="Corte de suministro temporal")),
    ])

    # Ruta C: Base -> Núcleo_Central directo (muy riesgosa, resultados extremos)
    ruta_C = Lottery([
        (0.15, Outcome(energia=200, etiqueta="Sintonía perfecta con el Núcleo_Central")),
        (0.25, Outcome(energia=100, etiqueta="Paso seguro con inestabilidad controlada")),
        (0.30, Outcome(energia=30, etiqueta="Pérdida de paquetes en tránsito")),
        (0.30, Outcome(energia=1, etiqueta="Firewall severo"))
    ])

    return {
        "Ruta_A_SectorLuz_TorreIO": ruta_A,
        "Ruta_B_Portal_Arena": ruta_B,
        "Ruta_C_Base_Nucleo": ruta_C,
    }


# ---------------------------------------------------------------------
# Experimentos: variar aversión al riesgo y comparar
# ---------------------------------------------------------------------

def experimento_crra():
    print("=== Experimento CRRA (u(x) = x^(1-r)/(1-r); r=1 -> ln x) ===")
    loterias = construir_escenario_tron()

    for r in [0.0, 0.5, 1.0, 2.0]:
        u = CRRA(r=r)
        mejor, rep = elegir_mejor(loterias, u)
        print(f"\nAversión relativa r = {r}")
        for nombre, stats in rep.items():
            print(f"  {nombre}: EU={stats['EU']:.6f}, VE={stats['VE']:.2f}, CE={stats['CE']:.2f}, RP={stats['RP']:.2f}")
        print(f"  Mejor por EU -> {mejor}")

def experimento_cara():
    print("\n=== Experimento CARA (u(x) = -exp(-a x)) ===")
    loterias = construir_escenario_tron()

    for a in [0.005, 0.01, 0.02, 0.05]:
        u = CARA(a=a)
        mejor, rep = elegir_mejor(loterias, u)
        print(f"\nAversión absoluta a = {a}")
        for nombre, stats in rep.items():
            print(f"  {nombre}: EU={stats['EU']:.6f}, VE={stats['VE']:.2f}, CE={stats['CE']:.2f}, RP={stats['RP']:.2f}")
        print(f"  Mejor por EU -> {mejor}")

# ---------------------------------------------------------------------
# Simulación de elección por mín-conflictos local (ilustrativa)
# No sustituye teoría: solo muestra cómo una heurística local podría
# iterar hacia una asignación que aumente la utilidad esperada.
# ---------------------------------------------------------------------

def min_conflicts_choice(loterias: Dict[str, Lottery], u: Utility, pasos: int = 200, seed: int = 123) -> str:
    random.seed(seed)
    opciones = list(loterias.keys())
    actual = random.choice(opciones)
    eu_actual = loterias[actual].expected_utility(u)

    for _ in range(pasos):
        vecino = random.choice(opciones)
        eu_vecino = loterias[vecino].expected_utility(u)
        # Si reduce conflicto (aumenta EU), moverse
        if eu_vecino > eu_actual:
            actual, eu_actual = vecino, eu_vecino
    return actual

def experimento_min_conflicts():
    print("\n=== Heurística local (ilustrativa) ===")
    loterias = construir_escenario_tron()
    u = CRRA(r=1.0)  # log(x)
    eleccion = min_conflicts_choice(loterias, u, pasos=500)
    print(f"Elección heurística tras 500 pasos con CRRA r=1.0: {eleccion}")

# ---------------------------------------------------------------------
# Demo principal
# ---------------------------------------------------------------------

def demo():
    print("Teoría de la Utilidad en TRON: comparación de rutas energéticas")
    experimento_crra()
    experimento_cara()
    experimento_min_conflicts()

if __name__ == "__main__":
    demo()