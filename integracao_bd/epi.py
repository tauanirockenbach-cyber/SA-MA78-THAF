from database import conectar

def listar_epis():

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
        SELECT 
        m.id_risco,
        m.risco_nr01,
        m.epis_obrigatorios
    FROM Matriz_Riscos_EPI AS m
    """

    cursor.execute(sql)
    dados = cursor.fetchall()

    for epi in dados:
        print(epi)
    
    cursor.close()
    conexao.close()

def opcao_desejada_epi():
    while True:
        print("\n")
        print("------Menu EPI------")
        print("Listar Epi = 1")
        print("Sair = 0")
        opcao_epi = int(input("Coloque qual opção deseja: "))
        if opcao_epi == 1:
            print("\n")
            listar_epis()
        elif opcao_epi == 0:
            print("Voltando")
            break
        else:
            print("Opção invalida!")

def cadastrar_ferramenta(id_risco, risco_nr01, epis_obrigatorios):
    
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    insert into ferramentas (id_risco, risco_nr01, epis_obrigatorios)
    values (%s, %s, %s)
    """
    valores = (id_risco, risco_nr01, epis_obrigatorios)

    cursor.execute(sql, valores)
    conexao.commit()

    print(f"EPI cadastrado com sucesso!")

    cursor.close()
    conexao.close()

def atualizar_status(id_ferramenta, status_ferramenta):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    update Almoxarifado_Ferramentas
    set status_ferramenta = %s
    where id_ferramenta = %s
    """
    valores = (id_ferramenta, status_ferramenta)

    cursor.execute(sql, valores)
    conexao.commit()

    print(f"Status da ferramenta {id_ferramenta} atualizado com sucesso!")

    cursor.close()
    conexao.close()

def deletar_ferramenta(id_ferramenta):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    DELETE from Almoxarifado_Ferramentas
    where id_ferramenta = %s
    """

    valores = (id_ferramenta,)

    cursor.execute(sql, valores)
    conexao.commit()

    print(f"Ferramenta {id_ferramenta} deletada com sucesso!")

    cursor.close()
    conexao.close()