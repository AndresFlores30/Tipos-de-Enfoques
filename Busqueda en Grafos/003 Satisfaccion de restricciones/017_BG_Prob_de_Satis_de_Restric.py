"""
SISTEMA DE SATISFACCION DE RESTRICCIONES (CSP) - TRON DIGITAL

Este modulo implementa un algoritmo completo de CSP para asignar canales de energia
a sectores del Grid de TRON. Utiliza backtracking con heuristicas avanzadas para
encontrar una asignacion valida que cumpla todas las restricciones del sistema.
"""

from typing import Dict, List, Callable, Optional, Tuple
from collections import defaultdict
import copy


class CSP:
    """
    Clase que representa un Problema de Satisfaccion de Restricciones (CSP).
    
    Un CSP consiste en:
    - Variables: Elementos que necesitan asignacion
    - Dominios: Valores posibles para cada variable
    - Restricciones: Reglas que limitan las asignaciones validas
    """
    
    def __init__(
        self,
        variables: List[str],
        dominios: Dict[str, List[str]],
        vecinos: Dict[str, List[str]],
        restriccion_binaria: Callable[[str, str, str, str], bool],
        restriccion_unaria: Optional[Callable[[str, str], bool]] = None,
        restricciones_globales: Optional[List[Callable[[Dict[str, str]], bool]]] = None
    ) -> None:
        """
        Inicializa el problema CSP.
        
        Parametros:
            variables: Lista de nombres de variables
            dominios: Diccionario {variable: [valores_posibles]}
            vecinos: Diccionario de adyacencias entre variables
            restriccion_binaria: Funcion que verifica restricciones entre pares de variables
            restriccion_unaria: Funcion para restricciones individuales por variable
            restricciones_globales: Restricciones que involucran multiples variables
        """
        self.variables = variables
        self.dominios = {v: list(dominios[v]) for v in variables}
        self.vecinos = {v: list(vecinos.get(v, [])) for v in variables}
        self.restriccion_binaria = restriccion_binaria
        self.restriccion_unaria = restriccion_unaria or (lambda var, val: True)
        self.restricciones_globales = restricciones_globales or []
        self.pasos: List[str] = []  # Registro de pasos del algoritmo

    def consistente(self, asignacion: Dict[str, str], var: str, val: str) -> bool:
        """
        Verifica si una asignacion es consistente con todas las restricciones.
        
        Parametros:
            asignacion: Asignacion actual de variables
            var: Variable que se quiere asignar
            val: Valor que se quiere asignar a la variable
            
        Retorna:
            bool: True si la asignacion es consistente
        """
        # Verificar restriccion unaria
        if not self.restriccion_unaria(var, val):
            return False
            
        # Verificar restricciones binarias con vecinos ya asignados
        for vecino in self.vecinos[var]:
            if vecino in asignacion:
                if not self.restriccion_binaria(var, vecino, val, asignacion[vecino]):
                    return False
                    
        # Verificar restricciones globales
        for restriccion_global in self.restricciones_globales:
            if not self._evaluar_restriccion_global_parcial(restriccion_global, asignacion | {var: val}):
                return False
                
        return True

    def _evaluar_restriccion_global_parcial(self, restriccion_global: Callable, asignacion: Dict[str, str]) -> bool:
        """
        Evalua una restriccion global con asignacion parcial.
        
        Si falta alguna variable requerida, se considera temporalmente valida.
        """
        try:
            return restriccion_global(asignacion)
        except KeyError:
            # Si falta alguna variable, no podemos evaluar completamente
            return True

    def forward_checking(
        self,
        var: str,
        val: str,
        dominios_actuales: Dict[str, List[str]],
        asignacion: Dict[str, str]
    ) -> Optional[Dict[str, List[str]]]:
        """
        Realiza forward checking: poda dominios de variables vecinas.
        
        Elimina valores de los dominios de vecinos que serian inconsistentes
        con la asignacion actual.
        """
        dominios_podados = copy.deepcopy(dominios_actuales)
        
        for vecino in self.vecinos[var]:
            if vecino not in asignacion:  # Solo vecinos no asignados
                valores_validos = []
                
                for valor_vecino in dominios_podados[vecino]:
                    # Verificar si este valor del vecino es compatible
                    es_compatible = (
                        self.restriccion_binaria(var, vecino, val, valor_vecino) and
                        self.restriccion_unaria(vecino, valor_vecino)
                    )
                    
                    if es_compatible:
                        # Verificar restricciones globales
                        asignacion_hipotetica = asignacion | {var: val, vecino: valor_vecino}
                        globales_ok = all(
                            self._evaluar_restriccion_global_parcial(rg, asignacion_hipotetica)
                            for rg in self.restricciones_globales
                        )
                        
                        if globales_ok:
                            valores_validos.append(valor_vecino)
                
                dominios_podados[vecino] = valores_validos
                
                # Si un vecino queda sin valores validos, falla el forward checking
                if not valores_validos:
                    return None
                    
        return dominios_podados


