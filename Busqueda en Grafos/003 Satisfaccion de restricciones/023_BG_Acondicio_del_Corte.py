"""
SISTEMA DE CONDICIONAMIENTO POR CORTE (CUTSET CONDITIONING) - TRON DIGITAL

Este modulo implementa el algoritmo de Cutset Conditioning para resolver
Problemas de Satisfaccion de Restricciones (CSP). La tecnica identifica
un conjunto de variables (cutset) que, al ser eliminadas, convierte el
grafo de restricciones en un arbol o bosque, permitiendo una resolucion
mas eficiente mediante la combinacion de enumeracion y backtracking.
"""

from collections import deque
from itertools import product


# ==============================
# CONFIGURACION CSP PARA TRON
# ==============================

# Variables del sistema (sectores del Grid)
VARIABLES = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]

# Canales de energia disponibles
COLORES = ["Azul", "Cian", "Blanco", "Ambar"]

# Dominios iniciales (todos los colores para todas las variables)
DOMINIOS = {variable: COLORES.copy() for variable in VARIABLES}

# Grafo de adyacencias (restricciones de vecindad)
VECINOS = {
    "Base": ["Sector_Luz", "Portal"],
    "Sector_Luz": ["Base", "Arena"],
    "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
    "Torre_IO": ["Arena", "Nucleo_Central"],
    "Portal": ["Base", "Arena"],
    "Nucleo_Central": ["Torre_IO"],
}


def restriccion_unaria(variable: str, valor: str) -> bool:
    """
    Aplica restricciones unarias (individuales) para cada variable.
    
    Parametros:
        variable: Nombre de la variable a verificar
        valor: Valor propuesto para la variable
        
    Retorna:
        bool: True si el valor cumple las restricciones unarias
    """
    # Nucleo Central debe ser Blanco por estabilidad del sistema
    if variable == "Nucleo_Central": 
        return valor == "Blanco"
    
    # Torre IO no puede ser Ambar por interferencias con I/O
    if variable == "Torre_IO":       
        return valor != "Ambar"
    
    # Sector Luz prefiere canales de alta luminosidad
    if variable == "Sector_Luz":     
        return valor in ("Azul", "Cian")
    
    return True


def restriccion_binaria(variable1: str, variable2: str, valor1: str, valor2: str) -> bool:
    """
    Aplica restricciones binarias entre variables vecinas.
    
    Parametros:
        variable1: Primera variable
        variable2: Segunda variable  
        valor1: Valor de la primera variable
        valor2: Valor de la segunda variable
        
    Retorna:
        bool: True si los valores cumplen las restricciones binarias
    """
    # Si las variables son vecinas, deben tener valores diferentes
    if variable2 in VECINOS.get(variable1, []): 
        return valor1 != valor2
    return True


# ==============================
# FUNCIONES AUXILIARES
# ==============================

def podar_restricciones_unarias(dominios: dict) -> bool:
    """
    Elimina valores que violan restricciones unarias de los dominios.
    
    Parametros:
        dominios: Diccionario de dominios actuales
        
    Retorna:
        bool: False si algun dominio queda vacio (inconsistencia), True en caso contrario
    """
    for variable in VARIABLES:
        # Filtrar valores que cumplan restricciones unarias
        dominios[variable] = [valor for valor in dominios[variable] if restriccion_unaria(variable, valor)]
        
        # Si algun dominio queda vacio, el problema es inconsistente
        if not dominios[variable]: 
            return False
            
    return True


def encontrar_corte_por_deshojado() -> list:
    """
    Encuentra un conjunto de corte aproximado usando la heuristica de deshojado.
    
    La heuristica elimina iterativamente nodos con grado <= 1 hasta que
    solo quedan nodos con grado >= 2, que forman el corte aproximado.
    
    Retorna:
        list: Lista de variables que forman el conjunto de corte
    """
    # Calcular grados iniciales de cada variable
    grados = {variable: len(VECINOS[variable]) for variable in VARIABLES}
    eliminadas = set()
    
    # Cola para procesar variables con grado <= 1
    cola = deque([variable for variable in VARIABLES if grados[variable] <= 1])
    
    while cola:
        variable_actual = cola.popleft()
        
        # Si ya fue eliminada, continuar
        if variable_actual in eliminadas:
            continue
            
        # Marcar como eliminada
        eliminadas.add(variable_actual)
        
        # Actualizar grados de los vecinos
        for vecino in VECINOS[variable_actual]:
            if vecino in eliminadas:
                continue
                
            grados[vecino] -= 1
            
            # Si el vecino ahora tiene grado 1, agregarlo a la cola
            if grados[vecino] == 1:
                cola.append(vecino)
    
    # El corte son las variables que no fueron eliminadas
    return sorted([variable for variable in VARIABLES if variable not in eliminadas])


