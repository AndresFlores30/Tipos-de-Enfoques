"""
SISTEMA DE REDES DE DECISION (INFLUENCE DIAGRAM) - TRON DIGITAL

Este modulo implementa una Red de Decision para modelar estrategias optimas
en el Grid de TRON. Combina variables aleatorias del entorno (Interferencia,
Firewall, Sensor) con decisiones de ruta y funciones de utilidad para
determinar politicas optimas y calcular el valor de la informacion.
"""

from typing import Dict, Tuple, List


# ============================================================
# FUNCIONES AUXILIARES PROBABILISTICAS
# ============================================================

def normalizar_distribucion(distribucion: Dict[str, float]) -> Dict[str, float]:
    """
    Normaliza una distribucion de probabilidad para que sume 1.
    
    Parametros:
        distribucion: Diccionario con valores no normalizados
        
    Retorna:
        Dict[str, float]: Distribucion normalizada
        
    Lanza:
        ValueError: Si la distribucion no es normalizable
    """
    suma_total = sum(distribucion.values())
    
    if suma_total <= 0:
        raise ValueError("Distribucion no normalizable: suma total <= 0")
        
    return {clave: valor / suma_total for clave, valor in distribucion.items()}


# ============================================================
# DEFINICION DE LA RED DE DECISION TRON
# ============================================================

# Probabilidad prior de Interferencia en el sistema
# Representa la probabilidad de que haya niveles altos de interferencia
PROBABILIDAD_INTERFERENCIA = {
    "Baja": 0.6,   # 60% probabilidad de interferencia baja
    "Alta": 0.4,   # 40% probabilidad de interferencia alta
}

# Probabilidad de estado del Firewall (independiente de la interferencia)
# Representa si los firewalls del sistema estan activos o no
PROBABILIDAD_FIREWALL = {
    "Off": 0.7,    # 70% probabilidad de firewall desactivado
    "On": 0.3,     # 30% probabilidad de firewall activado
}

# Probabilidad condicional del Sensor dado el estado de Interferencia
# Modela la precision del sensor para detectar interferencias
PROBABILIDAD_SENSOR_DADO_INTERFERENCIA = {
    # Si la interferencia es Baja:
    ("OK", "Baja"): 0.85,      # 85% de detectar correctamente estado OK
    ("Alerta", "Baja"): 0.15,  # 15% de falso positivo (alerta erronea)
    
    # Si la interferencia es Alta:
    ("OK", "Alta"): 0.25,      # 25% de falso negativo (no detecta interferencia)
    ("Alerta", "Alta"): 0.75,  # 75% de detectar correctamente alerta
}

# Rutas disponibles para la decision
RUTAS_DISPONIBLES = ["Sector_Luz", "Portal", "Arena"]

# Diccionario global para almacenar las utilidades
UTILIDADES: Dict[Tuple[str, str, str], float] = {}


def definir_utilidad(interferencia: str, firewall: str, ruta: str, valor: float):
    """
    Define el valor de utilidad para una combinacion especifica de estados.
    
    Parametros:
        interferencia: Estado de interferencia ("Baja" o "Alta")
        firewall: Estado del firewall ("Off" o "On")  
        ruta: Ruta seleccionada
        valor: Valor de utilidad (energia neta esperada)
    """
    UTILIDADES[(interferencia, firewall, ruta)] = valor


# Definicion de utilidades basadas en caracteristicas del mundo TRON:
# - Sector_Luz: Excelente rendimiento con interferencia baja, muy sensible a interferencia alta
# - Portal: Balanceado, mas resistente a firewalls pero variable con interferencia
# - Arena: Alternativa moderada, afectada por ambos factores

