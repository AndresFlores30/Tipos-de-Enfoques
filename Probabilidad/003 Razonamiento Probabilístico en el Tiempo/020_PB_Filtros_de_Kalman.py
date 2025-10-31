"""
PROGRAMA: FILTRO DE KALMAN

Este programa implementa un Filtro de Kalman para estimar el estado de un sistema dinámico
con incertidumbre en las mediciones y en el modelo.

El Filtro de Kalman es un algoritmo recursivo que estima el estado de un sistema:
- Predice el siguiente estado basado en el modelo dinámico
- Actualiza la estimación usando mediciones ruidosas
- Proporciona una estimación óptima en el sentido de mínimos cuadrados

Componentes principales:
1. Modelo de estado: x_k = F * x_{k-1} + B * u_k + w_k
2. Modelo de medición: z_k = H * x_k + v_k
3. Donde w_k ~ N(0, Q) y v_k ~ N(0, R) son ruidos gaussianos

El algoritmo tiene dos pasos:
- Predicción: Usa el modelo para predecir el estado y covarianza
- Actualización: Corrige la predicción con las mediciones
"""

import numpy as np

# =============================================================================
# CLASE DEL FILTRO DE KALMAN
# =============================================================================
class FiltroKalman:
    def __init__(self, dim_estado, dim_medicion):
        """
        Inicializa el Filtro de Kalman
        
        Args:
            dim_estado: Dimensión del vector de estado
            dim_medicion: Dimensión del vector de medición
        """
        self.dim_estado = dim_estado
        self.dim_medicion = dim_medicion
        
        # Matrices del modelo
        self.F = None  # Matriz de transición de estado
        self.B = None  # Matriz de control
        self.H = None  # Matriz de observación
        self.Q = None  # Covarianza del ruido del proceso
        self.R = None  # Covarianza del ruido de medición
        
        # Estado y covarianza
        self.x = None  # Estado estimado
        self.P = None  # Covarianza del error de estimación
        
        # Historial para tracking
        self.historial_estados = []
        self.historial_covarianzas = []
        self.historial_mediciones = []
        
    def inicializar(self, x0, P0, F, H, Q, R, B=None):
        """
        Inicializa los parámetros del filtro
        
        Args:
            x0: Estado inicial
            P0: Covarianza inicial del error
            F: Matriz de transición de estado
            H: Matriz de observación
            Q: Covarianza del ruido del proceso
            R: Covarianza del ruido de medición
            B: Matriz de control (opcional)
        """
        self.x = x0
        self.P = P0
        self.F = F
        self.H = H
        self.Q = Q
        self.R = R
        self.B = B if B is not None else np.zeros((self.dim_estado, 1))
        
        # Guardar estado inicial
        self.historial_estados.append(x0.copy())
        self.historial_covarianzas.append(P0.copy())
        
        print("Filtro de Kalman inicializado correctamente")
        
    def predecir(self, u=None):
        """
        Paso de predicción del filtro
        
        Args:
            u: Vector de control (opcional)
        
        Returns:
            tuple: (x_predicho, P_predicho)
        """
        # Predicción del estado
        if u is None:
            u = np.zeros((self.B.shape[1], 1))
        
        x_predicho = self.F @ self.x + self.B @ u
        
        # Predicción de la covarianza
        P_predicho = self.F @ self.P @ self.F.T + self.Q
        
        return x_predicho, P_predicho
    
    def actualizar(self, z, x_predicho, P_predicho):
        """
        Paso de actualización del filtro
        
        Args:
            z: Vector de medición
            x_predicho: Estado predicho
            P_predicho: Covarianza predicha
        
        Returns:
            tuple: (x_actualizado, P_actualizado)
        """
        # Innovación (diferencia entre medición real y predicha)
        y = z - self.H @ x_predicho
        
        # Covarianza de la innovación
        S = self.H @ P_predicho @ self.H.T + self.R
        
        # Ganancia de Kalman (cuánto confiar en la medición)
        K = P_predicho @ self.H.T @ np.linalg.inv(S)
        
        # Actualización del estado
        x_actualizado = x_predicho + K @ y
        
        # Actualización de la covarianza
        I = np.eye(self.dim_estado)
        P_actualizado = (I - K @ self.H) @ P_predicho
        
        return x_actualizado, P_actualizado
    
    def paso_completo(self, z, u=None):
        """
        Ejecuta un paso completo del filtro (predicción + actualización)
        
        Args:
            z: Vector de medición
            u: Vector de control (opcional)
        """
        # Paso de predicción
        x_pred, P_pred = self.predecir(u)
        
        # Paso de actualización
        x_act, P_act = self.actualizar(z, x_pred, P_pred)
        
        # Actualizar estado interno
        self.x = x_act
        self.P = P_act
        
        # Guardar en historial
        self.historial_estados.append(x_act.copy())
        self.historial_covarianzas.append(P_act.copy())
        self.historial_mediciones.append(z.copy())
        
        return x_act, P_act
    
    def obtener_historial(self):
        """Retorna el historial completo de estimaciones"""
        return {
            'estados': self.historial_estados,
            'covarianzas': self.historial_covarianzas,
            'mediciones': self.historial_mediciones
        }

