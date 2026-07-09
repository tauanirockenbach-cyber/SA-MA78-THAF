from database import conectar

def listar_ferramentas():
    
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    select 
        f.id_ferramenta,
        f.nome_ferramenta,
        f.status_ferramenta
    from Almoxarifado_Ferramentas AS f
    """

    cursor.execute(sql)
    dados = cursor.fetchall()


    for ferramentas in dados:
        print(ferramentas)

    cursor.close()
    conexao.close()

def cadastrar_ferramenta(id_ferramenta, nome_ferramenta, status_ferramenta):
    
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    insert into ferramentas (id_ferramenta, nome_ferramenta, status_ferramenta)
    values (%s, %s, %s)
    """
    valores = (id_ferramenta, nome_ferramenta, status_ferramenta)

    cursor.execute(sql, valores)
    conexao.commit()

    print(f"Ferramenta {nome_ferramenta} cadastrado(a) com sucesso!")

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