VALORES_UTILIDAD = {
    # Sector_Luz - Ruta de alto rendimiento pero sensible
    ("Baja", "Off", "Sector_Luz"): 120,  # Condiciones optimas
    ("Baja", "On",  "Sector_Luz"): 85,   # Firewall reduce eficiencia
    ("Alta", "Off", "Sector_Luz"): 60,   # Interferencia alta afecta mucho
    ("Alta", "On",  "Sector_Luz"): 30,   # Condiciones criticas

    # Portal - Ruta balanceada y resistente
    ("Baja", "Off", "Portal"):     100,  # Buen rendimiento
    ("Baja", "On",  "Portal"):     95,   # Poca afectacion por firewall
    ("Alta", "Off", "Portal"):     80,   # Moderada afectacion por interferencia
    ("Alta", "On",  "Portal"):     55,   # Condiciones adversas

    # Arena - Ruta alternativa moderada
    ("Baja", "Off", "Arena"):       90,  # Rendimiento aceptable
    ("Baja", "On",  "Arena"):       70,  # Afectado por firewall
    ("Alta", "Off", "Arena"):       50,  # Afectado por interferencia
    ("Alta", "On",  "Arena"):       20,  # Condiciones muy adversas
}

# Cargar todas las utilidades definidas
for clave, valor in VALORES_UTILIDAD.items():
    definir_utilidad(*clave, valor)


# ============================================================
# INFERENCIA Y CALCULOS DE UTILIDAD ESPERADA
# ============================================================

def probabilidad_interferencia_dado_sensor(lectura_sensor: str) -> Dict[str, float]:
    """
    Calcula la probabilidad posterior de Interferencia dado una lectura del sensor.
    
    Usa el teorema de Bayes: P(Interferencia | Sensor) ∝ P(Sensor | Interferencia) * P(Interferencia)
    
    Parametros:
        lectura_sensor: Lectura del sensor ("OK" o "Alerta")
        
    Retorna:
        Dict[str, float]: Distribucion posterior normalizada de Interferencia
    """
    numeradores = {}
    
    # Calcular numeradores para cada estado de interferencia
    for estado_interferencia, probabilidad_prior in PROBABILIDAD_INTERFERENCIA.items():
        probabilidad_condicional = PROBABILIDAD_SENSOR_DADO_INTERFERENCIA[(lectura_sensor, estado_interferencia)]
        numeradores[estado_interferencia] = probabilidad_condicional * probabilidad_prior
    
    return normalizar_distribucion(numeradores)


def utilidad_esperada_accion_dado_evidencia(ruta: str, lectura_sensor: str) -> float:
    """
    Calcula la utilidad esperada de una accion dado un valor observado del sensor.
    
    EU[ruta | Sensor] = Σ_i Σ_f U(interferencia, firewall, ruta) * P(firewall) * P(interferencia | sensor)
    
    Parametros:
        ruta: Ruta a evaluar
        lectura_sensor: Lectura observada del sensor
        
    Retorna:
        float: Utilidad esperada condicionada a la evidencia
    """
    # Obtener distribucion posterior de interferencia dado el sensor
    probabilidad_interferencia_posterior = probabilidad_interferencia_dado_sensor(lectura_sensor)
    
    utilidad_esperada = 0.0
    
    # Calcular suma sobre todos los estados posibles
    for estado_interferencia, prob_interferencia in probabilidad_interferencia_posterior.items():
        for estado_firewall, prob_firewall in PROBABILIDAD_FIREWALL.items():
            utilidad = UTILIDADES[(estado_interferencia, estado_firewall, ruta)]
            utilidad_esperada += utilidad * prob_firewall * prob_interferencia
            
    return utilidad_esperada


def mejor_accion_dado_sensor(lectura_sensor: str) -> Tuple[str, float, Dict[str, float]]:
    """
    Encuentra la mejor accion y su utilidad esperada dado un valor del sensor.
    
    Parametros:
        lectura_sensor: Lectura observada del sensor
        
    Retorna:
        Tuple: (mejor_ruta, mejor_utilidad, utilidades_por_accion)
    """
    utilidades_por_accion = {}
    mejor_ruta = None
    mejor_utilidad = float("-inf")
    
    for ruta in RUTAS_DISPONIBLES:
        utilidad_esperada = utilidad_esperada_accion_dado_evidencia(ruta, lectura_sensor)
        utilidades_por_accion[ruta] = utilidad_esperada
        
        if utilidad_esperada > mejor_utilidad:
            mejor_ruta = ruta
            mejor_utilidad = utilidad_esperada
            
    return mejor_ruta, mejor_utilidad, utilidades_por_accion


