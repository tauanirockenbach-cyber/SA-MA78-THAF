from database import conectar
import time


# -----------------------------------------------------------------------------
# Lê um número inteiro informado pelo usuário.
# Enquanto um valor inválido for digitado, solicita novamente.
# -----------------------------------------------------------------------------
def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem)
        try:
            return int(valor)
        except ValueError:
            print("Digite apenas números.")


# -----------------------------------------------------------------------------
# Lê um texto informado pelo usuário, não aceitando campo vazio.
# -----------------------------------------------------------------------------
def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("O campo não pode ficar vazio.")


# -----------------------------------------------------------------------------
# Relatório de quantidade de Ordens de Serviço (OS) por setor.
# -----------------------------------------------------------------------------
def relatorio_producao_por_setor():
    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco
        conexao = conectar()
        cursor = conexao.cursor()

        # Conta quantas OS existem por setor, através das máquinas vinculadas
        sql = """
        SELECT
            S.nome_setor,
            COUNT(O.id_os) AS total_os
        FROM Setores S
        LEFT JOIN Maquinas M
            ON M.id_setor = S.id_setor
        LEFT JOIN Ordens_Servico O
            ON O.tag_equipamento = M.tag_equipamento
        GROUP BY S.nome_setor
        ORDER BY total_os DESC
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        # Verifica se existem setores cadastrados
        if not dados:
            print("Nenhum setor cadastrado.")
            return

        # Exibe o relatório
        for nome_setor, total_os in dados:
            print(f"\nSetor: {nome_setor}")
            print(f"Total de OS: {total_os}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao gerar relatório de OS por setor:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# Relatório de quantidade de máquinas por setor.
# -----------------------------------------------------------------------------
def qnt_maq_setores():
    conexao = None
    cursor = None

    try:
        # Abre conexão com o banco de dados
        conexao = conectar()
        cursor = conexao.cursor()

        # Conta quantas máquinas existem em cada setor
        # O LEFT JOIN garante que setores sem máquinas também sejam exibidos
        sql = """
        SELECT
            S.nome_setor,
            COUNT(M.id_maquina)
        FROM Setores S
        LEFT JOIN Maquinas M
            ON M.id_setor = S.id_setor
        GROUP BY S.nome_setor
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        # Verifica se existem setores cadastrados
        if not dados:
            print("Nenhum setor cadastrado.")
            return

        # Exibe o nome do setor e sua quantidade de máquinas
        for nome_setor, quantidade in dados:
            print(f"Setor: {nome_setor} | Quantidade de Máquinas: {quantidade}")

    except Exception as erro:
        print("Erro ao contar máquinas por setor:", erro)

    finally:
        # Fecha cursor e conexão
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 1) Quais máquinas estão em manutenção ou paradas?
# -----------------------------------------------------------------------------
def maquinas_manutencao_ou_paradas():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT MM.nome_maquina, M.status_operacional
        FROM Modelos_Maquinas AS MM
        JOIN Maquinas AS M ON MM.id_maquina = M.id_maquina
        WHERE M.status_operacional IN ('Em Manutenção', 'Parado')
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma máquina em manutenção ou parada.")
            return

        for nome_maquina, status in dados:
            print(f"\nMáquina: {nome_maquina}")
            print(f"Status: {status}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar máquinas em manutenção/parada:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 2) Histórico de manutenções de um equipamento específico (por tag).
# -----------------------------------------------------------------------------
def historico_manutencao_maq_especifica():
    conexao = None
    cursor = None

    try:
        tag = ler_texto("Informe a tag do equipamento (ex: AJU-FR-05): ")

        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT M.tag_equipamento, MM.nome_maquina, M.ultima_manutencao
        FROM Maquinas M
        JOIN Modelos_Maquinas MM ON M.id_maquina = MM.id_maquina
        WHERE M.tag_equipamento = %s
        """

        cursor.execute(sql, (tag,))
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum registro encontrado para essa tag.")
            return

        for tag_equipamento, nome_maquina, ultima_manutencao in dados:
            print(f"\nTag: {tag_equipamento}")
            print(f"Máquina: {nome_maquina}")
            print(f"Última manutenção: {ultima_manutencao}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar histórico de manutenção do equipamento:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 3) Histórico de manutenção de um tipo de máquina.
# -----------------------------------------------------------------------------
def historico_manutencao_tipo_maq():
    conexao = None
    cursor = None

    try:
        nome_maquina = ler_texto("Informe o tipo/nome da máquina (ex: Furadeira de Coluna): ")

        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT M.tag_equipamento, MM.nome_maquina, M.ultima_manutencao
        FROM Maquinas M
        JOIN Modelos_Maquinas MM ON M.id_maquina = MM.id_maquina
        WHERE MM.nome_maquina = %s
        """

        cursor.execute(sql, (nome_maquina,))
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum registro encontrado para esse tipo de máquina.")
            return

        for tag_equipamento, nome_maq, ultima_manutencao in dados:
            print(f"\nTag: {tag_equipamento}")
            print(f"Máquina: {nome_maq}")
            print(f"Última manutenção: {ultima_manutencao}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar histórico de manutenção por tipo de máquina:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 4) Ordens de serviço abertas em um período informado.
# -----------------------------------------------------------------------------
def os_por_periodo():
    conexao = None
    cursor = None

    try:
        data_inicio = ler_texto("Informe a data inicial (AAAA-MM-DD): ")
        data_fim = ler_texto("Informe a data final (AAAA-MM-DD): ")

        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT id_os, tag_equipamento, descricao_falha, data_abertura
        FROM Ordens_Servico
        WHERE data_abertura BETWEEN %s AND %s
        """

        cursor.execute(sql, (data_inicio, data_fim))
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma OS aberta nesse período.")
            return

        for id_os, tag_equipamento, descricao_falha, data_abertura in dados:
            print(f"\nOS: {id_os}")
            print(f"Equipamento: {tag_equipamento}")
            print(f"Falha: {descricao_falha}")
            print(f"Abertura: {data_abertura}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar OS por período:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 5) Quem são os técnicos ativos?
# -----------------------------------------------------------------------------
def tecnicos_ativos():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT nome_usuario, email_usuario, status_usuario
        FROM Usuarios
        WHERE cargo_usuario = 'Tecnico'
          AND status_usuario = 'Ativo'
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum técnico ativo encontrado.")
            return

        for nome_usuario, email_usuario, status_usuario in dados:
            print(f"\nTécnico: {nome_usuario}")
            print(f"Email: {email_usuario}")
            print(f"Status: {status_usuario}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar técnicos ativos:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 6) Alerta de estoque baixo.
# -----------------------------------------------------------------------------
def estoque_baixo():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT nome_peca, quantidade_estoque
        FROM Almoxarifado_Pecas
        WHERE quantidade_estoque < 10
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma peça com estoque baixo.")
            return

        for nome_peca, quantidade_estoque in dados:
            print(f"\nPeça: {nome_peca}")
            print(f"Quantidade em estoque: {quantidade_estoque}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar peças com estoque baixo:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 7) OS abertas ou em andamento e o técnico responsável.
# -----------------------------------------------------------------------------
def os_andamento():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT OS.id_os, OS.descricao_falha, OS.status_os, U.nome_usuario
        FROM Ordens_Servico AS OS
        JOIN Usuarios AS U ON U.id_usuario = OS.id_usuario
        WHERE OS.status_os IN ('Aberto', 'Em andamento')
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma OS aberta ou em andamento.")
            return

        for id_os, descricao_falha, status_os, nome_usuario in dados:
            print(f"\nOS: {id_os}")
            print(f"Falha: {descricao_falha}")
            print(f"Status: {status_os}")
            print(f"Técnico responsável: {nome_usuario}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar OS em andamento:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 8) Valor total em peças no almoxarifado.
# -----------------------------------------------------------------------------
def valor_total_pecas():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT SUM(quantidade_estoque * custo_unitario) AS valor_total
        FROM Almoxarifado_Pecas
        """

        cursor.execute(sql)
        (valor_total,) = cursor.fetchone()

        if valor_total is None:
            print("Não há peças cadastradas no almoxarifado.")
            return

        print(f"\nValor total em peças no almoxarifado: R$ {valor_total:.2f}")

    except Exception as erro:
        print("Erro ao calcular valor total de peças:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 9) Relatório de custos por Ordem de Serviço concluída.
# -----------------------------------------------------------------------------
def custos_os_concluida():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT OS.id_os, SUM(OM.quantidade_utilizada * A.custo_unitario) AS valor_total
        FROM Ordens_Servico AS OS
        JOIN OS_Materiais AS OM ON OM.id_os = OS.id_os
        JOIN Almoxarifado_Pecas AS A ON A.id_peca = OM.id_peca
        WHERE OS.status_os = 'Concluído'
        GROUP BY OS.id_os
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma OS concluída com materiais utilizados.")
            return

        for id_os, valor_total in dados:
            print(f"\nOS: {id_os}")
            print(f"Custo total de peças: R$ {valor_total:.2f}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao calcular custos por OS concluída:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 10) EPIs obrigatórios para uma OS específica (informada pelo usuário).
# -----------------------------------------------------------------------------
def epi_os():
    conexao = None
    cursor = None

    try:
        id_os = ler_inteiro("Informe o número da OS: ")

        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT OS.descricao_falha, EPI.epis_obrigatorios
        FROM Ordens_Servico AS OS
        JOIN OS_Seguranca AS S ON OS.id_os = S.id_os
        JOIN Matriz_Riscos_EPI AS EPI ON EPI.id_risco = S.id_risco
        WHERE OS.id_os = %s
        """

        cursor.execute(sql, (id_os,))
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum EPI obrigatório encontrado para essa OS.")
            return

        for descricao_falha, epis_obrigatorios in dados:
            print(f"\nFalha: {descricao_falha}")
            print(f"EPIs obrigatórios: {epis_obrigatorios}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar EPIs da OS:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 11) OS concluídas por cada técnico.
# -----------------------------------------------------------------------------
def os_concluida_por_tecnico():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT U.nome_usuario, COUNT(OS.id_os) AS os_concluidas
        FROM Usuarios AS U
        JOIN Ordens_Servico AS OS ON OS.id_usuario = U.id_usuario
        WHERE OS.status_os = 'Concluído'
        GROUP BY U.nome_usuario
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma OS concluída registrada.")
            return

        for nome_usuario, os_concluidas in dados:
            print(f"Técnico: {nome_usuario} | OS concluídas: {os_concluidas}")

    except Exception as erro:
        print("Erro ao buscar OS concluídas por técnico:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 12) Setores que geraram maior custo com manutenção de peças.
# -----------------------------------------------------------------------------
def setores_que_geram_mais_custo():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT S.nome_setor, SUM(OM.quantidade_utilizada * A.custo_unitario) AS valor_gasto_pecas
        FROM OS_Materiais AS OM
        JOIN Almoxarifado_Pecas AS A ON A.id_peca = OM.id_peca
        JOIN Ordens_Servico AS OS ON OS.id_os = OM.id_os
        JOIN Maquinas AS M ON M.tag_equipamento = OS.tag_equipamento
        JOIN Setores AS S ON S.id_setor = M.id_setor
        GROUP BY S.nome_setor
        ORDER BY valor_gasto_pecas DESC
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum gasto com peças registrado por setor.")
            return

        for nome_setor, valor_gasto in dados:
            print(f"\nSetor: {nome_setor}")
            print(f"Valor gasto em peças: R$ {valor_gasto:.2f}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar setores com maior custo:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 13) Ferramentas que nunca foram utilizadas em nenhuma OS.
# -----------------------------------------------------------------------------
def ferramentas_nunca_usadas_os():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT nome_ferramenta
        FROM Almoxarifado_Ferramentas
        WHERE id_ferramenta NOT IN (SELECT id_ferramenta FROM OS_Ferramentas)
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Todas as ferramentas já foram utilizadas em alguma OS.")
            return

        for (nome_ferramenta,) in dados:
            print(f"Ferramenta nunca utilizada: {nome_ferramenta}")

    except Exception as erro:
        print("Erro ao buscar ferramentas nunca utilizadas:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 14) Quantidade de máquinas por fabricante.
# -----------------------------------------------------------------------------
def quant_maquinas_fabricante():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT fabricante_maquina, COUNT(nome_maquina) AS quantidade_maquinas
        FROM Modelos_Maquinas
        GROUP BY fabricante_maquina
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum fabricante cadastrado.")
            return

        for fabricante_maquina, quantidade_maquinas in dados:
            print(f"Fabricante: {fabricante_maquina} | Quantidade: {quantidade_maquinas}")

    except Exception as erro:
        print("Erro ao buscar quantidade de máquinas por fabricante:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 15) OS em andamento por cada técnico.
# -----------------------------------------------------------------------------
def os_em_andamento_por_tecnico():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT U.nome_usuario, COUNT(OS.id_os) AS os_em_andamento
        FROM Usuarios AS U
        JOIN Ordens_Servico AS OS ON OS.id_usuario = U.id_usuario
        WHERE OS.status_os = 'Em andamento'
        GROUP BY U.nome_usuario
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma OS em andamento no momento.")
            return

        for nome_usuario, os_em_andamento in dados:
            print(f"Técnico: {nome_usuario} | OS em andamento: {os_em_andamento}")

    except Exception as erro:
        print("Erro ao buscar OS em andamento por técnico:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 16) Alertas de devolução de ferramentas atrasadas ou com prazo vencido.
# -----------------------------------------------------------------------------
def alertas_devolucao_ferramentas():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            MF.id_movimentacao,
            AF.nome_ferramenta,
            MF.id_os,
            U_Tec.nome_usuario AS tecnico_solicitante,
            U_Alm.nome_usuario AS almoxarife_responsavel,
            MF.data_retirada,
            MF.data_devolucao_prevista,
            MF.status_movimentacao
        FROM Movimentacao_Ferramentas MF
        JOIN OS_Ferramentas OSF ON MF.id_os_ferramenta = OSF.id_os_ferramenta
        JOIN Almoxarifado_Ferramentas AF ON OSF.id_ferramenta = AF.id_ferramenta
        JOIN Usuarios U_Tec ON MF.id_usuario_solicitante = U_Tec.id_usuario
        LEFT JOIN Usuarios U_Alm ON MF.id_usuario_entregador = U_Alm.id_usuario
        WHERE MF.status_movimentacao = 'Atrasado'
           OR (MF.data_devolucao_prevista < NOW() AND MF.data_devolucao_real IS NULL)
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhuma ferramenta com devolução atrasada ou vencida.")
            return

        for (id_movimentacao, nome_ferramenta, id_os, tecnico_solicitante,
             almoxarife_responsavel, data_retirada, data_devolucao_prevista,
             status_movimentacao) in dados:
            print(f"\nMovimentação: {id_movimentacao}")
            print(f"Ferramenta: {nome_ferramenta}")
            print(f"OS: {id_os}")
            print(f"Técnico solicitante: {tecnico_solicitante}")
            print(f"Almoxarife responsável: {almoxarife_responsavel}")
            print(f"Retirada: {data_retirada}")
            print(f"Devolução prevista: {data_devolucao_prevista}")
            print(f"Status: {status_movimentacao}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar alertas de devolução de ferramentas:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 17) Componentes com saldo zero e que possuem OS demandando esse material.
# -----------------------------------------------------------------------------
def componentes_sem_estoque_demandados():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT
            AP.id_peca,
            AP.nome_peca,
            AP.unidade_medida,
            AP.custo_unitario,
            COUNT(OSM.id_os) AS vezes_solicitada_em_os
        FROM Almoxarifado_Pecas AP
        JOIN OS_Materiais OSM ON AP.id_peca = OSM.id_peca
        WHERE AP.quantidade_estoque = 0
        GROUP BY
            AP.id_peca,
            AP.nome_peca,
            AP.unidade_medida,
            AP.custo_unitario
        ORDER BY vezes_solicitada_em_os DESC
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum componente zerado com demanda em OS.")
            return

        for (id_peca, nome_peca, unidade_medida, custo_unitario,
             vezes_solicitada_em_os) in dados:
            print(f"\nPeça: {nome_peca} (ID {id_peca})")
            print(f"Unidade: {unidade_medida}")
            print(f"Custo unitário: R$ {custo_unitario:.2f}")
            print(f"Vezes solicitada em OS: {vezes_solicitada_em_os}")
            print("-" * 40)

    except Exception as erro:
        print("Erro ao buscar componentes sem estoque demandados:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# 18) Tempo médio de reparo por técnico.
# -----------------------------------------------------------------------------
def tempo_medio_reparo_tecnico():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        SELECT U.nome_usuario,
               SEC_TO_TIME(AVG(TIME_TO_SEC(TIMEDIFF(OS.hh_fim, OS.hh_inicio)))) AS tempo_medio_trabalho
        FROM Usuarios AS U
        JOIN Ordens_Servico AS OS ON OS.id_usuario = U.id_usuario
        WHERE OS.status_os = 'Concluído'
          AND OS.hh_fim IS NOT NULL
        GROUP BY U.nome_usuario
        """

        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum dado de tempo de reparo disponível.")
            return

        for nome_usuario, tempo_medio_trabalho in dados:
            print(f"Técnico: {nome_usuario} | Tempo médio de reparo: {tempo_medio_trabalho}")

    except Exception as erro:
        print("Erro ao calcular tempo médio de reparo por técnico:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# -----------------------------------------------------------------------------
# Menu principal de relatórios.
# -----------------------------------------------------------------------------
def opcao_desejada_relatorio():

    while True:
        # Exibe o menu de opções
        print("\n------ Menu Relatórios ------")
        print(" 1 - Relatório de OS por Setor")
        print(" 2 - Quantidade de Máquinas por Setor")
        print(" 3 - Máquinas em Manutenção ou Paradas")
        print(" 4 - Histórico de Manutenção de Equipamento Específico")
        print(" 5 - Histórico de Manutenção por Tipo de Máquina")
        print(" 6 - OS Abertas em um Período")
        print(" 7 - Técnicos Ativos")
        print(" 8 - Alerta de Estoque Baixo")
        print(" 9 - OS Abertas/Em Andamento e Técnico Responsável")
        print("10 - Valor Total em Peças no Almoxarifado")
        print("11 - Custos por OS Concluída")
        print("12 - EPIs Obrigatórios de uma OS")
        print("13 - OS Concluídas por Técnico")
        print("14 - Setores com Maior Custo em Peças")
        print("15 - Ferramentas Nunca Utilizadas em OS")
        print("16 - Quantidade de Máquinas por Fabricante")
        print("17 - OS em Andamento por Técnico")
        print("18 - Alertas de Devolução de Ferramentas")
        print("19 - Componentes Zerados e Demandados")
        print("20 - Tempo Médio de Reparo por Técnico")
        print(" 0 - Sair")

        # Lê a opção escolhida
        opcao_relatorio = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_relatorio == 1:
            print("\n--- Relatório de OS por Setor ---")
            relatorio_producao_por_setor()
            time.sleep(2)

        elif opcao_relatorio == 2:
            print("\n--- Máquinas por Setor ---")
            qnt_maq_setores()
            time.sleep(2)

        elif opcao_relatorio == 3:
            print("\n--- Máquinas em Manutenção ou Paradas ---")
            maquinas_manutencao_ou_paradas()
            time.sleep(2)

        elif opcao_relatorio == 4:
            print("\n--- Histórico de Manutenção de Equipamento Específico ---")
            historico_manutencao_maq_especifica()
            time.sleep(2)

        elif opcao_relatorio == 5:
            print("\n--- Histórico de Manutenção por Tipo de Máquina ---")
            historico_manutencao_tipo_maq()
            time.sleep(2)

        elif opcao_relatorio == 6:
            print("\n--- OS Abertas em um Período ---")
            os_por_periodo()
            time.sleep(2)

        elif opcao_relatorio == 7:
            print("\n--- Técnicos Ativos ---")
            tecnicos_ativos()
            time.sleep(2)

        elif opcao_relatorio == 8:
            print("\n--- Alerta de Estoque Baixo ---")
            estoque_baixo()
            time.sleep(2)

        elif opcao_relatorio == 9:
            print("\n--- OS Abertas/Em Andamento e Técnico Responsável ---")
            os_andamento()
            time.sleep(2)

        elif opcao_relatorio == 10:
            print("\n--- Valor Total em Peças no Almoxarifado ---")
            valor_total_pecas()
            time.sleep(2)

        elif opcao_relatorio == 11:
            print("\n--- Custos por OS Concluída ---")
            custos_os_concluida()
            time.sleep(2)

        elif opcao_relatorio == 12:
            print("\n--- EPIs Obrigatórios de uma OS ---")
            epi_os()
            time.sleep(2)

        elif opcao_relatorio == 13:
            print("\n--- OS Concluídas por Técnico ---")
            os_concluida_por_tecnico()
            time.sleep(2)

        elif opcao_relatorio == 14:
            print("\n--- Setores com Maior Custo em Peças ---")
            setores_que_geram_mais_custo()
            time.sleep(2)

        elif opcao_relatorio == 15:
            print("\n--- Ferramentas Nunca Utilizadas em OS ---")
            ferramentas_nunca_usadas_os()
            time.sleep(2)

        elif opcao_relatorio == 16:
            print("\n--- Quantidade de Máquinas por Fabricante ---")
            quant_maquinas_fabricante()
            time.sleep(2)

        elif opcao_relatorio == 17:
            print("\n--- OS em Andamento por Técnico ---")
            os_em_andamento_por_tecnico()
            time.sleep(2)

        elif opcao_relatorio == 18:
            print("\n--- Alertas de Devolução de Ferramentas ---")
            alertas_devolucao_ferramentas()
            time.sleep(2)

        elif opcao_relatorio == 19:
            print("\n--- Componentes Zerados e Demandados ---")
            componentes_sem_estoque_demandados()
            time.sleep(2)

        elif opcao_relatorio == 20:
            print("\n--- Tempo Médio de Reparo por Técnico ---")
            tempo_medio_reparo_tecnico()
            time.sleep(2)

        elif opcao_relatorio == 0:
            print("Voltando...")
            break

        else:
            print("Opção inválida!")
