"""
PROGRAMA: FILTRADO DE PARTÍCULAS (PARTICLE FILTER)

Este programa implementa un Filtro de Partículas (Particle Filter) también conocido
como Método de Monte Carlo Secuencial (SMC) para estimación de estados en sistemas
no lineales y no gaussianos.

El Filtro de Partículas representa la distribución de probabilidad del estado
usando un conjunto de partículas (muestras) con pesos asociados.

Ventajas sobre el Filtro de Kalman:
- Maneja sistemas no lineales
- Maneja distribuciones no gaussianas
- Más robusto ante multimodalidades

Pasos principales:
1. Inicialización: Generar partículas iniciales
2. Predicción: Muestrear nuevo estado según el modelo de transición
3. Actualización: Actualizar pesos según la verosimilitud de las mediciones
4. Remuestreo: Evitar la degeneración de partículas
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# CLASE DEL FILTRADO DE PARTÍCULAS
# =============================================================================
class FiltroParticulas:
    def __init__(self, n_particulas, dim_estado, modelo_transicion, modelo_medicion):
        """
        Inicializa el Filtro de Partículas
        
        Args:
            n_particulas: Número de partículas
            dim_estado: Dimensión del espacio de estado
            modelo_transicion: Función que define la transición de estado
            modelo_medicion: Función que define el modelo de medición
        """
        self.n_particulas = n_particulas
        self.dim_estado = dim_estado
        self.modelo_transicion = modelo_transicion
        self.modelo_medicion = modelo_medicion
        
        # Partículas y pesos
        self.particulas = None
        self.pesos = None
        self.estado_estimado = None
        
        # Historial
        self.historial_particulas = []
        self.historial_pesos = []
        self.historial_estimaciones = []
        
    def inicializar(self, distribucion_inicial):
        """
        Inicializa las partículas según una distribución inicial
        
        Args:
            distribucion_inicial: Función que genera muestras iniciales
        """
        self.particulas = distribucion_inicial(self.n_particulas)
        self.pesos = np.ones(self.n_particulas) / self.n_particulas
        self.estado_estimado = self._calcular_estimacion()
        
        # Guardar estado inicial
        self.historial_particulas.append(self.particulas.copy())
        self.historial_pesos.append(self.pesos.copy())
        self.historial_estimaciones.append(self.estado_estimado.copy())
        
        print(f"Filtro de Partículas inicializado con {self.n_particulas} partículas")
        
    def predecir(self, u=None, ruido_proceso=None):
        """
        Paso de predicción: propaga las partículas según el modelo de transición
        """
        for i in range(self.n_particulas):
            self.particulas[i] = self.modelo_transicion(self.particulas[i], u, ruido_proceso)
    
    def actualizar(self, medicion, ruido_medicion=1.0):
        """
        Paso de actualización: actualiza los pesos según la verosimilitud
        """
        # Calcular verosimilitud para cada partícula
        verosimilitudes = np.zeros(self.n_particulas)
        
        for i in range(self.n_particulas):
            # Probabilidad de la medición dado el estado de la partícula
            verosimilitud = self.modelo_medicion(medicion, self.particulas[i], ruido_medicion)
            verosimilitudes[i] = verosimilitud
        
        # Actualizar pesos (multiplicar por verosimilitud y normalizar)
        self.pesos *= verosimilitudes
        self.pesos += 1e-300  # Evitar ceros absolutos
        self.pesos /= np.sum(self.pesos)
        
        # Calcular nueva estimación
        self.estado_estimado = self._calcular_estimacion()
    
    def remuestrear(self):
        """
        Paso de remuestreo: evita la degeneración de partículas
        usando remuestreo sistemático
        """
        # Calcular número efectivo de partículas
        neff = 1.0 / np.sum(self.pesos ** 2)
        
        # Umbral para remuestreo (típicamente N/2)
        umbral = self.n_particulas / 2
        
        if neff < umbral:
            # Remuestreo sistemático
            indices = self._remuestreo_sistematico()
            self.particulas = self.particulas[indices]
            self.pesos = np.ones(self.n_particulas) / self.n_particulas
            return True
        return False
    
    def _remuestreo_sistematico(self):
        """Implementa remuestreo sistemático"""
        indices = np.zeros(self.n_particulas, dtype=int)
        cumsum = np.cumsum(self.pesos)
        
        # Paso sistemático
        paso = 1.0 / self.n_particulas
        posicion = np.random.uniform(0, paso)
        
        i, j = 0, 0
        while i < self.n_particulas:
            while posicion > cumsum[j]:
                j += 1
            indices[i] = j
            posicion += paso
            i += 1
            
        return indices
    
    def _calcular_estimacion(self):
        """Calcula la estimación del estado como promedio ponderado"""
        return np.average(self.particulas, weights=self.pesos, axis=0)
    
    def paso_completo(self, medicion, u=None, ruido_proceso=None, ruido_medicion=1.0):
        """
        Ejecuta un paso completo del filtro
        """
        # Predicción
        self.predecir(u, ruido_proceso)
        
        # Actualización
        self.actualizar(medicion, ruido_medicion)
        
        # Remuestreo (si es necesario)
        remuestreado = self.remuestrear()
        
        # Guardar en historial
        self.historial_particulas.append(self.particulas.copy())
        self.historial_pesos.append(self.pesos.copy())
        self.historial_estimaciones.append(self.estado_estimado.copy())
        
        return self.estado_estimado, remuestreado
    
    def obtener_estadisticas(self):
        """Calcula estadísticas de las partículas"""
        media = self._calcular_estimacion()
        covarianza = np.cov(self.particulas.T, aweights=self.pesos)
        neff = 1.0 / np.sum(self.pesos ** 2)
        
        return {
            'media': media,
            'covarianza': covarianza,
            'neff': neff,
            'min': np.min(self.particulas, axis=0),
            'max': np.max(self.particulas, axis=0)
        }

# =============================================================================
# EJEMPLO 1: SEGUIMIENTO DE OBJETO NO LINEAL
# =============================================================================
def ejemplo_seguimiento_no_lineal():
    """
    Ejemplo de seguimiento de un objeto con movimiento no lineal
    (modelo de coordenadas polares)
    """
    print("=== EJEMPLO 1: SEGUIMIENTO NO LINEAL EN COORDENADAS POLARES ===\n")
    
    # Parámetros
    n_particulas = 1000
    n_pasos = 50
    dt = 0.1
    
    # Modelo de transición no lineal (movimiento en coordenadas polares)
    def modelo_transicion_polar(estado, u=None, ruido=None):
        """Modelo de transición: movimiento circular con ruido"""
        r, theta, w = estado  # radio, ángulo, velocidad angular
        
        # Evolución del estado
        theta_nuevo = theta + w * dt
        r_nuevo = r  # radio constante
        
        # Agregar ruido
        if ruido is not None:
            r_nuevo += np.random.normal(0, ruido[0])
            theta_nuevo += np.random.normal(0, ruido[1])
            w += np.random.normal(0, ruido[2])
        
        return np.array([r_nuevo, theta_nuevo % (2*np.pi), w])
    
    # Modelo de medición no lineal (conversión a coordenadas cartesianas)
    def modelo_medicion_polar(medicion, estado, ruido_medicion):
        """Modelo de medición: conversión a cartesianas con ruido"""
        r, theta, w = estado
        
        # Convertir a coordenadas cartesianas
        x_est = r * np.cos(theta)
        y_est = r * np.sin(theta)
        
        # Verosimilitud gaussiana
        error_x = medicion[0] - x_est
        error_y = medicion[1] - y_est
        
        verosimilitud = np.exp(-0.5 * (error_x**2 + error_y**2) / ruido_medicion**2)
        
        return verosimilitud
    
    # Distribución inicial
    def distribucion_inicial_polar(n):
        """Genera partículas iniciales"""
        particulas = np.zeros((n, 3))
        particulas[:, 0] = np.random.normal(5, 1, n)  # radio ~ N(5, 1)
        particulas[:, 1] = np.random.uniform(0, 2*np.pi, n)  # ángulo uniforme
        particulas[:, 2] = np.random.normal(1, 0.2, n)  # velocidad angular ~ N(1, 0.2)
        return particulas
    
    # Crear filtro
    filtro = FiltroParticulas(
        n_particulas=n_particulas,
        dim_estado=3,
        modelo_transicion=modelo_transicion_polar,
        modelo_medicion=modelo_medicion_polar
    )
    
    # Inicializar
    filtro.inicializar(distribucion_inicial_polar)
    
    print(f"Filtro configurado para seguimiento en coordenadas polares")
    print(f"Número de partículas: {n_particulas}")
    
    # Simular sistema real
    estado_real = np.array([5.0, 0.0, 1.0])  # [radio, angulo, velocidad_angular]
    estados_reales = [estado_real.copy()]
    mediciones_reales = []
    
    # Generar trayectoria real y mediciones
    for k in range(n_pasos):
        # Evolución real (sin ruido de proceso para simplicidad)
        estado_real = modelo_transicion_polar(estado_real)
        estados_reales.append(estado_real.copy())
        
        # Generar medición ruidosa
        x_real = estado_real[0] * np.cos(estado_real[1])
        y_real = estado_real[0] * np.sin(estado_real[1])
        
        ruido_med = 0.5
        x_med = x_real + np.random.normal(0, ruido_med)
        y_med = y_real + np.random.normal(0, ruido_med)
        
        mediciones_reales.append(np.array([x_med, y_med]))
    
    # Ejecutar filtro
    print(f"\nEjecutando filtro de partículas por {n_pasos} pasos...")
    estimaciones = []
    neff_historial = []
    
    for k in range(n_pasos):
        medicion = mediciones_reales[k]
        estimacion, remuestreado = filtro.paso_completo(
            medicion, 
            ruido_proceso=[0.1, 0.05, 0.02],  # ruido del proceso
            ruido_medicion=0.5
        )
        
        estimaciones.append(estimacion)
        
        # Calcular estadísticas
        stats = filtro.obtener_estadisticas()
        neff_historial.append(stats['neff'])
        
        if k < 3 or k >= n_pasos - 3:
            estado_actual = estados_reales[k+1]
            error_r = abs(estado_actual[0] - estimacion[0])
            error_theta = abs(estado_actual[1] - estimacion[1]) % (2*np.pi)
            
            print(f"Paso {k+1}:")
            print(f"  Real: r={estado_actual[0]:.3f}, θ={estado_actual[1]:.3f}")
            print(f"  Est:  r={estimacion[0]:.3f}, θ={estimacion[1]:.3f}")
            print(f"  Error: r={error_r:.3f}, θ={error_theta:.3f}")
            print(f"  N_eff: {stats['neff']:.1f}/{n_particulas}")
            if remuestreado:
                print("  [REMUESTREO REALIZADO]")
    
    # Análisis de resultados
    print(f"\n--- ANÁLISIS DE RESULTADOS ---")
    
    # Calcular errores finales
    error_final_r = abs(estados_reales[-1][0] - estimaciones[-1][0])
    error_final_theta = abs(estados_reales[-1][1] - estimaciones[-1][1]) % (2*np.pi)
    
    print(f"Error final - Radio: {error_final_r:.4f}, Ángulo: {error_final_theta:.4f}")
    print(f"Número efectivo de partículas promedio: {np.mean(neff_historial):.1f}")
    
    return filtro, estados_reales, estimaciones, mediciones_reales

# =============================================================================
# EJEMPLO 2: ESTIMACIÓN DE PARÁMETROS CON MULTIMODALIDAD
# =============================================================================
def ejemplo_estimacion_multimodal():
    """
    Ejemplo que demuestra la capacidad del filtro de partículas
    para manejar distribuciones multimodales
    """
    print("\n" + "="*70)
    print("=== EJEMPLO 2: ESTIMACIÓN CON DISTRIBUCIÓN MULTIMODAL ===")
    print("="*70 + "\n")
    
    n_particulas = 2000
    n_pasos = 30
    
    # Modelo simple de transición (random walk)
    def modelo_transicion_simple(estado, u=None, ruido=None):
        nuevo_estado = estado.copy()
        if ruido is not None:
            nuevo_estado += np.random.normal(0, ruido, size=estado.shape)
        return nuevo_estado
    
    # Modelo de medición con multimodalidad
    def modelo_medicion_multimodal(medicion, estado, ruido_medicion):
        # Verosimilitud multimodal: dos picos posibles
        verosimilitud1 = np.exp(-0.5 * (medicion - estado)**2 / ruido_medicion**2)
        verosimilitud2 = np.exp(-0.5 * (medicion - (estado + 5))**2 / ruido_medicion**2)
        verosimilitud3 = np.exp(-0.5 * (medicion - (estado - 5))**2 / ruido_medicion**2)
        
        # Combinar verosimilitudes
        return 0.6 * verosimilitud1 + 0.2 * verosimilitud2 + 0.2 * verosimilitud3
    
    # Distribución inicial amplia
    def distribucion_inicial_multimodal(n):
        return np.random.uniform(-10, 10, (n, 1))
    
    # Crear filtro
    filtro = FiltroParticulas(
        n_particulas=n_particulas,
        dim_estado=1,
        modelo_transicion=modelo_transicion_simple,
        modelo_medicion=modelo_medicion_multimodal
    )
    
    filtro.inicializar(distribucion_inicial_multimodal)
    
    print("Filtro configurado para estimación multimodal")
    print("Distribución de verosimilitud con tres modos")
    
    # Secuencia de mediciones que cambian entre modos
    mediciones = []
    valores_reales = [0.0]  # Estado real (desconocido)
    
    for k in range(n_pasos):
        # Cambiar entre modos cada 10 pasos
        if k < 10:
            medicion_real = 0.0
        elif k < 20:
            medicion_real = 5.0
        else:
            medicion_real = -5.0
            
        # Agregar ruido
        medicion_ruidosa = medicion_real + np.random.normal(0, 0.5)
        mediciones.append(medicion_ruidosa)
        valores_reales.append(medicion_real)
    
    # Ejecutar filtro
    print(f"\nEjecutando filtro con {n_pasos} mediciones...")
    estimaciones = []
    
    for k in range(n_pasos):
        estimacion, remuestreado = filtro.paso_completo(
            mediciones[k],
            ruido_proceso=0.1,
            ruido_medicion=0.5
        )
        estimaciones.append(estimacion[0])
        
        if k in [0, 9, 10, 19, 20, 29]:
            stats = filtro.obtener_estadisticas()
            print(f"Paso {k+1}:")
            print(f"  Medición: {mediciones[k]:.2f}")
            print(f"  Estimación: {estimacion[0]:.2f}")
            print(f"  Real: {valores_reales[k+1]:.2f}")
            print(f"  Partículas en [-10,-2]: {np.sum(filtro.particulas < -2)}")
            print(f"  Partículas en [-2,2]: {np.sum((filtro.particulas >= -2) & (filtro.particulas <= 2))}")
            print(f"  Partículas en [2,10]: {np.sum(filtro.particulas > 2)}")
    
    print(f"\nEl filtro puede seguir cambios entre modos múltiples")
    return filtro, valores_reales, estimaciones, mediciones

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    """
    Función principal que ejecuta todos los ejemplos
    """
    print("=== FILTRADO DE PARTÍCULAS - ESTIMACIÓN NO LINEAL Y NO GAUSSIANA ===\n")
    
    # Ejemplo 1: Seguimiento no lineal
    filtro1, estados_reales1, estimaciones1, mediciones1 = ejemplo_seguimiento_no_lineal()
    
    # Ejemplo 2: Estimación multimodal
    filtro2, valores_reales2, estimaciones2, mediciones2 = ejemplo_estimacion_multimodal()
    
    # =============================================================================
    # EXPLICACIÓN CONCEPTUAL
    # =============================================================================
    print("\n" + "="*70)
    print("=== EXPLICACIÓN CONCEPTUAL DEL FILTRADO DE PARTÍCULAS ===")
    print("="*70)
    
    print("\n1. ¿QUÉ ES EL FILTRADO DE PARTÍCULAS?")
    print("   - Método de Monte Carlo Secuencial para estimación de estados")
    print("   - Representa distribuciones con conjuntos de muestras ponderadas")
    print("   - Ideal para sistemas no lineales y no gaussianos")
    
    print("\n2. VENTAJAS SOBRE FILTRO DE KALMAN:")
    print("   - Maneja no linealidades arbitrarias")
    print("   - Maneja distribuciones multimodales")
    print("   - No requiere suposiciones gaussianas")
    print("   - Más robusto ante modelos imperfectos")
    
    print("\n3. PASOS PRINCIPALES:")
    print("   a) INICIALIZACIÓN:")
    print("      - Generar N partículas de distribución inicial")
    print("      - Asignar pesos uniformes: 1/N")
    
    print("   b) PREDICCIÓN:")
    print("      - Propagar cada partícula según modelo de transición")
    print("      - Agregar ruido del proceso")
    
    print("   c) ACTUALIZACIÓN:")
    print("      - Calcular verosimilitud para cada partícula")
    print("      - Actualizar pesos: w_i = w_i * p(z|x_i)")
    print("      - Normalizar pesos")
    
    print("   d) REMUESTREO:")
    print("      - Calcular N_eff = 1 / Σ(w_i²)")
    print("      - Si N_eff < N/2, remuestrear")
    print("      - Eliminar partículas con peso bajo")
    print("      - Duplicar partículas con peso alto")
    
    print("\n4. APLICACIONES TÍPICAS:")
    print("   - Seguimiento de objetos en visión por computador")
    print("   - Localización de robots (SLAM)")
    print("   - Navegación en GPS-denied environments")
    print("   - Estimación financiera y económica")
    print("   - Procesamiento de señales biomédicas")
    
    print("\n5. CONSIDERACIONES PRÁCTICAS:")
    print("   - Número de partículas: trade-off precisión vs computación")
    print("   - Degeneración: sin remuestreo, pocas partículas tienen peso")
    print("   - Sample impoverishment: pérdida de diversidad")
    print("   - Elección de distribución de propuesta")
    
    print("\n6. VARIANTES AVANZADAS:")
    print("   - Particle Smoothing: suavizado hacia atrás")
    print("   - Rao-Blackwellized: combina con filtro de Kalman")
    print("   - Auxiliary Particle Filter: mejor propuesta")
    print("   - Regularized Particle Filter: evita impoverishment")
    
    print("\n=== DEMOSTRACIÓN COMPLETADA ===")

# Ejecutar el programa
if __name__ == "__main__":
    main()