def utilidad_esperada_accion_prior(ruta: str) -> float:
    """
    Calcula la utilidad esperada de una accion sin observar el sensor.
    
    EU[ruta] = Σ_i Σ_f U(interferencia, firewall, ruta) * P(interferencia) * P(firewall)
    
    Parametros:
        ruta: Ruta a evaluar
        
    Retorna:
        float: Utilidad esperada sin informacion del sensor
    """
    utilidad_esperada = 0.0
    
    for estado_interferencia, prob_interferencia in PROBABILIDAD_INTERFERENCIA.items():
        for estado_firewall, prob_firewall in PROBABILIDAD_FIREWALL.items():
            utilidad = UTILIDADES[(estado_interferencia, estado_firewall, ruta)]
            utilidad_esperada += utilidad * prob_firewall * prob_interferencia
            
    return utilidad_esperada


def mejor_accion_sin_sensor() -> Tuple[str, float, Dict[str, float]]:
    """
    Encuentra la mejor accion sin informacion del sensor.
    
    Retorna:
        Tuple: (mejor_ruta, mejor_utilidad, utilidades_por_accion)
    """
    utilidades_por_accion = {}
    mejor_ruta = None
    mejor_utilidad = float("-inf")
    
    for ruta in RUTAS_DISPONIBLES:
        utilidad_esperada = utilidad_esperada_accion_prior(ruta)
        utilidades_por_accion[ruta] = utilidad_esperada
        
        if utilidad_esperada > mejor_utilidad:
            mejor_ruta = ruta
            mejor_utilidad = utilidad_esperada
            
    return mejor_ruta, mejor_utilidad, utilidades_por_accion


def probabilidad_sensor(lectura_sensor: str) -> float:
    """
    Calcula la probabilidad marginal de una lectura del sensor.
    
    P(Sensor) = Σ_i P(Sensor | Interferencia=i) * P(Interferencia=i)
    
    Parametros:
        lectura_sensor: Lectura del sensor a evaluar
        
    Retorna:
        float: Probabilidad de la lectura del sensor
    """
    probabilidad_total = 0.0
    
    for estado_interferencia, prob_interferencia in PROBABILIDAD_INTERFERENCIA.items():
        probabilidad_condicional = PROBABILIDAD_SENSOR_DADO_INTERFERENCIA[(lectura_sensor, estado_interferencia)]
        probabilidad_total += probabilidad_condicional * prob_interferencia
        
    return probabilidad_total


def utilidad_esperada_con_politica() -> Tuple[Dict[str, str], float]:
    """
    Calcula la politica optima y la utilidad esperada maxima (MEU) con observacion del sensor.
    
    MEU = Σ_e P(Sensor=e) * max_a EU[a | Sensor=e]
    
    Retorna:
        Tuple: (politica_optima, meu_con_sensor)
    """
    politica_optima = {}
    meu_total = 0.0
    
    for lectura_sensor in ["OK", "Alerta"]:
        mejor_ruta, utilidad_mejor_ruta, _ = mejor_accion_dado_sensor(lectura_sensor)
        politica_optima[lectura_sensor] = mejor_ruta
        
        probabilidad_lectura = probabilidad_sensor(lectura_sensor)
        meu_total += probabilidad_lectura * utilidad_mejor_ruta
        
    return politica_optima, meu_total


def valor_informacion_perfecta() -> float:
    """
    Calcula el Valor de la Informacion Perfecta (VPI) del sensor.
    
    VPI = MEU(con sensor) - MEU(sin sensor)
    
    Retorna:
        float: Valor de la informacion proporcionada por el sensor
    """
    politica, meu_con_sensor = utilidad_esperada_con_politica()
    _, meu_sin_sensor, _ = mejor_accion_sin_sensor()
    
    return meu_con_sensor - meu_sin_sensor


