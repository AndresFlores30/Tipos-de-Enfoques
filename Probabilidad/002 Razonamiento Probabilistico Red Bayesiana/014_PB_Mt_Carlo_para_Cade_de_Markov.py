import random
import numpy as np

class MCTron:
    def __init__(self):
        """
        Inicializa el sistema de simulación Monte Carlo para Cadenas de Markov
        en el universo de Tron.
        
        Atributos:
            estados: Locaciones posibles en el grid de Tron
            matriz_transicion: Probabilidades de transición entre estados
            recompensas: Recompensa/penalización por visitar cada estado
        """
        # Estados posibles en el grid de Tron
        self.estados = [
            "CUADRICULA_SEGURA",    # Área segura del sistema
            "PUERTA_ENERGIA",       # Fuente de energía
            "ARENA_JUEGOS",         # Arena de competencias
            "TORRE_CONTROL",        # Centro de control
            "SECTOR_CORRUPTION"     # Área corrupta/peligrosa
        ]
        
        # Matriz de transición de Markov: P(estado_siguiente | estado_actual)
        # Cada fila suma 1.0 (distribución de probabilidad)
        self.matriz_transicion = {
            "CUADRICULA_SEGURA": [0.2, 0.3, 0.3, 0.1, 0.1],  # Desde CUADRICULA_SEGURA
            "PUERTA_ENERGIA": [0.4, 0.1, 0.2, 0.2, 0.1],     # Desde PUERTA_ENERGIA
            "ARENA_JUEGOS": [0.3, 0.2, 0.2, 0.2, 0.1],       # Desde ARENA_JUEGOS
            "TORRE_CONTROL": [0.1, 0.3, 0.2, 0.3, 0.1],      # Desde TORRE_CONTROL
            "SECTOR_CORRUPTION": [0.1, 0.1, 0.1, 0.1, 0.6]   # Desde SECTOR_CORRUPTION
        }
        
        # Recompensas por estado (sistema de recompensa inmediata)
        self.recompensas = {
            "CUADRICULA_SEGURA": 1,    # Recompensa pequeña por seguridad
            "PUERTA_ENERGIA": 3,       # Recompensa alta por energía
            "ARENA_JUEGOS": 2,         # Recompensa media por juegos
            "TORRE_CONTROL": 4,        # Recompensa muy alta por control
            "SECTOR_CORRUPTION": -2    # Penalización por corrupción
        }
    
    def transicion_estado(self, estado_actual):
        """
        Realiza una transición de estado según la matriz de Markov.
        
        Args:
            estado_actual: Estado desde el cual se realiza la transición
            
        Returns:
            str: Estado siguiente seleccionado aleatoriamente según las probabilidades
        """
        # Obtener probabilidades de transición desde el estado actual
        probabilidades = self.matriz_transicion[estado_actual]
        
        # Seleccionar estado siguiente basado en las probabilidades
        # random.choices selecciona un elemento de self.estados con weights=probabilidades
        estado_siguiente = random.choices(self.estados, weights=probabilidades)[0]
        
        return estado_siguiente
    
    def simulacion_monte_carlo(self, estado_inicial, n_simulaciones, pasos_por_simulacion):
        """
        Realiza simulaciones de Monte Carlo para estimar propiedades
        de la cadena de Markov a largo plazo.
        
        Args:
            estado_inicial: Estado desde el que comienzan todas las simulaciones
            n_simulaciones: Número de trayectorias independientes a simular
            pasos_por_simulacion: Longitud de cada trayectoria
            
        Returns:
            tuple: (visitas_estados, recompensa_total, historial_simulaciones)
        """
        print("=== MONTE CARLO PARA CADENAS DE MARKOV - SISTEMA TRON ===")
        print(f"Estado inicial: {estado_inicial}")
        print(f"Simulaciones: {n_simulaciones}, Pasos por simulacion: {pasos_por_simulacion}")
        print("\nEjecutando simulaciones...")
        
        # Inicializar contadores para estadísticas
        visitas_estados = {estado: 0 for estado in self.estados}
        recompensa_total = 0
        historial_simulaciones = []
        
        # Ejecutar todas las simulaciones
        for i in range(n_simulaciones):
            estado_actual = estado_inicial
            recompensa_simulacion = 0
            camino = [estado_actual]  # Registrar el camino de esta simulación
            
            # Ejecutar pasos en la cadena de Markov
            for paso in range(pasos_por_simulacion):
                # Realizar transición al siguiente estado
                estado_siguiente = self.transicion_estado(estado_actual)
                recompensa = self.recompensas[estado_siguiente]
                
                # Actualizar estadísticas
                visitas_estados[estado_siguiente] += 1
                recompensa_simulacion += recompensa
                
                # Preparar siguiente iteración
                estado_actual = estado_siguiente
                camino.append(estado_actual)
            
            # Acumular resultados de esta simulación
            recompensa_total += recompensa_simulacion
            historial_simulaciones.append(camino)
            
            # Mostrar ejemplos de las primeras simulaciones
            if i < 3:  # Mostrar solo primeras 3 simulaciones como ejemplo
                print(f"\nSimulacion {i+1}:")
                # Mostrar solo los primeros 5 estados para no saturar la salida
                if len(camino) > 5:
                    print(f"  Camino: {' -> '.join(camino[:5])}...")
                else:
                    print(f"  Camino: {' -> '.join(camino)}")
                print(f"  Recompensa total: {recompensa_simulacion}")
        
        return visitas_estados, recompensa_total, historial_simulaciones
    
    def calcular_probabilidades_estacionarias(self, visitas_estados, total_visitas):
        """
        Calcula las probabilidades estacionarias estimadas basadas en
        la frecuencia de visitas a cada estado.
        
        Args:
            visitas_estados: Diccionario con conteo de visitas por estado
            total_visitas: Número total de visitas registradas
            
        Returns:
            dict: Probabilidades estacionarias estimadas para cada estado
        """
        print("\n" + "="*60)
        print("PROBABILIDADES ESTACIONARIAS ESTIMADAS")
        print("="*60)
        
        probabilidades = {}
        for estado, visitas in visitas_estados.items():
            # La probabilidad estacionaria se estima como frecuencia relativa
            prob = visitas / total_visitas
            probabilidades[estado] = prob
            print(f"{estado}: {prob:.4f} ({visitas} visitas)")
        
        return probabilidades
    
    def mostrar_matriz_transicion(self):
        """
        Muestra la matriz de transición completa del sistema
        para facilitar la comprensión de las dinámicas de Markov.
        """
        print("\n" + "="*60)
        print("MATRIZ DE TRANSICION DE MARKOV")
        print("="*60)
        # Encabezado de la tabla
        print(f"{'Desde/Hacia':<20} {self.estados[0]:<20} {self.estados[1]:<20} {self.estados[2]:<20} {self.estados[3]:<20} {self.estados[4]:<20}")
        print("-"*120)
        
        # Mostrar cada fila de la matriz
        for i, estado_desde in enumerate(self.estados):
            probs = self.matriz_transicion[estado_desde]
            print(f"{estado_desde:<20}", end="")
            for prob in probs:
                print(f"{prob:<20.3f}", end="")
            print()
    
    def analizar_recompensas(self, recompensa_total, n_simulaciones, pasos_por_simulacion):
        """
        Analiza las recompensas obtenidas durante las simulaciones.
        
        Args:
            recompensa_total: Suma total de todas las recompensas
            n_simulaciones: Número de simulaciones ejecutadas
            pasos_por_simulacion: Pasos por simulación
            
        Returns:
            float: Recompensa promedio por simulación
        """
        print("\n" + "="*60)
        print("ANALISIS DE RECOMPENSAS")
        print("="*60)
        
        # Calcular métricas de recompensa
        recompensa_promedio = recompensa_total / n_simulaciones
        recompensa_por_paso = recompensa_promedio / pasos_por_simulacion
        
        print(f"Recompensa total acumulada: {recompensa_total}")
        print(f"Recompensa promedio por simulacion: {recompensa_promedio:.2f}")
        print(f"Recompensa promedio por paso: {recompensa_por_paso:.2f}")
        
        return recompensa_promedio

