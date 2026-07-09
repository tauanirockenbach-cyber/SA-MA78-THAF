from database import conectar

def qnt_maq_setores():
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT S.nome_setor,
           COUNT(MM.nome_maquina) AS quantidade_maquinas
    FROM Setores S
    JOIN Maquinas M ON M.id_setor = S.id_setor
    JOIN Modelos_Maquinas MM ON M.id_maquina = MM.id_maquina
    GROUP BY S.nome_setor;
    """

    cursor.execute(sql)

    dados = cursor.fetchall()

    for setor in dados:
        print(setor)

    cursor.close()
    conexao.close()

def listar_setor():
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT 
    id_setor,
    nome_setor,
    descricao_setor
    FROM Setores
    ORDER BY nome_setor ASC;
    """

    cursor.execute(sql)

    dados = cursor.fetchall()

    for setor in dados:
        print(setor)

    cursor.close()
    conexao.close()

def criar_setor(nome_setor, descricao_setor):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    INSERT INTO Setores (nome_setor, descricao_setor)
    VALUES (%s, %s);
    """

    cursor.execute(sql, (nome_setor, descricao_setor))
    conexao.commit()

    print("Setor cadastrado com sucesso!")

    cursor.close()
    conexao.close()

def atualizar_setor(id_setor, nome_setor, descricao_setor):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    UPDATE Setores
    SET nome_setor = %s,
        descricao_setor = %s
    WHERE id_setor = %s;
    """

    cursor.execute(sql, (nome_setor, descricao_setor, id_setor))
    conexao.commit()

    if cursor.rowcount > 0:
        print("Setor atualizado com sucesso!")
    else:
        print("Setor não encontrado.")

    cursor.close()
    conexao.close()

def deletar_setor(id_setor):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    DELETE FROM Setores
    WHERE id_setor = %s;
    """

    cursor.execute(sql, (id_setor,))
    conexao.commit()

    if cursor.rowcount > 0:
        print("Setor excluído com sucesso!")
    else:
        print("Setor não encontrado.")

    cursor.close()
    conexao.close()

def opcao_desejada_setor():
    while True:
        print("\n")
        print("------Menu Setor------")
        print("Listar setor = 1")
        print("Criar setor = 2")
        print("atualizar setor = 3")
        print("deletar setor = 4")
        print("Quantidade de maquina no setor = 5")
        print("Sair = 0")
        opcao_setor = int(input("Coloque qual opção deseja: "))
        if opcao_setor == 1:
            print("\n")
            listar_setor()
        elif opcao_setor == 2:
            print("\n")
            nome = input("Nome do setor: ")
            descricao = input("Descrição do setor: ")
            criar_setor(nome, descricao)
        elif opcao_setor == 3:
            print("\n")
            id_setor = int(input("ID do setor: "))
            nome = input("Novo nome: ")
            descricao = input("Nova descrição: ")
            atualizar_setor(id_setor, nome, descricao)
        elif opcao_setor == 4:
            print("\n")
            id_setor = int(input("ID do setor: "))
            deletar_setor(id_setor)
        elif opcao_setor == 5:
            print("\n")
            qnt_maq_setores()
        elif opcao_setor == 0:
            print("Voltando")
            break
        else:
            print("Opção invalida!")