# ============================================================
# DEMOSTRACION PRINCIPAL
# ============================================================

def demostrar_red_decision():
    """
    Funcion principal que demuestra el funcionamiento de la red de decision.
    """
    print("SISTEMA DE REDES DE DECISION - ESTRATEGIAS OPTIMAS EN TRON")
    print("=" * 70)
    print("Analisis de politicas condicionadas a observaciones del sensor")
    print("=" * 70)
    
    # Analisis sin informacion del sensor
    print("\n1. ANALISIS SIN OBSERVAR EL SENSOR (Politica Fija)")
    print("-" * 50)
    
    mejor_ruta_sin_sensor, utilidad_mejor_sin_sensor, utilidades_sin_sensor = mejor_accion_sin_sensor()
    
    for ruta in RUTAS_DISPONIBLES:
        print(f"   EU[{ruta:12}] = {utilidades_sin_sensor[ruta]:6.2f}")
    
    print(f"\n   MEJOR RUTA A PRIORI: {mejor_ruta_sin_sensor}")
    print(f"   UTILIDAD ESPERADA:   {utilidad_mejor_sin_sensor:.2f}")
    
    # Analisis con informacion del sensor
    print("\n2. ANALISIS CON OBSERVACION DEL SENSOR")
    print("-" * 50)
    
    for lectura_sensor in ["OK", "Alerta"]:
        mejor_ruta_con_sensor, utilidad_mejor_con_sensor, utilidades_con_sensor = mejor_accion_dado_sensor(lectura_sensor)
        posterior = probabilidad_interferencia_dado_sensor(lectura_sensor)
        
        print(f"\n   OBSERVACION: Sensor = {lectura_sensor}")
        print(f"   Probabilidad Posterior Interferencia:")
        print(f"     Baja: {posterior['Baja']:.3f}, Alta: {posterior['Alta']:.3f}")
        
        for ruta in RUTAS_DISPONIBLES:
            print(f"     EU[{ruta:12} | {lectura_sensor}] = {utilidades_con_sensor[ruta]:6.2f}")
        
        print(f"   MEJOR ACCION: {mejor_ruta_con_sensor}")
        print(f"   UTILIDAD ESPERADA: {utilidad_mejor_con_sensor:.2f}")
    
    # Politica optima y VPI
    print("\n3. POLITICA OPTIMA Y VALOR DE LA INFORMACION")
    print("-" * 50)
    
    politica_optima, meu_con_sensor = utilidad_esperada_con_politica()
    vpi = valor_informacion_perfecta()
    
    print("\n   POLITICA OPTIMA π* (Sensor → Ruta):")
    for lectura_sensor, ruta_optima in politica_optima.items():
        print(f"     Si Sensor = {lectura_sensor:6} → Elegir {ruta_optima}")
    
    print(f"\n   METRICAS COMPARATIVAS:")
    print(f"     MEU con observacion del sensor: {meu_con_sensor:8.2f}")
    print(f"     MEU sin observacion:           {utilidad_mejor_sin_sensor:8.2f}")
    print(f"     Valor de la Informacion (VPI): {vpi:8.2f}")
    
    # Interpretacion del VPI
    print(f"\n   INTERPRETACION DEL VPI:")
    if vpi > 10:
        print(f"     ALTO VALOR - El sensor proporciona informacion muy valiosa")
    elif vpi > 5:
        print(f"     VALOR MODERADO - El sensor es util pero no critico")
    else:
        print(f"     BAJO VALOR - El sensor aporta poca informacion adicional")
    
    print("\n" + "=" * 70)
    print("ANALISIS COMPLETADO - SISTEMA TRON OPTIMIZADO")
    print("=" * 70)


if __name__ == "__main__":
    demostrar_red_decision()