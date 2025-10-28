# Manto de Markov (Markov blanket) en una Red Bayesiana simple (TRON)

from typing import Dict, List, Set

class BayesNet:
    def __init__(self):
        self.parents: Dict[str, List[str]] = {}
        self.children: Dict[str, List[str]] = {}
        self.domain: Dict[str, List[str]] = {}

    def add_var(self, var: str, domain: List[str], parents: List[str]):
        self.parents[var] = parents[:]
        self.domain[var] = domain[:]
        # actualizar hijos
        for p in parents:
            self.children.setdefault(p, []).append(var)
        self.children.setdefault(var, [])

    def markov_blanket(self, var: str) -> Set[str]:
        """
        Manto de Markov de 'var' = Padres(var) ∪ Hijos(var) ∪ (Padres de los hijos de var, excluyendo var)
        """
        mb: Set[str] = set()
        # padres
        mb.update(self.parents.get(var, []))
        # hijos
        hijos = self.children.get(var, [])
        mb.update(hijos)
        # co-padres (spouses)
        for h in hijos:
            for p in self.parents.get(h, []):
                if p != var:
                    mb.add(p)
        return mb

    def others_outside_blanket(self, var: str) -> Set[str]:
        """Variables fuera del manto (ni el propio var)."""
        all_vars = set(self.parents.keys())
        return all_vars - self.markov_blanket(var) - {var}

def tron_bn_structure() -> BayesNet:
    bn = BayesNet()
    # Estructura:
    # Power → Gate, Sensor
    # Gate  → SafePath
    bn.add_var("Power",    ["Good", "Bad"],          parents=[])
    bn.add_var("Gate",     ["Open", "Closed"],       parents=["Power"])
    bn.add_var("Sensor",   ["OK", "Alert"],          parents=["Power"])
    bn.add_var("SafePath", ["Yes", "No"],            parents=["Gate"])
    return bn

def demo():
    bn = tron_bn_structure()
    consultas = ["Power", "Gate", "Sensor", "SafePath"]
    for v in consultas:
        mb = bn.markov_blanket(v)
        fuera = bn.others_outside_blanket(v)
        print(f"Variable: {v}")
        print(f"  Manto de Markov: {sorted(mb)}")
        print(f"  Fuera del manto (candidatos a independizarse dado MB): {sorted(fuera)}\n")

if __name__ == "__main__":
    demo()