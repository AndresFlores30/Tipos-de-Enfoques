import numpy as np

class SistemaTron:
    def __init__(self):
        """
        Inicializa el sistema de seguridad de Tron con programas y estados posibles.
        
        Atributos:
            programas: Lista de programas en el sistema
            estados: Estados posibles de los programas
        """
        self.programas = ["CLU", "TRON", "RAM", "FLYNN"]
        self.estados = ["operativo", "comprometido", "desconectado"]
        
    def verosimilitud_observacion(self, programa, observacion):
        """
        Calcula la verosimilitud P(observacion|programa) - Probabilidad de observar
        una evidencia dado un programa específico.
        
        Args:
            programa: Nombre del programa a evaluar
            observacion: Tipo de evidencia observada
            
        Returns:
            float: Probabilidad de la observación dado el programa
        """
        # Matriz de verosimilitudes predefinidas - representa el comportamiento
        # típico de cada programa para diferentes tipos de evidencias
        verosimilitudes = {
            "CLU": {
                "acceso_grid": 0.9,      # CLU frecuentemente accede al grid
                "comando_ilegal": 0.7,   # CLU tiene alta probabilidad de comandos ilegales
                "comunicacion_externa": 0.3  # CLU rara vez se comunica externamente
            },
            "TRON": {
                "acceso_grid": 0.8,      # TRON accede al grid regularmente
                "comando_ilegal": 0.2,   # TRON rara vez usa comandos ilegales
                "comunicacion_externa": 0.1  # TRON casi nunca se comunica externamente
            },
            "RAM": {
                "acceso_grid": 0.6,      # RAM tiene acceso moderado al grid
                "comando_ilegal": 0.4,   # RAM ocasionalmente usa comandos ilegales
                "comunicacion_externa": 0.6  # RAM se comunica externamente con frecuencia
            },
            "FLYNN": {
                "acceso_grid": 0.7,      # FLYNN accede al grid regularmente
                "comando_ilegal": 0.5,   # FLYNN tiene probabilidad media de comandos ilegales
                "comunicacion_externa": 0.8  # FLYNN frecuentemente se comunica externamente
            }
        }
        
        # Retorna la verosimilitud o 0.1 si no se encuentra (probabilidad por defecto)
        return verosimilitudes.get(programa, {}).get(observacion, 0.1)
    
    def probabilidad_prior(self, programa):
        """
        Calcula la probabilidad inicial P(programa) - Creencia previa sobre
        qué programa está ejecutando la acción antes de ver evidencias.
        
        Args:
            programa: Nombre del programa a evaluar
            
        Returns:
            float: Probabilidad prior del programa
        """
        # Distribución inicial de probabilidades basada en conocimiento del dominio
        priors = {
            "CLU": 0.3,      # Prior alto - CLU es el sistema principal
            "TRON": 0.4,     # Prior más alto - TRON es el protagonista activo
            "RAM": 0.2,      # Prior medio - RAM es un programa secundario
            "FLYNN": 0.1     # Prior bajo - FLYNN es un usuario raro
        }
        return priors.get(programa, 0.0)
    
    def ponderacion_verosimilitud(self, evidencias):
        """
        Realiza ponderación por verosimilitud para determinar qué programa
        es más probable dado las evidencias observadas.
        
        El método calcula: P(programa|evidencias) ∝ P(programa) * P(evidencias|programa)
        
        Args:
            evidencias: Lista de evidencias observadas
            
        Returns:
            dict: Probabilidades posteriores normalizadas para cada programa
        """
        print("=== SISTEMA TRON - ANALISIS DE SEGURIDAD ===")
        print(f"Evidencias observadas: {evidencias}")
        print("\nCalculando probabilidades posteriores...")
        
        resultados = {}
        
        # Para cada programa, calcular la ponderación por verosimilitud
        for programa in self.programas:
            # Paso 1: Obtener probabilidad prior P(programa)
            prior = self.probabilidad_prior(programa)
            
            # Paso 2: Calcular verosimilitud conjunta P(evidencias|programa)
            # Asumimos independencia condicional: P(ev1,ev2|prog) = P(ev1|prog)*P(ev2|prog)
            verosimilitud_conjunta = 1.0
            for evidencia in evidencias:
                verosimilitud = self.verosimilitud_observacion(programa, evidencia)
                verosimilitud_conjunta *= verosimilitud
            
            # Paso 3: Calcular peso de verosimilitud (numerador de Bayes)
            # P(programa) * P(evidencias|programa)
            peso_verosimilitud = prior * verosimilitud_conjunta
            resultados[programa] = peso_verosimilitud
            
            # Mostrar cálculos intermedios
            print(f"\n{programa}:")
            print(f"  Prior: P({programa}) = {prior:.3f}")
            print(f"  Verosimilitud: P(evidencias|{programa}) = {verosimilitud_conjunta:.6f}")
            print(f"  Peso verosimilitud: {peso_verosimilitud:.6f}")
        
        # Paso 4: Normalizar para obtener probabilidades posteriores
        # P(programa|evidencias) = peso_verosimilitud / sum(todos_los_pesos)
        total = sum(resultados.values())
        if total > 0:
            probabilidades_posteriores = {prog: peso/total for prog, peso in resultados.items()}
        else:
            # Caso extremo: si total es 0, asignar probabilidades uniformes
            probabilidades_posteriores = {prog: 0.0 for prog in self.programas}
        
        return probabilidades_posteriores

