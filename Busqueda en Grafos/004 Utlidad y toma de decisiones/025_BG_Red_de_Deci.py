# Redes de Decisión (Influence Diagram) en temática TRON
# - Chance: Interferencia, Firewall, Sensor (depende de Interferencia)
# - Decisión: Ruta (observa Sensor)
# - Utilidad: U(Interferencia, Firewall, Ruta)
# - Salidas: política óptima Sensor->Ruta, MEU con y sin observación, VPI

from typing import Dict, Tuple, List
from dataclasses import dataclass

# ------------------------------------------------------------
# Utilidades probabilísticas básicas
# ------------------------------------------------------------

def normalize(dist: Dict[str, float]) -> Dict[str, float]:
    s = sum(dist.values())
    if s <= 0:
        raise ValueError("Distribución no normalizable.")
    return {k: v / s for k, v in dist.items()}

# ------------------------------------------------------------
# Definición de la red de decisión TRON
# ------------------------------------------------------------

# P(Interferencia)
P_Interf = {
    "Baja": 0.6,
    "Alta": 0.4,
}

# P(Firewall) independiente de Interferencia (para simplificar)
P_Firewall = {
    "Off": 0.7,
    "On": 0.3,
}

# P(Sensor | Interferencia): el sensor es ruidoso pero informativo
# - Si Interferencia=Baja, el sensor dice "OK" con alta probabilidad.
# - Si Interferencia=Alta, el sensor tiende a "Alerta".
P_Sensor_given_Interf = {
    ("OK", "Baja"): 0.85,
    ("Alerta", "Baja"): 0.15,
    ("OK", "Alta"): 0.25,
    ("Alerta", "Alta"): 0.75,
}

# Acciones disponibles (decisión)
RUTAS = ["Sector_Luz", "Portal", "Arena"]

# Utilidad U(Interferencia, Firewall, Ruta)
# Interpretación: energía neta aproximada. Penaliza ir por rutas sensibles cuando hay interferencia o firewall activo.
# Puedes ajustar números para estudiar políticas distintas.
U: Dict[Tuple[str, str, str], float] = {}
def defU(interf: str, fw: str, ruta: str, val: float):
    U[(interf, fw, ruta)] = val

# Heurística de utilidad (coherente con el mundo TRON):
# - Sector_Luz: muy bueno con interferencia baja, ok con firewall off; sensible a firewall y a interferencia alta.
# - Portal: robusto al firewall pero más variable con interferencia alta.
# - Arena: ruta alternativa; mediana con baja, cae con alta y con firewall on.
valores = {
    ("Baja", "Off", "Sector_Luz"): 120,
    ("Baja", "On",  "Sector_Luz"): 85,
    ("Alta", "Off", "Sector_Luz"): 60,
    ("Alta", "On",  "Sector_Luz"): 30,

    ("Baja", "Off", "Portal"):     100,
    ("Baja", "On",  "Portal"):     95,   # portal tolera más firewall
    ("Alta", "Off", "Portal"):     80,
    ("Alta", "On",  "Portal"):     55,

    ("Baja", "Off", "Arena"):       90,
    ("Baja", "On",  "Arena"):       70,
    ("Alta", "Off", "Arena"):       50,
    ("Alta", "On",  "Arena"):       20,
}
for k, v in valores.items():
    defU(*k, v)

# ------------------------------------------------------------
# Inferencia: posteriors y utilidades esperadas
# ------------------------------------------------------------

def P_sensor(e: str) -> Dict[str, float]:
    """
    Posterior P(Interferencia | Sensor=e) por Bayes.
    """
    # Numeradores: P(e|i) P(i)
    num = {}
    for i in P_Interf.keys():
        num[i] = P_Sensor_given_Interf[(e, i)] * P_Interf[i]
    return normalize(num)

def expected_utility_of_action_given_evidence(ruta: str, sensor_obs: str) -> float:
    """
    EU[ ruta | Sensor = sensor_obs ] = sum_i sum_f U(i,f,ruta) P(f) P(i | sensor)
    Asumimos Firewall independiente de Interferencia y del Sensor.
    """
    p_i_given_e = P_sensor(sensor_obs)
    eu = 0.0
    for i, pi in p_i_given_e.items():
        for f, pf in P_Firewall.items():
            eu += U[(i, f, ruta)] * pf * pi
    return eu

