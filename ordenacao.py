def indice_prioridade(barreira, pesos=None):
    """
    Calcula e retorna o índice de prioridade via fórmula beneficio / (custo / 1000).
    A regra do benefício combina 'gravidade', 'pessoas_dia' e deve possuir
    uma regra de desempate predefinida baseada em pequenos incrementos.
    """
    if pesos is None:
        pesos = {"gravidade": 1.0, "pessoas_dia": 1.0}

    try:
        gravidade = float(barreira.get("gravidade", 1.0))
        pessoas = float(barreira.get("pessoas_dia", 1.0))
        custo = float(barreira.get("custo", 0.0))

        # Evita divisão por zero
        if custo <= 0:
            # Se for zero, o custo na formula fica como um valor muito pequeno
            custo = 0.01

        beneficio_base = (gravidade * pesos.get("gravidade", 1.0)) * (pessoas * pesos.get("pessoas_dia", 1.0))

        # Desempate predefinido:
        # Adiciona um incremento minúsculo baseado na gravidade e no inverso do custo,
        # garantindo que problemas mais graves e mais baratos ganhem prioridade em caso de empate
        desempate = (gravidade * 0.0001) + (1.0 / custo * 0.00001)

        beneficio_total = beneficio_base + desempate

        indice = beneficio_total / (custo / 1000.0)
        return indice

    except ValueError:
        return 0.0

def calcular_indices(lista, pesos=None):
    """
    Grava o índice calculado em cada dicionário da lista de registros.
    """
    for barreira in lista:
        indice = indice_prioridade(barreira, pesos)
        barreira["indice"] = indice

def bubble_sort(lista, chave="indice", crescente=False):
    """
    Implemente este algoritmo operando sobre uma cópia da lista e retornando
    obrigatoriamente a tupla: (lista_ordenada, comparacoes, trocas).
    Sem usar sorted() ou list.sort().
    """
    # Cria copia manual
    lista_copia = []
    for item in lista:
        lista_copia.append(item)

    n = 0
    for _ in lista_copia:
        n += 1

    comparacoes = 0
    trocas = 0

    for i in range(n):
        trocou = False
        # Últimos i elementos já estão no lugar
        for j in range(0, n - i - 1):
            comparacoes += 1

            valor_j = lista_copia[j].get(chave, 0)
            valor_proximo = lista_copia[j + 1].get(chave, 0)

            # Condição de troca
            precisa_trocar = False
            if crescente:
                if valor_j > valor_proximo:
                    precisa_trocar = True
            else:
                # Decrescente (maior para o menor)
                if valor_j < valor_proximo:
                    precisa_trocar = True

            if precisa_trocar:
                trocas += 1
                # Troca os elementos
                temp = lista_copia[j]
                lista_copia[j] = lista_copia[j+1]
                lista_copia[j+1] = temp
                trocou = True

        # Se nenhuma troca ocorreu nesta passagem, a lista já está ordenada
        if not trocou:
            break

    return (lista_copia, comparacoes, trocas)
