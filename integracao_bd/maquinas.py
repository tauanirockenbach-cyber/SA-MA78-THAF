# Importa a função responsável por estabelecer a conexão com o banco de dados
from database import conectar

# Importa a biblioteca time para utilizar pausas durante a execução do programa
import time


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

# Função que garante que o usuário digite apenas números inteiros.
# Caso seja informado um valor inválido, solicita a entrada novamente.
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# Função que verifica se a opção digitada pertence à lista de opções válidas.
# Enquanto o usuário informar uma opção inválida, será solicitada uma nova entrada.
def ler_opcao_valida(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem)
        if valor.lower() in opcoes_validas:
            return valor
        print("Opção inválida!")


# ---------------------------------------------------------------------------
# CRUD - Máquinas
# ---------------------------------------------------------------------------

# Função responsável por listar todas as máquinas cadastradas.
def listar_maquinas():
    # Inicializa a conexão e o cursor.
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco de dados.
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta SQL que busca todas as máquinas cadastradas.
        sql = '''
        SELECT tag_equipamento, id_maquina, numero_serie, localizacao_maquina,
               tipo_manutencao_padrao, status_operacional, ultima_manutencao, id_setor
        FROM Maquinas
        '''

        # Executa a consulta.
        cursor.execute(sql)

        # Obtém todos os registros retornados.
        dados = cursor.fetchall()

        # Verifica se existem máquinas cadastradas.
        if not dados:
            print("Nenhuma máquina cadastrada.")
            return

        # Exibe todas as máquinas encontradas.
        for tag, id_maq, serie, local, tipo, status, ultima, setor in dados:
            print(
                f"TAG: {tag} | ID: {id_maq} | Série: {serie} | "
                f"Local: {local} | Tipo OS: {tipo} | "
                f"Status: {status} | Última Manut.: {ultima} | "
                f"ID Setor: {setor}"
            )

    except Exception as erro:
        # Exibe mensagem caso ocorra erro durante a consulta.
        print("Erro ao listar máquinas:", erro)

    finally:
        # Fecha o cursor.
        if cursor:
            cursor.close()

        # Fecha a conexão com o banco.
        if conexao:
            conexao.close()


