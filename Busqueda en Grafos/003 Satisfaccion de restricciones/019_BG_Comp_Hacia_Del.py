"""
SISTEMA DE COMPROBACION HACIA DELANTE (FORWARD CHECKING) - TRON DIGITAL

Este modulo implementa un algoritmo de Satisfaccion de Restricciones (CSP)
con Forward Checking para asignar canales de energia a sectores del Grid de TRON.
La tecnica de forward checking poda dominios de variables vecinas inmediatamente
despues de cada asignacion, detectando conflictos de manera temprana.
"""

from typing import Dict, List, Callable, Optional, Tuple
import copy


class CSP:
    """
    Clase que representa un Problema de Satisfaccion de Restricciones (CSP).
    
    Un CSP consiste en variables, dominios y restricciones que definen
    las asignaciones validas entre ellos.
    """
    
    def __init__(
        self,
        variables: List[str],
        dominios: Dict[str, List[str]],
        vecinos: Dict[str, List[str]],
        restriccion_binaria: Callable[[str, str, str, str], bool],
        restriccion_unaria: Optional[Callable[[str, str], bool]] = None,
        restricciones_globales: Optional[List[Callable[[Dict[str, str]], bool]]] = None,
    ):
        """
        Inicializa el problema CSP.
        
        Parametros:
            variables: Lista de nombres de variables del problema
            dominios: Diccionario con los valores posibles para cada variable
            vecinos: Diccionario de adyacencias entre variables
            restriccion_binaria: Funcion que verifica restricciones entre pares de variables
            restriccion_unaria: Funcion para restricciones individuales por variable
            restricciones_globales: Restricciones que involucran multiples variables
        """
        self.variables = variables
        self.dominios = {variable: list(dominios[variable]) for variable in variables}
        self.vecinos = {variable: list(vecinos.get(variable, [])) for variable in variables}
        self.restriccion_binaria = restriccion_binaria
        self.restriccion_unaria = restriccion_unaria or (lambda var, val: True)
        self.restricciones_globales = restricciones_globales or []
        self.log: List[str] = []  # Registro de operaciones para debugging

    def consistente_local(self, asignacion: Dict[str, str], variable: str, valor: str) -> bool:
        """
        Verifica si una asignacion es localmente consistente.
        
        Parametros:
            asignacion: Asignacion actual de variables
            variable: Variable que se quiere asignar
            valor: Valor que se quiere asignar a la variable
            
        Retorna:
            bool: True si la asignacion es localmente consistente
        """
        # Verificar restriccion unaria
        if not self.restriccion_unaria(variable, valor):
            return False
            
        # Verificar restricciones binarias con vecinos ya asignados
        for vecino in self.vecinos[variable]:
            if vecino in asignacion:
                if not self.restriccion_binaria(variable, vecino, valor, asignacion[vecino]):
                    return False
        
        # Verificar restricciones globales con asignacion parcial
        for restriccion_global in self.restricciones_globales:
            try:
                asignacion_parcial = {**asignacion, variable: valor}
                if not restriccion_global(asignacion_parcial):
                    return False
            except KeyError:
                # Si la restriccion global requiere variables no asignadas, se pospone
                pass
                
        return True


# ==============================
# HEURISTICAS INTELIGENTES
# ==============================

def seleccionar_variable_MRV_Degree(
    csp: CSP, 
    asignacion: Dict[str, str], 
    dominios: Dict[str, List[str]]
) -> str:
    """
    Selecciona la siguiente variable usando heuristica MRV + Degree.
    
    MRV (Minimum Remaining Values): Variable con menos valores posibles
    Degree: En caso de empate, variable con mas vecinos no asignados
    
    Parametros:
        csp: Instancia del problema CSP
        asignacion: Asignacion actual
        dominios: Dominios actuales de las variables
        
    Retorna:
        str: Variable seleccionada
    """
    # Obtener variables no asignadas
    variables_no_asignadas = [variable for variable in csp.variables if variable not in asignacion]
    
    # MRV: encontrar variables con menor dominio restante
    tamano_minimo_dominio = min(len(dominios[variable]) for variable in variables_no_asignadas)
    candidatas_mrv = [
        variable for variable in variables_no_asignadas 
        if len(dominios[variable]) == tamano_minimo_dominio
    ]
    
    # Si solo hay una candidata MRV, retornarla
    if len(candidatas_mrv) == 1:
        return candidatas_mrv[0]
    
    # Degree heuristic: entre las candidatas MRV, elegir la con mas vecinos no asignados
    def calcular_grado_restante(variable: str) -> int:
        return sum(1 for vecino in csp.vecinos[variable] if vecino not in asignacion)
        
    return max(candidatas_mrv, key=calcular_grado_restante)


