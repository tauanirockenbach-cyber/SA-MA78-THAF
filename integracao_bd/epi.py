from database import conectar


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


def listar_epis():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "SELECT id_risco, risco_nr01, epis_obrigatorios FROM Matriz_Riscos_EPI"
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum EPI/Risco cadastrado.")
            return

        for id_risco, risco, epis in dados:
            print(f"ID Risco: {id_risco} | Risco NR01: {risco} | EPIs Obrigatórios: {epis}")

    except Exception as erro:
        print("Erro ao listar EPIs:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def cadastrar_epi(risco_nr01, epis_obrigatorios):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "INSERT INTO Matriz_Riscos_EPI (risco_nr01, epis_obrigatorios) VALUES (%s, %s)"
        cursor.execute(sql, (risco_nr01, epis_obrigatorios))
        conexao.commit()

        print("EPI cadastrado com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao cadastrar EPI:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_epi(id_risco, risco_nr01, epis_obrigatorios):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        UPDATE Matriz_Riscos_EPI
        SET risco_nr01 = %s, epis_obrigatorios = %s
        WHERE id_risco = %s
        """
        cursor.execute(sql, (risco_nr01, epis_obrigatorios, id_risco))
        conexao.commit()

        if cursor.rowcount > 0:
            print("EPI atualizado com sucesso!")
        else:
            print("EPI/Risco não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao atualizar EPI:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def deletar_epi(id_risco):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Matriz_Riscos_EPI WHERE id_risco = %s"
        cursor.execute(sql, (id_risco,))
        conexao.commit()

        if cursor.rowcount > 0:
            print("EPI deletado com sucesso!")
        else:
            print("EPI/Risco não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        # Se essa tabela for referenciada por outra (ex.: máquinas ou usuários
        # vinculados a um risco), tentar deletar pode violar chave estrangeira.
        print("Erro ao deletar EPI (verifique se esse risco ainda está vinculado a outro registro):", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def opcao_desejada_epi():
    while True:
        print("\n------ Menu EPI / Matriz de Riscos ------")
        print("1 = Listar EPIs")
        print("2 = Cadastrar EPI")
        print("3 = Atualizar EPI")
        print("4 = Deletar EPI")
        print("0 = Sair")

        opcao_epi = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_epi == 1:
            print("\n--- Lista de EPIs e Riscos ---")
            listar_epis()

        elif opcao_epi == 2:
            print("\n--- Cadastrar Novo EPI/Risco ---")
            risco = input("Risco (NR01): ")
            epis = input("EPIs Obrigatórios: ")
            cadastrar_epi(risco, epis)

        elif opcao_epi == 3:
            print("\n--- Atualizar EPI/Risco ---")
            id_r = ler_inteiro("ID do Risco que deseja atualizar: ")
            risco = input("Novo Risco (NR01): ")
            epis = input("Novos EPIs Obrigatórios: ")
            atualizar_epi(id_r, risco, epis)

        elif opcao_epi == 4:
            print("\n--- Deletar EPI/Risco ---")
            id_r = ler_inteiro("ID do Risco que deseja deletar: ")
            deletar_epi(id_r)

        elif opcao_epi == 0:
            print("Voltando")
            break

        else:
            print("Opção inválida!")