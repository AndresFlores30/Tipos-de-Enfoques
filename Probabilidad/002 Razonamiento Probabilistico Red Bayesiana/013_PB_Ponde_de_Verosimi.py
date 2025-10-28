import numpy as np

class SistemaTron:
    def __init__(self):
        self.programas = ["CLU", "TRON", "RAM", "FLYNN"]
        self.estados = ["operativo", "comprometido", "desconectado"]
        
    def verosimilitud_observacion(self, programa, observacion):
        """
        Calcula la verosimilitud P(observacion|programa)
        Probabilidad de ver cierta evidencia dado que el programa es específico
        """
        # Matriz de verosimilitudes predefinidas
        verosimilitudes = {
            "CLU": {"acceso_grid": 0.9, "comando_ilegal": 0.7, "comunicacion_externa": 0.3},
            "TRON": {"acceso_grid": 0.8, "comando_ilegal": 0.2, "comunicacion_externa": 0.1},
            "RAM": {"acceso_grid": 0.6, "comando_ilegal": 0.4, "comunicacion_externa": 0.6},
            "FLYNN": {"acceso_grid": 0.7, "comando_ilegal": 0.5, "comunicacion_externa": 0.8}
        }
        
        return verosimilitudes.get(programa, {}).get(observacion, 0.1)
    
    def probabilidad_prior(self, programa):
        """
        Probabilidad inicial P(programa)
        Creencia inicial sobre qué programa está ejecutando la acción
        """
        priors = {
            "CLU": 0.3,      # Alto prior - sistema principal
            "TRON": 0.4,     # Más probable - protagonista
            "RAM": 0.2,      # Prior medio
            "FLYNN": 0.1     # Prior bajo - usuario raro
        }
        return priors.get(programa, 0.0)
    
    def ponderacion_verosimilitud(self, evidencias):
        """
        Realiza ponderación por verosimilitud para determinar
        qué programa es más probable dado las evidencias observadas
        """
        print("=== SISTEMA TRON - ANALISIS DE SEGURIDAD ===")
        print(f"Evidencias observadas: {evidencias}")
        print("\nCalculando probabilidades posteriores...")
        
        resultados = {}
        
        for programa in self.programas:
            # Probabilidad prior P(programa)
            prior = self.probabilidad_prior(programa)
            
            # Calcular verosimilitud conjunta P(evidencias|programa)
            verosimilitud_conjunta = 1.0
            for evidencia in evidencias:
                verosimilitud = self.verosimilitud_observacion(programa, evidencia)
                verosimilitud_conjunta *= verosimilitud
            
            # Ponderación por verosimilitud
            peso_verosimilitud = prior * verosimilitud_conjunta
            resultados[programa] = peso_verosimilitud
            
            print(f"\n{programa}:")
            print(f"  Prior: P({programa}) = {prior:.3f}")
            print(f"  Verosimilitud: P(evidencias|{programa}) = {verosimilitud_conjunta:.6f}")
            print(f"  Peso verosimilitud: {peso_verosimilitud:.6f}")
        
        # Normalizar para obtener probabilidades posteriores
        total = sum(resultados.values())
        if total > 0:
            probabilidades_posteriores = {prog: peso/total for prog, peso in resultados.items()}
        else:
            probabilidades_posteriores = {prog: 0.0 for prog in self.programas}
        
        return probabilidades_posteriores

def mostrar_matriz_verosimilitud():
    """Muestra la matriz de verosimilitudes del sistema"""
    print("\n" + "="*60)
    print("MATRIZ DE VEROSIMILITUDES P(observacion|programa)")
    print("="*60)
    print(f"{'Programa':<10} {'acceso_grid':<12} {'comando_ilegal':<15} {'comunicacion_externa':<20}")
    print("-"*60)
    
    matriz = {
        "CLU": [0.9, 0.7, 0.3],
        "TRON": [0.8, 0.2, 0.1],
        "RAM": [0.6, 0.4, 0.6],
        "FLYNN": [0.7, 0.5, 0.8]
    }
    
    for programa, valores in matriz.items():
        print(f"{programa:<10} {valores[0]:<12.1f} {valores[1]:<15.1f} {valores[2]:<20.1f}")

def main():
    # Crear instancia del sistema Tron
    sistema = SistemaTron()
    
    # Mostrar matriz de verosimilitudes
    mostrar_matriz_verosimilitud()
    
    # Escenario 1: Posible intruso en el sistema
    print("\n" + "="*60)
    print("ESCENARIO 1: Actividad sospechosa detectada")
    print("="*60)
    evidencias1 = ["acceso_grid", "comando_ilegal"]
    prob_posterior1 = sistema.ponderacion_verosimilitud(evidencias1)
    
    print("\n" + "-"*50)
    print("RESULTADOS FINALES - Probabilidades Posteriores:")
    print("-"*50)
    for programa, prob in sorted(prob_posterior1.items(), key=lambda x: x[1], reverse=True):
        print(f"{programa}: {prob:.4f} ({prob*100:.1f}%)")
    
    programa_mas_probable = max(prob_posterior1, key=prob_posterior1.get)
    print(f"\n>>> Programa mas probable: {programa_mas_probable} <<<")
    
    # Escenario 2: Comunicación externa sospechosa
    print("\n" + "="*60)
    print("ESCENARIO 2: Comunicacion externa detectada")
    print("="*60)
    evidencias2 = ["comunicacion_externa", "acceso_grid"]
    prob_posterior2 = sistema.ponderacion_verosimilitud(evidencias2)
    
    print("\n" + "-"*50)
    print("RESULTADOS FINALES - Probabilidades Posteriores:")
    print("-"*50)
    for programa, prob in sorted(prob_posterior2.items(), key=lambda x: x[1], reverse=True):
        print(f"{programa}: {prob:.4f} ({prob*100:.1f}%)")
    
    programa_mas_probable2 = max(prob_posterior2, key=prob_posterior2.get)
    print(f"\n>>> Programa mas probable: {programa_mas_probable2} <<<")
    
    # Escenario 3: Múltiples evidencias
    print("\n" + "="*60)
    print("ESCENARIO 3: Patron complejo de actividad")
    print("="*60)
    evidencias3 = ["acceso_grid", "comando_ilegal", "comunicacion_externa"]
    prob_posterior3 = sistema.ponderacion_verosimilitud(evidencias3)
    
    print("\n" + "-"*50)
    print("RESULTADOS FINALES - Probabilidades Posteriores:")
    print("-"*50)
    for programa, prob in sorted(prob_posterior3.items(), key=lambda x: x[1], reverse=True):
        print(f"{programa}: {prob:.4f} ({prob*100:.1f}%)")
    
    programa_mas_probable3 = max(prob_posterior3, key=prob_posterior3.get)
    print(f"\n>>> Programa mas probable: {programa_mas_probable3} <<<")

if __name__ == "__main__":
    main()