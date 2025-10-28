"""
SISTEMA DE VALORACION DE INFORMACION PARA DECISIONES - TRON DIGITAL

Este modulo implementa metricas avanzadas para cuantificar el valor de la
informacion en la toma de decisiones bajo incertidumbre. Calcula EVPI (Valor
Esperado de la Informacion Perfecta) y EVSI (Valor Esperado de la Informacion
de Muestra) para determinar cuando vale la pena recolectar informacion antes
de tomar decisiones estrategicas.
"""

from typing import Dict, Tuple, List


# ============================================================
# MODELO PROBABILISTICO Y DE UTILIDADES PARA TRON
# ============================================================

# Probabilidad prior de Interferencia en el sistema
PROBABILIDAD_INTERFERENCIA = {
    "Baja": 0.6,   # 60% probabilidad de interferencia baja
    "Alta": 0.4,   # 40% probabilidad de interferencia alta
}

# Probabilidad de estado del Firewall (independiente)
PROBABILIDAD_FIREWALL = {
    "Off": 0.7,    # 70% probabilidad de firewall desactivado
    "On": 0.3,     # 30% probabilidad de firewall activado
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


# Definicion de utilidades basadas en caracteristicas del mundo TRON
VALORES_UTILIDAD = {
    # Sector_Luz - Alto rendimiento pero sensible a interferencias
    ("Baja", "Off", "Sector_Luz"): 120,
    ("Baja", "On",  "Sector_Luz"): 85,
    ("Alta", "Off", "Sector_Luz"): 60,
    ("Alta", "On",  "Sector_Luz"): 30,

    # Portal - Balanceado y resistente
    ("Baja", "Off", "Portal"):     100,
    ("Baja", "On",  "Portal"):      95,
    ("Alta", "Off", "Portal"):      80,
    ("Alta", "On",  "Portal"):      55,

    # Arena - Alternativa moderada
    ("Baja", "Off", "Arena"):       90,
    ("Baja", "On",  "Arena"):       70,
    ("Alta", "Off", "Arena"):       50,
    ("Alta", "On",  "Arena"):       20,
}

# Cargar todas las utilidades definidas
for clave, valor in VALORES_UTILIDAD.items():
    definir_utilidad(*clave, valor)


# ============================================================
# FUNCIONES BASE DE UTILIDAD ESPERADA
# ============================================================

def utilidad_esperada_ruta_sin_informacion(ruta: str) -> float:
    """
    Calcula la utilidad esperada de una ruta sin observar ninguna informacion.
    
    EU[ruta] = Σ_i Σ_f U(interferencia, firewall, ruta) * P(interferencia) * P(firewall)
    
    Parametros:
        ruta: Ruta a evaluar
        
    Retorna:
        float: Utilidad esperada sin informacion
    """
    utilidad_esperada = 0.0
    
    for estado_interferencia, prob_interferencia in PROBABILIDAD_INTERFERENCIA.items():
        for estado_firewall, prob_firewall in PROBABILIDAD_FIREWALL.items():
            utilidad = UTILIDADES[(estado_interferencia, estado_firewall, ruta)]
            utilidad_esperada += utilidad * prob_interferencia * prob_firewall
            
    return utilidad_esperada


def mejor_ruta_sin_informacion() -> Tuple[str, float, Dict[str, float]]:
    """
    Encuentra la mejor ruta sin informacion adicional.
    
    Retorna:
        Tuple: (mejor_ruta, mejor_utilidad, utilidades_por_ruta)
    """
    utilidades_por_ruta = {}
    mejor_ruta = None
    mejor_utilidad = float("-inf")
    
    for ruta in RUTAS_DISPONIBLES:
        utilidad_esperada = utilidad_esperada_ruta_sin_informacion(ruta)
        utilidades_por_ruta[ruta] = utilidad_esperada
        
        if utilidad_esperada > mejor_utilidad:
            mejor_ruta = ruta
            mejor_utilidad = utilidad_esperada
            
    return mejor_ruta, mejor_utilidad, utilidades_por_ruta


def probabilidad_posterior_interferencia_dado_sensor(
    lectura_sensor: str,
    probabilidad_ok_dado_baja: float,
    probabilidad_ok_dado_alta: float
) -> Dict[str, float]:
    """
    Calcula la probabilidad posterior de Interferencia dado una lectura del sensor.
    
    Usa el teorema de Bayes: P(Interferencia | Sensor) ∝ P(Sensor | Interferencia) * P(Interferencia)
    
    Parametros:
        lectura_sensor: Lectura del sensor ("OK" o "Alerta")
        probabilidad_ok_dado_baja: P(Sensor="OK" | Interferencia="Baja")
        probabilidad_ok_dado_alta: P(Sensor="OK" | Interferencia="Alta")
        
    Retorna:
        Dict[str, float]: Distribucion posterior normalizada
    """
    if lectura_sensor == "OK":
        numerador_baja = probabilidad_ok_dado_baja * PROBABILIDAD_INTERFERENCIA["Baja"]
        numerador_alta = probabilidad_ok_dado_alta * PROBABILIDAD_INTERFERENCIA["Alta"]
    else:  # Sensor = "Alerta"
        numerador_baja = (1 - probabilidad_ok_dado_baja) * PROBABILIDAD_INTERFERENCIA["Baja"]
        numerador_alta = (1 - probabilidad_ok_dado_alta) * PROBABILIDAD_INTERFERENCIA["Alta"]
    
    suma_total = numerador_baja + numerador_alta
    
    return {
        "Baja": numerador_baja / suma_total,
        "Alta": numerador_alta / suma_total
    }


def probabilidad_marginal_sensor(
    lectura_sensor: str,
    probabilidad_ok_dado_baja: float,
    probabilidad_ok_dado_alta: float
) -> float:
    """
    Calcula la probabilidad marginal de una lectura del sensor.
    
    P(Sensor) = Σ_i P(Sensor | Interferencia=i) * P(Interferencia=i)
    
    Parametros:
        lectura_sensor: Lectura del sensor a evaluar
        probabilidad_ok_dado_baja: P(Sensor="OK" | Interferencia="Baja")
        probabilidad_ok_dado_alta: P(Sensor="OK" | Interferencia="Alta")
        
    Retorna:
        float: Probabilidad de la lectura del sensor
    """
    if lectura_sensor == "OK":
        return (probabilidad_ok_dado_baja * PROBABILIDAD_INTERFERENCIA["Baja"] + 
                probabilidad_ok_dado_alta * PROBABILIDAD_INTERFERENCIA["Alta"])
    else:
        return ((1 - probabilidad_ok_dado_baja) * PROBABILIDAD_INTERFERENCIA["Baja"] + 
                (1 - probabilidad_ok_dado_alta) * PROBABILIDAD_INTERFERENCIA["Alta"])


def utilidad_esperada_ruta_condicionada_sensor(
    ruta: str,
    lectura_sensor: str,
    probabilidad_ok_dado_baja: float,
    probabilidad_ok_dado_alta: float
) -> float:
    """
    Calcula la utilidad esperada de una ruta dado un valor observado del sensor.
    
    EU[ruta | Sensor] = Σ_i Σ_f U(interferencia, firewall, ruta) * P(firewall) * P(interferencia | sensor)
    
    Parametros:
        ruta: Ruta a evaluar
        lectura_sensor: Lectura observada del sensor
        probabilidad_ok_dado_baja: P(Sensor="OK" | Interferencia="Baja")
        probabilidad_ok_dado_alta: P(Sensor="OK" | Interferencia="Alta")
        
    Retorna:
        float: Utilidad esperada condicionada a la evidencia
    """
    posterior = probabilidad_posterior_interferencia_dado_sensor(
        lectura_sensor, probabilidad_ok_dado_baja, probabilidad_ok_dado_alta
    )
    
    utilidad_esperada = 0.0
    
    for estado_interferencia, prob_interferencia in posterior.items():
        for estado_firewall, prob_firewall in PROBABILIDAD_FIREWALL.items():
            utilidad = UTILIDADES[(estado_interferencia, estado_firewall, ruta)]
            utilidad_esperada += utilidad * prob_firewall * prob_interferencia
            
    return utilidad_esperada


def mejor_ruta_condicionada_sensor(
    lectura_sensor: str,
    probabilidad_ok_dado_baja: float,
    probabilidad_ok_dado_alta: float
) -> Tuple[str, float, Dict[str, float]]:
    """
    Encuentra la mejor ruta y su utilidad esperada dado un valor del sensor.
    
    Parametros:
        lectura_sensor: Lectura observada del sensor
        probabilidad_ok_dado_baja: P(Sensor="OK" | Interferencia="Baja")
        probabilidad_ok_dado_alta: P(Sensor="OK" | Interferencia="Alta")
        
    Retorna:
        Tuple: (mejor_ruta, mejor_utilidad, utilidades_por_ruta)
    """
    utilidades_por_ruta = {}
    mejor_ruta = None
    mejor_utilidad = float("-inf")
    
    for ruta in RUTAS_DISPONIBLES:
        utilidad_esperada = utilidad_esperada_ruta_condicionada_sensor(
            ruta, lectura_sensor, probabilidad_ok_dado_baja, probabilidad_ok_dado_alta
        )
        utilidades_por_ruta[ruta] = utilidad_esperada
        
        if utilidad_esperada > mejor_utilidad:
            mejor_ruta = ruta
            mejor_utilidad = utilidad_esperada
            
    return mejor_ruta, mejor_utilidad, utilidades_por_ruta


# ============================================================
# METRICAS AVANZADAS DE VALOR DE INFORMACION
# ============================================================

def meu_con_sensor_imperfecto(
    probabilidad_ok_dado_baja: float,
    probabilidad_ok_dado_alta: float,
    costo_observacion: float = 0.0
) -> Tuple[float, Dict[str, str]]:
    """
    Calcula la Maxima Utilidad Esperada (MEU) al observar un sensor imperfecto.
    
    MEU = Σ_e P(Sensor=e) * max_a EU[a | Sensor=e] - costo_observacion
    
    Parametros:
        probabilidad_ok_dado_baja: Fiabilidad del sensor cuando interferencia es baja
        probabilidad_ok_dado_alta: Fiabilidad del sensor cuando interferencia es alta
        costo_observacion: Costo de activar y leer el sensor
        
    Retorna:
        Tuple: (meu_con_sensor, politica_optima)
    """
    meu_total = 0.0
    politica_optima: Dict[str, str] = {}
    
    for lectura_sensor in ["OK", "Alerta"]:
        # Probabilidad de esta lectura del sensor
        probabilidad_lectura = probabilidad_marginal_sensor(
            lectura_sensor, probabilidad_ok_dado_baja, probabilidad_ok_dado_alta
        )
        
        # Mejor accion para esta lectura
        mejor_ruta, utilidad_mejor_ruta, _ = mejor_ruta_condicionada_sensor(
            lectura_sensor, probabilidad_ok_dado_baja, probabilidad_ok_dado_alta
        )
        
        politica_optima[lectura_sensor] = mejor_ruta
        meu_total += probabilidad_lectura * utilidad_mejor_ruta
    
    # Restar costo de observacion
    meu_total -= costo_observacion
    
    return meu_total, politica_optima


def valor_esperado_informacion_perfecta_interferencia() -> float:
    """
    Calcula el EVPI (Expected Value of Perfect Information) sobre la Interferencia.
    
    EVPI = MEU(con informacion perfecta) - MEU(sin informacion)
    
    Representa el valor maximo que estariamos dispuestos a pagar por conocer
    exactamente el estado de la interferencia antes de decidir.
    
    Retorna:
        float: Valor del EVPI
    """
    meu_con_informacion_perfecta = 0.0
    
    # Para cada estado posible de interferencia
    for estado_interferencia, probabilidad_interferencia in PROBABILIDAD_INTERFERENCIA.items():
        # Encontrar la mejor utilidad posible conociendo exactamente la interferencia
        mejor_utilidad_estado = float("-inf")
        
        for ruta in RUTAS_DISPONIBLES:
            utilidad_esperada_ruta = 0.0
            # Solo sumamos sobre firewalls (ya conocemos interferencia)
            for estado_firewall, probabilidad_firewall in PROBABILIDAD_FIREWALL.items():
                utilidad = UTILIDADES[(estado_interferencia, estado_firewall, ruta)]
                utilidad_esperada_ruta += utilidad * probabilidad_firewall
            
            if utilidad_esperada_ruta > mejor_utilidad_estado:
                mejor_utilidad_estado = utilidad_esperada_ruta
        
        meu_con_informacion_perfecta += probabilidad_interferencia * mejor_utilidad_estado
    
    # MEU sin informacion
    _, meu_sin_informacion, _ = mejor_ruta_sin_informacion()
    
    return meu_con_informacion_perfecta - meu_sin_informacion


def valor_esperado_informacion_muestra_sensor(
    probabilidad_ok_dado_baja: float,
    probabilidad_ok_dado_alta: float,
    costo_observacion: float = 0.0
) -> Tuple[float, float, Dict[str, str]]:
    """
    Calcula el EVSI (Expected Value of Sample Information) del sensor.
    
    EVSI = MEU(con sensor) - MEU(sin sensor)
    
    Parametros:
        probabilidad_ok_dado_baja: Fiabilidad del sensor con interferencia baja
        probabilidad_ok_dado_alta: Fiabilidad del sensor con interferencia alta
        costo_observacion: Costo de usar el sensor
        
    Retorna:
        Tuple: (evsi, meu_con_sensor, politica_optima)
    """
    meu_con_sensor, politica_optima = meu_con_sensor_imperfecto(
        probabilidad_ok_dado_baja, probabilidad_ok_dado_alta, costo_observacion
    )
    
    _, meu_sin_sensor, _ = mejor_ruta_sin_informacion()
    
    evsi = meu_con_sensor - meu_sin_sensor
    return evsi, meu_con_sensor, politica_optima


def costo_maximo_racional_observacion(
    probabilidad_ok_dado_baja: float,
    probabilidad_ok_dado_alta: float
) -> float:
    """
    Calcula el umbral de costo maximo racional para observar el sensor.
    
    Es el costo que hace indiferente entre observar o no observar.
    costo* = MEU(con sensor sin costo) - MEU(sin informacion)
    
    Parametros:
        probabilidad_ok_dado_baja: Fiabilidad del sensor con interferencia baja
        probabilidad_ok_dado_alta: Fiabilidad del sensor con interferencia alta
        
    Retorna:
        float: Umbral de costo maximo racional
    """
    meu_sin_costo, _ = meu_con_sensor_imperfecto(
        probabilidad_ok_dado_baja, probabilidad_ok_dado_alta, costo_observacion=0.0
    )
    
    _, meu_sin_informacion, _ = mejor_ruta_sin_informacion()
    
    return max(0.0, meu_sin_costo - meu_sin_informacion)


# ============================================================
# DEMOSTRACION PRINCIPAL
# ============================================================

def demostrar_valor_informacion():
    """
    Funcion principal que demuestra el analisis de valor de la informacion.
    """
    print("SISTEMA DE VALORACION DE INFORMACION - ESTRATEGIAS TRON")
    print("=" * 70)
    print("Analisis de cuando vale la pena recolectar informacion antes de decidir")
    print("=" * 70)
    
    # 1. MEU sin informacion
    print("\n1. ANALISIS SIN INFORMACION ADICIONAL")
    print("-" * 50)
    
    mejor_ruta, meu_sin_info, utilidades = mejor_ruta_sin_informacion()
    
    print("Utilidades Esperadas sin informacion:")
    for ruta in RUTAS_DISPONIBLES:
        print(f"   EU[{ruta:12}] = {utilidades[ruta]:7.2f}")
    
    print(f"\n   MEJOR RUTA: {mejor_ruta}")
    print(f"   MEU (Maxima Utilidad Esperada): {meu_sin_info:.2f}")
    
    # 2. EVPI - Valor de la informacion perfecta
    print("\n2. VALOR DE LA INFORMACION PERFECTA (EVPI)")
    print("-" * 50)
    
    evpi = valor_esperado_informacion_perfecta_interferencia()
    print(f"   EVPI sobre Interferencia: {evpi:.2f}")
    print(f"\n   INTERPRETACION:")
    print(f"   - Es la mejora maxima esperable si conocieramos exactamente")
    print(f"     el estado de la interferencia antes de decidir")
    print(f"   - Representa el maximo que deberiamos pagar por informacion perfecta")
    print(f"   - Si el costo de obtener informacion > {evpi:.2f}, no vale la pena")
    
    # 3. EVSI - Valor de la informacion imperfecta del sensor
    print("\n3. VALOR DE LA INFORMACION IMPERFECTA (EVSI)")
    print("-" * 50)
    
    # Parametros del sensor (fiabilidad)
    probabilidad_ok_baja = 0.70  # P(Sensor="OK" | Interferencia="Baja")
    probabilidad_ok_alta = 0.20  # P(Sensor="OK" | Interferencia="Alta") 
    costo_sensor = 5.0           # Costo de activar el sensor
    
    evsi, meu_con_sensor, politica = valor_esperado_informacion_muestra_sensor(
        probabilidad_ok_baja, probabilidad_ok_alta, costo_sensor
    )
    
    print(f"   Sensor con fiabilidad:")
    print(f"     P(OK|Baja) = {probabilidad_ok_baja:.2f}")
    print(f"     P(OK|Alta) = {probabilidad_ok_alta:.2f}")
    print(f"   Costo de observacion: {costo_sensor:.2f}")
    print(f"\n   RESULTADOS:")
    print(f"   - MEU con sensor: {meu_con_sensor:.2f}")
    print(f"   - EVSI: {evsi:.2f}")
    
    print(f"\n   POLITICA OPTIMA CON SENSOR:")
    for lectura, ruta_optima in politica.items():
        print(f"     Si Sensor = {lectura:6} → Elegir {ruta_optima}")
    
    # 4. Umbral de costo racional
    print("\n4. UMBRAL DE COSTO RACIONAL")
    print("-" * 50)
    
    costo_umbral = costo_maximo_racional_observacion(probabilidad_ok_baja, probabilidad_ok_alta)
    
    print(f"   Umbral de costo maximo racional: {costo_umbral:.2f}")
    print(f"\n   INTERPRETACION:")
    print(f"   - Si costo real < {costo_umbral:.2f}: CONVIENE observar")
    print(f"   - Si costo real > {costo_umbral:.2f}: NO CONVIENE observar")
    print(f"   - Costo actual ({costo_sensor:.2f}) vs Umbral ({costo_umbral:.2f}): ", 
          "CONVIENE" if costo_sensor < costo_umbral else "NO CONVIENE")
    
    # 5. Analisis de sensibilidad
    print("\n5. ANALISIS DE SENSIBILIDAD - CALIDAD DEL SENSOR")
    print("-" * 50)
    print("   EVSI para diferentes niveles de fiabilidad (sin costo):")
    print("\n   P(OK|Baja)  P(OK|Alta)   EVSI")
    print("   " + "-" * 30)
    
    # Variar la calidad del sensor
    for prob_baja in [0.60, 0.70, 0.80, 0.85, 0.90]:
        for prob_alta in [0.50, 0.40, 0.30, 0.25, 0.20]:
            evsi_sin_costo, _, _ = valor_esperado_informacion_muestra_sensor(
                prob_baja, prob_alta, costo_observacion=0.0
            )
            print(f"     {prob_baja:6.2f}      {prob_alta:6.2f}     {evsi_sin_costo:6.2f}")
    
    print("\n" + "=" * 70)
    print("ANALISIS COMPLETADO - SISTEMA DE DECISION OPTIMIZADO")
    print("=" * 70)


if __name__ == "__main__":
    demostrar_valor_informacion()