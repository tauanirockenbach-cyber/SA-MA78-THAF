from database import conectar
from datetime import datetime
import time


# -----------------------------------------------------------------------------
# Lê um número inteiro informado pelo usuário.
# Enquanto um valor inválido for digitado, solicita novamente.
# -----------------------------------------------------------------------------
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# -----------------------------------------------------------------------------
# Valida uma opção digitada pelo usuário comparando com uma lista de opções.
# -----------------------------------------------------------------------------
def ler_opcao_valida(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem)
        if valor.lower() in opcoes_validas:
            return valor
        print("Opção inválida!")


# -----------------------------------------------------------------------------
# Lista todos os usuários cadastrados no banco de dados.
# -----------------------------------------------------------------------------
def listar_usuario():
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta todos os dados da tabela Usuarios
        sql = """
        SELECT
            id_usuario, nome_usuario, email_usuario, cargo_usuario,
            status_usuario, nivel_experiencia, disponibilidade_tecnico,
            telefone_usuario, data_nasc_usuario,
            id_setor, data_cadastro
        FROM Usuarios
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        # Verifica se existem usuários cadastrados
        if not dados:
            print("Nenhum usuário cadastrado.")
            return

        # Exibe cada usuário encontrado
        for usuario in dados:
            print(usuario)

    except Exception as erro:
        print("Erro ao listar usuários:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# Cadastra um novo usuário.
# -----------------------------------------------------------------------------
def criar_usuario(nome_usuario, email_usuario, senha, cargo_usuario,
                  status_usuario, nivel_experiencia,
                  disponibilidade_tecnico, telefone_usuario,
                  data_nasc_usuario, id_setor, data_cadastro):

    conexao = None
    cursor = None

    try:
        # Conecta ao banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Insere um novo usuário na tabela Usuarios
        sql = """
        INSERT INTO Usuarios
            (nome_usuario, email_usuario, senha, cargo_usuario,
            status_usuario, nivel_experiencia,
            disponibilidade_tecnico, telefone_usuario,
            data_nasc_usuario, id_setor, data_cadastro)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            nome_usuario,
            email_usuario,
            senha,
            cargo_usuario,
            status_usuario,
            nivel_experiencia,
            disponibilidade_tecnico,
            telefone_usuario,
            data_nasc_usuario,
            id_setor,
            data_cadastro
        )

        cursor.execute(sql, valores)
        conexao.commit()

        print("Usuário cadastrado com sucesso!")

    except Exception as erro:
        # Cancela alterações caso ocorra erro
        if conexao:
            conexao.rollback()

        # Erro comum: e-mail ou telefone duplicado
        print("Erro ao criar usuário (verifique se o e-mail ou telefone já estão cadastrados):", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# Atualiza cargo, telefone e setor de um usuário.
# -----------------------------------------------------------------------------
def atualizar_usuario(id_usuario, cargo_usuario, telefone_usuario, id_setor):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        UPDATE Usuarios
        SET cargo_usuario = %s,
            telefone_usuario = %s,
            id_setor = %s
        WHERE id_usuario = %s
        """

        valores = (
            cargo_usuario,
            telefone_usuario,
            id_setor,
            id_usuario
        )

        cursor.execute(sql, valores)
        conexao.commit()

        # Verifica se algum registro foi alterado
        if cursor.rowcount > 0:
            print("Usuário atualizado com sucesso!")
        else:
            print("Usuário não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()

        print("Erro ao atualizar usuário (verifique se o telefone já está em uso):", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# Exclui um usuário do banco de dados.
# -----------------------------------------------------------------------------
def excluir_usuario(id_usuario):
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Usuarios WHERE id_usuario = %s"

        cursor.execute(sql, (id_usuario,))
        conexao.commit()

        # Confirma se a exclusão ocorreu
        if cursor.rowcount > 0:
            print("Usuário deletado com sucesso!")
        else:
            print("Usuário não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()

        print("Erro ao deletar usuário:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

# -----------------------------------------------------------------------------
# Menu principal de gerenciamento de usuários.
# -----------------------------------------------------------------------------
def opcao_desejada_usuario():
    # Opções válidas para cada campo do cadastro
    opcoes_cargo = [
        'administrador', 'sistema', 'tecnico', 'entregador',
        'ceo', 'diretor', 'gerente', 'coordenador', 'supervisor'
    ]

    opcoes_status = ['ativo', 'inativo']

    opcao_nivel = [
        'junior', 'pleno', 'senior', 'master'
    ]

    opcao_disp = [
        'disponível', 'em campo', 'ferias', 'afastado'
    ]

    while True:
        # Exibe o menu de opções
        print("\n------ Menu Usuário ------")
        print("1 - Listar usuários")
        print("2 - Criar usuário")
        print("3 - Atualizar usuário")
        print("4 - Deletar usuário")
        print("0 - Sair")

        # Lê a opção escolhida
        opcao_usuario = ler_inteiro("Coloque qual opção deseja: ")

        # ---------------------------------------------------------------------
        # Lista todos os usuários cadastrados
        # ---------------------------------------------------------------------
        if opcao_usuario == 1:
            print("\n--- Lista de Usuários ---")
            listar_usuario()
            time.sleep(2)

        # ---------------------------------------------------------------------
        # Cadastro de um novo usuário
        # ---------------------------------------------------------------------
        elif opcao_usuario == 2:
            print("\n--- Criar Usuário ---")

            nome = input("Nome: ")
            email = input("Email: ")
            senha = input("Senha: ")

            cargo = ler_opcao_valida(
                "Cargo (Administrador, Sistema, Tecnico, Entregador, CEO, Diretor, Gerente, Coordenador, Supervisor): ",
                opcoes_cargo
            )

            status = ler_opcao_valida(
                "Status (Ativo, Inativo): ",
                opcoes_status
            )

            nivel_experiencia = ler_opcao_valida(
                "Nivel de experiencia (Junior, Pleno, Senior, Master): ",
                opcao_nivel
            )

            disponibilidade_tecnico = ler_opcao_valida(
                "Disponibilidade (Disponível, Em Campo, Ferias, Afastado): ",
                opcao_disp
            )

            telefone = input("Telefone: ")
            data_nasc = input("Data de Nascimento (AAAA-MM-DD): ")
            id_setor = ler_inteiro("ID do Setor: ")

            # Gera automaticamente a data e hora do cadastro
            data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            criar_usuario(
                nome,
                email,
                senha,
                cargo,
                status,
                nivel_experiencia,
                disponibilidade_tecnico,
                telefone,
                data_nasc,
                id_setor,
                data_cadastro
            )

        # ---------------------------------------------------------------------
        # Atualização de informações do usuário
        # ---------------------------------------------------------------------
        elif opcao_usuario == 3:
            print("\n--- Atualizar Usuário ---")

            id_u = ler_inteiro("Digite o ID do usuário que deseja atualizar: ")

            cargo = ler_opcao_valida(
                "Novo Cargo (Administrador, Sistema, Tecnico, Entregador, CEO, Diretor, Gerente, Coordenador, Supervisor): ",
                opcoes_cargo
            )

            telefone = input("Novo Telefone: ")
            id_setor = ler_inteiro("Novo ID do Setor: ")

            atualizar_usuario(
                id_u,
                cargo,
                telefone,
                id_setor
            )

        # ---------------------------------------------------------------------
        # Exclusão de um usuário
        # ---------------------------------------------------------------------
        elif opcao_usuario == 4:
            print("\n--- Deletar Usuário ---")

            id_u = ler_inteiro(
                "Digite o ID do usuário que deseja deletar: "
            )

            excluir_usuario(id_u)

        # ---------------------------------------------------------------------
        # Encerra o menu
        # ---------------------------------------------------------------------
        elif opcao_usuario == 0:
            print("Voltando...")
            break

        # ---------------------------------------------------------------------
        # Caso seja digitada uma opção inexistente
        # ---------------------------------------------------------------------
        else:
            print("Opção inválida!")