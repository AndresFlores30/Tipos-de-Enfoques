# - MEU sin información
# - EVPI (información perfecta sobre Interferencia)
# - EVSI (información imperfecta mediante un Sensor con ruido y costo)
# - Política óptima condicionada al sensor y análisis de sensibilidad

from typing import Dict, Tuple, List

# ------------------------------------------------------------
# Modelo TRON (probabilidades y utilidades)
# ------------------------------------------------------------

# P(Interferencia)
P_Interf = {"Baja": 0.6, "Alta": 0.4}

# P(Firewall) independiente para simplificar
P_Firewall = {"Off": 0.7, "On": 0.3}

# Acciones (rutas)
RUTAS = ["Sector_Luz", "Portal", "Arena"]

# Utilidad U(Interferencia, Firewall, Ruta)
U: Dict[Tuple[str, str, str], float] = {}
def defU(interf: str, fw: str, ruta: str, val: float):
    U[(interf, fw, ruta)] = val

valores = {
    ("Baja", "Off", "Sector_Luz"): 120,
    ("Baja", "On",  "Sector_Luz"): 85,
    ("Alta", "Off", "Sector_Luz"): 60,
    ("Alta", "On",  "Sector_Luz"): 30,

    ("Baja", "Off", "Portal"):     100,
    ("Baja", "On",  "Portal"):      95,
    ("Alta", "Off", "Portal"):      80,
    ("Alta", "On",  "Portal"):      55,

    ("Baja", "Off", "Arena"):       90,
    ("Baja", "On",  "Arena"):       70,
    ("Alta", "Off", "Arena"):       50,
    ("Alta", "On",  "Arena"):       20,
}
for k, v in valores.items():
    defU(*k, v)

# ------------------------------------------------------------
# Utilidades auxiliares
# ------------------------------------------------------------

def eu_ruta_priori(ruta: str) -> float:
    """EU[ruta] sin observar nada."""
    eu = 0.0
    for i, pi in P_Interf.items():
        for f, pf in P_Firewall.items():
            eu += U[(i, f, ruta)] * pi * pf
    return eu

def mejor_ruta_priori() -> Tuple[str, float, Dict[str, float]]:
    tabla = {a: eu_ruta_priori(a) for a in RUTAS}
    mejor = max(tabla, key=tabla.get)
    return mejor, tabla[mejor], tabla

def posterior_interf_dado_sensor(sensor: str,
                                 p_ok_dado_baja: float,
                                 p_ok_dado_alta: float) -> Dict[str, float]:
    """
    P(Interferencia | Sensor) con Bayes a partir de:
      P(Sensor=OK|Baja)=p_ok_dado_baja, P(Sensor=OK|Alta)=p_ok_dado_alta
      P(Sensor=Alerta|i) = 1 - P(Sensor=OK|i)
    """
    if sensor == "OK":
        num_baja = p_ok_dado_baja * P_Interf["Baja"]
        num_alta = p_ok_dado_alta * P_Interf["Alta"]
    else:
        num_baja = (1 - p_ok_dado_baja) * P_Interf["Baja"]
        num_alta = (1 - p_ok_dado_alta) * P_Interf["Alta"]
    s = num_baja + num_alta
    return {"Baja": num_baja / s, "Alta": num_alta / s}

def prob_sensor(sensor: str,
                p_ok_dado_baja: float,
                p_ok_dado_alta: float) -> float:
    """P(Sensor=sensor) marginal."""
    if sensor == "OK":
        return p_ok_dado_baja * P_Interf["Baja"] + p_ok_dado_alta * P_Interf["Alta"]
    return (1 - p_ok_dado_baja) * P_Interf["Baja"] + (1 - p_ok_dado_alta) * P_Interf["Alta"]

def eu_ruta_cond_sensor(ruta: str,
                        sensor: str,
                        p_ok_dado_baja: float,
                        p_ok_dado_alta: float) -> float:
    """EU[ruta | Sensor] suponiendo Firewall independiente del sensor e interferencia."""
    post = posterior_interf_dado_sensor(sensor, p_ok_dado_baja, p_ok_dado_alta)
    eu = 0.0
    for i, pi in post.items():
        for f, pf in P_Firewall.items():
            eu += U[(i, f, ruta)] * pi * pf
    return eu

def mejor_ruta_cond_sensor(sensor: str,
                           p_ok_dado_baja: float,
                           p_ok_dado_alta: float) -> Tuple[str, float, Dict[str, float]]:
    tabla = {a: eu_ruta_cond_sensor(a, sensor, p_ok_dado_baja, p_ok_dado_alta) for a in RUTAS}
    mejor = max(tabla, key=tabla.get)
    return mejor, tabla[mejor], tabla

# ------------------------------------------------------------
# EVPI, EVSI y política óptima con sensor
# ------------------------------------------------------------