def algoritmo_ac3(dominios: dict) -> bool:
    """
    Ejecuta el algoritmo AC-3 (Arc Consistency 3) para hacer consistencia de arcos.
    
    Parametros:
        dominios: Diccionario de dominios actuales
        
    Retorna:
        bool: True si se logro consistencia sin dominios vacios, False en caso contrario
    """
    # Inicializar cola con todos los arcos del grafo
    cola_arcos = deque()
    for variable1 in VARIABLES:
        for variable2 in VECINOS[variable1]:
            cola_arcos.append((variable1, variable2))

    def revisar_arco(variable1: str, variable2: str) -> bool:
        """
        Revisa un arco y elimina valores inconsistentes de variable1.
        
        Retorna:
            bool: True si se modifico el dominio de variable1
        """
        modificado = False
        valores_variable1 = dominios[variable1].copy()
        
        for valor1 in valores_variable1:
            # Verificar si existe algun valor en variable2 que sea compatible
            valor_compatible_encontrado = False
            
            for valor2 in dominios[variable2]:
                if (restriccion_binaria(variable1, variable2, valor1, valor2) and 
                    restriccion_unaria(variable2, valor2)):
                    valor_compatible_encontrado = True
                    break
                    
            # Si no hay valor compatible, eliminar valor1 del dominio
            if not valor_compatible_encontrado:
                dominios[variable1].remove(valor1)
                modificado = True
                
        return modificado

    # Procesar todos los arcos hasta que no haya cambios
    while cola_arcos:
        variable1, variable2 = cola_arcos.popleft()
        
        if revisar_arco(variable1, variable2):
            # Si el dominio de variable1 quedo vacio, el problema es inconsistente
            if not dominios[variable1]:
                return False
                
            # Agregar arcos inversos para revisar consistencia
            for vecino in VECINOS[variable1]:
                if vecino != variable2:
                    cola_arcos.append((vecino, variable1))
                    
    return True


def heuristica_mrv(dominios: dict, asignacion_actual: dict) -> str:
    """
    Selecciona la variable con menor numero de valores restantes (MRV).
    
    Parametros:
        dominios: Dominios actuales de las variables
        asignacion_actual: Asignaciones ya realizadas
        
    Retorna:
        str: Variable seleccionada
    """
    variables_no_asignadas = [variable for variable in VARIABLES if variable not in asignacion_actual]
    return min(variables_no_asignadas, key=lambda variable: len(dominios[variable]))


def es_consistente_local(variable: str, valor: str, asignacion_actual: dict) -> bool:
    """
    Verifica si una asignacion es localmente consistente.
    
    Parametros:
        variable: Variable a asignar
        valor: Valor propuesto
        asignacion_actual: Asignaciones ya realizadas
        
    Retorna:
        bool: True si la asignacion es consistente
    """
    # Verificar restriccion unaria
    if not restriccion_unaria(variable, valor):
        return False
        
    # Verificar restricciones binarias con variables ya asignadas
    for variable_asignada, valor_asignado in asignacion_actual.items():
        if not restriccion_binaria(variable, variable_asignada, valor, valor_asignado):
            return False
            
    return True


def backtracking_para_bosque(dominios: dict, asignacion_actual: dict) -> dict:
    """
    Algoritmo de backtracking optimizado para grafos tipo bosque.
    
    Parametros:
        dominios: Dominios actuales de las variables
        asignacion_actual: Asignaciones ya realizadas
        
    Retorna:
        dict: Solucion completa o None si no se encuentra
    """
    # Condicion de terminacion: todas las variables asignadas
    if len(asignacion_actual) == len(VARIABLES):
        return dict(asignacion_actual)
        
    # Seleccionar variable usando heuristica MRV
    variable = heuristica_mrv(dominios, asignacion_actual)
    
    # Probar todos los valores del dominio de la variable
    for valor in dominios[variable]:
        if es_consistente_local(variable, valor, asignacion_actual):
            # Realizar asignacion
            asignacion_actual[variable] = valor
            
            # Llamada recursiva
            resultado = backtracking_para_bosque(dominios, asignacion_actual)
            if resultado:
                return resultado
                
            # Backtrack: deshacer asignacion
            del asignacion_actual[variable]
            
    return None


# ==============================
# ALGORITMO PRINCIPAL - CUTSET CONDITIONING
# ==============================

