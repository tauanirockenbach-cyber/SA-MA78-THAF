from database import conectar
import time


# ---------------------------------------------------------------------------
# Função auxiliar: evita repetir o mesmo try/except de conversão em todo lugar
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Máquinas
# ---------------------------------------------------------------------------
def listar_maquinas():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = '''
        SELECT tag_equipamento, id_maquina, numero_serie, localizacao_maquina,
               tipo_manutencao_padrao, status_operacional, ultima_manutencao, id_setor
        FROM Maquinas
        '''
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma máquina cadastrada.")
            return

        for tag, id_maq, serie, local, tipo, status, ultima, setor in dados:
            print(f"TAG: {tag} | ID: {id_maq} | Série: {serie} | Local: {local} | "
                  f"Tipo OS: {tipo} | Status: {status} | Última Manut.: {ultima} | ID Setor: {setor}")

    except Exception as erro:
        print("Erro ao listar máquinas:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def listar_tag_maquina():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "SELECT tag_equipamento FROM Maquinas"
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma TAG cadastrada.")
            return

        for (tag,) in dados:
            print(f"TAG: {tag}")

    except Exception as erro:
        print("Erro ao listar TAGs:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def criar_maquina(tag_equipamento, id_maquina, numero_serie, localizacao_maquina,
                   tipo_manutencao_padrao, status_operacional, ultima_manutencao, id_setor):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = '''
        INSERT INTO Maquinas
            (tag_equipamento, id_maquina, numero_serie, localizacao_maquina,
             tipo_manutencao_padrao, status_operacional, ultima_manutencao, id_setor)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        valores = (tag_equipamento, id_maquina, numero_serie, localizacao_maquina,
                   tipo_manutencao_padrao, status_operacional, ultima_manutencao, id_setor)

        cursor.execute(sql, valores)
        conexao.commit()
        print("Máquina cadastrada com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao criar máquina:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_status_maquina(status_operacional, tag_equipamento):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "UPDATE Maquinas SET status_operacional = %s WHERE tag_equipamento = %s"
        cursor.execute(sql, (status_operacional, tag_equipamento))
        conexao.commit()

        if cursor.rowcount == 0:
            print("Nenhuma máquina encontrada com essa tag.")
        else:
            print("Status da máquina atualizado com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao atualizar status da máquina:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def deletar_maquina(tag_equipamento):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Maquinas WHERE tag_equipamento = %s"
        cursor.execute(sql, (tag_equipamento,))
        conexao.commit()

        if cursor.rowcount == 0:
            print("Nenhuma máquina encontrada com essa tag.")
        else:
            print("Máquina deletada do sistema.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao deletar máquina:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# Modelos de máquinas
# ---------------------------------------------------------------------------
def listar_modelos():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = '''
        SELECT id_maquina, nome_maquina, fabricante_maquina, nome_modelo,
               descricao_tecnica, potencia_especificacao
        FROM Modelos_Maquinas
        '''
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum modelo cadastrado.")
            return

        for id_maq, nome, fab, modelo, desc, pot in dados:
            print(f"ID Máq: {id_maq} | Nome: {nome} | Fabricante: {fab} | "
                  f"Modelo: {modelo} | Descrição: {desc} | Potência: {pot}")

    except Exception as erro:
        print("Erro ao listar modelos:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def criar_modelo_maquina(id_maquina, nome_maquina, fabricante_maquina, nome_modelo,
                          descricao_tecnica, potencia_especificacao):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = '''
        INSERT INTO Modelos_Maquinas
            (id_maquina, nome_maquina, fabricante_maquina, nome_modelo,
             descricao_tecnica, potencia_especificacao)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        valores = (id_maquina, nome_maquina, fabricante_maquina, nome_modelo,
                   descricao_tecnica, potencia_especificacao)

        cursor.execute(sql, valores)
        conexao.commit()
        print("Modelo de máquina novo cadastrado com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao criar modelo de máquina:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_modelo_maquina(fabricante_maquina, id_maquina):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "UPDATE Modelos_Maquinas SET fabricante_maquina = %s WHERE id_maquina = %s"
        cursor.execute(sql, (fabricante_maquina, id_maquina))
        conexao.commit()

        if cursor.rowcount == 0:
            print("Nenhum modelo encontrado com esse ID de máquina.")
        else:
            print("Fabricante da máquina atualizado com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao atualizar modelo de máquina:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def deletar_modelo_maquina(id_maquina):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Modelos_Maquinas WHERE id_maquina = %s"
        cursor.execute(sql, (id_maquina,))
        conexao.commit()

        if cursor.rowcount == 0:
            print("Nenhum modelo encontrado com esse ID de máquina.")
        else:
            print("Modelo de máquina deletado do sistema.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao deletar modelo de máquina:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------
def opcao_desejada_maq():
    opcoes_validas = ['preventiva', 'corretiva', 'preditiva']
    opcoes_validas2 = ['operando', 'parado']

    while True:
        print("\n------ Menu Máquina ------")
        print("1 = Listar máquina")
        print("2 = Criar máquina")
        print("3 = Atualizar status da máquina")
        print("4 = Deletar máquina")
        print("0 = Sair")

        opcao_maq = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_maq == 1:
            print("\n--- Lista de Máquinas ---")
            listar_maquinas()
            time.sleep(1)

        elif opcao_maq == 2:
            print("\n--- Cadastrar Nova Máquina ---")
            listar_tag_maquina()
            tag_equipamento = input("TAG do equipamento: ")
            id_maquina = ler_inteiro("ID da máquina: ")
            numero_serie = input("Número de série: ")
            localizacao_maquina = input("Localização da máquina: ")

            tipo_manutencao_padrao = ler_opcao_valida(
                "Tipo da manutenção padrão (Preventiva, Corretiva, Preditiva): ", opcoes_validas
            )
            status_operacional = ler_opcao_valida(
                "Qual estado operacional (Operando, Parado): ", opcoes_validas2
            )

            ultima_manutencao = input("Qual a última manutenção (AAAA-MM-DD): ")
            id_setor = ler_inteiro("ID do setor: ")

            criar_maquina(tag_equipamento, id_maquina, numero_serie, localizacao_maquina,
                          tipo_manutencao_padrao, status_operacional, ultima_manutencao, id_setor)

        elif opcao_maq == 3:
            print("\n--- Atualizar Status ---")
            listar_tag_maquina()
            status_operacional = ler_opcao_valida(
                "Novo status da operação (Operando, Parado): ", opcoes_validas2
            )
            tag_equipamento = input("Tag do equipamente: ")
            atualizar_status_maquina(status_operacional, tag_equipamento)

        elif opcao_maq == 4:
            print("\n--- Deletar Máquina ---")
            listar_tag_maquina()
            tag_equipamento = input("Tag do equipamento: ")
            deletar_maquina(tag_equipamento)

        elif opcao_maq == 0:
            print("Voltando")
            break

        else:
            print("Opção inválida!")


def opcao_desejada_mod():
    while True:
        print("\n------ Menu Modelo Máquina ------")
        print("1 = Listar modelo")
        print("2 = Criar modelo")
        print("3 = Atualizar modelo")
        print("4 = Deletar modelo")
        print("0 = Sair")

        opcao_mod = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_mod == 1:
            print("\n--- Lista de Modelos ---")
            listar_modelos()
            time.sleep(1)

        elif opcao_mod == 2:
            print("\n--- Cadastrar Novo Modelo ---")
            id_maquina = ler_inteiro("ID da máquina: ")
            nome_maquina = input("Coloque o nome da máquina: ")
            fabricante_maquina = input("Coloque o fabricante da máquina: ")
            nome_modelo = input("Coloque o modelo da máquina: ")
            descricao_tecnica = input("Coloque a descrição técnica: ")
            potencia_especificacao = input("Coloque a potência: ")
            criar_modelo_maquina(id_maquina, nome_maquina, fabricante_maquina, nome_modelo,
                                  descricao_tecnica, potencia_especificacao)

        elif opcao_mod == 3:
            print("\n--- Atualizar Fabricante ---")
            fabricante_maquina = input("Novo fabricante da máquina: ")
            id_maquina = ler_inteiro("ID da máquina: ")
            atualizar_modelo_maquina(fabricante_maquina, id_maquina)

        elif opcao_mod == 4:
            print("\n--- Deletar Modelo ---")
            id_maquina = ler_inteiro("ID da máquina associada ao modelo: ")
            deletar_modelo_maquina(id_maquina)

        elif opcao_mod == 0:
            print("Voltando")
            break

        else:
            print("Opção inválida!")