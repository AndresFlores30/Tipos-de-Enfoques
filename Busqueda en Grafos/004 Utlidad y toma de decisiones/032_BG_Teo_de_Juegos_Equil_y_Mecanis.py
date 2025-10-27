# Teoría de Juegos en TRON: Equilibrios y Mecanismos
# - Juego 2x2: mejores respuestas, Nash puro y mixto
# - EIED: eliminación iterada de estrategias estrictamente dominadas
# - Mecanismo: Subasta Vickrey (segundo precio) para ancho de banda

from typing import List, Tuple, Dict, Optional

# ============================================================
# 1) Juego normal-forma 2x2 (Tron vs. Sark)
#    Acciones: Tron ∈ {Sector_Luz, Portal}
#              Sark ∈ {Arena, Firewall}
#    Payoffs: tuplas (u_Tron, u_Sark) por celda
# ============================================================

A_TRON = ["Sector_Luz", "Portal"]
A_SARK = ["Arena", "Firewall"]

# Matriz de pagos indexada como M[i][j] con i=Tron, j=Sark
# Los números están tematizados pero son arbitrariamente simples.
M: List[List[Tuple[float, float]]] = [
    # Sark: Arena           Firewall
    [( 4.0,  2.0),       ( 1.0,  3.0)      ],  # Tron: Sector_Luz
    [( 2.5,  1.0),       ( 3.0,  2.5)      ],  # Tron: Portal
]

def best_responses_2x2(M) -> Dict[str, List[Tuple[int,int]]]:
    """
    Devuelve perfiles donde cada jugador responde mejor (marcas de mejores respuestas).
    """
    br = {"Tron": [], "Sark": []}
    # Mejores respuestas de Tron contra cada columna j
    for j in range(2):
        vals = [M[i][j][0] for i in range(2)]  # utilidades de Tron
        best_i = [i for i in range(2) if vals[i] == max(vals)]
        for i in best_i:
            br["Tron"].append((i, j))
    # Mejores respuestas de Sark contra cada fila i
    for i in range(2):
        vals = [M[i][j][1] for j in range(2)]  # utilidades de Sark
        best_j = [j for j in range(2) if vals[j] == max(vals)]
        for j in best_j:
            br["Sark"].append((i, j))
    return br

def nash_puros_2x2(M) -> List[Tuple[int,int]]:
    br = best_responses_2x2(M)
    BR_T = set(br["Tron"])
    BR_S = set(br["Sark"])
    return sorted(list(BR_T.intersection(BR_S)))

def mixed_equilibrium_2x2(M) -> Tuple[float, float]:
    """
    Equilibrio mixto para 2x2 (si no hay puro único):
    p = P(Tron=Sector_Luz), q = P(Sark=Arena)
    Indiferencia:
      Tron: EU(Sector_Luz)=EU(Portal) dada q
      Sark: EU(Arena)=EU(Firewall) dada p
    """
    # Notación: M[i][j] = (uT, uS) con i∈{0:SL,1:P}, j∈{0:Arena,1:Firewall}
    # Tron indiferente:
    #   q*uT(SL,A) + (1-q)*uT(SL,F) = q*uT(P,A) + (1-q)*uT(P,F)
    uT_SL_A, uT_SL_F = M[0][0][0], M[0][1][0]
    uT_P_A,  uT_P_F  = M[1][0][0], M[1][1][0]
    num_q = uT_P_F - uT_SL_F
    den_q = (uT_SL_A - uT_SL_F) - (uT_P_A - uT_P_F)
    q = num_q / den_q if den_q != 0 else 0.5  # fallback simple

    # Sark indiferente:
    #   p*uS(SL,A) + (1-p)*uS(P,A) = p*uS(SL,F) + (1-p)*uS(P,F)
    uS_SL_A, uS_P_A  = M[0][0][1], M[1][0][1]
    uS_SL_F, uS_P_F  = M[0][1][1], M[1][1][1]
    num_p = uS_P_F - uS_P_A
    den_p = (uS_SL_A - uS_P_A) - (uS_SL_F - uS_P_F)
    p = num_p / den_p if den_p != 0 else 0.5

    # Proyectar a [0,1] por robustez
    p = max(0.0, min(1.0, p))
    q = max(0.0, min(1.0, q))
    return p, q

def imprimir_resultados_2x2():
    print("Juego TRON 2x2 (Tron filas, Sark columnas):")
    for i, row in enumerate(M):
        fila = " | ".join(f"{A_TRON[i]} vs {A_SARK[j]}: {cell}" for j, cell in enumerate(row))
        print("  " + fila)
    br = best_responses_2x2(M)
    nash = nash_puros_2x2(M)
    print("\nMejores respuestas de Tron:", br["Tron"])
    print("Mejores respuestas de Sark:", br["Sark"])
    print("Nash puros:", [(A_TRON[i], A_SARK[j]) for (i,j) in nash])
    if not nash:
        p, q = mixed_equilibrium_2x2(M)
        print(f"Equilibrio mixto aproximado: p=Pr(Tron=Sector_Luz)={p:.3f}, q=Pr(Sark=Arena)={q:.3f}")