def mostrar_matriz_verosimilitud():
    """
    Muestra la matriz completa de verosimilitudes del sistema
    para facilitar la comprensión del modelo probabilístico.
    """
    print("\n" + "="*60)
    print("MATRIZ DE VEROSIMILITUDES P(observacion|programa)")
    print("="*60)
    print(f"{'Programa':<10} {'acceso_grid':<12} {'comando_ilegal':<15} {'comunicacion_externa':<20}")
    print("-"*60)
    
    # Definir matriz de verosimilitudes para visualización
    matriz = {
        "CLU": [0.9, 0.7, 0.3],
        "TRON": [0.8, 0.2, 0.1],
        "RAM": [0.6, 0.4, 0.6],
        "FLYNN": [0.7, 0.5, 0.8]
    }
    
    # Mostrar cada fila de la matriz
    for programa, valores in matriz.items():
        print(f"{programa:<10} {valores[0]:<12.1f} {valores[1]:<15.1f} {valores[2]:<20.1f}")

def main():
    """
    Función principal que ejecuta el sistema de ponderación de verosimilitud
    con diferentes escenarios de evidencia.
    """
    # Crear instancia del sistema Tron
    sistema = SistemaTron()
    
    # Mostrar matriz de verosimilitudes para referencia
    mostrar_matriz_verosimilitud()
    
    # Escenario 1: Actividad sospechosa típica de intruso
    print("\n" + "="*60)
    print("ESCENARIO 1: Actividad sospechosa detectada")
    print("="*60)
    evidencias1 = ["acceso_grid", "comando_ilegal"]
    prob_posterior1 = sistema.ponderacion_verosimilitud(evidencias1)
    
    # Mostrar resultados ordenados por probabilidad descendente
    print("\n" + "-"*50)
    print("RESULTADOS FINALES - Probabilidades Posteriores:")
    print("-"*50)
    for programa, prob in sorted(prob_posterior1.items(), key=lambda x: x[1], reverse=True):
        print(f"{programa}: {prob:.4f} ({prob*100:.1f}%)")
    
    # Identificar el programa más probable
    programa_mas_probable = max(prob_posterior1, key=prob_posterior1.get)
    print(f"\n>>> Programa mas probable: {programa_mas_probable} <<<")
    
    # Escenario 2: Comunicación externa (comportamiento diferente)
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
    
    # Escenario 3: Múltiples evidencias (caso complejo)
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
    # Punto de entrada del programa
    main()