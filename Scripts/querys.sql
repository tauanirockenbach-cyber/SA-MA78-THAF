-- Quais máquinas estão em manutenção ou paradas?
select MM.nome_maquina, M.status_operacional 
from Modelos_Maquinas as MM
join Maquinas as M on MM.id_maquina = M.id_maquina
where status_operacional in ('Em Manutenção', 'Parado');

-- Histórico de manutenções de um equipamento específico
select M.tag_equipamento, MM.nome_maquina, M.ultima_manutencao
from Maquinas as M
join Modelos_Maquinas as MM on M.id_maquina = MM.id_maquina
where M.tag_equipamento = 'AJU-FR-05';

-- Histórico de manutenção de um tipo de máquina
select M.tag_equipamento, MM.nome_maquina, M.ultima_manutencao
from Maquinas as M
join Modelos_Maquinas as MM on M.id_maquina = MM.id_maquina
where MM.nome_maquina = 'Furadeira de Coluna';

-- Quais ordens de serviço foram abertas no mês atual (Junho de 2026)?
select id_os, tag_equipamento, descricao_falha, data_abertura
from Ordens_Servico
where data_abertura between '2026-06-01' and '2026-06-30';

-- Quem são os técnicos ativos?
select nome_usuario, email_usuario, status_usuario from Usuarios
where cargo_usuario = 'Tecnico' 
    and status_usuario = 'Ativo';

-- Alerta de estoque baixo!
select nome_peca, quantidade_estoque 
from Almoxarifado_Pecas
where quantidade_estoque < 10;

-- Quais OS estão abertas ou em andamento e quem é o técnico responsável?
select OS.id_os, OS.descricao_falha, OS.status_os, U.nome_usuario 
from Ordens_Servico as OS
join Usuarios as U on U.id_usuario = OS.id_tecnico_responsavel;

-- Qual o valor total em peças no almoxarifado?
select sum(quantidade_estoque * custo_unitario) as Valor_total 
from Almoxarifado_Pecas;

-- Quantas máquinas cada setor possui?
select S.nome_setor, count(MM.nome_maquina) as quantidade_maquinas 
from Setores as S
join Maquinas as M on M.id_setor = S.id_setor
join Modelos_Maquinas as MM on M.id_maquina = MM.id_maquina
group by S.nome_setor
order by quantidade_maquinas desc;

-- Relatório de Custos por Ordem de Serviço concluída
select OS.id_os, sum(OM.quantidade_utilizada * A.custo_unitario) as Valor_total 
from Ordens_Servico as OS
join OS_Materiais as OM on OM.id_os = OS.id_os
join Almoxarifado_Pecas as A on A.id_peca = OM.id_peca
where OS.status_os = 'Concluído'
group by OS.id_os;

-- Quais EPIs o técnico deve usar para realizar a OS número 1003?
select OS.descricao_falha, EPI.epis_obrigatorios 
from Ordens_Servico as OS
join OS_Seguranca as S on OS.id_os = S.id_os
join Matriz_Riscos_EPI as EPI on EPI.id_risco = S.id_risco
where OS.id_os = 1003;

-- OS concluídas por cada técnico
select U.nome_usuario, count(OS.id_os) as OS_concluidas 
from Usuarios as U
join Ordens_Servico as OS on OS.id_tecnico_responsavel = U.id_usuario
where status_os = 'Concluído'
group by U.nome_usuario;

-- Quais setores geraram o maior custo com manutenção de peças?
select S.nome_setor, sum(OM.quantidade_utilizada * A.custo_unitario) as Valor_gasto_pecas
from OS_Materiais as OM
join Almoxarifado_Pecas as A on A.id_peca = OM.id_peca
join Ordens_Servico as OS on OS.id_os = OM.id_os
join Maquinas as M on M.tag_equipamento = OS.tag_equipamento
join Setores as S on S.id_setor = M.id_setor
group by S.nome_setor
order by Valor_gasto_pecas DESC;

-- Quais ferramentas nunca foram utilizadas em nenhuma Ordem de Serviço?
select nome_ferramenta as ferramentas_nao_utilizadas 
from Almoxarifado_Ferramentas
where id_ferramenta not in (select id_ferramenta from OS_Ferramentas);

-- Quantidade de Máquina por Fabricante
select fabricante_maquina, count(nome_maquina) as quantidade_maquinas from Modelos_Maquinas
group by fabricante_maquina;

