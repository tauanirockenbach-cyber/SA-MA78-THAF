# Arquivo principal do sistema.
# Responsável por exibir o menu principal e direcionar o usuário
# para o módulo correspondente à opção escolhida.

# Importa a função responsável pelo menu de Setores
from setor import opcao_desejada_setor

# Importa a função responsável pelo menu de Usuários
from usuario import opcao_desejada_usuario

# Importa a função responsável pelo menu de EPIs
from epi import opcao_desejada_epi

# Importa a função responsável pelo menu de Máquinas
from maquinas import opcao_desejada_maq

# Importa a função responsável pelo menu de Modelos de Máquinas
from maquinas import opcao_desejada_mod

# Importa a função responsável pelo menu de Peças
from pecas import opcao_desejada_peca

# Importa a função responsável pelo menu de Ordens de Serviço
from OS import opcao_desejada_manutencao

# Importa a função responsável pelo menu de Ferramentas
from ferramentas import opcao_desejada_ferramenta

# Importa a função responsável pelo menu de Movimentação de Ferramentas
from mov_ferramentas import opcao_desejada_movimentacao


# Mantém o menu principal em execução até que o usuário escolha sair
while True:

    # Exibe o logotipo do sistema em ASCII Art
    print("""

      ██████╗ ███████╗███╗   ███╗    ██╗   ██╗██╗███╗   ██╗██████╗  ██████╗ 
      ██╔══██╗██╔════╝████╗ ████║    ██║   ██║██║████╗  ██║██╔══██╗██╔═══██╗
      ██████╔╝█████╗  ██╔████╔██║    ██║   ██║██║██╔██╗ ██║██║  ██║██║   ██║
      ██╔══██╗██╔══╝  ██║╚██╔╝██║    ╚██╗ ██╔╝██║██║╚██╗██║██║  ██║██║   ██║
      ██████╔╝███████╗██║ ╚═╝ ██║     ╚████╔╝ ██║██║ ╚████║██████╔╝╚██████╔╝
      ╚═════╝ ╚══════╝╚═╝     ╚═╝      ╚═══╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  

      """)

    # Apenas uma linha em branco para melhorar a organização visual
    print("\n")

    # Exibe o menu principal do sistema
    print("------Menu Geral------")
    print("1 - Setor Menu")
    print("2 - Usuario Menu")
    print("3 - Epi Menu")
    print("4 - Maquinas Menu")
    print("5 - Modelo Maquina Menu")
    print("6 - Pecas Menu")
    print("7 - OS Menu")
    print("8 - Ferramentas")
    print("9 - Movimentação de ferramentas Menu")
    print("0 - Sair")

    # Lê a opção escolhida pelo usuário
    opcao = int(input("Coloque qual opção deseja: "))

    # Direciona para o menu de Setores
    if opcao == 1:
        opcao_desejada_setor()

    # Direciona para o menu de Usuários
    elif opcao == 2:
        opcao_desejada_usuario()

    # Direciona para o menu de EPIs
    elif opcao == 3:
        opcao_desejada_epi()

    # Direciona para o menu de Máquinas
    elif opcao == 4:
        opcao_desejada_maq()

    # Direciona para o menu de Modelos de Máquinas
    elif opcao == 5:
        opcao_desejada_mod()

    # Direciona para o menu de Peças
    elif opcao == 6:
        opcao_desejada_peca()

    # Direciona para o menu de Ordens de Serviço
    elif opcao == 7:
        opcao_desejada_manutencao()

    # Direciona para o menu de Ferramentas
    elif opcao == 8:
        opcao_desejada_ferramenta()

    # Direciona para o menu de Movimentação de Ferramentas
    elif opcao == 9:
        opcao_desejada_movimentacao()

    # Encerra a execução do sistema
    elif opcao == 0:
        print("Tchau!")
        break

    # Caso o usuário digite uma opção inexistente
    else:
        print("Opção inválida!")