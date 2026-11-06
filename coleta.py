import json
import os

def _contem(lista, item):
    """Verifica se um item está na lista iterativamente, evitando o operador 'in'"""
    if lista is None:
        return False
    for elemento in lista:
        if elemento == item:
            return True
    return False

def _chaves_ausentes(dicionario, chaves_obrigatorias):
    """Retorna lista de chaves obrigatorias que estao ausentes"""
    ausentes = []
    chaves_dict = dicionario.keys()
    for chave in chaves_obrigatorias:
        if not _contem(chaves_dict, chave):
            ausentes.append(chave)
    return ausentes

def validar_registro(barreira, codigos_usados=None):
    """
    Devolve uma lista de problemas (vazia se for válido) conferindo campos ausentes,
    código repetido, gravidade (apenas 1 a 5), custo zero ou negativo e medida negativa.
    """
    problemas = []

    if codigos_usados is None:
        codigos_usados = []

    chaves_obrigatorias = [
        "codigo", "ambiente", "tipo", "descricao", "medida", "unidade",
        "referencia_norma", "gravidade", "pessoas_dia", "custo",
        "intervencao", "coletado_por", "data_coleta"
    ]

    # Verifica campos ausentes
    ausentes = _chaves_ausentes(barreira, chaves_obrigatorias)
    if ausentes:
        str_ausentes = ""
        for i in range(len(ausentes)):
            str_ausentes += ausentes[i]
            if i < len(ausentes) - 1:
                str_ausentes += ", "
        problemas.append(f"Campos ausentes: {str_ausentes}")
        return problemas # Se faltam chaves, nem tenta validar o resto para nao dar KeyError

    # Verifica código repetido
    if _contem(codigos_usados, barreira["codigo"]):
        problemas.append(f"Código repetido: {barreira['codigo']}")

    # Verifica gravidade (1 a 5)
    try:
        gravidade = int(barreira["gravidade"])
        if gravidade < 1 or gravidade > 5:
            problemas.append(f"Gravidade inválida: {gravidade} (deve ser de 1 a 5)")
    except ValueError:
        problemas.append(f"Gravidade inválida: não é um número ({barreira['gravidade']})")

    # Verifica custo
    try:
        custo = float(barreira["custo"])
        if custo <= 0:
            problemas.append(f"Custo zero ou negativo: {custo}")
    except ValueError:
        problemas.append(f"Custo inválido: não é um número ({barreira['custo']})")

    # Verifica medida
    try:
        medida = float(barreira["medida"])
        if medida < 0:
            problemas.append(f"Medida negativa: {medida}")
    except ValueError:
        problemas.append(f"Medida inválida: não é um número ({barreira['medida']})")

    return problemas

def validar_setor(no, codigos=None):
    """
    Valida todas as barreiras da árvore recursivamente.
    Retorna um dicionario mapeando os codigos das barreiras para suas listas de problemas,
    somente se houver problemas.
    """
    if codigos is None:
        codigos = []

    todos_problemas = {}

    # Valida barreiras no nível atual
    if "barreiras" in no:
        for barreira in no["barreiras"]:
            problemas = validar_registro(barreira, codigos)

            # Adiciona codigo aos usados para checagem futura (mesmo se houver erro)
            codigo = barreira.get("codigo", "DESCONHECIDO")
            if codigo != "DESCONHECIDO":
                codigos.append(codigo)

            if problemas:
                todos_problemas[codigo] = problemas

    # Valida recursivamente nos subsetores
    if "subsetores" in no:
        for subsetor in no["subsetores"]:
            problemas_subsetor = validar_setor(subsetor, codigos)
            for cod, probs in problemas_subsetor.items():
                todos_problemas[cod] = probs

    return todos_problemas

def _dividir_string(texto, separador=";"):
    """
    Divide uma string iterativamente com base em um separador sem usar split().
    """
    partes = []
    atual = ""
    i = 0
    tamanho_sep = 0
    for _ in separador:
        tamanho_sep += 1

    tamanho_texto = 0
    for _ in texto:
        tamanho_texto += 1

    while i < tamanho_texto:
        fatia = ""
        for j in range(tamanho_sep):
            if i + j < tamanho_texto:
                fatia += texto[i+j]

        if fatia == separador:
            partes.append(atual)
            atual = ""
            i += tamanho_sep
        else:
            atual += texto[i]
            i += 1
    partes.append(atual)
    return partes

