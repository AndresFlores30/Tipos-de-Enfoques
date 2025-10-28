import random
import numpy as np

class MCTron:
    def __init__(self):
        # Estados posibles en el grid de Tron
        self.estados = ["CUADRICULA_SEGURA", "PUERTA_ENERGIA", "ARENA_JUEGOS", "TORRE_CONTROL", "SECTOR_CORRUPTION"]
        
        # Matriz de transición de Markov
        self.matriz_transicion = {
            "CUADRICULA_SEGURA": [0.2, 0.3, 0.3, 0.1, 0.1],
            "PUERTA_ENERGIA": [0.4, 0.1, 0.2, 0.2, 0.1],
            "ARENA_JUEGOS": [0.3, 0.2, 0.2, 0.2, 0.1],
            "TORRE_CONTROL": [0.1, 0.3, 0.2, 0.3, 0.1],
            "SECTOR_CORRUPTION": [0.1, 0.1, 0.1, 0.1, 0.6]
        }
        
        # Recompensas por estado
        self.recompensas = {
            "CUADRICULA_SEGURA": 1,
            "PUERTA_ENERGIA": 3,
            "ARENA_JUEGOS": 2,
            "TORRE_CONTROL": 4,
            "SECTOR_CORRUPTION": -2
        }
    
    def transicion_estado(self, estado_actual):
        """Realiza una transición de estado según la matriz de Markov"""
        probabilidades = self.matriz_transicion[estado_actual]
        estado_siguiente = random.choices(self.estados, weights=probabilidades)[0]
        return estado_siguiente
    
    def simulacion_monte_carlo(self, estado_inicial, n_simulaciones, pasos_por_simulacion):
        """Realiza simulaciones de Monte Carlo para la cadena de Markov"""
        print("=== MONTE CARLO PARA CADENAS DE MARKOV - SISTEMA TRON ===")
        print(f"Estado inicial: {estado_inicial}")
        print(f"Simulaciones: {n_simulaciones}, Pasos por simulacion: {pasos_por_simulacion}")
        print("\nEjecutando simulaciones...")
        
        # Estadísticas
        visitas_estados = {estado: 0 for estado in self.estados}
        recompensa_total = 0
        historial_simulaciones = []
        
        for i in range(n_simulaciones):
            estado_actual = estado_inicial
            recompensa_simulacion = 0
            camino = [estado_actual]
            
            for paso in range(pasos_por_simulacion):
                # Transición al siguiente estado
                estado_siguiente = self.transicion_estado(estado_actual)
                recompensa = self.recompensas[estado_siguiente]
                
                # Actualizar estadísticas
                visitas_estados[estado_siguiente] += 1
                recompensa_simulacion += recompensa
                
                # Preparar siguiente iteración
                estado_actual = estado_siguiente
                camino.append(estado_actual)
            
            recompensa_total += recompensa_simulacion
            historial_simulaciones.append(camino)
            
            if i < 3:  # Mostrar primeras 3 simulaciones como ejemplo
                print(f"\nSimulacion {i+1}:")
                print(f"  Camino: {' -> '.join(camino[:5])}..." if len(camino) > 5 else f"  Camino: {' -> '.join(camino)}")
                print(f"  Recompensa total: {recompensa_simulacion}")
        
        return visitas_estados, recompensa_total, historial_simulaciones
    
    def calcular_probabilidades_estacionarias(self, visitas_estados, total_visitas):
        """Calcula las probabilidades estacionarias basadas en las visitas"""
        print("\n" + "="*60)
        print("PROBABILIDADES ESTACIONARIAS ESTIMADAS")
        print("="*60)
        
        probabilidades = {}
        for estado, visitas in visitas_estados.items():
            prob = visitas / total_visitas
            probabilidades[estado] = prob
            print(f"{estado}: {prob:.4f} ({visitas} visitas)")
        
        return probabilidades
    
    def mostrar_matriz_transicion(self):
        """Muestra la matriz de transición del sistema"""
        print("\n" + "="*60)
        print("MATRIZ DE TRANSICION DE MARKOV")
        print("="*60)
        print(f"{'Desde/Hacia':<20} {self.estados[0]:<20} {self.estados[1]:<20} {self.estados[2]:<20} {self.estados[3]:<20} {self.estados[4]:<20}")
        print("-"*120)
        
        for i, estado_desde in enumerate(self.estados):
            probs = self.matriz_transicion[estado_desde]
            print(f"{estado_desde:<20}", end="")
            for prob in probs:
                print(f"{prob:<20.3f}", end="")
            print()
    
    def analizar_recompensas(self, recompensa_total, n_simulaciones, pasos_por_simulacion):
        """Analiza las recompensas obtenidas"""
        print("\n" + "="*60)
        print("ANALISIS DE RECOMPENSAS")
        print("="*60)
        
        recompensa_promedio = recompensa_total / n_simulaciones
        recompensa_por_paso = recompensa_promedio / pasos_por_simulacion
        
        print(f"Recompensa total acumulada: {recompensa_total}")
        print(f"Recompensa promedio por simulacion: {recompensa_promedio:.2f}")
        print(f"Recompensa promedio por paso: {recompensa_por_paso:.2f}")
        
        return recompensa_promedio

def main():
    # Crear sistema Tron
    sistema = MCTron()
    
    # Mostrar matriz de transición
    sistema.mostrar_matriz_transicion()
    
    # Mostrar recompensas
    print("\n" + "="*60)
    print("RECOMPENSAS POR ESTADO")
    print("="*60)
    for estado, recompensa in sistema.recompensas.items():
        print(f"{estado}: {recompensa}")
    
    # Parámetros de simulación
    estado_inicial = "CUADRICULA_SEGURA"
    n_simulaciones = 1000
    pasos_por_simulacion = 50
    
    # Ejecutar simulaciones de Monte Carlo
    visitas_estados, recompensa_total, historial = sistema.simulacion_monte_carlo(
        estado_inicial, n_simulaciones, pasos_por_simulacion
    )
    
    # Calcular resultados
    total_visitas = n_simulaciones * pasos_por_simulacion
    probabilidades_estacionarias = sistema.calcular_probabilidades_estacionarias(visitas_estados, total_visitas)
    
    # Analizar recompensas
    recompensa_promedio = sistema.analizar_recompensas(recompensa_total, n_simulaciones, pasos_por_simulacion)
    
    # Encontrar estado más visitado
    estado_mas_visitado = max(visitas_estados.items(), key=lambda x: x[1])
    print(f"\nEstado mas visitado: {estado_mas_visitado[0]} ({estado_mas_visitado[1]} visitas)")
    
    # Simulación adicional: comportamiento a largo plazo
    print("\n" + "="*60)
    print("PREDICCION A LARGO PLAZO")
    print("="*60)
    print("Basado en las probabilidades estacionarias, el sistema tenderá a:")
    
    estado_predominante = max(probabilidades_estacionarias.items(), key=lambda x: x[1])
    print(f"Estado mas probable: {estado_predominante[0]} (probabilidad: {estado_predominante[1]:.3f})")
    
    if estado_predominante[0] == "SECTOR_CORRUPTION":
        print("ALERTA: El sistema tiende hacia la corrupcion!")
    else:
        print("El sistema se mantiene estable.")

if __name__ == "__main__":
    main()