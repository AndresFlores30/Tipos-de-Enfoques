"""
SISTEMA DE TEORIA DE LA UTILIDAD PARA TOMA DE DECISIONES - TRON DIGITAL

Este modulo implementa modelos de teoria de la utilidad para evaluar rutas
en el Grid de TRON bajo condiciones de incertidumbre. Utiliza funciones de
utilidad para modelar la aversion al riesgo y calcular metricas clave que
permiten comparar estrategias de manera cuantitativa.
"""

import math


# =========================
# FUNCIONES DE UTILIDAD
# =========================

def utilidad_crra(energia: float, coeficiente_aversion: float) -> float:
    """
    Calcula la utilidad usando funcion CRRA (Constant Relative Risk Aversion).
    
    CRRA modela aversion relativa al riesgo constante. Es la funcion mas usada
    en economia para modelar preferencias bajo incertidumbre.
    
    Parametros:
        energia: Cantidad de energia (debe ser > 0)
        coeficiente_aversion: Coeficiente de aversion al riesgo (r >= 0)
            r = 0: neutral al riesgo
            r = 1: utilidad logaritmica
            r > 1: aversion al riesgo alta
            
    Retorna:
        float: Valor de utilidad
    """
    if energia <= 0:
        return float("-inf")  # Energia negativa o cero es catastrofica
    
    if coeficiente_aversion == 1.0:
        # Caso especial: utilidad logaritmica
        return math.log(energia)
    else:
        # Forma general de CRRA
        return energia**(1.0 - coeficiente_aversion) / (1.0 - coeficiente_aversion)


def inversa_utilidad_crra(utilidad: float, coeficiente_aversion: float) -> float:
    """
    Calcula la inversa de la funcion de utilidad CRRA.
    
    Convierte un valor de utilidad de vuelta a su equivalente en energia.
    
    Parametros:
        utilidad: Valor de utilidad a convertir
        coeficiente_aversion: Coeficiente de aversion al riesgo
        
    Retorna:
        float: Equivalente en energia
    """
    if coeficiente_aversion == 1.0:
        # Inversa del logaritmo
        return math.exp(utilidad)
    else:
        base = (1.0 - coeficiente_aversion) * utilidad
        return 0.0 if base <= 0 else base**(1.0/(1.0 - coeficiente_aversion))


def utilidad_cara(energia: float, coeficiente_aversion: float) -> float:
    """
    Calcula la utilidad usando funcion CARA (Constant Absolute Risk Aversion).
    
    CARA modela aversion absoluta al riesgo constante. Es util cuando la
    aversion al riesgo no depende del nivel de riqueza inicial.
    
    Parametros:
        energia: Cantidad de energia (puede ser cualquier valor real)
        coeficiente_aversion: Coeficiente de aversion al riesgo (a > 0)
        
    Retorna:
        float: Valor de utilidad (siempre negativo)
    """
    return -math.exp(-coeficiente_aversion * energia)


def inversa_utilidad_cara(utilidad: float, coeficiente_aversion: float) -> float:
    """
    Calcula la inversa de la funcion de utilidad CARA.
    
    Parametros:
        utilidad: Valor de utilidad a convertir (debe ser < 0)
        coeficiente_aversion: Coeficiente de aversion al riesgo
        
    Retorna:
        float: Equivalente en energia
        
    Lanza:
        ValueError: Si la utilidad no es negativa
    """
    if utilidad >= 0:
        raise ValueError("Para CARA, la utilidad debe ser negativa (u(x) < 0).")
    return -math.log(-utilidad) / coeficiente_aversion


# =========================
# METRICAS DE EVALUACION
# =========================

def utilidad_esperada(loteria: list, funcion_utilidad: callable) -> float:
    """
    Calcula la utilidad esperada de una loteria.
    
    La utilidad esperada es la suma ponderada de las utilidades de cada
    resultado posible, donde los pesos son las probabilidades.
    
    Parametros:
        loteria: Lista de tuplas (probabilidad, energia)
        funcion_utilidad: Funcion que calcula utilidad para un nivel de energia
        
    Retorna:
        float: Utilidad esperada
    """
    return sum(probabilidad * funcion_utilidad(energia) for probabilidad, energia in loteria)


def equivalente_cierto(loteria: list, funcion_utilidad: callable, inversa_utilidad: callable) -> float:
    """
    Calcula el equivalente cierto de una loteria.
    
    El equivalente cierto es la cantidad segura de energia que proporciona
    la misma utilidad que la loteria riesgosa.
    
    Parametros:
        loteria: Lista de tuplas (probabilidad, energia)
        funcion_utilidad: Funcion que calcula utilidad
        inversa_utilidad: Funcion inversa de la utilidad
        
    Retorna:
        float: Equivalente cierto en unidades de energia
    """
    utilidad_esp = utilidad_esperada(loteria, funcion_utilidad)
    return inversa_utilidad(utilidad_esp)