# Função responsável por listar apenas as TAGs das máquinas.
def listar_tag_maquina():
    conexao = None
    cursor = None
    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta SQL que retorna somente as TAGs.
        sql = "SELECT tag_equipamento FROM Maquinas"

        cursor.execute(sql)

        # Armazena todas as TAGs encontradas.
        dados = cursor.fetchall()

        # Caso nenhuma TAG exista.
        if not dados:
            print("Nenhuma TAG cadastrada.")
            return

        # Exibe cada TAG cadastrada.
        for (tag,) in dados:
            print(f"TAG: {tag}")

    except Exception as erro:
        print("Erro ao listar TAGs:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função responsável por cadastrar uma nova máquina.
def criar_maquina(tag_equipamento, id_maquina, numero_serie, localizacao_maquina,
                  tipo_manutencao_padrao, status_operacional,
                  ultima_manutencao, id_setor):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL para inserir uma nova máquina.
        sql = '''
        INSERT INTO Maquinas
            (tag_equipamento, id_maquina, numero_serie,
             localizacao_maquina, tipo_manutencao_padrao,
             status_operacional, ultima_manutencao, id_setor)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''

        # Agrupa os valores que serão enviados ao banco.
        valores = (
            tag_equipamento,
            id_maquina,
            numero_serie,
            localizacao_maquina,
            tipo_manutencao_padrao,
            status_operacional,
            ultima_manutencao,
            id_setor
        )

        # Executa o INSERT.
        cursor.execute(sql, valores)

        # Confirma a inserção no banco.
        conexao.commit()

        print("Máquina cadastrada com sucesso!")

    except Exception as erro:
        # Desfaz alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao criar máquina:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função responsável por atualizar o status operacional de uma máquina.
def atualizar_status_maquina(status_operacional, tag_equipamento):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Atualiza o status da máquina pela TAG.
        sql = """
        UPDATE Maquinas
        SET status_operacional = %s
        WHERE tag_equipamento = %s
        """

        cursor.execute(sql, (status_operacional, tag_equipamento))

        # Salva as alterações.
        conexao.commit()

        # Verifica se alguma linha foi alterada.
        if cursor.rowcount == 0:
            print("Nenhuma máquina encontrada com essa tag.")
        else:
            print("Status da máquina atualizado com sucesso!")

    except Exception as erro:
        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao atualizar status da máquina:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()
# Função responsável por remover uma máquina utilizando sua TAG.
def deletar_maquina(tag_equipamento):

    # Inicializa conexão e cursor.
    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco de dados.
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL para excluir a máquina correspondente à TAG informada.
        sql = "DELETE FROM Maquinas WHERE tag_equipamento = %s"

        # Executa o comando DELETE.
        cursor.execute(sql, (tag_equipamento,))

        # Confirma a exclusão no banco.
        conexao.commit()

        # Verifica se alguma máquina foi removida.
        if cursor.rowcount == 0:
            print("Nenhuma máquina encontrada com essa tag.")
        else:
            print("Máquina deletada do sistema.")

    except Exception as erro:
        # Desfaz alterações caso ocorra algum erro.
        if conexao:
            conexao.rollback()

        print("Erro ao deletar máquina:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# CRUD - Modelos de Máquinas
# ---------------------------------------------------------------------------

# Função responsável por listar todos os modelos de máquinas cadastrados.
def listar_modelos():

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta SQL que retorna todos os modelos cadastrados.
        sql = '''
        SELECT id_maquina, nome_maquina, fabricante_maquina, nome_modelo,
               descricao_tecnica, potencia_especificacao
        FROM Modelos_Maquinas
        '''

        # Executa a consulta.
        cursor.execute(sql)

        # Obtém todos os registros encontrados.
        dados = cursor.fetchall()

        # Verifica se existem modelos cadastrados.
        if not dados:
            print("Nenhum modelo cadastrado.")
            return

        # Exibe cada modelo encontrado.
        for id_maq, nome, fab, modelo, desc, pot in dados:
            print(
                f"ID Máq: {id_maq} | Nome: {nome} | "
                f"Fabricante: {fab} | Modelo: {modelo} | "
                f"Descrição: {desc} | Potência: {pot}"
            )

    except Exception as erro:
        print("Erro ao listar modelos:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função responsável por cadastrar um novo modelo de máquina.
def criar_modelo_maquina(id_maquina, nome_maquina, fabricante_maquina,
                         nome_modelo, descricao_tecnica,
                         potencia_especificacao):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL para inserir um novo modelo.
        sql = '''
        INSERT INTO Modelos_Maquinas
            (id_maquina, nome_maquina, fabricante_maquina,
             nome_modelo, descricao_tecnica,
             potencia_especificacao)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''

        # Agrupa os dados que serão enviados ao banco.
        valores = (
            id_maquina,
            nome_maquina,
            fabricante_maquina,
            nome_modelo,
            descricao_tecnica,
            potencia_especificacao
        )

        # Executa o INSERT.
        cursor.execute(sql, valores)

        # Salva as alterações.
        conexao.commit()

        print("Modelo de máquina novo cadastrado com sucesso!")

    except Exception as erro:
        # Desfaz alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao criar modelo de máquina:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função responsável por atualizar o fabricante de um modelo.
def atualizar_modelo_maquina(fabricante_maquina, id_maquina):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Atualiza o fabricante do modelo correspondente ao ID informado.
        sql = """
        UPDATE Modelos_Maquinas
        SET fabricante_maquina = %s
        WHERE id_maquina = %s
        """

        cursor.execute(sql, (fabricante_maquina, id_maquina))

        # Salva as alterações.
        conexao.commit()

        # Verifica se algum registro foi atualizado.
        if cursor.rowcount == 0:
            print("Nenhum modelo encontrado com esse ID de máquina.")
        else:
            print("Fabricante da máquina atualizado com sucesso!")

    except Exception as erro:
        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao atualizar modelo de máquina:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Função responsável por excluir um modelo de máquina.
def deletar_modelo_maquina(id_maquina):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Comando SQL responsável por excluir o modelo.
        sql = "DELETE FROM Modelos_Maquinas WHERE id_maquina = %s"

        # Executa o DELETE.
        cursor.execute(sql, (id_maquina,))

        # Confirma a exclusão.
        conexao.commit()

        # Verifica se algum registro foi removido.
        if cursor.rowcount == 0:
            print("Nenhum modelo encontrado com esse ID de máquina.")
        else:
            print("Modelo de máquina deletado do sistema.")

    except Exception as erro:
        # Desfaz alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao deletar modelo de máquina:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------

# Menu responsável pelas operações relacionadas às máquinas.
def opcao_desejada_maq():

    # Lista dos tipos de manutenção permitidos.
    opcoes_validas = ['preventiva', 'corretiva', 'preditiva']

    # Lista dos estados operacionais permitidos.
    opcoes_validas2 = ['operando', 'parado']

    # Mantém o menu em execução até que o usuário escolha sair.
    while True:

        # Exibe as opções disponíveis.
        print("\n------ Menu Máquina ------")
        print("1 = Listar máquina")
        print("2 = Criar máquina")
        print("3 = Atualizar status da máquina")
        print("4 = Deletar máquina")
        print("0 = Sair")

        # Lê a opção escolhida.
        opcao_maq = ler_inteiro("Coloque qual opção deseja: ")

        # Lista todas as máquinas.
        if opcao_maq == 1:
            print("\n--- Lista de Máquinas ---")
            listar_maquinas()
            time.sleep(1)

        # Cadastra uma nova máquina.
        elif opcao_maq == 2:
            print("\n--- Cadastrar Nova Máquina ---")

            listar_tag_maquina()

            tag_equipamento = input("TAG do equipamento: ")
            id_maquina = ler_inteiro("ID da máquina: ")
            numero_serie = input("Número de série: ")
            localizacao_maquina = input("Localização da máquina: ")

            tipo_manutencao_padrao = ler_opcao_valida(
                "Tipo da manutenção padrão (Preventiva, Corretiva, Preditiva): ",
                opcoes_validas
            )

            status_operacional = ler_opcao_valida(
                "Qual estado operacional (Operando, Parado): ",
                opcoes_validas2
            )

            ultima_manutencao = input("Qual a última manutenção (AAAA-MM-DD): ")
            id_setor = ler_inteiro("ID do setor: ")

            criar_maquina(
                tag_equipamento,
                id_maquina,
                numero_serie,
                localizacao_maquina,
                tipo_manutencao_padrao,
                status_operacional,
                ultima_manutencao,
                id_setor
            )

        # Atualiza o status de uma máquina.
        elif opcao_maq == 3:
            print("\n--- Atualizar Status ---")

            listar_tag_maquina()

            status_operacional = ler_opcao_valida(
                "Novo status da operação (Operando, Parado): ",
                opcoes_validas2
            )

            tag_equipamento = input("Tag do equipamento: ")

            atualizar_status_maquina(status_operacional, tag_equipamento)

        # Exclui uma máquina.
        elif opcao_maq == 4:
            print("\n--- Deletar Máquina ---")

            listar_tag_maquina()

            tag_equipamento = input("Tag do equipamento: ")

            deletar_maquina(tag_equipamento)

        # Retorna ao menu principal.
        elif opcao_maq == 0:
            print("Voltando")
            break

        # Caso seja digitada uma opção inválida.
        else:
            print("Opção inválida!")


# Menu responsável pelas operações relacionadas aos modelos de máquinas.
def opcao_desejada_mod():

    # Mantém o menu em execução até que o usuário escolha sair.
    while True:

        # Exibe as opções disponíveis.
        print("\n------ Menu Modelo Máquina ------")
        print("1 - Listar modelo")
        print("2 - Criar modelo")
        print("3 - Atualizar modelo")
        print("4 - Deletar modelo")
        print("0 - Sair")

        # Lê a opção escolhida.
        opcao_mod = ler_inteiro("Coloque qual opção deseja: ")

        # Lista todos os modelos cadastrados.
        if opcao_mod == 1:
            print("\n--- Lista de Modelos ---")
            listar_modelos()
            time.sleep(1)

        # Cadastra um novo modelo.
        elif opcao_mod == 2:
            print("\n--- Cadastrar Novo Modelo ---")

            id_maquina = ler_inteiro("ID da máquina: ")
            nome_maquina = input("Coloque o nome da máquina: ")
            fabricante_maquina = input("Coloque o fabricante da máquina: ")
            nome_modelo = input("Coloque o modelo da máquina: ")
            descricao_tecnica = input("Coloque a descrição técnica: ")
            potencia_especificacao = input("Coloque a potência: ")

            criar_modelo_maquina(
                id_maquina,
                nome_maquina,
                fabricante_maquina,
                nome_modelo,
                descricao_tecnica,
                potencia_especificacao
            )

        # Atualiza o fabricante de um modelo.
        elif opcao_mod == 3:
            print("\n--- Atualizar Fabricante ---")

            fabricante_maquina = input("Novo fabricante da máquina: ")
            id_maquina = ler_inteiro("ID da máquina: ")

            atualizar_modelo_maquina(fabricante_maquina, id_maquina)

        # Exclui um modelo.
        elif opcao_mod == 4:
            print("\n--- Deletar Modelo ---")

            id_maquina = ler_inteiro("ID da máquina associada ao modelo: ")

            deletar_modelo_maquina(id_maquina)

        # Retorna ao menu principal.
        elif opcao_mod == 0:
            print("Voltando")
            break

        # Caso seja digitada uma opção inválida.
        else:
            print("Opção inválida!")