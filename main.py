import os
from coleta import (
    importar_ficha_campo,
    validar_registro,
    validar_setor,
    gravar_inventario,
    ler_inventario,
    construir_arvore
)
from recursao import (
    custo_total,
    contar_barreiras,
    contar_por_tipo,
    profundidade,
    achatar,
    caminho_da_barreira,
    resumo_hierarquico,
    melhor_pacote_exaustivo
)
from ordenacao import (
    calcular_indices,
    bubble_sort
)

def menu():
    print("\n--- MENU: CAMPUS ACESSÍVEL ---")
    print("1. Importar dados, validar e exibir resumo")
    print("2. Gerar ranking de prioridade (E3)")
    print("3. Executar tudo (Checkpoint 1 completo)")
    print("0. Sair")
    opcao = input("Escolha uma opção: ")
    return opcao

def main():
    # Usando o arquivo da academia fornecido
    caminho_txt = "ficha_de_campo.txt"
    caminho_json = "inventario_academia.json"

    while True:
        opcao = menu()

        if opcao == "0":
            break

        elif opcao in ["1", "3"]:
            print(f"\n[1] Importando dados de: {caminho_txt}")
            registros, erros_importacao = importar_ficha_campo(caminho_txt)
            if erros_importacao:
                print("Erros de importação:")
                for erro in erros_importacao:
                    print(f" - {erro}")

            print(f"\nTotal de registros importados: {len(registros)}")

            print("\n[2] Construindo árvore hierárquica...")
            arvore = construir_arvore(registros)

            print("\n[3] Validando setor...")
            problemas = validar_setor(arvore)
            if problemas:
                print("Problemas encontrados na validação:")
                for cod, probs in problemas.items():
                    print(f" - Barreira {cod}:")
                    for p in probs:
                        print(f"   * {p}")
            else:
                print("Validação concluída: 0 erros.")

            print(f"\n[4] Gravando inventário em {caminho_json}...")
            if gravar_inventario(caminho_json, arvore):
                print("Inventário gravado com sucesso.")

            print("\n[5] Resumo Hierárquico do Campus:")
            print("===========================================")
            resumo_hierarquico(arvore)
            print("===========================================")

            # Print additional info from recursao
            print(f"\nCusto total do campus: R$ {custo_total(arvore):.2f}")
            print(f"Total de barreiras: {contar_barreiras(arvore)}")
            print(f"Profundidade da árvore: {profundidade(arvore)}")

        if opcao in ["2", "3"]:
            # Só faz sentido se tivermos a arvore construída. Se opcao for 2 e nao tem arvore, lemos do json.
            arvore = ler_inventario(caminho_json)
            if arvore is None:
                print("Inventário não encontrado. Execute a opção 1 primeiro.")
                continue

            print("\n[6] Achatando árvore para gerar ranking...")
            lista_plana = achatar(arvore)

            print("\n[7] Calculando índices de prioridade...")
            pesos = {"gravidade": 1.0, "pessoas_dia": 1.0}
            calcular_indices(lista_plana, pesos)

            print("\n[8] Ordenando barreiras (Bubble Sort)...")
            # Queremos a maior prioridade primeiro (decrescente)
            lista_ordenada, comparacoes, trocas = bubble_sort(lista_plana, chave="indice", crescente=False)

            print(f"Ordenação concluída com {comparacoes} comparações e {trocas} trocas.")
            print("\n--- RANKING DE PRIORIDADE (Top 10) ---")

            # Print the top ones (or all if < 10), avoid built ins max/min/len if strict, but len is ok for print logic
            # Using procedural loops
            limite = 10
            count = 0
            for b in lista_ordenada:
                if count >= limite:
                    break
                cod = b.get("codigo", "N/A")
                ind = b.get("indice", 0.0)
                custo = b.get("custo", 0.0)
                cam = b.get("caminho_hierarquico", "")
                print(f"{count+1}. [{cod}] Índice: {ind:.2f} | Custo: R$ {custo:.2f} | Caminho: {cam}")
                count += 1

        if opcao == "3":
            print("\n[9] Testando algoritmo exaustivo (Orçamento: R$ 2000.00)...")
            orcamento = 2000.00
            # Precisamos de uma lista menor para o exaustivo não estourar.
            # A lista de academia tem 15 registros. 2^15 = 32768 combinações, que é rápido o suficiente.
            contador = [0]
            melhor_pacote = melhor_pacote_exaustivo(lista_plana, orcamento, pesos, 0, contador)

            soma_beneficios = 0
            soma_custos = 0.0
            print(f"\nMelhor pacote encontrado (exploradas {contador[0]} combinações):")
            for b in melhor_pacote:
                cod = b.get("codigo", "N/A")
                custo = b.get("custo", 0.0)
                grav = int(b.get("gravidade", 1))
                pesos_dia = int(b.get("pessoas_dia", 1))
                beneficio = grav * pesos_dia
                soma_beneficios += beneficio
                soma_custos += custo
                print(f" - {cod} (Custo: R$ {custo:.2f})")

            print(f"Total Custo: R$ {soma_custos:.2f} | Total Benefício: {soma_beneficios}")

if __name__ == "__main__":
    main()
