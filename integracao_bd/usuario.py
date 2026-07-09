from database import conectar
from datetime import datetime

def listar_usuario():
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    select 
    id_usuario,
    nome_usuario,
    email_usuario,
    cargo_usuario,
    status_usuario,
    telefone_usuario,
    data_nasc_usuario,
    id_setor,
    data_cadastro
    FROM Usuarios
    """

    cursor.execute(sql)
    dados = cursor.fetchall()
    for Usuarios in dados: 
        print(Usuarios)

    cursor.close()
    conexao.close()

def criar_usuario(nome_usuario, email_usuario, senha_hash, cargo_usuario, status_usuario, telefone_usuario, data_nasc_usuario, id_setor, data_cadastro):
    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = """ 
        INSERT INTO Usuarios (nome_usuario, email_usuario, senha_hash, cargo_usuario, status_usuario, telefone_usuario, data_nasc_usuario, id_setor, data_cadastro) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
    """
    
    valores = (nome_usuario, email_usuario, senha_hash, cargo_usuario, status_usuario, telefone_usuario, data_nasc_usuario, id_setor, data_cadastro)
    
    cursor.execute(sql, valores)
    conexao.commit()
    
    print("Funcionário cadastrado com sucesso!")
    cursor.close()
    conexao.close()

def atualizar_usuario(cargo_usuario,telefone_usuario,id_setor):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """UPDATE Usuarios
    SET cargo_usuario = %s
    WHERE id_funcionario = %s
    """
    valores = (cargo_usuario,telefone_usuario,id_setor)
    cursor.execute(sql, valores)
    conexao.commit()

    print("Usuario atualizado com sucesso!")

    cursor.close()
    conexao.close()

def excluir_usuario(id_usuario):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    delete from Usuarios
    where id_usuario = %s
    """
    valores = (id_usuario)
    cursor.execute(sql, (valores,))
    conexao.commit()

    cursor.close()
    conexao.close()



def opcao_desejada_usuario():
    while True:
        print("\n")
        print("------Menu Usuario------")
        print("Listar usuarios = 1")
        print("Criar usuarios = 2")
        print("Atualizar usuarios = 3")
        print("Deletar usuario = 4")
        print("Sair = 0")
        opcao_usuario = int(input("Coloque qual opção deseja: "))
        if opcao_usuario == 1:
            print("\n")
            listar_usuario()
        elif opcao_usuario == 2:
            print("\n")
            criar_usuario()
        elif opcao_usuario == 3:
            print("\n")
            atualizar_usuario()
        elif opcao_usuario == 4:
            print("\n")
            excluir_usuario()
        elif opcao_usuario == 0:
            print("Voltando")
            break
        else:
            print("Opção invalida!")