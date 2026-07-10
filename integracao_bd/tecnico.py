from database import conectar


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
        if valor.lower() in [o.lower() for o in opcoes_validas]:
            return valor
        print("Opção inválida!")


def buscar_usuario_por_id(cursor, id_usuario):
    """Busca email e telefone do usuário para preencher os campos de
    Tecnicos que são chave estrangeira para Usuarios (evita erro de FK
    por digitação errada e evita pedir dado duplicado ao usuário)."""
    cursor.execute(
        "SELECT email_usuario, telefone_usuario FROM Usuarios WHERE id_usuario = %s",
        (id_usuario,)
    )
    return cursor.fetchone()


def tecnico_ja_existe(cursor, id_usuario):
    cursor.execute(
        "SELECT 1 FROM Tecnicos WHERE id_usuario = %s",
        (id_usuario,)
    )
    return cursor.fetchone() is not None


def listar_usuarios_disponiveis(cursor):
    """Mostra só os usuários que existem em Usuarios e AINDA NÃO estão em
    Tecnicos. Isso evita que a pessoa tente usar um ID que já é técnico
    ou que confunda id_usuario com id_tecnico."""
    sql = """
    SELECT u.id_usuario, u.nome_usuario
    FROM Usuarios u
    LEFT JOIN Tecnicos t ON t.id_usuario = u.id_usuario
    WHERE t.id_usuario IS NULL
    ORDER BY u.id_usuario
    """
    cursor.execute(sql)
    return cursor.fetchall()