def ordenar_valores_LCV(
    csp: CSP, 
    variable: str, 
    dominios: Dict[str, List[str]], 
    asignacion: Dict[str, str]
) -> List[str]:
    """
    Ordena valores usando heuristica LCV (Least Constraining Value).
    
    Prioriza valores que eliminan menos opciones de las variables vecinas.
    
    Parametros:
        csp: Instancia del problema CSP
        variable: Variable cuyos valores se van a ordenar
        dominios: Dominios actuales
        asignacion: Asignacion actual
        
    Retorna:
        List[str]: Valores ordenados por menor impacto primero
    """
    puntajes_valores = []
    
    for valor in dominios[variable]:
        impacto_total = 0
        
        # Calcular impacto en cada vecino no asignado
        for vecino in csp.vecinos[variable]:
            if vecino not in asignacion:
                # Contar valores del vecino que serian incompatibles con este valor
                for valor_vecino in dominios[vecino]:
                    if not csp.restriccion_binaria(variable, vecino, valor, valor_vecino):
                        impacto_total += 1
                        
        puntajes_valores.append((valor, impacto_total))
    
    # Ordenar por menor impacto (LCV)
    puntajes_valores.sort(key=lambda x: x[1])
    return [valor for valor, _ in puntajes_valores]


# ==============================
# COMPROBACION HACIA DELANTE (FORWARD CHECKING)
# ==============================

def forward_checking(
    csp: CSP,
    variable: str,
    valor: str,
    dominios: Dict[str, List[str]],
    asignacion: Dict[str, str],
) -> Optional[Dict[str, List[str]]]:
    """
    Realiza comprobacion hacia delante (forward checking).
    
    Despues de asignar variable=valor, poda los dominios de las variables
    vecinas no asignadas, eliminando valores que serian inconsistentes.
    
    Parametros:
        csp: Instancia del problema CSP
        variable: Variable que se acaba de asignar
        valor: Valor asignado a la variable
        dominios: Dominios actuales de las variables
        asignacion: Asignacion actual
        
    Retorna:
        Optional[Dict]: Nuevos dominios podados, o None si se detecta un dominio vacio
    """
    nuevos_dominios = copy.deepcopy(dominios)
    
    # Fijar el dominio de la variable asignada a solo el valor elegido
    nuevos_dominios[variable] = [valor]

    # Revisar todos los vecinos de la variable asignada
    for vecino in csp.vecinos[variable]:
        # Solo considerar vecinos no asignados
        if vecino in asignacion:
            continue
            
        valores_permitidos = []
        
        # Filtrar valores del vecino que sean compatibles con la nueva asignacion
        for valor_vecino in nuevos_dominios[vecino]:
            # Verificar restriccion binaria
            if not csp.restriccion_binaria(variable, vecino, valor, valor_vecino):
                continue
                
            # Verificar restriccion unaria del vecino
            if not csp.restriccion_unaria(vecino, valor_vecino):
                continue
                
            # Verificar restricciones globales con asignacion parcial
            globales_consistentes = True
            for restriccion_global in csp.restricciones_globales:
                try:
                    asignacion_hipotetica = {**asignacion, variable: valor, vecino: valor_vecino}
                    if not restriccion_global(asignacion_hipotetica):
                        globales_consistentes = False
                        break
                except KeyError:
                    # Si faltan variables, continuar
                    pass
                    
            if globales_consistentes:
                valores_permitidos.append(valor_vecino)
        
        # Si un vecino queda sin valores permitidos, detectar fallo
        if not valores_permitidos:
            csp.log.append(f"PODA TOTAL: {vecino} sin valores validos al asignar {variable}={valor}")
            return None
            
        # Registrar si hubo poda en este vecino
        if len(valores_permitidos) < len(nuevos_dominios[vecino]):
            csp.log.append(
                f"Poda en {vecino}: {nuevos_dominios[vecino]} -> {valores_permitidos} por {variable}={valor}"
            )
            
        nuevos_dominios[vecino] = valores_permitidos
        
    return nuevos_dominios