# ============================================================
# HEURISTICAS INTELIGENTES
# ============================================================

def seleccionar_variable_MRV_Degree(csp: CSP, asignacion: Dict[str, str], dominios: Dict[str, List[str]]) -> str:
    """
    Selecciona la siguiente variable a asignar usando heuristica MRV + Degree.
    
    MRV (Minimum Remaining Values): Variable con menos valores posibles
    Degree: En caso de empate, variable con mas vecinos no asignados
    """
    variables_no_asignadas = [v for v in csp.variables if v not in asignacion]
    
    # MRV: encontrar variables con menor dominio restante
    tamano_minimo_dominio = min(len(dominios[v]) for v in variables_no_asignadas)
    candidatas_mrv = [v for v in variables_no_asignadas if len(dominios[v]) == tamano_minimo_dominio]
    
    if len(candidatas_mrv) == 1:
        return candidatas_mrv[0]
        
    # Degree heuristic: entre las candidatas MRV, elegir la con mas vecinos no asignados
    def calcular_grado_restante(variable: str) -> int:
        return sum(1 for vecino in csp.vecinos[variable] if vecino not in asignacion)
        
    return max(candidatas_mrv, key=calcular_grado_restante)


def ordenar_valores_LCV(csp: CSP, variable: str, dominios: Dict[str, List[str]], asignacion: Dict[str, str]) -> List[str]:
    """
    Ordena valores usando heuristica LCV (Least Constraining Value).
    
    Prioriza valores que dejan mas opciones para las variables vecinas.
    """
    puntajes_valores = []
    
    for valor in dominios[variable]:
        impacto_total = 0
        
        # Calcular cuantos valores eliminaria este valor en los vecinos
        for vecino in csp.vecinos[variable]:
            if vecino not in asignacion:
                for valor_vecino in dominios[vecino]:
                    if not csp.restriccion_binaria(variable, vecino, valor, valor_vecino):
                        impacto_total += 1
                        
        puntajes_valores.append((valor, impacto_total))
    
    # Ordenar por menor impacto (LCV)
    puntajes_valores.sort(key=lambda x: x[1])
    return [valor for valor, _ in puntajes_valores]


# ============================================================
# ALGORITMO PRINCIPAL DE BACKTRACKING
# ============================================================

def backtracking_buscar(csp: CSP) -> Tuple[Optional[Dict[str, str]], List[str]]:
    """
    Ejecuta backtracking con forward checking y heuristicas.
    
    Retorna:
        Tuple: (solucion, pasos) donde solucion es el diccionario de asignaciones
    """
    asignacion: Dict[str, str] = {}
    dominios_actuales = copy.deepcopy(csp.dominios)
    
    # Poda inicial por restricciones unarias
    for variable in csp.variables:
        dominios_actuales[variable] = [
            valor for valor in dominios_actuales[variable] 
            if csp.restriccion_unaria(variable, valor)
        ]
        if not dominios_actuales[variable]:
            csp.pasos.append(f"Fallo temprano: dominio vacio en {variable} por restriccion unaria.")
            return None, csp.pasos

    def backtracking_recursivo(asignacion_actual: Dict[str, str], dominios_actuales: Dict[str, List[str]]) -> Optional[Dict[str, str]]:
        """Funcion recursiva interna de backtracking."""
        
        # Condicion de terminacion: todas las variables asignadas
        if len(asignacion_actual) == len(csp.variables):
            # Verificar todas las restricciones globales
            if all(restriccion_global(asignacion_actual) for restriccion_global in csp.restricciones_globales):
                return asignacion_actual
            return None

        # Seleccionar variable usando heuristica MRV + Degree
        variable = seleccionar_variable_MRV_Degree(csp, asignacion_actual, dominios_actuales)
        
        # Ordenar valores usando heuristica LCV
        valores_ordenados = ordenar_valores_LCV(csp, variable, dominios_actuales, asignacion_actual)
        
        for valor in valores_ordenados:
            if csp.consistente(asignacion_actual, variable, valor):
                # Realizar asignacion
                csp.pasos.append(f"Asignar {variable} = {valor}")
                asignacion_actual[variable] = valor
                
                # Forward checking: podar dominios de vecinos
                nuevos_dominios = csp.forward_checking(variable, valor, dominios_actuales, asignacion_actual)
                
                if nuevos_dominios is not None:
                    # Llamada recursiva
                    resultado = backtracking_recursivo(asignacion_actual, nuevos_dominios)
                    if resultado is not None:
                        return resultado
                
                # Backtrack: deshacer asignacion
                csp.pasos.append(f"Retroceder {variable} = {valor}")
                del asignacion_actual[variable]
                
        return None

    # Ejecutar backtracking
    solucion = backtracking_recursivo(asignacion, dominios_actuales)
    return solucion, csp.pasos