# ============================================================
# 2) EIED: Eliminación iterada de estrategias estrictamente dominadas
#    Versión sencilla para matriz m×n de pagos de TRON (jugador 1) y SARK (jugador 2).
# ============================================================

def eied(payoff_T: List[List[float]], payoff_S: List[List[float]],
         acts_T: List[str], acts_S: List[str]) -> Tuple[List[str], List[str]]:
    """
    Elimina estrategias estrictamente dominadas hasta alcanzar un conjunto reducido.
    Regresa (acts_T_reducidas, acts_S_reducidas).
    """
    rows = list(range(len(acts_T)))
    cols = list(range(len(acts_S)))
    changed = True
    while changed:
        changed = False
        # Dominancia para Tron (por filas)
        to_remove = set()
        for i in rows:
            for k in rows:
                if i == k: continue
                # k domina estrictamente a i si payoff_T[k][j] > payoff_T[i][j] para todo j en cols
                if all(payoff_T[k][j] > payoff_T[i][j] for j in cols):
                    to_remove.add(i)
                    break
        if to_remove:
            rows = [i for i in rows if i not in to_remove]
            changed = True

        # Dominancia para Sark (por columnas)
        to_remove = set()
        for j in cols:
            for l in cols:
                if j == l: continue
                # l domina estrictamente a j si payoff_S[i][l] > payoff_S[i][j] para todo i en rows
                if all(payoff_S[i][l] > payoff_S[i][j] for i in rows):
                    to_remove.add(j)
                    break
        if to_remove:
            cols = [j for j in cols if j not in to_remove]
            changed = True

    actsT_red = [acts_T[i] for i in rows]
    actsS_red = [acts_S[j] for j in cols]
    return actsT_red, actsS_red

def demo_eied():
    # Juego 3x3 simple (valores inventados)
    actsT = ["Sector_Luz", "Portal", "Arena"]
    actsS = ["Firewall", "BloqueoIO", "Cebado"]
    T = [
        [3, 2, 1],
        [4, 1, 0],
        [2, 2, 2],
    ]
    S = [
        [1, 4, 3],
        [0, 2, 1],
        [1, 3, 2],
    ]
    redT, redS = eied(T, S, actsT, actsS)
    print("\nEIED (estricta):")
    print("  Tron reduce a:", redT)
    print("  Sark reduce a:", redS)

# ============================================================
# 3) Mecanismo TRON: Subasta de Segundo Precio (Vickrey)
#    Bien: “ancho de banda” único del Grid.
#    Propiedad: decir la verdad es estrategia débilmente dominante.
# ============================================================

def vickrey_winner(bids: Dict[str, float]) -> Tuple[str, float]:
    """
    Regresa (ganador, precio_pagado) donde el precio es la 2ª oferta más alta.
    """
    orden = sorted(bids.items(), key=lambda kv: kv[1], reverse=True)
    ganador, bmax = orden[0]
    precio = orden[1][1] if len(orden) > 1 else 0.0
    return ganador, precio

def demo_vickrey():
    # Valoraciones privadas (no observables) y pujas (bids)
    valuations = {
        "Tron":  120.0,
        "Sark":   95.0,
        "CLU":   110.0,
    }
    # Caso 1: todos sinceros
    bids_truth = valuations.copy()
    w1, p1 = vickrey_winner(bids_truth)
    print("\nVickrey — todos sinceros:")
    print("  ganador:", w1, "precio:", p1)

    # Caso 2: Tron intenta inflar (no mejora utilidad si ya ganaba)
    bids_lie = {"Tron": 200.0, "Sark": 95.0, "CLU": 110.0}
    w2, p2 = vickrey_winner(bids_lie)
    print("Vickrey — Tron infla su puja:")
    print("  ganador:", w2, "precio:", p2)

    # Utilidad del ganador = valoración - precio (si gana), 0 si pierde
    def utilidad(nombre, w, precio, vals, bids):
        return (vals[nombre] - precio) if nombre == w else 0.0

    u1_tron = utilidad("Tron", w1, p1, valuations, bids_truth)
    u2_tron = utilidad("Tron", w2, p2, valuations, bids_lie)
    print(f"Utilidad Tron sincero: {u1_tron:.1f}  vs  mintiendo: {u2_tron:.1f}")

# ============================================================
# Demo principal
# ============================================================

def main():
    imprimir_resultados_2x2()
    demo_eied()
    demo_vickrey()

if __name__ == "__main__":
    main()