# =============================================================================
# EJEMPLO 1: SEGUIMIENTO DE POSICIÓN Y VELOCIDAD
# =============================================================================
def ejemplo_seguimiento_posicion():
    """
    Ejemplo de filtro de Kalman para seguimiento de posición y velocidad
    de un objeto en movimiento unidimensional con aceleración constante
    """
    print("=== EJEMPLO 1: SEGUIMIENTO DE POSICIÓN Y VELOCIDAD ===\n")
    
    # Parámetros de simulación
    dt = 0.1  # Intervalo de tiempo (segundos)
    tiempo_total = 5.0  # Tiempo total de simulación (segundos)
    n_pasos = int(tiempo_total / dt)
    
    # Dimensiones
    dim_estado = 2  # [posición, velocidad]
    dim_medicion = 1  # Solo medimos posición
    
    # Crear filtro de Kalman
    kf = FiltroKalman(dim_estado, dim_medicion)
    
    # Matriz de transición de estado (modelo de movimiento)
    # x_{k+1} = [1 dt; 0 1] * x_k + [0.5*dt^2; dt] * a
    F = np.array([
        [1, dt],
        [0, 1]
    ])
    
    # Matriz de observación (medimos solo posición)
    H = np.array([[1, 0]])
    
    # Covarianza del ruido del proceso
    # Representa la incertidumbre en el modelo
    q_pos = 0.1  # Incertidumbre en posición
    q_vel = 0.1  # Incertidumbre en velocidad
    Q = np.array([
        [q_pos, 0],
        [0, q_vel]
    ])
    
    # Covarianza del ruido de medición
    R = np.array([[0.1]])  # Incertidumbre en medición de posición
    
    # Estado inicial [posición, velocidad]
    x0 = np.array([[0], [1]])  # Empieza en posición 0 con velocidad 1 m/s
    
    # Covarianza inicial del error
    P0 = np.array([
        [1, 0],
        [0, 1]
    ])
    
    # Inicializar filtro
    kf.inicializar(x0, P0, F, H, Q, R)
    
    print("Parámetros del filtro:")
    print(f"Matriz F:\n{F}")
    print(f"Matriz H:\n{H}")
    print(f"Matriz Q:\n{Q}")
    print(f"Matriz R:\n{R}")
    print(f"Estado inicial: posición={x0[0,0]:.2f}m, velocidad={x0[1,0]:.2f}m/s")
    
    # Simular movimiento real y mediciones ruidosas
    print(f"\nSimulando {n_pasos} pasos de {dt} segundos...")
    
    # Valores reales (desconocidos en la práctica)
    posicion_real = [0]
    velocidad_real = [1]
    aceleracion = 0.2  # m/s²
    
    # Mediciones ruidosas
    mediciones = []
    estados_reales = []
    
    for k in range(n_pasos):
        # Evolución del sistema real
        vel_nueva = velocidad_real[-1] + aceleracion * dt
        pos_nueva = posicion_real[-1] + velocidad_real[-1] * dt + 0.5 * aceleracion * dt**2
        
        posicion_real.append(pos_nueva)
        velocidad_real.append(vel_nueva)
        estados_reales.append(np.array([[pos_nueva], [vel_nueva]]))
        
        # Generar medición ruidosa
        ruido_medicion = np.random.normal(0, np.sqrt(R[0,0]))
        medicion = pos_nueva + ruido_medicion
        mediciones.append(np.array([[medicion]]))
    
    # Ejecutar filtro de Kalman
    print("\nEjecutando filtro de Kalman...")
    estimaciones = []
    
    for k in range(n_pasos):
        z = mediciones[k]
        x_est, P_est = kf.paso_completo(z)
        estimaciones.append(x_est)
        
        if k < 3 or k >= n_pasos - 3:  # Mostrar primeros y últimos pasos
            pos_real = estados_reales[k][0, 0]
            vel_real = estados_reales[k][1, 0]
            pos_med = z[0, 0]
            pos_est = x_est[0, 0]
            vel_est = x_est[1, 0]
            
            print(f"Paso {k+1}:")
            print(f"  Real:      pos={pos_real:6.3f}m, vel={vel_real:6.3f}m/s")
            print(f"  Medición:  pos={pos_med:6.3f}m")
            print(f"  Estimado:  pos={pos_est:6.3f}m, vel={vel_est:6.3f}m/s")
            print(f"  Error pos: {abs(pos_real - pos_est):6.3f}m")
    
    # Análisis de resultados
    print(f"\n--- ANÁLISIS DE RESULTADOS ---")
    
    # Calcular errores
    errores_posicion = []
    for k in range(n_pasos):
        error = abs(estados_reales[k][0, 0] - estimaciones[k][0, 0])
        errores_posicion.append(error)
    
    error_promedio = np.mean(errores_posicion)
    error_maximo = np.max(errores_posicion)
    
    print(f"Error promedio de posición: {error_promedio:.4f} m")
    print(f"Error máximo de posición: {error_maximo:.4f} m")
    print(f"Desviación estándar del ruido de medición: {np.sqrt(R[0,0]):.4f} m")
    
    # Mostrar evolución de la covarianza
    historial = kf.obtener_historial()
    P_final = historial['covarianzas'][-1]
    print(f"\nCovarianza final:")
    print(f"  Varianza posición: {P_final[0,0]:.6f}")
    print(f"  Varianza velocidad: {P_final[1,1]:.6f}")
    
    return kf, estados_reales, estimaciones, mediciones