def ler_id_usuario_para_novo_tecnico():
    """Mostra os usuários disponíveis (que ainda não são técnicos) e fica
    pedindo um ID até receber um válido dessa lista. Retorna None se o
    usuário cancelar digitando 0."""
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        disponiveis = listar_usuarios_disponiveis(cursor)

        if not disponiveis:
            print("Não há usuários disponíveis para virar técnico (todos já são técnicos).")
            return None

        print("\nUsuários disponíveis para cadastrar como técnico (o ID do técnico será igual ao ID abaixo):")
        for id_usuario, nome in disponiveis:
            print(f"  ID: {id_usuario} | Nome: {nome}")

        ids_disponiveis = {id_usuario for id_usuario, _ in disponiveis}

        while True:
            id_usuario = ler_inteiro("\nID do usuário vinculado (0 para cancelar): ")
            if id_usuario == 0:
                return None

            if id_usuario not in ids_disponiveis:
                # Verifica o motivo exato para dar uma mensagem clara
                usuario = buscar_usuario_por_id(cursor, id_usuario)
                if not usuario:
                    print("Não existe usuário com esse ID. Escolha um ID da lista acima.")
                elif tecnico_ja_existe(cursor, id_usuario):
                    print("Esse usuário já é técnico. Escolha um ID da lista acima.")
                else:
                    print("ID inválido. Escolha um ID da lista acima.")
                continue

            return id_usuario

    except Exception as erro:
        print("Erro ao verificar o usuário:", erro)
        return None

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def listar_tecnicos():
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # Nome de coluna corrigido: é "disponibilidade_tecnico", não "disponibilidade_tecnica"
        sql = """
        SELECT t.id_tecnico, t.id_usuario, t.email_usuario, t.telefone_usuario,
               t.id_setor, t.cargo_tecnico, t.nivel_experiencia, t.disponibilidade_tecnico
        FROM Tecnicos AS t
        """
        cursor.execute(sql)
        dados = cursor.fetchall()

        if not dados:
            print("Nenhum técnico cadastrado.")
            return

        for tecnico in dados:
            print(tecnico)

    except Exception as erro:
        print("Erro ao listar técnicos:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def cadastrar_tecnico(id_usuario, id_setor, cargo_tecnico, nivel_experiencia, disponibilidade_tecnico):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # email_usuario e telefone_usuario são FK para Usuarios: buscamos
        # do próprio usuário em vez de pedir digitado, para não violar a FK.
        usuario = buscar_usuario_por_id(cursor, id_usuario)
        if not usuario:
            print("Não existe usuário com esse ID. Cadastro cancelado.")
            return

        email_usuario, telefone_usuario = usuario

        # Tecnicos tem 3 chaves UNIQUE: id_usuario, email_usuario e
        # telefone_usuario. Um id_usuario "livre" não garante que o e-mail
        # ou telefone dele não estejam presos a um registro órfão antigo
        # em Tecnicos (de antes das correções, quando eram digitados à mão).
        cursor.execute("SELECT id_tecnico, id_usuario FROM Tecnicos WHERE email_usuario = %s", (email_usuario,))
        conflito_email = cursor.fetchone()
        if conflito_email:
            print(f"Não é possível cadastrar: o e-mail '{email_usuario}' já está em uso pelo "
                  f"técnico de ID {conflito_email[0]} (id_usuario {conflito_email[1]}). "
                  "Provavelmente é um registro antigo/órfão — apague-o ou corrija antes de continuar.")
            return

        cursor.execute("SELECT id_tecnico, id_usuario FROM Tecnicos WHERE telefone_usuario = %s", (telefone_usuario,))
        conflito_telefone = cursor.fetchone()
        if conflito_telefone:
            print(f"Não é possível cadastrar: o telefone '{telefone_usuario}' já está em uso pelo "
                  f"técnico de ID {conflito_telefone[0]} (id_usuario {conflito_telefone[1]}). "
                  "Provavelmente é um registro antigo/órfão — apague-o ou corrija antes de continuar.")
            return

        # id_tecnico é AUTO_INCREMENT, mas inserimos explicitamente o mesmo
        # valor de id_usuario, para que o ID do técnico seja sempre idêntico
        # ao ID do usuário (nunca um número diferente gerado pelo banco).
        sql = """
        INSERT INTO Tecnicos
            (id_tecnico, id_usuario, email_usuario, telefone_usuario, id_setor,
             cargo_tecnico, nivel_experiencia, disponibilidade_tecnico)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (id_usuario, id_usuario, email_usuario, telefone_usuario, id_setor,
                   cargo_tecnico, nivel_experiencia, disponibilidade_tecnico)

        cursor.execute(sql, valores)
        conexao.commit()

        print(f"Técnico(a) cadastrado(a) com sucesso! ID do técnico: {id_usuario} (igual ao ID do usuário)")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao cadastrar técnico:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_experiencia_tecnico(id_tecnico, nivel_experiencia):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        UPDATE Tecnicos
        SET nivel_experiencia = %s
        WHERE id_tecnico = %s
        """
        valores = (nivel_experiencia, id_tecnico)
        cursor.execute(sql, valores)
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"Nível de experiência do técnico {id_tecnico} atualizado com sucesso!")
        else:
            print("Técnico não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao atualizar experiência do técnico:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def atualizar_disponibilidade_tecnico(id_tecnico, disponibilidade_tecnico):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = """
        UPDATE Tecnicos
        SET disponibilidade_tecnico = %s
        WHERE id_tecnico = %s
        """
        valores = (disponibilidade_tecnico, id_tecnico)
        cursor.execute(sql, valores)
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"Disponibilidade do técnico {id_tecnico} atualizada com sucesso!")
        else:
            print("Técnico não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao atualizar disponibilidade do técnico:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def deletar_tecnico(id_tecnico):
    conexao = None
    cursor = None
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        sql = "DELETE FROM Tecnicos WHERE id_tecnico = %s"
        cursor.execute(sql, (id_tecnico,))
        conexao.commit()

        if cursor.rowcount > 0:
            print(f"Técnico {id_tecnico} deletado com sucesso!")
        else:
            print("Técnico não encontrado.")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print("Erro ao deletar técnico:", erro)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


def opcao_desejada_tecnico():
    opcoes_nivel = ['junior', 'pleno', 'senior', 'master']
    opcoes_disponibilidade = ['disponível', 'em campo', 'férias', 'afastado']

    while True:
        print("\n------ Menu Técnico ------")
        print("1 = Listar técnicos")
        print("2 = Cadastrar técnico")
        print("3 = Atualizar experiência do técnico")
        print("4 = Atualizar disponibilidade do técnico")
        print("5 = Deletar técnico")
        print("0 = Sair")

        opcao_tecnico = ler_inteiro("Coloque qual opção deseja: ")

        if opcao_tecnico == 1:
            print("\n--- Lista de Técnicos ---")
            listar_tecnicos()

        elif opcao_tecnico == 2:
            print("\n--- Cadastrar Novo Técnico ---")
            id_usuario = ler_id_usuario_para_novo_tecnico()
            if id_usuario is None:
                print("Cadastro cancelado.")
                continue
            id_setor = ler_inteiro("ID do setor: ")
            cargo_tecnico = input("Cargo técnico: ")
            nivel_experiencia = ler_opcao_valida(
                "Nível de experiência (Junior, Pleno, Senior, Master): ", opcoes_nivel
            )
            disponibilidade_tecnico = ler_opcao_valida(
                "Disponibilidade (Disponível, Em Campo, Férias, Afastado): ", opcoes_disponibilidade
            )

            cadastrar_tecnico(id_usuario, id_setor, cargo_tecnico,
                              nivel_experiencia, disponibilidade_tecnico)

        elif opcao_tecnico == 3:
            print("\n--- Atualizar Experiência do Técnico ---")
            id_tecnico = ler_inteiro("ID do técnico (igual ao ID do usuário): ")
            nivel_experiencia = ler_opcao_valida(
                "Novo nível de experiência (Junior, Pleno, Senior, Master): ", opcoes_nivel
            )
            atualizar_experiencia_tecnico(id_tecnico, nivel_experiencia)

        elif opcao_tecnico == 4:
            print("\n--- Atualizar Disponibilidade do Técnico ---")
            id_tecnico = ler_inteiro("ID do técnico (igual ao ID do usuário): ")
            disponibilidade_tecnico = ler_opcao_valida(
                "Nova disponibilidade (Disponível, Em Campo, Férias, Afastado): ", opcoes_disponibilidade
            )
            atualizar_disponibilidade_tecnico(id_tecnico, disponibilidade_tecnico)

        elif opcao_tecnico == 5:
            print("\n--- Deletar Técnico ---")
            id_tecnico = ler_inteiro("ID do técnico que deseja deletar (igual ao ID do usuário): ")
            deletar_tecnico(id_tecnico)

        elif opcao_tecnico == 0:
            print("Voltando")
            break

        else:
            print("Opção inválida!")