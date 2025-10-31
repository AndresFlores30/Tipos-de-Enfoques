"""
PROGRAMA: RECONOCIMIENTO DEL HABLA CON MODELOS OCULTOS DE MARKOV

Este programa implementa un sistema básico de reconocimiento del habla usando
Modelos Ocultos de Markov (HMM) para reconocer palabras a partir de 
características acústicas.

Componentes principales:
1. Extracción de características: MFCC (Mel Frequency Cepstral Coefficients)
2. Modelado acústico: HMMs para cada palabra
3. Decodificación: Algoritmo de Viterbi para encontrar la palabra más probable
4. Entrenamiento: Algoritmo Baum-Welch para ajustar los parámetros del HMM

Flujo del sistema:
Señal de audio → Extracción MFCC → Características → Decodificación Viterbi → Palabra reconocida
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import dct

# =============================================================================
# EXTRACCIÓN DE CARACTERÍSTICAS MFCC
# =============================================================================
class ExtractorMFCC:
    """
    Clase para extraer coeficientes cepstrales en frecuencia Mel (MFCC)
    que son características acústicas comúnmente usadas en reconocimiento del habla
    """
    
    def __init__(self, tasa_muestreo=16000, tam_ventana=0.025, desplazamiento_ventana=0.01, 
                 num_coeficientes=13, num_filtros=26):
        self.tasa_muestreo = tasa_muestreo
        self.tam_ventana = int(tasa_muestreo * tam_ventana)  # Muestras
        self.desplazamiento_ventana = int(tasa_muestreo * desplazamiento_ventana)
        self.num_coeficientes = num_coeficientes
        self.num_filtros = num_filtros
        self.filtros_mel = None
        
        # Crear banco de filtros Mel
        self._crear_banco_filtros_mel()
    
    def _hertz_a_mel(self, freq):
        """Convierte frecuencia en Hz a escala Mel"""
        return 2595 * np.log10(1 + freq / 700)
    
    def _mel_a_hertz(self, mel):
        """Convierte escala Mel a frecuencia en Hz"""
        return 700 * (10 ** (mel / 2595) - 1)
    
    def _crear_banco_filtros_mel(self):
        """Crea el banco de filtros triangulares en escala Mel"""
        # Frecuencias mínima y máxima en escala Mel
        mel_min = 0
        mel_max = self._hertz_a_mel(self.tasa_muestreo / 2)
        
        # Puntos equiespaciados en escala Mel
        puntos_mel = np.linspace(mel_min, mel_max, self.num_filtros + 2)
        puntos_hz = self._mel_a_hertz(puntos_mel)
        
        # Convertir a bins de FFT
        bins_fft = np.floor((self.tam_ventana + 1) * puntos_hz / self.tasa_muestreo)
        
        # Crear filtros triangulares
        self.filtros_mel = np.zeros((self.num_filtros, self.tam_ventana // 2 + 1))
        
        for i in range(1, self.num_filtros + 1):
            left = int(bins_fft[i - 1])
            center = int(bins_fft[i])
            right = int(bins_fft[i + 1])
            
            # Crear filtro triangular
            for j in range(left, center):
                self.filtros_mel[i-1, j] = (j - bins_fft[i-1]) / (bins_fft[i] - bins_fft[i-1])
            for j in range(center, right):
                self.filtros_mel[i-1, j] = (bins_fft[i+1] - j) / (bins_fft[i+1] - bins_fft[i])
    
    def extraer_mfcc(self, senal_audio):
        """
        Extrae características MFCC de una señal de audio
        
        Args:
            senal_audio: Array con la señal de audio
            
        Returns:
            numpy.array: Matriz de características MFCC [frames x coeficientes]
        """
        # Preénfasis (realtce altas frecuencias)
        senal_preenfasis = np.append(senal_audio[0], senal_audio[1:] - 0.97 * senal_audio[:-1])
        
        # Segmentación en ventanas
        num_frames = 1 + (len(senal_preenfasis) - self.tam_ventana) // self.desplazamiento_ventana
        frames = np.zeros((num_frames, self.tam_ventana))
        
        for i in range(num_frames):
            start = i * self.desplazamiento_ventana
            end = start + self.tam_ventana
            if end <= len(senal_preenfasis):
                frames[i] = senal_preenfasis[start:end]
        
        # Aplicar ventana de Hamming
        frames *= np.hamming(self.tam_ventana)
        
        # Calcular espectro de potencia
        fft_frames = np.fft.rfft(frames, axis=1)
        espectro_potencia = (np.abs(fft_frames) ** 2) / self.tam_ventana
        
        # Aplicar filtros Mel
        energia_mel = np.dot(espectro_potencia, self.filtros_mel.T)
        
        # Log de la energía
        log_energia_mel = np.log(energia_mel + 1e-10)
        
        # Transformada discreta del coseno (DCT)
        mfcc = dct(log_energia_mel, type=2, axis=1, norm='ortho')[:, :self.num_coeficientes]
        
        return mfcc

# =============================================================================
# MODELO HMM PARA RECONOCIMIENTO DE PALABRAS
# =============================================================================
class HMMPalabra:
    """
    Modelo HMM para una palabra específica en el reconocimiento del habla
    """
    
    def __init__(self, nombre_palabra, num_estados=5, num_mezclas=3, dim_caracteristicas=13):
        self.nombre_palabra = nombre_palabra
        self.num_estados = num_estados
        self.num_mezclas = num_mezclas
        self.dim_caracteristicas = dim_caracteristicas
        
        # Parámetros del HMM
        self.pi = None  # Distribución inicial
        self.A = None   # Matriz de transición
        self.means = None  # Medias de las GMM
        self.covs = None   # Covarianzas de las GMM
        self.weights = None  # Pesos de las mezclas
        
        self.inicializar_parametros()
    
    def inicializar_parametros(self):
        """Inicializa los parámetros del HMM"""
        # Distribución inicial (generalmente empieza en el primer estado)
        self.pi = np.zeros(self.num_estados)
        self.pi[0] = 1.0
        
        # Matriz de transición (modelo left-to-right típico en habla)
        self.A = np.zeros((self.num_estados, self.num_estados))
        for i in range(self.num_estados):
            if i < self.num_estados - 1:
                self.A[i, i] = 0.6      # Permanecer en el mismo estado
                self.A[i, i+1] = 0.4    # Moverse al siguiente estado
            else:
                self.A[i, i] = 1.0      # Estado final absorbente
        
        # Parámetros de las GMM para cada estado
        self.means = np.random.randn(self.num_estados, self.num_mezclas, self.dim_caracteristicas) * 0.1
        self.covs = np.ones((self.num_estados, self.num_mezclas, self.dim_caracteristicas)) * 0.1
        self.weights = np.ones((self.num_estados, self.num_mezclas)) / self.num_mezclas
    
    def probabilidad_emision(self, observacion, estado):
        """
        Calcula la probabilidad de emisión para una observación en un estado
        
        Args:
            observacion: Vector de características
            estado: Índice del estado
            
        Returns:
            float: Probabilidad de emisión
        """
        prob = 0.0
        for m in range(self.num_mezclas):
            # Distribución gaussiana multivariada
            diff = observacion - self.means[estado, m]
            exponente = -0.5 * np.sum(diff**2 / self.covs[estado, m])
            normalizacion = 1.0 / np.sqrt(np.prod(2 * np.pi * self.covs[estado, m]))
            prob += self.weights[estado, m] * normalizacion * np.exp(exponente)
        
        return max(prob, 1e-10)  # Evitar underflow
    
    def algoritmo_viterbi(self, secuencia_observaciones):
        """
        Algoritmo de Viterbi para encontrar la secuencia de estados más probable
        
        Args:
            secuencia_observaciones: Secuencia de vectores MFCC
            
        Returns:
            tuple: (log_probabilidad, secuencia_estados)
        """
        T = len(secuencia_observaciones)
        
        # Inicialización
        delta = np.zeros((T, self.num_estados))
        psi = np.zeros((T, self.num_estados), dtype=int)
        
        # Primer paso
        for j in range(self.num_estados):
            delta[0, j] = np.log(self.pi[j]) + np.log(self.probabilidad_emision(secuencia_observaciones[0], j))
        
        # Recursión
        for t in range(1, T):
            for j in range(self.num_estados):
                max_valor = -np.inf
                max_idx = 0
                
                for i in range(self.num_estados):
                    valor = delta[t-1, i] + np.log(self.A[i, j])
                    if valor > max_valor:
                        max_valor = valor
                        max_idx = i
                
                delta[t, j] = max_valor + np.log(self.probabilidad_emision(secuencia_observaciones[t], j))
                psi[t, j] = max_idx
        
        # Backtracking
        secuencia_estados = np.zeros(T, dtype=int)
        secuencia_estados[T-1] = np.argmax(delta[T-1])
        
        for t in range(T-2, -1, -1):
            secuencia_estados[t] = psi[t+1, secuencia_estados[t+1]]
        
        log_probabilidad = np.max(delta[T-1])
        
        return log_probabilidad, secuencia_estados

# =============================================================================
# SISTEMA DE RECONOCIMIENTO COMPLETO
# =============================================================================
class ReconocedorHabla:
    """
    Sistema completo de reconocimiento del habla usando HMMs
    """
    
    def __init__(self):
        self.extractor = ExtractorMFCC()
        self.modelos_palabras = {}
        self.palabras_entrenadas = []
    
    def agregar_palabra(self, nombre_palabra, num_estados=5):
        """Agrega un nuevo modelo HMM para una palabra"""
        self.modelos_palabras[nombre_palabra] = HMMPalabra(
            nombre_palabra, 
            num_estados=num_estados,
            dim_caracteristicas=self.extractor.num_coeficientes
        )
        self.palabras_entrenadas.append(nombre_palabra)
        print(f"Modelo para palabra '{nombre_palabra}' agregado")
    
    def entrenar_modelo(self, nombre_palabra, ejemplos_audio, max_iter=10):
        """
        Entrena un modelo HMM usando el algoritmo Baum-Welch simplificado
        
        Args:
            nombre_palabra: Palabra a entrenar
            ejemplos_audio: Lista de señales de audio de entrenamiento
            max_iter: Número máximo de iteraciones
        """
        if nombre_palabra not in self.modelos_palabras:
            print(f"Error: Modelo para '{nombre_palabra}' no existe")
            return
        
        modelo = self.modelos_palabras[nombre_palabra]
        print(f"Entrenando modelo para '{nombre_palabra}' con {len(ejemplos_audio)} ejemplos...")
        
        # Extraer características de todos los ejemplos
        todas_caracteristicas = []
        for audio in ejemplos_audio:
            mfcc = self.extractor.extraer_mfcc(audio)
            todas_caracteristicas.append(mfcc)
        
        # Versión simplificada de entrenamiento
        for iteracion in range(max_iter):
            print(f"  Iteración {iteracion + 1}/{max_iter}")
            
            # Aquí iría el algoritmo Baum-Welch completo
            # Por simplicidad, hacemos una actualización básica
            
            # Promedio de características por estado (aproximación)
            for estado in range(modelo.num_estados):
                # Actualizar medias (simplificado)
                for mezcla in range(modelo.num_mezclas):
                    # En un entrenamiento real, esto se calcularía con las suficientes estadísticas
                    modelo.means[estado, mezcla] += np.random.normal(0, 0.01, modelo.dim_caracteristicas)
        
        print(f"Entrenamiento de '{nombre_palabra}' completado")
    
    def reconocer(self, senal_audio):
        """
        Reconoce la palabra en una señal de audio
        
        Args:
            senal_audio: Señal de audio a reconocer
            
        Returns:
            tuple: (palabra_reconocida, probabilidades)
        """
        # Extraer características MFCC
        caracteristicas = self.extractor.extraer_mfcc(senal_audio)
        
        # Calcular probabilidad para cada modelo
        probabilidades = {}
        secuencias_estados = {}
        
        for palabra, modelo in self.modelos_palabras.items():
            log_prob, secuencia_estados = modelo.algoritmo_viterbi(caracteristicas)
            probabilidades[palabra] = log_prob
            secuencias_estados[palabra] = secuencia_estados
        
        # Encontrar la palabra con mayor probabilidad
        palabra_reconocida = max(probabilidades, key=probabilidades.get)
        
        return palabra_reconocida, probabilidades, secuencias_estados

# =============================================================================
# GENERACIÓN DE DATOS SIMULADOS
# =============================================================================
def generar_audio_simulado(palabra, duracion=1.0, tasa_muestreo=16000):
    """
    Genera señales de audio simuladas para diferentes palabras
    (En un sistema real, estos serían audios reales)
    """
    t = np.linspace(0, duracion, int(tasa_muestreo * duracion))
    
    if palabra == "hola":
        # Señal con dos tonos para "ho-la"
        senal = 0.5 * np.sin(2 * np.pi * 200 * t) * np.exp(-2 * t)
        senal += 0.3 * np.sin(2 * np.pi * 300 * t) * np.exp(-2 * (t - 0.3))
    elif palabra == "adiós":
        # Señal con tono descendente para "a-diós"
        frecuencias = 400 - 200 * t
        senal = 0.6 * np.sin(2 * np.pi * frecuencias * t)
    elif palabra == "sí":
        # Señal corta y aguda para "sí"
        senal = 0.8 * np.sin(2 * np.pi * 350 * t) * np.exp(-8 * t)
    elif palabra == "no":
        # Señal con dos pulsos cortos para "no"
        senal = 0.7 * np.sin(2 * np.pi * 250 * t) * (np.exp(-10 * t) + 0.5 * np.exp(-10 * (t - 0.2)))
    else:
        # Señal por defecto
        senal = 0.5 * np.sin(2 * np.pi * 250 * t)
    
    # Agregar ruido
    ruido = 0.05 * np.random.randn(len(senal))
    senal += ruido
    
    # Normalizar
    senal = senal / np.max(np.abs(senal))
    
    return senal

# =============================================================================
# EJEMPLO PRÁCTICO
# =============================================================================
def demostracion_reconocimiento_habla():
    """
    Demostración completa de un sistema de reconocimiento del habla
    """
    print("=== SISTEMA DE RECONOCIMIENTO DEL HABLA CON HMM ===\n")
    
    # Crear reconocedor
    reconocedor = ReconocedorHabla()
    
    # Definir vocabulario
    palabras = ["hola", "adiós", "sí", "no"]
    
    print("1. INICIALIZACIÓN DEL SISTEMA:")
    print(f"   Vocabulario: {palabras}")
    print(f"   Características: MFCC con {reconocedor.extractor.num_coeficientes} coeficientes")
    
    # Agregar modelos para cada palabra
    for palabra in palabras:
        reconocedor.agregar_palabra(palabra, num_estados=4)
    
    # Generar datos de entrenamiento simulados
    print("\n2. ENTRENAMIENTO DE MODELOS:")
    datos_entrenamiento = {}
    
    for palabra in palabras:
        # Generar 5 ejemplos de entrenamiento por palabra
        ejemplos = []
        for i in range(5):
            audio = generar_audio_simulado(palabra)
            ejemplos.append(audio)
        datos_entrenamiento[palabra] = ejemplos
        
        # Entrenar modelo (versión simplificada)
        reconocedor.entrenar_modelo(palabra, ejemplos, max_iter=3)
    
    # Probar reconocimiento
    print("\n3. PRUEBA DE RECONOCIMIENTO:")
    
    # Generar señales de prueba
    pruebas = [
        ("hola", generar_audio_simulado("hola")),
        ("adiós", generar_audio_simulado("adiós")),
        ("sí", generar_audio_simulado("sí")),
        ("no", generar_audio_simulado("no"))
    ]
    
    resultados = []
    
    for palabra_real, audio_prueba in pruebas:
        palabra_reconocida, probabilidades, secuencias = reconocedor.reconocer(audio_prueba)
        
        resultados.append({
            'palabra_real': palabra_real,
            'palabra_reconocida': palabra_reconocida,
            'correcto': palabra_real == palabra_reconocida,
            'probabilidades': probabilidades
        })
        
        print(f"\n   Prueba: '{palabra_real}'")
        print(f"   Reconocido como: '{palabra_reconocida}'")
        print(f"   Resultado: {'✓ CORRECTO' if palabra_real == palabra_reconocida else '✗ INCORRECTO'}")
        print(f"   Probabilidades logarítmicas:")
        for palabra, prob in probabilidades.items():
            indicador = " ←" if palabra == palabra_reconocida else ""
            print(f"     {palabra}: {prob:.2f}{indicador}")
    
    # Estadísticas
    print("\n4. ESTADÍSTICAS DE RENDIMIENTO:")
    correctos = sum(1 for r in resultados if r['correcto'])
    total = len(resultados)
    precision = correctos / total * 100
    
    print(f"   Palabras correctas: {correctos}/{total}")
    print(f"   Precisión: {precision:.1f}%")
    
    # Visualización de características (opcional)
    print("\n5. ANÁLISIS DE CARACTERÍSTICAS:")
    print("   Extracción de MFCC para la palabra 'hola':")
    audio_ejemplo = generar_audio_simulado("hola")
    mfcc = reconocedor.extractor.extraer_mfcc(audio_ejemplo)
    
    print(f"   Número de frames: {mfcc.shape[0]}")
    print(f"   Número de coeficientes MFCC: {mfcc.shape[1]}")
    print(f"   Ejemplo de vector MFCC (primer frame): {mfcc[0, :3]}...")
    
    return reconocedor, resultados

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def demo():
    """
    Función principal con explicación conceptual completa
    """
    print("=== RECONOCIMIENTO DEL HABLA - SISTEMA COMPLETO ===\n")
    
    # Ejecutar demostración
    reconocedor, resultados = demostracion_reconocimiento_habla()
    
    # =============================================================================
    # EXPLICACIÓN CONCEPTUAL
    # =============================================================================
    print("\n" + "="*80)
    print("EXPLICACIÓN CONCEPTUAL DEL RECONOCIMIENTO DEL HABLA")
    print("="*80)
    
    print("\n1. ¿QUÉ ES EL RECONOCIMIENTO DEL HABLA?")
    print("   - Conversión de señales de audio en texto")
    print("   - Clasificación de patrones acústicos en palabras")
    print("   - Combinación de procesamiento de señales y aprendizaje automático")
    
    print("\n2. COMPONENTES PRINCIPALES:")
    print("   a) EXTRACCIÓN DE CARACTERÍSTICAS (MFCC):")
    print("      - Preénfasis: realce de altas frecuencias")
    print("      - Ventaneo: división en segmentos cortos (20-30ms)")
    print("      - FFT: conversión al dominio frecuencial")
    print("      - Filtros Mel: banco de filtros en escala perceptual")
    print("      - Log-compresión: simulación de respuesta auditiva humana")
    print("      - DCT: decorrelación para obtener coeficientes cepstrales")
    
    print("   b) MODELADO ACÚSTICO (HMM):")
    print("      - Estados: representan fonemas o partes de fonemas")
    print("      - Transiciones: modelan la secuencia temporal")
    print("      - Emisiones: distribuciones de características acústicas")
    print("      - Topología: generalmente left-to-right para habla")
    
    print("   c) DECODIFICACIÓN (VITERBI):")
    print("      - Encuentra la secuencia de estados más probable")
    print("      - Considera tanto las observaciones como las transiciones")
    print("      - Eficiente mediante programación dinámica")
    
    print("\n3. FLUJO DE PROCESAMIENTO:")
    print("   Audio → Preprocesamiento → Extracción MFCC → HMM → Palabra reconocida")
    print("   Señal → Características → Modelado → Decodificación → Resultado")
    
    print("\n4. APLICACIONES PRÁCTICAS:")
    print("   - Asistentes virtuales (Siri, Alexa, Google Assistant)")
    print("   - Sistemas de dictado")
    print("   - Comandos por voz")
    print("   - Transcripción automática")
    print("   - Sistemas de atención al cliente")
    
    print("\n5. DESAFÍOS TÉCNICOS:")
    print("   - Variabilidad entre hablantes")
    print("   - Ruido ambiental")
    print("   - Vocabulario extenso")
    print("   - Habla continua (no aislada)")
    print("   - Diferentes acentos y dialectos")
    
    print("\n6. TENDENCIAS ACTUALES:")
    print("   - Redes neuronales profundas (DNN-HMM)")
    print("   - Modelos end-to-end (WaveNet, Transformer)")
    print("   - Aprendizaje por transferencia")
    print("   - Modelos multilingües")
    print("   - Procesamiento en edge devices")
    
    print("\n7. EXTENSIONES AVANZADAS:")
    print("   - Reconocimiento de hablante")
    print("   - Detección de idioma")
    print("   - Análisis de emociones")
    print("   - Reconocimiento de comandos contextuales")
    
    print("\n=== DEMOSTRACIÓN COMPLETADA ===")

# Ejecutar el programa (Lo cual da error por cuestiones de la laptop)
if __name__ == "__main__":
    demo()