# Importa a função responsável por conectar ao banco de dados.
from database import conectar

# Importa a classe datetime para manipulação de datas e horários.
from datetime import datetime


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

# Função que garante que o usuário digite apenas números inteiros.
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# Função que valida se a opção digitada pertence à lista de opções permitidas.
def ler_opcao_valida(mensagem, opcoes_validas):
    while True:
        valor = input(mensagem)

        if valor.lower() in [o.lower() for o in opcoes_validas]:
            return valor

        print("Opção inválida!")


# ---------------------------------------------------------------------------
# ORDENS DE SERVIÇO
# ---------------------------------------------------------------------------

# Lista todas as Ordens de Serviço cadastradas.
def listar_ordens_servico():

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Consulta SQL que retorna todas as Ordens de Serviço.
        sql = """
        SELECT
            os.id_os,
            os.tag_equipamento,
            os.descricao_falha,
            os.data_abertura,
            os.hh_inicio,
            os.hh_fim,
            os.status_os,
            os.id_usuario
        FROM Ordens_Servico AS os
        """

        # Executa a consulta.
        cursor.execute(sql)

        # Armazena todos os registros retornados.
        dados = cursor.fetchall()

        # Caso não existam registros.
        if not dados:
            print("Nenhuma ordem de serviço cadastrada.")
            return

        # Exibe todas as Ordens de Serviço.
        for os_ in dados:
            print(os_)

    except Exception as erro:
        print("Erro ao listar ordens de serviço:", erro)

    finally:
        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Cria uma nova Ordem de Serviço.
def criar_ordem_servico(id_os, tag_equipamento, descricao_falha,
                        data_abertura, hh_inicio, id_usuario):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Insere uma nova Ordem de Serviço.
        # O status será "Aberto" por padrão.
        # O horário de término permanecerá nulo até o encerramento.
        sql = """
        INSERT INTO Ordens_Servico
            (id_os,
             tag_equipamento,
             descricao_falha,
             data_abertura,
             hh_inicio,
             id_usuario)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        valores = (
            id_os,
            tag_equipamento,
            descricao_falha,
            data_abertura,
            hh_inicio,
            id_usuario
        )

        cursor.execute(sql, valores)

        # Salva as alterações.
        conexao.commit()

        print(f"OS {id_os} criada com sucesso!")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print(
            "Erro ao criar OS (verifique se o ID já existe ou se equipamento/usuário são válidos):",
            erro
        )

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Atualiza o status de uma Ordem de Serviço.
def atualizar_status_os(id_os, status_os):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Atualiza apenas o status da Ordem de Serviço.
        sql = """
        UPDATE Ordens_Servico
        SET status_os = %s
        WHERE id_os = %s
        """

        cursor.execute(sql, (status_os, id_os))

        # Salva as alterações.
        conexao.commit()

        # Verifica se a OS existe.
        if cursor.rowcount > 0:
            print(f"Status da OS {id_os} atualizado para '{status_os}'!")
        else:
            print("OS não encontrada.")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print(
            "Erro ao atualizar status (verifique se o valor é válido para o ENUM):",
            erro
        )

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Encerra uma Ordem de Serviço.
def encerrar_os(id_os, hh_fim):

    # Atualiza o horário final e altera o status para Concluído.

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        UPDATE Ordens_Servico
        SET
            hh_fim = %s,
            status_os = 'Concluído'
        WHERE id_os = %s
        """

        cursor.execute(sql, (hh_fim, id_os))

        # Salva as alterações.
        conexao.commit()

        # Verifica se a OS foi encontrada.
        if cursor.rowcount > 0:
            print(f"OS {id_os} encerrada com sucesso!")
        else:
            print("OS não encontrada.")

    except Exception as erro:

        # Desfaz alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print(
            "Erro ao encerrar OS (verifique se o horário de término é posterior ao de início):",
            erro
        )

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Remove uma Ordem de Serviço.
def deletar_ordem_servico(id_os):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Exclui a Ordem de Serviço.
        # Os registros relacionados serão apagados automaticamente
        # devido ao ON DELETE CASCADE.
        sql = "DELETE FROM Ordens_Servico WHERE id_os = %s"

        cursor.execute(sql, (id_os,))

        # Salva as alterações.
        conexao.commit()

        # Verifica se a OS foi removida.
        if cursor.rowcount > 0:
            print(f"OS {id_os} deletada com sucesso!")
        else:
            print("OS não encontrada.")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao deletar OS:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# FERRAMENTAS DA ORDEM DE SERVIÇO
# ---------------------------------------------------------------------------

