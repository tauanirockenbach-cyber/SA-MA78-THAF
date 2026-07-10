from database import conectar

def listar_pecas():
    conexao = conectar()
    cursor = conexao.cursor()

        
    sql = """
            SELECT
            p.id_peca,
            p.nome_peca,
            p.quantidade_estoque,
            p.unidade_medida,
            p.custo_unitario,
            p.chk_quantidade_estoque,
            p.chk_custo_unitario
            FROM Almoxarifado_Pecas AS p
        """
    cursor.execute(sql)

    dados = cursor.fetchall()

        
    for pecas in dados:

        print(pecas)
    
    cursor.close()
    conexao.close()

def cadastrar_peca(id_peca, nome_peca, quantidade_estoque, unidade_medida, custo_unitario, chk_quantidade_estoque, chk_custo_unitario):
    conexao = conectar()
    cursor = conexao.cursor()
    sql = """
        INSERT INTO Tecnicos (id_peca, nome_peca, quantidade_estoque, unidade_medida, custo_unitario, chk_quantidade_estoque, chk_custo_unitario) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
     """
    valores = (id_peca, nome_peca, quantidade_estoque, unidade_medida, custo_unitario, chk_quantidade_estoque, chk_custo_unitario)
    cursor.execute(sql, valores)
    conexao.commit()
    print(f"Peça {id_peca} cadastrado(a) com sucesso!")
    
    cursor.close()
    conexao.close()

def atualizar_quantidade_estoque(id_peca, quantidade_estoque):
    conexao = conectar()
    cursor = conexao.cursor()
    sql = """
            UPDATE Almoxarifado_Pecas 
            SET quantidade_estoque = %s 
            WHERE id_peca = %s
        """
        
    valores = (quantidade_estoque, id_peca) 
    cursor.execute(sql, valores)
    conexao.commit()
    print(f"Quantidade da peça {id_peca} atualizada com sucesso!")
    conexao.rollback()
    
    cursor.close()
    conexao.close()

def deletar_tecnico(id_peca):
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = """
            DELETE FROM Almoxarifado_Pecas
            WHERE id_tecnico = %s
        """
    valores = (id_peca,)
    cursor.execute(sql, valores)
    conexao.commit()
    print(f"Peça {id_peca} deletada com sucesso!")
    
    conexao.rollback()

    cursor.close()
    conexao.close()