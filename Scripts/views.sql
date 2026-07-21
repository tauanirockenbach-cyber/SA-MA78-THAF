-- CRIAÇÃO DE VIEWS

-- Quais máquinas estão em manutenção ou paradas?
CREATE VIEW maquinas_manutencao_ou_paradas AS
select MM.nome_maquina, M.status_operacional 
from Modelos_Maquinas as MM
join Maquinas as M on MM.id_maquina = M.id_maquina
where status_operacional in ('Em Manutenção', 'Parado');

-- Histórico de manutenções de um equipamento específico
CREATE VIEW historico_manutencao_maq_especifica AS
select M.tag_equipamento, MM.nome_maquina, M.ultima_manutencao
from Maquinas as M
join Modelos_Maquinas as MM on M.id_maquina = MM.id_maquina
where M.tag_equipamento = 'AJU-FR-05';

-- Histórico de manutenção de um tipo de máquina
CREATE VIEW historico_manutencao_tipo_maq AS
select M.tag_equipamento, MM.nome_maquina, M.ultima_manutencao
from Maquinas as M
join Modelos_Maquinas as MM on M.id_maquina = MM.id_maquina
where MM.nome_maquina = 'Furadeira de Coluna';

-- Quais ordens de serviço foram abertas no mês (Junho de 2026)?
CREATE VIEW os_junho_2026 AS
select id_os, tag_equipamento, descricao_falha, data_abertura
from Ordens_Servico
where data_abertura between '2026-06-01' and '2026-06-30';

-- Quem são os técnicos ativos?
CREATE VIEW tecnicos_ativos AS
select nome_usuario, email_usuario, status_usuario from Usuarios
where cargo_usuario = 'Tecnico' 
    and status_usuario = 'Ativo';

-- Alerta de estoque baixo!
CREATE VIEW estoque_baixo AS
select nome_peca, quantidade_estoque 
from Almoxarifado_Pecas
where quantidade_estoque < 10;

-- Quais OS estão abertas ou em andamento e quem é o técnico responsável?
CREATE VIEW os_andamento AS
select OS.id_os, OS.descricao_falha, OS.status_os, U.nome_usuario
from Ordens_Servico as OS
join Usuarios as U on U.id_usuario = OS.id_usuario
where OS.status_os in ('Aberto', 'Em andamento');

-- Qual o valor total em peças no almoxarifado?
CREATE VIEW valor_total_pecas AS
select sum(quantidade_estoque * custo_unitario) as Valor_total 
from Almoxarifado_Pecas;

-- Quantas máquinas cada setor possui?
CREATE VIEW quant_maquinas_setor AS
select S.nome_setor, count(MM.nome_maquina) as quantidade_maquinas 
from Setores as S
join Maquinas as M on M.id_setor = S.id_setor
join Modelos_Maquinas as MM on M.id_maquina = MM.id_maquina
group by S.nome_setor
order by quantidade_maquinas desc;

-- Relatório de Custos por Ordem de Serviço concluída
CREATE VIEW custos_os_concluida AS
select OS.id_os, sum(OM.quantidade_utilizada * A.custo_unitario) as Valor_total 
from Ordens_Servico as OS
join OS_Materiais as OM on OM.id_os = OS.id_os
join Almoxarifado_Pecas as A on A.id_peca = OM.id_peca
where OS.status_os = 'Concluído'
group by OS.id_os;

-- Quais EPIs o técnico deve usar para realizar a OS número 1003?
CREATE VIEW epi_os_1003 AS
select OS.descricao_falha, EPI.epis_obrigatorios 
from Ordens_Servico as OS
join OS_Seguranca as S on OS.id_os = S.id_os
join Matriz_Riscos_EPI as EPI on EPI.id_risco = S.id_risco
where OS.id_os = 1003;

-- OS concluídas por cada técnico
CREATE VIEW os_concluida_por_tecnico AS
select U.nome_usuario, count(OS.id_os) as OS_concluidas 
from Usuarios as U
join Ordens_Servico as OS on OS.id_usuario = U.id_usuario
where status_os = 'Concluído'
group by U.nome_usuario;

