"""
MANTO DE MARKOV EN RED BAYESIANA TRON - AISLAMIENTO PROBABILÍSTICO

Este código demuestra el concepto del Manto de Markov (Markov Blanket) en redes bayesianas.
El Manto de Markov de una variable es el conjunto mínimo de variables que la aísla
probabilísticamente del resto de la red. Es fundamental para:
- Inferencia eficiente (solo necesitamos el manto para actualizar creencias)
- Entender dependencias condicionales
- Algoritmos de aprendizaje y razonamiento

En el contexto TRON: Identifica qué variables son relevantes para predecir el estado
de cada componente del sistema, dado que conocemos su Manto de Markov.
"""

from typing import Dict, List, Set

class BayesNet:
    def __init__(self):
        self.parents: Dict[str, List[str]] = {}   # Variable -> lista de sus padres
        self.children: Dict[str, List[str]] = {}  # Variable -> lista de sus hijos
        self.domain: Dict[str, List[str]] = {}    # Variable -> valores posibles

    def add_var(self, var: str, domain: List[str], parents: List[str]):
        # Agrega una variable a la red con su dominio y padres
        self.parents[var] = parents[:]  # Copia la lista de padres
        self.domain[var] = domain[:]    # Copia el dominio de valores
        # Actualizar las relaciones de hijos
        for p in parents:
            self.children.setdefault(p, []).append(var)  # Agrega var como hijo de p
        self.children.setdefault(var, [])  # Asegura que var tenga entrada de hijos

    def markov_blanket(self, var: str) -> Set[str]:
        """
        Calcula el Manto de Markov de una variable.
        
        El Manto de Markov consiste en:
        1. Los padres de la variable
        2. Los hijos de la variable  
        3. Los otros padres de los hijos (co-padres o 'spouses')
        
        Propiedad clave: Dado su Manto de Markov, la variable es condicionalmente
        independiente de todas las demás variables en la red.
        
        Args:
            var: Variable para la cual calcular el manto
            
        Returns:
            Conjunto de variables que forman el Manto de Markov
        """
        mb: Set[str] = set()
        
        # 1. Agregar los padres directos
        mb.update(self.parents.get(var, []))
        
        # 2. Agregar los hijos directos
        hijos = self.children.get(var, [])
        mb.update(hijos)
        
        # 3. Agregar los co-padres (otros padres de los hijos, excluyendo la variable misma)
        for h in hijos:
            for p in self.parents.get(h, []):
                if p != var:  # Excluir la variable actual
                    mb.add(p)
                    
        return mb

    def others_outside_blanket(self, var: str) -> Set[str]:
        """
        Encuentra las variables que están fuera del Manto de Markov.
        
        Estas son las variables que son condicionalmente independientes
        de la variable dada, cuando conocemos su Manto de Markov.
        
        Args:
            var: Variable de referencia
            
        Returns:
            Conjunto de variables fuera del manto (excluyendo la variable misma)
        """
        all_vars = set(self.parents.keys())  # Todas las variables en la red
        return all_vars - self.markov_blanket(var) - {var}  # Excluir el manto y la variable misma


def tron_bn_structure() -> BayesNet:
    """
    Construye la estructura de la red bayesiana de TRON.
    
    Estructura causal:
    Power → Gate, Sensor
    Gate → SafePath
    
    Returns:
        Red bayesiana con la estructura de TRON
    """
    bn = BayesNet()
    # Power: variable raíz que influye en Gate y Sensor
    bn.add_var("Power",    ["Good", "Bad"],          parents=[])
    # Gate: depende de Power, influye en SafePath
    bn.add_var("Gate",     ["Open", "Closed"],       parents=["Power"])
    # Sensor: depende solo de Power
    bn.add_var("Sensor",   ["OK", "Alert"],          parents=["Power"])
    # SafePath: depende solo de Gate
    bn.add_var("SafePath", ["Yes", "No"],            parents=["Gate"])
    return bn


def main():
    """
    Demuestra el concepto de Manto de Markov para cada variable en TRON.
    
    Muestra cómo cada variable está probabilísticamente aislada del resto
    de la red cuando conocemos las variables en su Manto de Markov.
    """
    bn = tron_bn_structure()
    consultas = ["Power", "Gate", "Sensor", "SafePath"]
    
    print("MANTO DE MARKOV - SISTEMA TRON")
    print("=" * 60)
    print("Estructura de la red: Power → {Gate, Sensor}, Gate → SafePath")
    print()
    
    for v in consultas:
        mb = bn.markov_blanket(v)
        fuera = bn.others_outside_blanket(v)
        
        print(f"Variable: {v}")
        print(f"  Manto de Markov: {sorted(mb)}")
        print(f"  Fuera del manto: {sorted(fuera)}")
        
        # Interpretación específica para cada variable
        if v == "Power":
            print("  Interpretacion: Para predecir Power, necesitamos conocer")
            print("  sus efectos (Gate, Sensor) y los otros factores que afectan")
            print("  esos efectos (en este caso, no hay co-padres)")
            
        elif v == "Gate":
            print("  Interpretacion: Gate depende de su causa (Power) y")
            print("  sus efectos (SafePath). No hay co-padres.")
            
        elif v == "Sensor":
            print("  Interpretacion: Sensor solo depende de Power y no")
            print("  tiene hijos, por lo tanto su manto es solo Power.")
            
        elif v == "SafePath":
            print("  Interpretacion: SafePath depende de Gate y no tiene hijos.")
            print("  Los co-padres son Power (otro padre de Gate).")
        
        print()



if __name__ == "__main__":
    main()