def importar_ficha_campo(caminho):
    """
    Lê o arquivo da ficha separado por ponto e vírgula e retorna (registros, erros).
    """
    registros = []
    erros = []

    if not os.path.exists(caminho):
        erros.append(f"Arquivo não encontrado: {caminho}")
        return registros, erros

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        if not linhas:
            erros.append("Arquivo vazio")
            return registros, erros

        # Pega cabeçalho
        linha_cabecalho = linhas[0].strip('\n').strip()
        cabecalho = _dividir_string(linha_cabecalho, ";")

        # Lê cada linha
        for i in range(1, len(linhas)):
            linha = linhas[i].strip('\n').strip()
            if not linha:
                continue

            valores = _dividir_string(linha, ";")

            if len(valores) != len(cabecalho):
                erros.append(f"Linha {i+1} tem um número incorreto de colunas: esperava {len(cabecalho)}, obteve {len(valores)}")
                continue

            registro = {}
            for j in range(len(cabecalho)):
                chave = cabecalho[j]
                valor = valores[j]

                # Conversão de tipos básicos baseada nos dados conhecidos (tentativa)
                if chave in ["gravidade", "pessoas_dia"]:
                    try:
                        valor = int(valor)
                    except:
                        pass
                elif chave in ["custo", "medida"]:
                    try:
                        valor = float(valor)
                    except:
                        pass

                registro[chave] = valor

            registros.append(registro)

    except Exception as e:
        erros.append(f"Erro ao ler arquivo: {str(e)}")

    return registros, erros

def gravar_inventario(caminho, setor):
    """
    Faz a persistência do inventário em arquivo JSON.
    """
    try:
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(setor, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao gravar inventário: {e}")
        return False

def ler_inventario(caminho):
    """
    Lê a persistência do inventário em arquivo JSON.
    """
    if not os.path.exists(caminho):
        return None

    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler inventário: {e}")
        return None

def construir_arvore(registros):
    """
    Constrói a árvore hierárquica a partir da lista plana de registros,
    utilizando a coluna "caminho" (ex: "Academia > Receção e Espera > Entrada").
    """
    arvore = {"nome": "Raiz", "barreiras": [], "subsetores": []}

    for registro in registros:
        # A chave de caminho baseada no txt fornecido
        caminho_str = registro.get("caminho", "Desconhecido")
        partes_caminho = _dividir_string(caminho_str, " > ")

        # Remove a chave caminho se quiser limpar, mas podemos deixar
        # O prompt diz "gravando a string do caminho hierárquico dentro de cada registro" depois em achatar
        # então é melhor manter o original como veio do txt ou remover e deixar que `achatar` grave.
        # Vou apenas usar para construir a árvore.

        no_atual = arvore

        # Percorre as partes do caminho para descer na arvore ou criar nós
        for i in range(len(partes_caminho)):
            parte = partes_caminho[i]

            # Atualiza o nome da raiz se for o primeiro nível (ex: Academia)
            if i == 0 and no_atual["nome"] == "Raiz":
                no_atual["nome"] = parte

            # Se não é o último nível, precisamos ir mais fundo
            if i < len(partes_caminho) - 1:
                proxima_parte = partes_caminho[i+1]

                # Procura se o proximo no ja existe nos subsetores
                encontrou = False
                for sub in no_atual["subsetores"]:
                    if sub["nome"] == proxima_parte:
                        no_atual = sub
                        encontrou = True
                        break

                # Se não encontrou, cria um novo
                if not encontrou:
                    novo_no = {"nome": proxima_parte, "barreiras": [], "subsetores": []}
                    no_atual["subsetores"].append(novo_no)
                    no_atual = novo_no
            else:
                # É o último nível do caminho, adiciona a barreira aqui
                no_atual["barreiras"].append(registro)

    return arvore
