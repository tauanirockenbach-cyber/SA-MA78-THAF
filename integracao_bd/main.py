# Arquivo principal responsável por exibir o menu interativo e controlar o fluxo do sistema.
from setor import opcao_desejada_setor
from usuario import opcao_desejada_usuario
from epi import opcao_desejada_epi
from maquinas import opcao_desejada_maq
from maquinas import opcao_desejada_mod
from pecas import opcao_desejada_peca
from OS import opcao_desejada_manutencao
from ferramentas import opcao_desejada_ferramenta
from mov_ferramentas import opcao_desejada_movimentacao

while True:
    print("""

      ██████╗ ███████╗███╗   ███╗    ██╗   ██╗██╗███╗   ██╗██████╗  ██████╗ 
      ██╔══██╗██╔════╝████╗ ████║    ██║   ██║██║████╗  ██║██╔══██╗██╔═══██╗
      ██████╔╝█████╗  ██╔████╔██║    ██║   ██║██║██╔██╗ ██║██║  ██║██║   ██║
      ██╔══██╗██╔══╝  ██║╚██╔╝██║    ╚██╗ ██╔╝██║██║╚██╗██║██║  ██║██║   ██║
      ██████╔╝███████╗██║ ╚═╝ ██║     ╚████╔╝ ██║██║ ╚████║██████╔╝╚██████╔╝
      ╚═════╝ ╚══════╝╚═╝     ╚═╝      ╚═══╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝  
      """)
    print("\n")
    print("------Menu Geral------")
    print("Setor Menu = 1")
    print("Usuario Menu = 2")
    print("Epi Menu = 3")
    print("Maquinas Menu = 4")
    print("Modelo Maquina Menu = 5")
    print("Pecas Menu = 6")
    print("OS Menu = 7")
    print("Ferramentas = 8")
    print("Movimentação de ferramentas Menu = 9")
    
    print("Sair = 0")

    opcao = int(input("Coloque qual opção deseja: "))

    if opcao == 1:
        opcao_desejada_setor()
    elif opcao == 2:
        opcao_desejada_usuario()
    elif opcao == 3:
        opcao_desejada_epi()
    elif opcao == 4:
        opcao_desejada_maq()
    elif opcao == 5:
        opcao_desejada_mod()
    elif opcao == 6:
        opcao_desejada_peca()
    elif opcao == 7:
        opcao_desejada_manutencao()
    elif opcao == 8:
        opcao_desejada_ferramenta()
    elif opcao == 9:
        opcao_desejada_movimentacao()

    elif opcao == 0:
        print("Tchau!")
        break
    else: 
        print("Opção inválida!")