def prima_riesgo(loteria: list, equivalente_cierto_valor: float) -> float:
    """
    Calcula la prima de riesgo de una loteria.
    
    La prima de riesgo es la diferencia entre el valor esperado y el equivalente
    cierto. Representa cuanto esta dispuesto a pagar el agente para evitar el riesgo.
    
    Parametros:
        loteria: Lista de tuplas (probabilidad, energia)
        equivalente_cierto_valor: Equivalente cierto calculado
        
    Retorna:
        float: Prima de riesgo
    """
    valor_esperado = sum(probabilidad * energia for probabilidad, energia in loteria)
    return valor_esperado - equivalente_cierto_valor


# =========================
# ESCENARIO TRON - DEFINICION DE RUTAS
# =========================

def definir_rutas_tron():
    """
    Define las rutas disponibles en el Grid de TRON como loterias.
    
    Cada ruta es representada como una lista de resultados posibles
    con sus respectivas probabilidades y niveles de energia.
    
    Retorna:
        dict: Diccionario con las rutas y sus caracteristicas
    """
    # Ruta A: Estable pero modesta - baja varianza, rendimiento consistente
    ruta_A = [
        (0.90, 80),   # 90% probabilidad de 80 unidades (caso normal)
        (0.10, 40)    # 10% probabilidad de 40 unidades (pequeño problema)
    ]
    
    # Ruta B: Balance riesgo-recompensa - moderada varianza
    ruta_B = [
        (0.60, 50),   # 60% probabilidad de 50 unidades (rendimiento base)
        (0.35, 120),  # 35% probabilidad de 120 unidades (bonus por eficiencia)
        (0.05, 5)     # 5% probabilidad de 5 unidades (fallo temporal)
    ]
    
    # Ruta C: Alta recompensa con alto riesgo - maxima varianza
    ruta_C = [
        (0.15, 200),  # 15% probabilidad de 200 unidades (jackpot)
        (0.25, 100),  # 25% probabilidad de 100 unidades (buen rendimiento)
        (0.30, 30),   # 30% probabilidad de 30 unidades (rendimiento bajo)
        (0.30, 1)     # 30% probabilidad de 1 unidad (casi fallo total)
    ]
    
    return {
        "Ruta_A_SectorLuz_TorreIO": ruta_A,    # Ruta conservadora
        "Ruta_B_Portal_Arena": ruta_B,         # Ruta balanceada  
        "Ruta_C_Base_Nucleo": ruta_C,          # Ruta agresiva
    }


# =========================
# COMPARACION DE ESTRATEGIAS
# =========================

def comparar_loterias(modo="CRRA", coeficiente_r=1.0, coeficiente_a=0.01):
    """
    Compara todas las rutas usando teoria de la utilidad.
    
    Evalua cada ruta calculando metricas clave y determina la estrategia
    optima segun la funcion de utilidad seleccionada.
    
    Parametros:
        modo: Tipo de funcion de utilidad ("CRRA" o "CARA")
        coeficiente_r: Coeficiente de aversion para CRRA
        coeficiente_a: Coeficiente de aversion para CARA
    """
    # Obtener las rutas definidas
    loterias = definir_rutas_tron()
    
    # Configurar funciones segun el modo seleccionado
    if modo == "CRRA":
        funcion_utilidad = lambda x: utilidad_crra(x, coeficiente_r)
        funcion_inversa = lambda u: inversa_utilidad_crra(u, coeficiente_r)
        titulo = f"CRRA (Coeficiente Aversion = {coeficiente_r})"
        descripcion_riesgo = _obtener_descripcion_riesgo_crra(coeficiente_r)
        
    elif modo == "CARA":
        funcion_utilidad = lambda x: utilidad_cara(x, coeficiente_a)
        funcion_inversa = lambda u: inversa_utilidad_cara(u, coeficiente_a)
        titulo = f"CARA (Coeficiente Aversion = {coeficiente_a})"
        descripcion_riesgo = _obtener_descripcion_riesgo_cara(coeficiente_a)
        
    else:
        raise ValueError("Modo debe ser 'CRRA' o 'CARA'")

    print("=" * 70)
    print("SISTEMA DE EVALUACION DE RUTAS - TEORIA DE LA UTILIDAD")
    print("=" * 70)
    print(f"Modelo: {titulo}")
    print(f"Perfil de Riesgo: {descripcion_riesgo}")
    print("=" * 70)
    
    # Encabezado de la tabla
    print(f"{'RUTA':<25} {'VE':<8} {'UE':<12} {'EC':<8} {'PR':<8} {'RECOMENDACION'}")
    print("-" * 70)
    
    mejor_ruta = None
    mejor_utilidad = float("-inf")
    
    # Evaluar cada ruta
    for nombre, loteria in loterias.items():
        # Calcular metricas
        valor_esperado = sum(p * x for p, x in loteria)
        utilidad_esp = utilidad_esperada(loteria, funcion_utilidad)
        equivalente_cierto_val = equivalente_cierto(loteria, funcion_utilidad, funcion_inversa)
        prima_riesgo_val = prima_riesgo(loteria, equivalente_cierto_val)
        
        # Determinar recomendacion
        recomendacion = _obtener_recomendacion(prima_riesgo_val, valor_esperado)
        
        # Imprimir resultados
        print(f"{nombre:<25} {valor_esperado:<8.1f} {utilidad_esp:<12.6f} "
              f"{equivalente_cierto_val:<8.1f} {prima_riesgo_val:<8.1f} {recomendacion}")
        
        # Actualizar mejor ruta
        if utilidad_esp > mejor_utilidad:
            mejor_utilidad = utilidad_esp
            mejor_ruta = nombre
    
    # Resultado final
    print("=" * 70)
    print(f"MEJOR RUTA POR UTILIDAD ESPERADA: {mejor_ruta}")
    print("=" * 70)