def main():
    """
    Función principal que ejecuta el sistema de simulación Monte Carlo
    para Cadenas de Markov con diferentes análisis.
    """
    # Crear sistema Tron de simulación
    sistema = MCTron()
    
    # Mostrar matriz de transición para referencia
    sistema.mostrar_matriz_transicion()
    
    # Mostrar sistema de recompensas
    print("\n" + "="*60)
    print("RECOMPENSAS POR ESTADO")
    print("="*60)
    for estado, recompensa in sistema.recompensas.items():
        print(f"{estado}: {recompensa}")
    
    # Configurar parámetros de simulación
    estado_inicial = "CUADRICULA_SEGURA"
    n_simulaciones = 1000      # Número grande para buena estimación
    pasos_por_simulacion = 50  # Suficientes pasos para convergencia
    
    # Ejecutar simulaciones de Monte Carlo
    visitas_estados, recompensa_total, historial = sistema.simulacion_monte_carlo(
        estado_inicial, n_simulaciones, pasos_por_simulacion
    )
    
    # Calcular probabilidades estacionarias (distribución límite)
    total_visitas = n_simulaciones * pasos_por_simulacion
    probabilidades_estacionarias = sistema.calcular_probabilidades_estacionarias(
        visitas_estados, total_visitas
    )
    
    # Analizar desempeño en términos de recompensas
    recompensa_promedio = sistema.analizar_recompensas(
        recompensa_total, n_simulaciones, pasos_por_simulacion
    )
    
    # Encontrar estado más visitado (moda empírica)
    estado_mas_visitado = max(visitas_estados.items(), key=lambda x: x[1])
    print(f"\nEstado mas visitado: {estado_mas_visitado[0]} ({estado_mas_visitado[1]} visitas)")
    
    # Análisis predictivo basado en resultados
    print("\n" + "="*60)
    print("PREDICCION A LARGO PLAZO")
    print("="*60)
    print("Basado en las probabilidades estacionarias, el sistema tenderá a:")
    
    # Identificar estado predominante
    estado_predominante = max(probabilidades_estacionarias.items(), key=lambda x: x[1])
    print(f"Estado mas probable: {estado_predominante[0]} (probabilidad: {estado_predominante[1]:.3f})")
    
    # Análisis de seguridad del sistema
    if estado_predominante[0] == "SECTOR_CORRUPTION":
        print("ALERTA: El sistema tiende hacia la corrupcion!")
    else:
        print("El sistema se mantiene estable.")

if __name__ == "__main__":
    # Punto de entrada del programa
    main()