-- Quais setores geraram o maior custo com manutenção de peças?
CREATE VIEW setores_que_geram_mais_custo AS
select S.nome_setor, sum(OM.quantidade_utilizada * A.custo_unitario) as Valor_gasto_pecas
from OS_Materiais as OM
join Almoxarifado_Pecas as A on A.id_peca = OM.id_peca
join Ordens_Servico as OS on OS.id_os = OM.id_os
join Maquinas as M on M.tag_equipamento = OS.tag_equipamento
join Setores as S on S.id_setor = M.id_setor
group by S.nome_setor
order by Valor_gasto_pecas DESC;

-- Quais ferramentas nunca foram utilizadas em nenhuma Ordem de Serviço?
CREATE VIEW ferramentas_nunca_usadas_os AS
select nome_ferramenta as ferramentas_nao_utilizadas 
from Almoxarifado_Ferramentas
where id_ferramenta not in (select id_ferramenta from OS_Ferramentas);

-- Quantidade de Máquina por Fabricante
CREATE VIEW quant_maquinas_fabricante AS
select fabricante_maquina, count(nome_maquina) as quantidade_maquinas from Modelos_Maquinas
group by fabricante_maquina;

-- OS em andamento por cada técnico
CREATE VIEW os_em_andamento_por_tecnico AS
select U.nome_usuario, count(OS.id_os) as OS_em_andamento 
from Usuarios as U
join Ordens_Servico as OS on OS.id_usuario = U.id_usuario
where status_os = 'Em andamento'
group by U.nome_usuario;

-- Quais ferramentas estão com o prazo de devolução expirado no dia de hoje ou marcadas com problemas, identificando o técnico solicitante e o almoxarife responsável.
CREATE VIEW alertas_devolucao_ferramentas AS
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
   OR (MF.data_devolucao_prevista < NOW() AND MF.data_devolucao_real IS NULL);

-- Quais componentes do almoxarifado que estão com saldo zero e que possuem ordens de serviço atreladas precisando desse material.
CREATE VIEW componentes_sem_estoque_demandados AS
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
CREATE VIEW seguranca_epis_por_equipamento AS
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
CREATE VIEW ranking_falhas_por_modelo AS
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

-- Indicador de tempo médio de reparo por técnico
CREATE VIEW tempo_medio_reparo_tecnico AS
select U.nome_usuario, 
    sec_to_time(avg(time_to_sec(timediff(OS.hh_fim, OS.hh_inicio)))) as tempo_medio_trabalho 
from Usuarios as U
join Ordens_Servico as OS on OS.id_usuario = U.id_usuario
where status_os = 'Concluído'
    and OS.hh_fim is not null
group by U.nome_usuario;

-- Componentes mais utilizados pela fábrica
CREATE VIEW pecas_mais_usadas_fabrica AS
select nome_peca, sum(OM.id_peca) as quantidade_pecas_usadas, S.nome_setor as setor_mais_usado 
from OS_Materiais as OM 
join Almoxarifado_Pecas as AP on OM.id_peca = AP.id_peca
join Ordens_Servico as OS on OM.id_os = OS.id_os
join Maquinas as M on M.tag_equipamento = OS.tag_equipamento
join Setores as S on M.id_setor = S.id_setor
group by S.nome_setor, nome_peca
order by quantidade_pecas_usadas desc;

-- Máquina que quebrou mais nos últimos 5 anos
CREATE VIEW historico_falhas_equipamento_5_anos AS
select MM.nome_maquina, M.tag_equipamento, count(OS.id_os) as quantidade_falhas
from Maquinas as M
join Modelos_Maquinas as MM on M.id_maquina = MM.id_maquina
join Ordens_Servico as OS on OS.tag_equipamento = M.tag_equipamento
where data_abertura >= date_sub(now(), interval 5 year)
group by tag_equipamento
order by quantidade_falhas desc;

-- Painel de Status: Onde está cada pessoa (Técnicos)?
CREATE VIEW painel_status_tecnicos AS
select U.disponibilidade_tecnico, count(U.id_usuario) as quantidade_tecnicos
from Usuarios as U
where cargo_usuario = 'Tecnico'
group by U.disponibilidade_tecnico;