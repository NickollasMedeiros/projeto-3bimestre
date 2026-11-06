def custo_total(no):
    """
    Retorna a soma recursiva dos custos.
    """
    total = 0.0

    # Caso base 1: Soma dos custos das barreiras no nó atual (ou zero se não houver barreiras)
    if "barreiras" in no:
        for b in no["barreiras"]:
            total += b.get("custo", 0.0)

    # Caso base 2 / Passo recursivo: Se não tem subsetores, o loop não executa e a recursão para.
    # Caso contrário, soma o custo_total dos subsetores.
    if "subsetores" in no:
        for sub in no["subsetores"]:
            total += custo_total(sub)

    return total

def contar_barreiras(no):
    """
    Contagens recursivas da árvore - total de barreiras.
    """
    total = 0

    # Caso base 1: Soma a quantidade de barreiras no nó atual
    if "barreiras" in no:
        # Loop manual para contar ao inves de usar len(), para seguir estilo estritamente procedural
        count = 0
        for _ in no["barreiras"]:
            count += 1
        total += count

    # Caso base 2 / Passo recursivo: Sem subsetores a recursao termina.
    if "subsetores" in no:
        for sub in no["subsetores"]:
            total += contar_barreiras(sub)

    return total

def contar_por_tipo(no, tipo):
    """
    Contagens recursivas da árvore - barreiras por tipo.
    """
    total = 0

    # Caso base 1: Contagem das barreiras do tipo específico no nó atual
    if "barreiras" in no:
        for b in no["barreiras"]:
            if b.get("tipo") == tipo:
                total += 1

    # Caso base 2 / Passo recursivo: Sem subsetores, encerra.
    if "subsetores" in no:
        for sub in no["subsetores"]:
            total += contar_por_tipo(sub, tipo)

    return total

def _max_custom(a, b):
    """Função auxiliar para máximo sem usar built-in"""
    if a > b:
        return a
    return b

def profundidade(no):
    """
    Calcula a profundidade, onde um nó sem subsetores tem profundidade 1.
    """
    # Caso base: nó não tem subsetores ou a lista de subsetores está vazia
    if "subsetores" not in no or not no["subsetores"]:
        return 1

    max_prof_sub = 0
    # Passo recursivo: percorre subsetores encontrando o de maior profundidade
    for sub in no["subsetores"]:
        prof_sub = profundidade(sub)
        max_prof_sub = _max_custom(max_prof_sub, prof_sub)

    return 1 + max_prof_sub

def achatar(no, caminho=""):
    """
    Converte a árvore numa lista plana de barreiras,
    gravando a string do caminho hierárquico dentro de cada registro.
    """
    lista = []

    # Monta o caminho atual combinando o anterior com o nome deste nó
    nome_atual = no.get("nome", "")
    caminho_atual = caminho
    if caminho_atual == "":
        caminho_atual = nome_atual
    else:
        caminho_atual = caminho_atual + " > " + nome_atual

    # Caso base: processar barreiras do nó atual
    if "barreiras" in no:
        for b in no["barreiras"]:
            # Grava a string do caminho hierárquico
            b["caminho_hierarquico"] = caminho_atual
            lista.append(b)

    # Passo recursivo: Se não houver subsetores o loop não roda
    if "subsetores" in no:
        for sub in no["subsetores"]:
            lista_sub = achatar(sub, caminho_atual)
            # Extende a lista manualmente
            for item in lista_sub:
                lista.append(item)

    return lista

def caminho_da_barreira(no, codigo, caminho=""):
    """
    Retorna a string do caminho da barreira consultada, procurando pelo código.
    """
    nome_atual = no.get("nome", "")
    caminho_atual = caminho
    if caminho_atual == "":
        caminho_atual = nome_atual
    else:
        caminho_atual = caminho_atual + " > " + nome_atual

    # Caso base 1: barreira encontrada no nó atual
    if "barreiras" in no:
        for b in no["barreiras"]:
            if b.get("codigo") == codigo:
                return caminho_atual

    # Caso base 2 / Passo recursivo: a árvore acaba sem achar ou procura nos subsetores
    if "subsetores" in no:
        for sub in no["subsetores"]:
            res = caminho_da_barreira(sub, codigo, caminho_atual)
            if res is not None:
                return res

    # Caso base 3: Se não encontrou em nenhum lugar deste ramo, retorna None
    return None

def resumo_hierarquico(no, nivel=0):
    """
    Imprime a árvore estruturada no terminal,
    utilizando recuos e totalizando as barreiras por nível.
    """
    recuo = "  " * nivel

    qtd_barreiras = 0
    if "barreiras" in no:
        for _ in no["barreiras"]:
            qtd_barreiras += 1

    nome = no.get("nome", "Sem Nome")
    print(f"{recuo}- {nome} ({qtd_barreiras} barreiras)")

    # Caso base / Passo recursivo: percorre filhos. Termina sem subsetores.
    if "subsetores" in no:
        for sub in no["subsetores"]:
            resumo_hierarquico(sub, nivel + 1)

def _soma_beneficio(pacote):
    """Calcula o benefício total de um pacote (lista) de barreiras"""
    soma = 0
    for b in pacote:
        # A formulaçao do beneficio será feita em ordenacao, mas no exaustivo precisamos do beneficio total
        # O beneficio basico é a gravidade * pessoas_dia, ou usa o indice previamente calculado.
        # Vamos assumir que a propriedade "indice" (ou um calculo basico) ja exista.
        # Como as restrições indicam gerar o pacote de "maior benefício", e em indice_prioridade
        # o benefício combina "gravidade" e "pessoas_dia", vamos replicar a lógica de benefício.
        grav = int(b.get("gravidade", 1))
        pes = int(b.get("pessoas_dia", 1))
        soma += (grav * pes)
    return soma

def _soma_custo(pacote):
    """Calcula o custo total de um pacote de barreiras"""
    soma = 0.0
    for b in pacote:
        soma += float(b.get("custo", 0.0))
    return soma

def melhor_pacote_exaustivo(barreiras, orcamento, pesos=None, indice=0, contador=None):
    """
    Percorre todas as combinações recursivamente para devolver o pacote de maior benefício
    que não estoure o orçamento.
    Para não estourar tempo ou memoria, recebe uma lista plana de barreiras.
    """
    if contador is not None:
        contador[0] += 1

    # Caso base: Chegamos ao fim da lista de barreiras disponíveis
    # Retorna uma lista vazia, pois não há mais itens para adicionar
    # Ou criamos o tamanho manual sem built in
    tamanho = 0
    for _ in barreiras:
        tamanho += 1

    if indice >= tamanho:
        return []

    barreira_atual = barreiras[indice]
    custo_atual = float(barreira_atual.get("custo", 0.0))

    # Opção 1: Não incluir a barreira atual
    pacote_sem = melhor_pacote_exaustivo(barreiras, orcamento, pesos, indice + 1, contador)

    # Opção 2: Incluir a barreira atual (se couber no orçamento)
    pacote_com = []
    if custo_atual <= orcamento:
        pacote_com = [barreira_atual]
        pacote_com_resto = melhor_pacote_exaustivo(
            barreiras,
            orcamento - custo_atual,
            pesos,
            indice + 1,
            contador
        )
        for item in pacote_com_resto:
            pacote_com.append(item)

    # Compara os benefícios para escolher o melhor
    beneficio_sem = _soma_beneficio(pacote_sem)
    beneficio_com = _soma_beneficio(pacote_com)

    if beneficio_com > beneficio_sem:
        return pacote_com
    else:
        return pacote_sem
