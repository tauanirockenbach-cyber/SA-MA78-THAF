# Importa a função responsável por conectar ao banco de dados
from database import conectar


# Função para garantir que o usuário digite apenas números inteiros
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# Função para listar todos os riscos e seus respectivos EPIs
def listar_epis():
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco de dados
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta para buscar todos os registros da tabela
        sql = "SELECT id_risco, risco_nr01, epis_obrigatorios FROM Matriz_Riscos_EPI"
        cursor.execute(sql)

        # Armazena todos os registros encontrados
        dados = cursor.fetchall()

        # Caso não existam registros
        if not dados:
            print("Nenhum EPI/Risco cadastrado.")
            return

        # Exibe cada registro encontrado
        for id_risco, risco, epis in dados:
            print(f"ID Risco: {id_risco} | Risco NR01: {risco} | EPIs Obrigatórios: {epis}")

    except Exception as erro:
        print("Erro ao listar EPIs:", erro)

    finally:
        # Fecha o cursor
        if cursor:
            cursor.close()

        # Fecha a conexão com o banco
        if conexao:
            conexao.close()


# Função para cadastrar um novo risco e seus EPIs obrigatórios
def cadastrar_epi(risco_nr01, epis_obrigatorios):
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL para inserir um novo registro
        sql = """
        INSERT INTO Matriz_Riscos_EPI
        (risco_nr01, epis_obrigatorios)
        VALUES (%s, %s)
        """

        cursor.execute(sql, (risco_nr01, epis_obrigatorios))

        # Salva as alterações no banco
        conexao.commit()

        print("EPI cadastrado com sucesso!")

    except Exception as erro:
        # Desfaz alterações em caso de erro
        if conexao:
            conexao.rollback()

        print("Erro ao cadastrar EPI:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função para atualizar um registro existente
def atualizar_epi(id_risco, risco_nr01, epis_obrigatorios):
    conexao = None
    cursor = None
    try:
        # Conecta ao banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Atualiza o risco e os EPIs conforme o ID informado
        sql = """
        UPDATE Matriz_Riscos_EPI
        SET risco_nr01 = %s,
            epis_obrigatorios = %s
        WHERE id_risco = %s
        """

        cursor.execute(sql, (risco_nr01, epis_obrigatorios, id_risco))

        # Salva as alterações
        conexao.commit()

        # Verifica se algum registro foi atualizado
        if cursor.rowcount > 0:
            print("EPI atualizado com sucesso!")
        else:
            print("EPI/Risco não encontrado.")

    except Exception as erro:
        # Cancela alterações caso ocorra erro
        if conexao:
            conexao.rollback()

        print("Erro ao atualizar EPI:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função para excluir um risco pelo ID
def deletar_epi(id_risco):
    conexao = None
    cursor = None
    try:
        # Conecta ao banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Remove o registro correspondente ao ID informado
        sql = "DELETE FROM Matriz_Riscos_EPI WHERE id_risco = %s"

        cursor.execute(sql, (id_risco,))

        # Salva as alterações
        conexao.commit()

        # Verifica se algum registro foi removido
        if cursor.rowcount > 0:
            print("EPI deletado com sucesso!")
        else:
            print("EPI/Risco não encontrado.")

    except Exception as erro:
        # Desfaz alterações caso ocorra erro
        if conexao:
            conexao.rollback()

        print("Erro ao deletar EPI (verifique se esse risco ainda está vinculado a outro registro):", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Menu principal do CRUD de EPIs
def opcao_desejada_epi():

    # Mantém o menu em execução até o usuário escolher sair
    while True:

        # Exibe as opções disponíveis
        print("\n------ Menu EPI / Matriz de Riscos ------")
        print("1 - Listar EPIs")
        print("2 - Cadastrar EPI")
        print("3 - Atualizar EPI")
        print("4 - Deletar EPI")
        print("0 - Sair")

        # Lê a opção escolhida pelo usuário
        opcao_epi = ler_inteiro("Coloque qual opção deseja: ")

        # Opção para listar registros
        if opcao_epi == 1:
            print("\n--- Lista de EPIs e Riscos ---")
            listar_epis()

        # Opção para cadastrar novo registro
        elif opcao_epi == 2:
            print("\n--- Cadastrar Novo EPI/Risco ---")

            risco = input("Risco (NR01): ")
            epis = input("EPIs Obrigatórios: ")

            cadastrar_epi(risco, epis)

        # Opção para atualizar registro existente
        elif opcao_epi == 3:
            print("\n--- Atualizar EPI/Risco ---")

            id_r = ler_inteiro("ID do Risco que deseja atualizar: ")
            risco = input("Novo Risco (NR01): ")
            epis = input("Novos EPIs Obrigatórios: ")

            atualizar_epi(id_r, risco, epis)

        # Opção para excluir registro
        elif opcao_epi == 4:
            print("\n--- Deletar EPI/Risco ---")

            id_r = ler_inteiro("ID do Risco que deseja deletar: ")

            deletar_epi(id_r)

        # Encerra o menu
        elif opcao_epi == 0:
            print("Voltando...")
            break

        # Caso seja digitada uma opção inválida
        else:
            print("Opção inválida!")