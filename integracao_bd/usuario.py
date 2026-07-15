from database import conectar
from datetime import datetime
import time


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


def ler_opcao_valida(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem)
        if valor.lower() in opcoes_validas:
            return valor
        print("Opção inválida!")


def listar_usuario():
    conexao = None 
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            id_usuario, nome_usuario, email_usuario, cargo_usuario,
            status_usuario, nivel_experiencia, disponibilidade_tecnico, telefone_usuario, data_nasc_usuario,
            id_setor, data_cadastro
        FROM Usuarios
        """
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum usuário cadastrado.")
            return

        for usuario in dados:
            print(usuario)

    except Exception as erro:
        print("Erro ao listar usuários:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def criar_usuario(nome_usuario, email_usuario, senha, cargo_usuario, status_usuario, nivel_experiencia,
                   disponibilidade_tecnico, telefone_usuario, data_nasc_usuario, id_setor, data_cadastro):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # A coluna na tabela se chama "senha", não "senha_hash"
        sql = """
        INSERT INTO Usuarios
            (nome_usuario, email_usuario, senha, cargo_usuario, status_usuario, nivel_experiencia,
            disponibilidade_tecnico, telefone_usuario, data_nasc_usuario, id_setor, data_cadastro)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (nome_usuario, email_usuario, senha, cargo_usuario, status_usuario, nivel_experiencia,
                    disponibilidade_tecnico, telefone_usuario, data_nasc_usuario, id_setor, data_cadastro)

        cursor.execute(sql, valores)
        conexao.commit()

        print("Usuário cadastrado com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        # email_usuario e telefone_usuario são UNIQUE na tabela: erro comum aqui
        # é tentar cadastrar um e-mail ou telefone que já existe.
        print("Erro ao criar usuário (verifique se o e-mail ou telefone já estão cadastrados):", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_usuario(id_usuario, cargo_usuario, telefone_usuario, id_setor):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        UPDATE Usuarios
        SET cargo_usuario = %s, telefone_usuario = %s, id_setor = %s
        WHERE id_usuario = %s
        """
        valores = (cargo_usuario, telefone_usuario, id_setor, id_usuario)
        cursor.execute(sql, valores)
        conexao.commit()

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


def excluir_usuario(id_usuario):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Usuarios WHERE id_usuario = %s"
        cursor.execute(sql, (id_usuario,))
        conexao.commit()

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


def opcao_desejada_usuario():
    opcoes_cargo = [
        'administrador', 'sistema', 'tecnico', 'entregador',
        'ceo', 'diretor', 'gerente', 'coordenador', 'supervisor'
    ]
    opcoes_status = ['ativo', 'inativo']
    opcao_nivel = ['junior', 'pleno', 'senior', 'master']
    opcao_disp = ['disponível', 'em campo', 'ferias', 'afastado']

    while True:
        print("\n------ Menu Usuário ------")
        print("1 - Listar usuários")
        print("2 - Criar usuário")
        print("3 - Atualizar usuário")
        print("4 - Deletar usuário")
        print("0 - Sair")

        opcao_usuario = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_usuario == 1:
            print("\n--- Lista de Usuários ---")
            listar_usuario()
            time.sleep(2)

        elif opcao_usuario == 2:
            print("\n--- Criar Usuário ---")
            nome = input("Nome: ")
            email = input("Email: ")
            senha = input("Senha: ")
            cargo = ler_opcao_valida(
                "Cargo (Administrador, Sistema, Tecnico, Entregador, CEO, "
                "Diretor, Gerente, Coordenador, Supervisor): ",
                opcoes_cargo
            )
            status = ler_opcao_valida("Status (Ativo, Inativo): ", opcoes_status)
            nivel_experiencia = ler_opcao_valida("Nivel de experiencia (Junior, Pleno, Senior, Master): ", opcao_nivel )
            disponibilidade_tecnico = ler_opcao_valida("Disponibilidade (Disponível, Em Campo, Ferias, Afastado): ", opcao_disp)
            telefone = input("Telefone: ")
            data_nasc = input("Data de Nascimento (AAAA-MM-DD): ")
            id_setor = ler_inteiro("ID do Setor: ")
            data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            criar_usuario(nome, email, senha, cargo, status, nivel_experiencia, 
                          disponibilidade_tecnico, telefone, data_nasc, id_setor, data_cadastro)

        elif opcao_usuario == 3:
            print("\n--- Atualizar Usuário ---")
            id_u = ler_inteiro("Digite o ID do usuário que deseja atualizar: ")
            cargo = ler_opcao_valida(
                "Novo Cargo (Administrador, Sistema, Tecnico, Entregador, CEO, "
                "Diretor, Gerente, Coordenador, Supervisor): ",
                opcoes_cargo
            )
            telefone = input("Novo Telefone: ")
            id_setor = ler_inteiro("Novo ID do Setor: ")

            atualizar_usuario(id_u, cargo, telefone, id_setor)

        elif opcao_usuario == 4:
            print("\n--- Deletar Usuário ---")
            id_u = ler_inteiro("Digite o ID do usuário que deseja deletar: ")
            excluir_usuario(id_u)

        elif opcao_usuario == 0:
            print("Voltando...")
            break

        else:
            print("Opção inválida!")