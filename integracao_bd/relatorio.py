def relatorio_producao_por_setor():
    # conecta no banco
    conexao = conectar()
    cursor = conexao.cursor()

    # soma a produção por setor
    sql = """
    SELECT 
        s.nome AS setor,
        SUM(o.quantidade_produzida) AS total_produtos
    FROM setor s
    JOIN funcionario f
        ON f.id_setor = s.id_setor
    JOIN ordem_producao o
        ON o.id_funcionario = f.id_funcionario
    GROUP BY s.nome
    ORDER BY total_produtos DESC
    """
    cursor.execute(sql)
    dados = cursor.fetchall()

    # imprime o relatório
    print("\n ----- Produção por setor -----")
    for relatorio in dados:
        print(f"\nSetor: {relatorio[0]}")
        print(f"\nTotal Produzido: {relatorio[1]}")
        print("-" * 40)

    cursor.close()
    conexao.close()


if __name__ == "__main__":
    relatorio_producao_por_setor()