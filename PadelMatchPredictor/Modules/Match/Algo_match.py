from Modules.Match.match_result import MatchState

def probability_match(estado: MatchState):
    """
    Retorna (IfWin, IfLoss) según la lógica básica:
      - (t1_sets,t2_sets) = (0,0) => (0.75, 0.25)
      - (1,0) => (1.0, 0.50)
      - (0,1) => (0.50, 0.0)
      - (1,1) => (1.0, 0.0)
      - cualquier otro => (0.0, 0.0)
    """

    t1 = estado.t1_sets
    t2 = estado.t2_sets

    # 0-0 => (0.75, 0.25)
    if t1 == 0 and t2 == 0:
        return (0.75, 0.25)

    # 1-0 => (1.0, 0.50)
    elif t1 == 1 and t2 == 0:
        return (1.0, 0.50)

    # 0-1 => (0.50, 0.0)
    elif t1 == 0 and t2 == 1:
        return (0.50, 0.0)

    # 1-1 => (1.0, 0.0)
    elif t1 == 1 and t2 == 1:
        return (1.0, 0.0)

    # Cualquier otro => (0.0, 0.0)
    return (0.0, 0.0)


# Ejemplo de uso
if __name__=="__main__":
    # Importando supuestamente desde match_result ya está,
    # creamos varios estados y los probamos
    """
    # Caso 0-0
    s1 = MatchState(0,0,0,0,0,0,1)
    print("Estado (0,0):", probability_match(s1))  # (0.75, 0.25)

    # Caso 1-0
    s2 = MatchState(0,0,0,0,1,0,1)
    print("Estado (1,0):", probability_match(s2))  # (1.0, 0.50)

    # Caso 0-1
    s3 = MatchState(0,0,0,0,0,1,1)
    print("Estado (0,1):", probability_match(s3))  # (0.50, 0.0)

    # Caso 1-1
    s4 = MatchState(0,0,0,0,1,1,1)
    print("Estado (1,1):", probability_match(s4))  # (1.0, 0.0)

    # Otro (ej: 2-0)
    s5 = MatchState(0,0,0,0,2,0,1)
    print("Estado (2,0):", probability_match(s5))  # (0.0, 0.0)
    """