# ==============================
# ALGORITMO DE BACKTRACKING CON FORWARD CHECKING
# ==============================

def backtracking_forward_checking(csp: CSP) -> Tuple[Optional[Dict[str, str]], List[str]]:
    """
    Ejecuta backtracking con forward checking.
    
    Combina backtracking tradicional con forward checking para podar
    dominios de manera temprana y reducir el espacio de busqueda.
    
    Parametros:
        csp: Instancia del problema CSP a resolver
        
    Retorna:
        Tuple: (solucion, log) donde solucion es el diccionario de asignaciones
    """
    asignacion: Dict[str, str] = {}
    dominios_actuales = copy.deepcopy(csp.dominios)

    # Poda inicial por restricciones unarias
    for variable in csp.variables:
        valores_filtrados = [
            valor for valor in dominios_actuales[variable] 
            if csp.restriccion_unaria(variable, valor)
        ]
        
        if not valores_filtrados:
            csp.log.append(f"FALLO INICIAL: Dominio vacio en {variable} por restriccion unaria")
            return None, csp.log
            
        if len(valores_filtrados) < len(dominios_actuales[variable]):
            csp.log.append(f"Poda unaria en {variable}: {dominios_actuales[variable]} -> {valores_filtrados}")
            
        dominios_actuales[variable] = valores_filtrados

    def backtracking_recursivo(
        asignacion_actual: Dict[str, str], 
        dominios_actuales: Dict[str, List[str]]
    ) -> Optional[Dict[str, str]]:
        """
        Funcion recursiva interna de backtracking.
        """
        # Condicion de terminacion: todas las variables asignadas
        if len(asignacion_actual) == len(csp.variables):
            # Verificacion final de todas las restricciones globales
            if all(restriccion_global(asignacion_actual) for restriccion_global in csp.restricciones_globales):
                return asignacion_actual
            return None

        # Seleccionar variable usando heuristica MRV + Degree
        variable = seleccionar_variable_MRV_Degree(csp, asignacion_actual, dominios_actuales)
        
        # Ordenar valores usando heuristica LCV
        valores_ordenados = ordenar_valores_LCV(csp, variable, dominios_actuales, asignacion_actual)
        
        for valor in valores_ordenados:
            if csp.consistente_local(asignacion_actual, variable, valor):
                # Realizar asignacion
                csp.log.append(f"ASIGNAR: {variable} = {valor}")
                asignacion_actual[variable] = valor
                
                # Aplicar forward checking
                nuevos_dominios = forward_checking(csp, variable, valor, dominios_actuales, asignacion_actual)
                
                if nuevos_dominios is not None:
                    # Llamada recursiva con dominios podados
                    resultado = backtracking_recursivo(asignacion_actual, nuevos_dominios)
                    if resultado is not None:
                        return resultado
                        
                # Backtrack: deshacer asignacion si no se encontro solucion
                csp.log.append(f"RETROCEDER: {variable} = {valor}")
                del asignacion_actual[variable]
                
        return None

    # Ejecutar algoritmo de backtracking
    solucion = backtracking_recursivo(asignacion, dominios_actuales)
    return solucion, csp.log


# ==============================
# CONFIGURACION ESPECIFICA PARA TRON
# ==============================