# =============================================================================
# EJEMPLO 2: SISTEMA MASA-RESORTE-AMORTIGUADOR
# =============================================================================
def ejemplo_sistema_masa_resorte():
    """
    Ejemplo de filtro de Kalman para un sistema masa-resorte-amortiguador
    """
    print("\n" + "="*70)
    print("=== EJEMPLO 2: SISTEMA MASA-RESORTE-AMORTIGUADOR ===")
    print("="*70 + "\n")
    
    # Parámetros del sistema
    m = 1.0    # Masa (kg)
    k = 0.5    # Constante del resorte (N/m)
    c = 0.1    # Coeficiente de amortiguamiento (Ns/m)
    dt = 0.05  # Intervalo de tiempo (s)
    
    # Dimensiones
    dim_estado = 2  # [posición, velocidad]
    dim_medicion = 2  # Medimos posición y velocidad (pero con ruido)
    
    # Crear filtro
    kf = FiltroKalman(dim_estado, dim_medicion)
    
    # Matriz de transición (discretización del sistema continuo)
    # Sistema: m*x'' + c*x' + k*x = 0
    A_cont = np.array([
        [0, 1],
        [-k/m, -c/m]
    ])
    
    # Discretización (aproximación de primer orden)
    F = np.eye(2) + A_cont * dt
    
    # Matriz de observación (medimos ambos estados)
    H = np.eye(2)
    
    # Covarianzas
    Q = np.array([
        [0.01, 0],
        [0, 0.02]
    ])  # Ruido del proceso
    
    R = np.array([
        [0.1, 0],
        [0, 0.2]
    ])  # Ruido de medición
    
    # Estado inicial [posición, velocidad]
    x0 = np.array([[1], [0]])  # Desplazamiento inicial de 1m, velocidad 0
    
    P0 = np.array([
        [0.5, 0],
        [0, 0.5]
    ])
    
    # Inicializar filtro
    kf.inicializar(x0, P0, F, H, Q, R)
    
    print("Sistema Masa-Resorte-Amortiguador:")
    print(f"Masa: {m} kg, Resorte: {k} N/m, Amortiguamiento: {c} Ns/m")
    print(f"Matriz F:\n{F}")
    print(f"Estado inicial: posición={x0[0,0]:.2f}m, velocidad={x0[1,0]:.2f}m/s")
    
    # Simulación
    n_pasos = 100
    estados_reales = [x0.copy()]
    mediciones = []
    
    print(f"\nSimulando {n_pasos} pasos...")
    
    for k in range(n_pasos):
        # Evolución real del sistema
        x_actual = estados_reales[-1]
        x_siguiente = F @ x_actual
        
        # Agregar algo de ruido del proceso al sistema real
        ruido_proceso = np.random.multivariate_normal(
            [0, 0], Q
        ).reshape(2, 1)
        x_siguiente += ruido_proceso * 0.1
        
        estados_reales.append(x_siguiente)
        
        # Generar medición ruidosa
        ruido_medicion = np.random.multivariate_normal(
            [0, 0], R
        ).reshape(2, 1)
        medicion = x_siguiente + ruido_medicion
        mediciones.append(medicion)
    
    # Ejecutar filtro
    estimaciones = []
    for k in range(n_pasos):
        z = mediciones[k]
        x_est, P_est = kf.paso_completo(z)
        estimaciones.append(x_est)
    
    # Resultados
    pos_final_real = estados_reales[-1][0, 0]
    pos_final_est = estimaciones[-1][0, 0]
    error_final = abs(pos_final_real - pos_final_est)
    
    print(f"\n--- RESULTADOS SISTEMA MASA-RESORTE ---")
    print(f"Posición final real: {pos_final_real:.4f} m")
    print(f"Posición final estimada: {pos_final_est:.4f} m")
    print(f"Error final: {error_final:.4f} m")
    
    # Análisis de covarianza
    historial = kf.obtener_historial()
    P_final = historial['covarianzas'][-1]
    print(f"\nCovarianza final del error:")
    print(f"  σ² posición: {P_final[0,0]:.6f}")
    print(f"  σ² velocidad: {P_final[1,1]:.6f}")
    print(f"  Covarianza: {P_final[0,1]:.6f}")
    
    return kf, estados_reales, estimaciones

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    """
    Función principal que ejecuta todos los ejemplos
    """
    print("=== FILTRO DE KALMAN - ESTIMACIÓN DE ESTADOS CON INCERTIDUMBRE ===\n")
    
    # Ejemplo 1: Seguimiento de posición y velocidad
    kf1, estados_reales1, estimaciones1, mediciones1 = ejemplo_seguimiento_posicion()
    
    # Ejemplo 2: Sistema masa-resorte-amortiguador
    kf2, estados_reales2, estimaciones2 = ejemplo_sistema_masa_resorte()
    
    # =============================================================================
    # EXPLICACIÓN CONCEPTUAL
    # =============================================================================
    print("\n" + "="*70)
    print("=== EXPLICACIÓN CONCEPTUAL DEL FILTRO DE KALMAN ===")
    print("="*70)
    
    print("\n1. ¿QUÉ ES EL FILTRO DE KALMAN?")
    print("   - Algoritmo recursivo para estimar el estado de sistemas dinámicos")
    print("   - Combina predicciones del modelo con mediciones ruidosas")
    print("   - Óptimo para sistemas lineales con ruido gaussiano")
    
    print("\n2. COMPONENTES PRINCIPALES:")
    print("   - Modelo de estado: x_k = F * x_{k-1} + B * u_k + w_k")
    print("   - Modelo de medición: z_k = H * x_k + v_k")
    print("   - Ruidos: w_k ~ N(0, Q), v_k ~ N(0, R)")
    
    print("\n3. DOS PASOS FUNDAMENTALES:")
    print("   a) PREDICCIÓN:")
    print("      - Predice el estado futuro usando el modelo")
    print("      - x_pred = F * x_actual")
    print("      - P_pred = F * P_actual * F' + Q")
    
    print("   b) ACTUALIZACIÓN:")
    print("      - Corrige la predicción con mediciones reales")
    print("      - y = z - H * x_pred  (innovación)")
    print("      - S = H * P_pred * H' + R")
    print("      - K = P_pred * H' * inv(S)  (ganancia de Kalman)")
    print("      - x_actualizado = x_pred + K * y")
    print("      - P_actualizado = (I - K * H) * P_pred")
    
    print("\n4. APLICACIONES TÍPICAS:")
    print("   - Navegación y guiado de vehículos")
    print("   - Seguimiento de objetos en radar")
    print("   - Sistemas de control automático")
    print("   - Procesamiento de señales biomédicas")
    print("   - Fusión de datos de sensores")
    
    print("\n5. VENTAJAS:")
    print("   - Computacionalmente eficiente")
    print("   - Maneja incertidumbre de forma óptima")
    print("   - Proporciona estimaciones de error (covarianza)")
    print("   - Funciona en tiempo real")
    
    print("\n6. LIMITACIONES:")
    print("   - Asume linealidad del sistema")
    print("   - Asume ruido gaussiano")
    print("   - Requiere conocimiento preciso del modelo")
    print("   - Sensible a malas inicializaciones")
    
    print("\n=== DEMOSTRACIÓN COMPLETADA ===")

# Ejecutar el programa
if __name__ == "__main__":
    main()