def _obtener_descripcion_riesgo_crra(coeficiente: float) -> str:
    """Obtiene descripcion del perfil de riesgo para CRRA."""
    if coeficiente == 0:
        return "NEUTRAL AL RIESGO"
    elif coeficiente < 1:
        return "AVERSION BAJA AL RIESGO"
    elif coeficiente == 1:
        return "AVERSION MODERADA AL RIESGO (Logaritmica)"
    else:
        return "AVERSION ALTA AL RIESGO"


def _obtener_descripcion_riesgo_cara(coeficiente: float) -> str:
    """Obtiene descripcion del perfil de riesgo para CARA."""
    if coeficiente < 0.005:
        return "AVERSION MUY BAJA AL RIESGO"
    elif coeficiente < 0.02:
        return "AVERSION MODERADA AL RIESGO"
    else:
        return "AVERSION ALTA AL RIESGO"


def _obtener_recomendacion(prima_riesgo: float, valor_esperado: float) -> str:
    """Determina la recomendacion basada en las metricas."""
    if prima_riesgo < 5:
        return "BAJO RIESGO"
    elif prima_riesgo < 15:
        return "RIESGO MODERADO"
    else:
        return "ALTO RIESGO"


# =========================
# EJECUCION PRINCIPAL
# =========================

if __name__ == "__main__":
    """
    Demo principal del sistema de evaluacion de utilidad.
    
    Permite comparar diferentes rutas bajo distintos perfiles de aversion al riesgo.
    """
    
    print("SISTEMA DE TOMA DE DECISIONES BAJO INCERTIDUMBRE - TRON DIGITAL")
    print("Analisis de rutas usando Teoria de la Utilidad")
    print()
    
    # Configuracion 1: Aversion moderada al riesgo (CRRA logaritmica)
    print("CONFIGURACION 1: Decisionista Conservador")
    comparar_loterias(modo="CRRA", coeficiente_r=1.0)
    print("\n")
    
    # Configuracion 2: Neutral al riesgo
    print("CONFIGURACION 2: Decisionista Neutral al Riesgo")
    comparar_loterias(modo="CRRA", coeficiente_r=0.0)
    print("\n")
    
    # Configuracion 3: Aversion alta al riesgo (CARA)
    print("CONFIGURACION 3: Decisionista Muy Conservador")
    comparar_loterias(modo="CARA", coeficiente_a=0.02)
    print("\n")
    
    # Explicacion de metricas
    print("LEYENDA DE METRICAS:")
    print("  VE  = Valor Esperado (promedio ponderado por probabilidades)")
    print("  UE  = Utilidad Esperada (suma ponderada de utilidades)")
    print("  EC  = Equivalente Cierto (energia segura equivalente)")
    print("  PR  = Prima de Riesgo (VE - EC, cuanto se paga por evitar riesgo)")
    print()
    print("RECOMENDACIONES BASADAS EN PRIMA DE RIESGO:")
    print("  PR < 5:  Bajo Riesgo - Estrategia Conservadora")
    print("  PR 5-15: Riesgo Moderado - Estrategia Balanceada")  
    print("  PR > 15: Alto Riesgo - Estrategia Agresiva")