-- OS em andamento por cada técnico
select U.nome_usuario, count(OS.id_os) as OS_em_andamento 
from Usuarios as U
join Ordens_Servico as OS on OS.id_tecnico_responsavel = U.id_usuario
where status_os = 'Em andamento'
group by U.nome_usuario;

-- Quais ferramentas estão com o prazo de devolução expirado no dia de hoje ou marcadas com problemas, identificando o técnico solicitante e o almoxarife responsável.
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
JOIN Almoxarifado_Ferramentas AF ON MF.id_ferramenta = AF.id_ferramenta
JOIN Tecnicos T ON MF.id_tecnico_solicitante = T.id_tecnico
JOIN Usuarios U_Tec ON T.id_usuario = U_Tec.id_usuario
LEFT JOIN Usuarios U_Alm ON MF.id_almoxarife_entregador = U_Alm.id_usuario
WHERE MF.status_movimentacao = 'Atrasado'
   OR MF.status_movimentacao = 'Extraviado'
   OR (MF.data_devolucao_prevista < NOW() AND MF.data_devolucao_real IS NULL);


-- Quais componentes do almoxarifado que estão com saldo zero e que possuem ordens de serviço atreladas precisando desse material.
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
ORDER BY vezes_solicitada_em_os DESC;


-- Cronograma de riscos e EPIs obrigatórios por equipamento ativo.
SELECT DISTINCT
    M.tag_equipamento,
    MM.nome_maquina,
    S.nome_setor,
    MR.risco_nr01,
    MR.epis_obrigatorios
FROM Maquinas M
JOIN Modelos_Maquinas MM ON M.id_maquina = MM.id_maquina
JOIN Setores S ON M.id_setor = S.id_setor
JOIN Ordens_Servico OS ON M.tag_equipamento = OS.tag_equipamento
JOIN OS_Seguranca OSS ON OS.id_os = OSS.id_os
JOIN Matriz_Riscos_EPI MR ON OSS.id_risco = MR.id_risco
WHERE M.status_operacional = 'Operando'
ORDER BY S.nome_setor, M.tag_equipamento;


-- Exiba quais fabricantes e modelos específicos de equipamentos estão gerando o maior volume de ordens de serviço por falhas mecânicas/operacionais.
SELECT
    MM.fabricante_maquina,
    MM.nome_modelo,
    MM.potencia_especificacao,
    COUNT(OS.id_os) AS total_de_quebras_registradas
FROM Ordens_Servico OS
JOIN Maquinas M ON OS.tag_equipamento = M.tag_equipamento
JOIN Modelos_Maquinas MM ON M.id_maquina = MM.id_maquina
GROUP BY
    MM.id_maquina,
    MM.fabricante_maquina,
    MM.nome_modelo,
    MM.potencia_especificacao
ORDER BY total_de_quebras_registradas DESC;


-- Quais ferramentas foram alocadas/utilizadas em cada Ordem de Serviço?
SELECT 
    OSF.id_os,
    OS.descricao_falha,
    AF.nome_ferramenta
FROM OS_Ferramentas AS OSF
JOIN Ordens_Servico AS OS ON OS.id_os = OSF.id_os
JOIN Almoxarifado_Ferramentas AS AF ON AF.id_ferramenta = OSF.id_ferramenta
ORDER BY OSF.id_os ASC;

-- Quais ferramentas estão atualmente 'Em Uso' e qual o prazo limite para devolução?
SELECT 
    MF.id_movimentacao,
    AF.nome_ferramenta,
    U.nome_usuario AS tecnico_solicitante,
    MF.data_retirada,
    MF.data_devolucao_prevista
FROM Movimentacao_Ferramentas AS MF
JOIN Almoxarifado_Ferramentas AS AF ON MF.id_ferramenta = AF.id_ferramenta
JOIN Tecnicos AS T ON MF.id_tecnico_solicitante = T.id_tecnico
JOIN Usuarios AS U ON T.id_usuario = U.id_usuario
WHERE MF.status_movimentacao = 'Em Uso'
ORDER BY MF.data_devolucao_prevista ASC;

-- Qual é o perfil dos técnicos (nível, cargo, setor) e quem está disponível para chamados?
SELECT 
    U.nome_usuario,
    T.cargo_tecnico,
    T.nivel_experiencia,
    S.nome_setor,
    T.disponibilidade_tecnico
FROM Tecnicos AS T
JOIN Usuarios AS U ON T.id_usuario = U.id_usuario
LEFT JOIN Setores AS S ON T.id_setor = S.id_setor
ORDER BY 
    T.disponibilidade_tecnico ASC, 
    T.nivel_experiencia DESC;