def condicionamiento_por_corte():
    """
    Algoritmo principal de Cutset Conditioning.
    
    Divide el problema en dos partes:
    1. Enumeracion sobre el conjunto de corte
    2. Resolucion eficiente del bosque restante
    
    Retorna:
        dict: Solucion encontrada o None si no existe
    """
    print("INICIANDO CONDICIONAMIENTO POR CORTE - SISTEMA TRON")
    print("=" * 50)
    
    # Copia inicial de dominios
    dominios_iniciales = {variable: DOMINIOS[variable].copy() for variable in VARIABLES}
    
    # Poda inicial por restricciones unarias
    if not podar_restricciones_unarias(dominios_iniciales):
        print("PROBLEMA INCONSISTENTE: Dominio vacio tras poda unaria")
        return None

    # Encontrar conjunto de corte aproximado
    conjunto_corte = encontrar_corte_por_deshojado()
    variables_restantes = [variable for variable in VARIABLES if variable not in conjunto_corte]
    
    print(f"Conjunto de corte encontrado: {conjunto_corte if conjunto_corte else '(vacio)'}")
    print(f"Variables restantes (bosque): {variables_restantes}")

    # Caso especial: si el corte esta vacio, el grafo ya es un bosque
    if not conjunto_corte:
        print("El grafo ya es un bosque - resolviendo directamente con backtracking...")
        
        dominios_actuales = {variable: dominios_iniciales[variable].copy() for variable in VARIABLES}
        
        # Aplicar AC-3 para consistencia
        if not algoritmo_ac3(dominios_actuales):
            print("PROBLEMA INCONSISTENTE tras AC-3")
            return None
            
        # Resolver con backtracking
        solucion = backtracking_para_bosque(dominios_actuales, {})
        imprimir_solucion(solucion)
        return solucion

    # FASE 1: Enumeracion sobre el conjunto de corte
    print(f"\nEnumerando {len(conjunto_corte)} variables del corte...")
    
    # Generar todas las combinaciones posibles para el corte
    combinaciones_corte = [dominios_iniciales[variable] for variable in conjunto_corte]
    
    for valores_corte in product(*combinaciones_corte):
        # Crear asignacion parcial para el corte
        asignacion_corte = dict(zip(conjunto_corte, valores_corte))
        
        # Verificar consistencia interna del corte
        corte_consistente = True
        for variable1, valor1 in asignacion_corte.items():
            for variable2, valor2 in asignacion_corte.items():
                if variable1 == variable2:
                    continue
                    
                # Verificar restricciones binarias dentro del corte
                if variable2 in VECINOS[variable1] and valor1 == valor2:
                    corte_consistente = False
                    break
                    
            if not corte_consistente:
                break
                
        if not corte_consistente:
            continue

        # FASE 2: Resolver el bosque restante
        dominios_actuales = {variable: dominios_iniciales[variable].copy() for variable in VARIABLES}
        
        # Fijar valores del corte en los dominios
        for variable, valor in asignacion_corte.items():
            dominios_actuales[variable] = [valor]

        # Aplicar AC-3 para propagar restricciones
        if not algoritmo_ac3(dominios_actuales):
            continue  # Esta combinacion del corte es inconsistente

        # Resolver el bosque restante con backtracking
        solucion = backtracking_para_bosque(dominios_actuales, dict(asignacion_corte))
        
        if solucion:
            print(f"SOLUCION ENCONTRADA para combinacion del corte: {asignacion_corte}")
            imprimir_solucion(solucion)
            return solucion

    print("NO SE ENCONTRO SOLUCION: Todas las combinaciones del corte fueron inconsistentes")
    return None


def imprimir_solucion(solucion: dict):
    """
    Imprime la solucion de forma legible.
    
    Parametros:
        solucion: Diccionario con la asignacion final
    """
    if not solucion:
        print("SIN SOLUCION")
        return
        
    print("\n" + "=" * 50)
    print("SOLUCION FINAL ENCONTRADA:")
    print("=" * 50)
    
    for variable in VARIABLES:
        print(f"  {variable:15} = {solucion[variable]}")
    
    # Verificacion de restricciones
    print("\nVERIFICACION DE RESTRICCIONES:")
    print("-" * 30)
    
    # Verificar restricciones unarias
    for variable, valor in solucion.items():
        if not restriccion_unaria(variable, valor):
            print(f"x Violacion unaria en {variable}={valor}")
        else:
            print(f"* {variable} cumple restricciones unarias")
    
    # Verificar restricciones binarias
    for variable1 in VARIABLES:
        for variable2 in VECINOS[variable1]:
            if not restriccion_binaria(variable1, variable2, solucion[variable1], solucion[variable2]):
                print(f"x Violacion binaria: {variable1}={solucion[variable1]}, {variable2}={solucion[variable2]}")
            else:
                print(f"* Restriccion binaria {variable1}-{variable2} cumplida")


# ==============================
# EJECUCION PRINCIPAL
# ==============================

if __name__ == "__main__":
    condicionamiento_por_corte()