# ============================================================
# CONFIGURACION ESPECIFICA PARA TRON
# ============================================================

def construir_CSP_TRON() -> CSP:
    """
    Construye el problema CSP especifico para el mundo de TRON.
    
    Asigna canales de energia a sectores del Grid con restricciones tematicas.
    """
    # Sectores del Grid de TRON
    variables = ["Base", "Sector_Luz", "Arena", "Torre_IO", "Portal", "Nucleo_Central"]

    # Canales de energia disponibles
    canales = ["Azul", "Cian", "Blanco", "Ambar"]

    # Todos los sectores pueden usar cualquier canal inicialmente
    dominios = {sector: canales.copy() for sector in variables}

    # Conexiones entre sectores (restricciones de adyacencia)
    vecinos = {
        "Base": ["Sector_Luz", "Portal"],
        "Sector_Luz": ["Base", "Arena"],
        "Arena": ["Sector_Luz", "Torre_IO", "Portal"],
        "Torre_IO": ["Arena", "Nucleo_Central"],
        "Portal": ["Base", "Arena"],
        "Nucleo_Central": ["Torre_IO"]
    }

    def restriccion_binaria(sector1: str, sector2: str, canal1: str, canal2: str) -> bool:
        """Sectores adyacentes no pueden tener el mismo canal."""
        if sector2 in vecinos.get(sector1, []):
            return canal1 != canal2
        return True

    def restriccion_unaria(sector: str, canal: str) -> bool:
        """Restricciones individuales para cada sector."""
        # Nucleo Central debe ser Blanco por estabilidad
        if sector == "Nucleo_Central":
            return canal == "Blanco"
            
        # Torre IO no puede ser Ambar (interferencia con I/O)
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
        """Al menos dos sectores deben usar Cian para redundancia."""
        if len(asignacion) < len(variables):
            return True  # Solo verificar cuando todas esten asignadas
        conteo_cian = sum(1 for canal in asignacion.values() if canal == "Cian")
        return conteo_cian >= 2

    # Crear y retornar el CSP
    return CSP(
        variables=variables,
        dominios=dominios,
        vecinos=vecinos,
        restriccion_binaria=restriccion_binaria,
        restriccion_unaria=restriccion_unaria,
        restricciones_globales=[restriccion_global_base_portal, restriccion_global_minimo_cian],
    )


# ============================================================
# EJECUCION Y DEMOSTRACION
# ============================================================

def demostrar_CSP_TRON():
    """Funcion principal que ejecuta y muestra los resultados del CSP."""
    print("SISTEMA DE ASIGNACION DE CANALES ENERGETICOS - TRON")
    print("=" * 50)
    
    # Construir y resolver el CSP
    csp_tron = construir_CSP_TRON()
    solucion, pasos = backtracking_buscar(csp_tron)

    # Mostrar proceso
    print("\nREGISTRO DEL PROCESO:")
    print("-" * 30)
    for paso in pasos:
        print(f"  {paso}")

    # Mostrar resultados
    print("\n" + "=" * 50)
    if solucion is None:
        print("NO SE ENCONTRO SOLUCION")
        print("El sistema no puede asignar canales cumpliendo todas las restricciones.")
    else:
        print("SOLUCION ENCONTRADA:")
        print("-" * 30)
        for sector in csp_tron.variables:
            print(f"  {sector:15} = {solucion[sector]}")
        
        print("\nANALISIS DE LA SOLUCION:")
        print("-" * 30)
        print("* Nucleo Central es Blanco (estabilidad del sistema)")
        print("* Torre IO no es Ambar (evita interferencias)")
        print("* Sector Luz usa Azul o Cian (alta luminosidad)")
        print("* Sectores adyacentes tienen canales diferentes")
        print("* Base y Portal no son ambos Azul")
        print("* Al menos dos sectores usan Cian (redundancia)")


if __name__ == "__main__":
    demostrar_CSP_TRON()