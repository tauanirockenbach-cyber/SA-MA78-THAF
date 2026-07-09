from database import conectar

def listar_maquinas():
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = '''SELECT
    tag_equipamento, 
    id_maquina, 
    numero_serie, 
    localizacao_maquina,
    tipo_manutencao_padrao,
    status_operacional,
    ultima_manutencao,
    id_setor
    FROM Maquinas
    '''
    
    cursor.execute(sql)
    dados = cursor.fetchall()
    
    for maquinas in dados:
        print(maquinas)
        
    cursor.close()
    conexao.close()

def criar_maquina(tag_equipamento, 
    id_maquina, 
    numero_serie, 
    localizacao_maquina,
    tipo_manutencao_padrao,
    status_operacional,
    ultima_manutencao,
    id_setor):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = '''
    INSERT INTO Maquinas
        (tag_equipamento, 
        id_maquina, 
        numero_serie, 
        localizacao_maquina,
        tipo_manutencao_padrao,
        status_operacional,
        ultima_manutencao,
        id_setor)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)
    '''

    valores = (tag_equipamento, 
    id_maquina, 
    numero_serie, 
    localizacao_maquina,
    tipo_manutencao_padrao,
    status_operacional,
    ultima_manutencao,
    id_setor)
    cursor.execute(sql, valores)
    conexao.commit()


    print("Máquina nova cadastrada com sucesso!")
    cursor.close()
    conexao.close()

def atualizar_status_maquina(status_operacional, id_maquina):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = '''
    UPDATE Maquinas
    SET status_operacional = %s
    WHERE id_maquina = %s
    '''
    valores = (status_operacional, id_maquina)
    cursor.execute(sql, valores)
    conexao.commit()

    print("Status da máquina atualizado com sucesso!")

    cursor.close()
    conexao.close()

def deletar_maquina(id_maquina):
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = '''
    DELETE FROM Maquina 
    WHERE id_maquina = %s
    '''
    
    valores = (id_maquina,)
    cursor.execute(sql, (valores))
    conexao.commit()
    
    print("Máquina deletada do sistema.")
    
    cursor.close()
    conexao.close()

#============================================================
#Modelo Maquina

def listar_modelos():
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = '''SELECT
    id_maquina,
    nome_maquina,
    fabricante_maquina,
    nome_modelo,
    descricao_tecnica,
    potencia_especificacao
    FROM Modelos_Maquinas
    '''
    
    cursor.execute(sql)
    dados = cursor.fetchall()
    
    for modelos in dados:
        print(modelos)
        
    cursor.close()
    conexao.close()

def criar_modelo_maquina(id_maquina, 
                         nome_maquina, 
                         fabricante_maquina, 
                         nome_modelo, descricao_tecnica, 
                         potencia_especificacao):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = '''
    INSERT INTO Modelos_Maquinas
        (id_maquina, 
        nome_maquina, 
        fabricante_maquina, 
        nome_modelo, descricao_tecnica, 
        potencia_especificacao)
    VALUES
    (%s, %s, %s, %s, %s)
    '''

    valores = (id_maquina, 
                nome_maquina, 
                fabricante_maquina, 
                nome_modelo, descricao_tecnica, 
                potencia_especificacao)
    cursor.execute(sql, valores)
    conexao.commit()


    print("Modelo de maquina nova cadastrado com sucesso!")
    cursor.close()
    conexao.close()

def atualizar_modelo_maquina(fabricante_maquina, id_maquina):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = '''
    UPDATE Modelos_Maquinas
    SET fabricante_maquina = %s
    WHERE id_maquina = %s
    '''
    valores = (fabricante_maquina, id_maquina)
    cursor.execute(sql, valores)
    conexao.commit()

    print("Fabricante da maquina atualizado com sucesso!")

    cursor.close()
    conexao.close()

def deletar_modelo_maquina(id_maquina):
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = '''
    DELETE FROM Modelos_Maquinas 
    WHERE id_maquina = %s
    '''
    
    valores = (id_maquina,)
    cursor.execute(sql, (valores))
    conexao.commit()
    
    print("Modelo de máquina deletado do sistema.")
    
    cursor.close()
    conexao.close()

def opcao_desejada_maq():
    while True:
        print("\n")
        print("------Menu Maquina------")
        print("Listar maquina = 1")
        print("Criar maquina = 2")
        print("atualizar maquina = 3")
        print("deletar maquina = 4")
        print("Sair = 0")
        opcao_maq = int(input("Coloque qual opção deseja: "))
        if opcao_maq == 1:
            print("\n")
            listar_maquinas()
        elif opcao_maq == 2:
            print("\n")
            tag_equipamento = input("tag do equipamento: ")
            id_aquina = input("ID da aquina: ")
            numero_serie = input("Numero da serie: ")
            localizacao_maquina = input("Localização da maquina: ")
            tipo_manutencao_padrao = input("Tipo da manutenção padrão: ")
            status_operacional = input("Qual estado operacional: ")
            ultima_manutencao = input("Qual a ultima manutenção: ")
            id_setor = input("ID do setor: ")
            criar_maquina(tag_equipamento,id_aquina,numero_serie,localizacao_maquina,tipo_manutencao_padrao,status_operacional,ultima_manutencao,id_setor)
        elif opcao_maq == 3:
            print("\n")
            status_operacional = int(input("Status da opecação: "))
            id_maquina = input("ID da maquina: ")
            atualizar_status_maquina(status_operacional, id_maquina)
        elif opcao_maq == 4:
            print("\n")
            id_maquina = int(input("ID da maquina: "))
            deletar_maquina(id_maquina)
        elif opcao_maq == 0:
            print("Voltando")
            break
        else:
            print("Opção invalida!")