# Vincula uma ferramenta a uma Ordem de Serviço.
def adicionar_ferramenta_os(id_os, id_ferramenta):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Insere o vínculo entre a OS e a ferramenta.
        sql = """
        INSERT INTO OS_Ferramentas (id_os, id_ferramenta)
        VALUES (%s, %s)
        """

        cursor.execute(sql, (id_os, id_ferramenta))

        # Salva as alterações.
        conexao.commit()

        print(f"Ferramenta {id_ferramenta} vinculada à OS {id_os}!")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print(
            "Erro ao vincular ferramenta (verifique se a OS e a ferramenta existem):",
            erro
        )

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Lista todas as ferramentas vinculadas a uma Ordem de Serviço.
def listar_ferramentas_os(id_os):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            id_os_ferramenta,
            id_os,
            id_ferramenta
        FROM OS_Ferramentas
        WHERE id_os = %s
        """

        cursor.execute(sql, (id_os,))

        dados = cursor.fetchall()

        # Verifica se existem ferramentas cadastradas para essa OS.
        if not dados:
            print("Nenhuma ferramenta vinculada a essa OS.")
            return

        # Exibe todas as ferramentas encontradas.
        for item in dados:
            print(item)

    except Exception as erro:
        print("Erro ao listar ferramentas da OS:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()

# ---------------------------------------------------------------------------
# MATERIAIS (PEÇAS) DA ORDEM DE SERVIÇO
# ---------------------------------------------------------------------------

# Vincula uma peça/material a uma Ordem de Serviço.
def adicionar_material_os(id_os, id_peca, quantidade_utilizada):

    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        # Insere o vínculo entre a OS e a peça utilizada.
        sql = """
        INSERT INTO OS_Materiais
            (id_os, id_peca, quantidade_utilizada)
        VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (id_os, id_peca, quantidade_utilizada))

        # Salva as alterações.
        conexao.commit()

        print(f"Material (peça {id_peca}) vinculado à OS {id_os}!")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao vincular material (verifique se OS/peça existem e se a quantidade é maior que 0):", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Lista todos os materiais vinculados a uma Ordem de Serviço.