def construir_CSP_TRON() -> CSP:
    """
    Construye el problema CSP especifico para el mundo de TRON.
    
    Asigna canales de energia a sectores del Grid con restricciones tematicas
    que reflejan las caracteristicas del universo TRON.
    
    Retorna:
        CSP: Instancia configurada del problema
    """
    # Sectores del Grid de TRON
    variables = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]

    # Canales de energia disponibles
    canales = ["Azul", "Cian", "Blanco", "Ambar"]

    # Todos los sectores pueden usar cualquier canal inicialmente
    dominios = {sector: list(canales) for sector in variables}

    # Conexiones entre sectores (restricciones de adyacencia)
    vecinos = {
        "Base": ["Sector_Luz", "Portal"],
        "Sector_Luz": ["Base", "Arena"],
        "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
        "Torre_IO": ["Arena", "Nucleo_Central"],
        "Portal": ["Base", "Arena"],
        "Nucleo_Central": ["Torre_IO"],
    }

    def restriccion_binaria(sector1: str, sector2: str, canal1: str, canal2: str) -> bool:
        """Sectores adyacentes no pueden tener el mismo canal."""
        if sector2 in vecinos.get(sector1, []):
            return canal1 != canal2
        return True

    def restriccion_unaria(sector: str, canal: str) -> bool:
        """Restricciones individuales para cada sector."""
        # Nucleo Central debe ser Blanco por estabilidad del sistema
        if sector == "Nucleo_Central":
            return canal == "Blanco"
            
        # Torre IO no puede ser Ambar (interferencia con operaciones I/O)
        if sector == "Torre_IO":
            return canal != "Ambar"
            
        # Sector Luz prefiere canales de alta luminosidad
        if sector == "Sector_Luz":
            return canal in ("Azul", "Cian")
            
        return True

    def restriccion_global_base_portal(asignacion: Dict[str, str]) -> bool:
        """Base y Portal no pueden ser ambos Azul simultaneamente."""
        if "Base" in asignacion and "Portal" in asignacion:
            return not (asignacion["Base"] == "Azul" and asignacion["Portal"] == "Azul")
        return True

    def restriccion_global_minimo_cian(asignacion: Dict[str, str]) -> bool:
        """Al menos dos sectores deben usar Cian para redundancia del sistema."""
        if len(asignacion) < len(variables):
            return True  # Solo verificar cuando todas esten asignadas
        conteo_cian = sum(1 for canal in asignacion.values() if canal == "Cian")
        return conteo_cian >= 2

    # Crear y retornar la instancia CSP
    return CSP(
        variables=variables,
        dominios=dominios,
        vecinos=vecinos,
        restriccion_binaria=restriccion_binaria,
        restriccion_unaria=restriccion_unaria,
        restricciones_globales=[restriccion_global_base_portal, restriccion_global_minimo_cian],
    )


# ==============================
# DEMOSTRACION PRINCIPAL
# ==============================

def demostrar_forward_checking():
    """
    Funcion principal que demuestra el funcionamiento del forward checking.
    """
    print("SISTEMA DE COMPROBACION HACIA DELANTE - TRON DIGITAL")
    print("=" * 60)
    print("Asignacion de Canales Energeticos con Forward Checking")
    print("=" * 60)
    
    # Construir y resolver el CSP
    csp_tron = construir_CSP_TRON()
    solucion, registro = backtracking_forward_checking(csp_tron)

    # Mostrar proceso detallado
    print("\nREGISTRO DETALLADO DEL PROCESO:")
    print("-" * 40)
    for linea in registro:
        print(f"  {linea}")

    # Mostrar resultados
    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print("-" * 30)
    
    if solucion is None:
        print("NO SE ENCONTRO SOLUCION")
        print("El sistema no puede asignar canales cumpliendo todas las restricciones.")
    else:
        print("SOLUCION ENCONTRADA:")
        for variable in csp_tron.variables:
            print(f"  {variable:15} = {solucion[variable]}")
        
        # Analisis de la solucion
        print("\nVERIFICACION DE RESTRICCIONES:")
        print("-" * 30)
        print("* Nucleo Central es Blanco (estabilidad)")
        print("* Torre IO no es Ambar (sin interferencias)") 
        print("* Sector Luz usa Azul o Cian (alta luminosidad)")
        print("* Sectores adyacentes tienen canales diferentes")
        print("* Base y Portal no son ambos Azul")
        
        conteo_cian = sum(1 for canal in solucion.values() if canal == "Cian")
        print(f"* {conteo_cian} sectores usan Cian (redundancia)")


if __name__ == "__main__":
    demostrar_forward_checking()