def best_action_given_sensor(sensor_obs: str) -> Tuple[str, float, Dict[str, float]]:
    """
    Devuelve la mejor ruta y su EU dado el valor observado del sensor,
    junto con las EU por acción para análisis.
    """
    by_action = {}
    best_a, best_eu = None, float("-inf")
    for a in RUTAS:
        eu = expected_utility_of_action_given_evidence(a, sensor_obs)
        by_action[a] = eu
        if eu > best_eu:
            best_a, best_eu = a, eu
    return best_a, best_eu, by_action

def prior_expected_utility_of_action(ruta: str) -> float:
    """
    EU[ruta] sin observar el sensor: sum_i sum_f U(i,f,ruta) P(i) P(f).
    """
    eu = 0.0
    for i, pi in P_Interf.items():
        for f, pf in P_Firewall.items():
            eu += U[(i, f, ruta)] * pf * pi
    return eu

def best_action_without_sensor() -> Tuple[str, float, Dict[str, float]]:
    by_action = {}
    best_a, best_eu = None, float("-inf")
    for a in RUTAS:
        eu = prior_expected_utility_of_action(a)
        by_action[a] = eu
        if eu > best_eu:
            best_a, best_eu = a, eu
    return best_a, best_eu, by_action

def probability_of_sensor(e: str) -> float:
    """
    P(Sensor=e) = sum_i P(e|i) P(i)
    """
    s = 0.0
    for i, pi in P_Interf.items():
        s += P_Sensor_given_Interf[(e, i)] * pi
    return s

def MEU_with_policy() -> Tuple[Dict[str, str], float]:
    """
    Calcula la política óptima π*: Sensor -> Ruta y su utilidad esperada MEU.
    MEU = sum_e P(e) * max_a EU[a | e]
    """
    policy = {}
    MEU = 0.0
    for e in ["OK", "Alerta"]:
        a_star, eu_star, _ = best_action_given_sensor(e)
        policy[e] = a_star
        MEU += probability_of_sensor(e) * eu_star
    return policy, MEU

def value_of_perfect_information() -> float:
    """
    VPI del sensor = MEU(con observar Sensor) - MEU(sin observar Sensor)
    """
    policy, meu_with = MEU_with_policy()
    _, meu_wo, _ = best_action_without_sensor()
    return meu_with - meu_wo

# ------------------------------------------------------------
# Demo
# ------------------------------------------------------------

def demo():
    print("=== Red de Decisión TRON: política óptima condicionada al Sensor ===\n")

    # Mejor acción sin observar el sensor
    a0, eu0, tabla0 = best_action_without_sensor()
    print("Sin observar el Sensor (política fija):")
    for a in RUTAS:
        print(f"  EU[{a}] = {tabla0[a]:.2f}")
    print(f"  Mejor ruta a priori: {a0} con EU = {eu0:.2f}\n")

    # Mejor acción condicionada a cada observación del sensor
    for e in ["OK", "Alerta"]:
        a_e, eu_e, tabla_e = best_action_given_sensor(e)
        post = P_sensor(e)
        print(f"Observando Sensor={e}:")
        print(f"  Posterior Interferencia | {e}: " +
              ", ".join([f"{i}={post[i]:.3f}" for i in ["Baja","Alta"]]))
        for a in RUTAS:
            print(f"  EU[{a} | {e}] = {tabla_e[a]:.2f}")
        print(f"  Mejor acción dado {e}: {a_e} con EU = {eu_e:.2f}\n")

    # Política óptima y VPI
    policy, meu_with = MEU_with_policy()
    vpi = value_of_perfect_information()
    print("Política óptima π* observando el Sensor:")
    for e in ["OK", "Alerta"]:
        print(f"  Si Sensor={e} -> elegir {policy[e]}")
    print(f"\nMEU con observación del Sensor: {meu_with:.2f}")
    print(f"MEU sin observación:           {eu0:.2f}")
    print(f"Valor de la Información (VPI): {vpi:.2f}")

if __name__ == "__main__":
    demo()