def meu_con_sensor(p_ok_dado_baja: float,
                   p_ok_dado_alta: float,
                   costo_obs: float = 0.0) -> Tuple[float, Dict[str, str]]:
    """
    MEU al observar un sensor imperfecto con costo de observación.
    Política: para cada e en {OK, Alerta}, elegir la ruta con mayor EU dado e.
    """
    meu = 0.0
    policy: Dict[str, str] = {}
    for e in ["OK", "Alerta"]:
        p_e = prob_sensor(e, p_ok_dado_baja, p_ok_dado_alta)
        a_e, eu_e, _ = mejor_ruta_cond_sensor(e, p_ok_dado_baja, p_ok_dado_alta)
        policy[e] = a_e
        meu += p_e * eu_e
    meu -= costo_obs
    return meu, policy

def evpi_interferencia() -> float:
    """
    EVPI respecto a Interferencia: observar el estado real de Interferencia antes de decidir.
    """
    meu_perfect = 0.0
    for i, pi in P_Interf.items():
        # Mejor acción con conocimiento perfecto de i
        mejor_eu_i = max(
            sum(U[(i, f, ruta)] * P_Firewall[f] for f in P_Firewall) for ruta in RUTAS
        )
        meu_perfect += pi * mejor_eu_i
    _, meu0, _ = mejor_ruta_priori()
    return meu_perfect - meu0

def evsi_sensor(p_ok_dado_baja: float,
                p_ok_dado_alta: float,
                costo_obs: float = 0.0) -> Tuple[float, float, Dict[str, str]]:
    """
    EVSI del sensor con parámetros dados:
    devuelve (EVSI, MEU_con_sensor, policy).
    """
    meu1, policy = meu_con_sensor(p_ok_dado_baja, p_ok_dado_alta, costo_obs=costo_obs)
    _, meu0, _ = mejor_ruta_priori()
    return (meu1 - meu0), meu1, policy

def costo_maximo_racional(p_ok_dado_baja: float, p_ok_dado_alta: float) -> float:
    """
    Umbral de costo tal que el decisor es indiferente entre observar o no:
    costo* = MEU_con_sensor_sin_costo - MEU_sin_info
    """
    meu_sin_costo, _ = meu_con_sensor(p_ok_dado_baja, p_ok_dado_alta, costo_obs=0.0)
    _, meu0, _ = mejor_ruta_priori()
    return max(0.0, meu_sin_costo - meu0)

# ------------------------------------------------------------
# Demo
# ------------------------------------------------------------

def demo():
    print("=== Valor de la Información en TRON ===\n")

    # 1) MEU sin información
    a0, meu0, tabla0 = mejor_ruta_priori()
    print("Sin observar sensor:")
    for a in RUTAS:
        print(f"  EU[{a}] = {tabla0[a]:.2f}")
    print(f"  Mejor ruta a priori: {a0} con MEU = {meu0:.2f}\n")

    # 2) EVPI (información perfecta sobre Interferencia)
    evpi = evpi_interferencia()
    print(f"EVPI sobre Interferencia: {evpi:.2f}")
    print("Interpretación: mejora máxima esperable si conociéramos exactamente la interferencia antes de decidir.\n")

    # 3) EVSI con sensor imperfecto
    # Parámetros de fiabilidad del sensor:
    #   p_ok_dado_baja = P(Sensor=OK | Interferencia=Baja)
    #   p_ok_dado_alta = P(Sensor=OK | Interferencia=Alta)
    p_ok_baja = 0.70
    p_ok_alta = 0.20
    costo = 5.0  # costo de observar el sensor (energía/unidades equivalentes)

    evsi, meu1, policy = evsi_sensor(p_ok_baja, p_ok_alta, costo_obs=costo)
    print(f"Con sensor imperfecto (costo={costo:.2f}):")
    print(f"  MEU con sensor = {meu1:.2f}")
    print(f"  EVSI = MEU_con_sensor - MEU_sin_info = {evsi:.2f}")
    print("  Política óptima condicionada al sensor:")
    for e in ["OK", "Alerta"]:
        print(f"    Si Sensor={e} -> Ruta {policy[e]}")
    print()

    # 4) Umbral de costo racional para observar
    c_star = costo_maximo_racional(p_ok_baja, p_ok_alta)
    print(f"Costo máximo racional de observación (indiferencia): {c_star:.2f}")
    print("Si el costo real es menor que este umbral, conviene observar; si es mayor, no conviene.\n")

    # 5) Análisis de sensibilidad del EVSI respecto a la calidad del sensor
    print("Sensibilidad del EVSI al variar la calidad del sensor (sin costo):")
    print("  pOK|Baja  pOK|Alta   EVSI")
    for p_baja in [0.60, 0.70, 0.80, 0.85, 0.90]:
        for p_alta in [0.50, 0.40, 0.30, 0.25, 0.20]:
            evsi_sin_costo, _, _ = evsi_sensor(p_baja, p_alta, costo_obs=0.0)
            print(f"   {p_baja:6.2f}   {p_alta:6.2f}   {evsi_sin_costo:6.2f}")
        print()

if __name__ == "__main__":
    demo()