def listar_materiais_os(id_os):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            id_os_material,
            id_os,
            id_peca,
            quantidade_utilizada
        FROM OS_Materiais
        WHERE id_os = %s
        """

        cursor.execute(sql, (id_os,))

        dados = cursor.fetchall()

        # Verifica se existem materiais vinculados.
        if not dados:
            print("Nenhum material vinculado a essa OS.")
            return

        # Exibe os materiais encontrados.
        for item in dados:
            print(item)

    except Exception as erro:
        print("Erro ao listar materiais da OS:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# RISCOS / EPI DA ORDEM DE SERVIÇO
# ---------------------------------------------------------------------------

# Vincula um risco (EPI) a uma Ordem de Serviço.
def adicionar_risco_os(id_os, id_risco):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        INSERT INTO OS_Seguranca (id_os, id_risco)
        VALUES (%s, %s)
        """

        cursor.execute(sql, (id_os, id_risco))

        # Salva as alterações.
        conexao.commit()

        print(f"Risco {id_risco} vinculado à OS {id_os}!")

    except Exception as erro:

        # Cancela alterações caso ocorra erro.
        if conexao:
            conexao.rollback()

        print("Erro ao vincular risco (verifique se a OS e o risco existem):", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# Lista todos os riscos vinculados a uma Ordem de Serviço.
def listar_riscos_os(id_os):

    conexao = None
    cursor = None

    try:

        # Abre conexão com o banco.
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            id_os_seguranca,
            id_os,
            id_risco
        FROM OS_Seguranca
        WHERE id_os = %s
        """

        cursor.execute(sql, (id_os,))

        dados = cursor.fetchall()

        # Verifica se existem riscos cadastrados.
        if not dados:
            print("Nenhum risco vinculado a essa OS.")
            return

        # Exibe todos os riscos encontrados.
        for item in dados:
            print(item)

    except Exception as erro:
        print("Erro ao listar riscos da OS:", erro)

    finally:

        # Fecha cursor e conexão.
        if cursor:
            cursor.close()

        if conexao:
            conexao.close()


# ---------------------------------------------------------------------------
# MENU - ORDENS DE SERVIÇO
# ---------------------------------------------------------------------------

# Menu principal das Ordens de Serviço.
def opcao_desejada_manutencao():

    # Lista de status válidos.
    opcoes_status = ['Aberto', 'Em andamento', 'Concluído']

    while True:

        # Exibe o menu principal.
        print("\n------ Menu Manutenção (OS) ------")
        print("1 - Listar ordens de serviço")
        print("2 - Criar ordem de serviço")
        print("3 - Atualizar status da OS")
        print("4 - Encerrar OS")
        print("5 - Deletar OS")
        print("6 - Gerenciar ferramentas/materiais/riscos da OS")
        print("0 - Sair")

        opcao = ler_inteiro("Coloque qual opção deseja: ")

        # Lista todas as Ordens de Serviço.
        if opcao == 1:
            print("\n--- Lista de Ordens de Serviço ---")
            listar_ordens_servico()

        # Cria uma nova Ordem de Serviço.
        elif opcao == 2:
            print("\n--- Criar Ordem de Serviço ---")

            id_os = ler_inteiro("ID da OS: ")
            tag_equipamento = input("TAG do Equipamento: ")
            descricao_falha = input("Descrição da Falha: ")
            data_abertura = input("Data de Abertura (AAAA-MM-DD): ")
            hh_inicio = input("Horário de Início (HH:MM:SS): ")

            id_usuario_input = input(
                "ID do Usuário responsável (deixe em branco se não houver): "
            )

            id_usuario = int(id_usuario_input) if id_usuario_input.strip() else None

            criar_ordem_servico(
                id_os,
                tag_equipamento,
                descricao_falha,
                data_abertura,
                hh_inicio,
                id_usuario
            )

        # Atualiza o status da Ordem de Serviço.
        elif opcao == 3:
            print("\n--- Atualizar Status da OS ---")

            id_os = ler_inteiro("ID da OS: ")

            status_os = ler_opcao_valida(
                f"Novo Status {opcoes_status}: ",
                opcoes_status
            )

            atualizar_status_os(id_os, status_os)

        # Encerra uma Ordem de Serviço.
        elif opcao == 4:
            print("\n--- Encerrar OS ---")

            id_os = ler_inteiro("ID da OS: ")
            hh_fim = input("Horário de Término (HH:MM:SS): ")

            encerrar_os(id_os, hh_fim)

        # Remove uma Ordem de Serviço.
        elif opcao == 5:
            print("\n--- Deletar OS ---")

            id_os = ler_inteiro("ID da OS que deseja deletar: ")

            deletar_ordem_servico(id_os)

        # Abre o menu de relacionamentos.
        elif opcao == 6:
            opcao_desejada_os_relacionamentos()

        # Sai do menu.
        elif opcao == 0:
            print("Voltando...")
            break

        else:
            print("Opção inválida!")


# Menu responsável pelos relacionamentos da Ordem de Serviço.
def opcao_desejada_os_relacionamentos():

    while True:

        # Exibe o menu de relacionamentos.
        print("\n--- Ferramentas / Materiais / Riscos da OS ---")
        print("1 - Vincular ferramenta a uma OS")
        print("2 - Listar ferramentas de uma OS")
        print("3 - Vincular material (peça) a uma OS")
        print("4 - Listar materiais de uma OS")
        print("5 - Vincular risco/EPI a uma OS")
        print("6 - Listar riscos de uma OS")
        print("0 - Voltar")

        opcao = ler_inteiro("Coloque qual opção deseja: ")

        # Vincula uma ferramenta.
        if opcao == 1:
            id_os = ler_inteiro("ID da OS: ")
            id_ferramenta = ler_inteiro("ID da Ferramenta: ")

            adicionar_ferramenta_os(id_os, id_ferramenta)

        # Lista as ferramentas da OS.
        elif opcao == 2:
            id_os = ler_inteiro("ID da OS: ")

            listar_ferramentas_os(id_os)

        # Vincula um material.
        elif opcao == 3:
            id_os = ler_inteiro("ID da OS: ")
            id_peca = ler_inteiro("ID da Peça: ")
            quantidade_utilizada = ler_inteiro("Quantidade Utilizada: ")

            adicionar_material_os(
                id_os,
                id_peca,
                quantidade_utilizada
            )

        # Lista os materiais da OS.
        elif opcao == 4:
            id_os = ler_inteiro("ID da OS: ")

            listar_materiais_os(id_os)

        # Vincula um risco.
        elif opcao == 5:
            id_os = ler_inteiro("ID da OS: ")
            id_risco = ler_inteiro("ID do Risco: ")

            adicionar_risco_os(id_os, id_risco)

        # Lista os riscos da OS.
        elif opcao == 6:
            id_os = ler_inteiro("ID da OS: ")

            listar_riscos_os(id_os)

        # Retorna ao menu anterior.
        elif opcao == 0:
            break

        # Opção inválida.
        else:
            print("Opção inválida!")