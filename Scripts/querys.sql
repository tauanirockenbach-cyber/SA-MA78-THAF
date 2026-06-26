-- Quais ferramentas estão em manutenção ou calibração?
select nome_ferramenta, status_ferramenta 
from Almoxarifado_Ferramentas 
where status_ferramenta in ('Manutenção');

-- Histórico de manutenções de um equipamento específico
select tag_equipamento, nome_maquina, ultima_manutencao
from Maquinas_Ativos
where tag_equipamento = 'AJU-FR-05';

-- Histórico de manutenção de um tipo de máquina
select tag_equipamento, nome_maquina, ultima_manutencao
from Maquinas_Ativos
where nome_maquina = 'Furadeira de Coluna';

-- Quais ordens de serviço foram abertas no mês atual (Junho de 2026)?
select id_os, tag_equipamento, descricao_falha, data_abertura
from Ordens_Servico
where data_abertura between '2026-06-01' and '2026-06-30';

-- Quais máquinas estão paradas no momento?
select nome_maquina, tag_equipamento, localizacao_maquina, status_operacional
from Maquinas_Ativos
where status_operacional = 'Em Manutenção' or status_operacional = 'Parado';

-- Quem são os técnicos ativos?
select nome_usuario, email_usuario, status_usuario from Usuarios
where perfil_usuario = 'Tecnico' 
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
select S.nome_setor, count(M.nome_maquina) as quantidade_maquinas 
from Setores as S
join Maquinas_Ativos as M on M.id_setor = S.id_setor
group by S.nome_setor
order by quantidade_maquinas desc;

-- Relatório de Custos por Ordem de Serviço concluída´
select OS.id_os, sum(OM.quantidade_utilizada * A.custo_unitario) as Valor_total 
from Ordens_Servico as OS
join OS_Materiais as OM on OM.id_os = OS.id_os
join Almoxarifado_Pecas as A on A.id_peca = OM.id_peca
where OS.status_os = 'Concluído'
group by OS.id_os;

-- Quais EPIs o técnico deve usar para realizar a OS número 1001?
select OS.descricao_falha, EPI.epis_obrigatorios 
from Ordens_Servico as OS
join OS_Seguranca as S on OS.id_os = S.id_os
join Matriz_Riscos_EPI as EPI on EPI.id_risco = S.id_risco
where OS.id_os = 1001;

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
join Maquinas_Ativos as MA on MA.tag_equipamento = OS.tag_equipamento
join Setores as S on S.id_setor = MA.id_setor
group by S.nome_setor
order by Valor_gasto_pecas DESC;

-- Quais ferramentas nunca foram utilizadas em nenhuma Ordem de Serviço?
select nome_ferramenta as ferramentas_nao_utilizadas 
from Almoxarifado_Ferramentas
where id_ferramenta not in (select id_ferramenta from OS_Ferramentas);

-- Quantidade de Máquina por Fabricante
select fabricante_maquina, count(nome_maquina) from Modelos_Maquinas
group by fabricante_maquina;

-- Qual foi o ultimo registro de atividade de cada usuário?
select nome_usuario, max(data_hora)
from Logs_Acesso as LA
join Usuarios as U on LA.id_usuario = U.id_usuario
group by LA.id_usuario;

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
    U_Sol.nome_usuario AS técnico_solicitante,
    U_Ent.nome_usuario AS almoxarife_entregador,
    MF.data_retirada,
    MF.data_devolucao_prevista,
    MF.status_movimentacao
FROM Movimentacao_Ferramentas MF
JOIN Almoxarifado_Ferramentas AF ON MF.id_ferramenta = AF.id_ferramenta
JOIN Usuarios U_Sol ON MF.id_solicitante = U_Sol.id_usuario
LEFT JOIN Usuarios U_Ent ON MF.id_entregador = U_Ent.id_usuario
WHERE MF.status_movimentacao = 'Atrasado' 
   OR (MF.data_devolucao_prevista < NOW() AND MF.data_devolucao_real IS NULL);

-- Quais componentes do almoxarifado que estão com saldo zero e que possuem ordens de serviço atreladas precisando desse material. 

SELECT 
    AP.id_peca,
    AP.nome_peca,
    AP.unidade_medida,
    AP.custo_unitario,
    COUNT(OSM.id_os) AS vezes_solicitada_em_os
FROM Almoxarifado_Pecas AP
LEFT JOIN OS_Materiais OSM ON AP.id_peca = OSM.id_peca
WHERE AP.quantidade_estoque = 0
GROUP BY AP.id_peca, AP.nome_peca
ORDER BY vezes_solicitada_em_os DESC;

-- Cronograma de riscos e EPIs obrigatórios por equipamento ativo 
SELECT DISTINCT
    MA.tag_equipamento,
    MA.nome_maquina,
    S.nome_setor,
    MR.risco_nr01,
    MR.epis_obrigatorios
FROM Maquinas_Ativos MA
JOIN Setores S ON MA.id_setor = S.id_setor
JOIN Ordens_Servico OS ON MA.tag_equipamento = OS.tag_equipamento
JOIN OS_Seguranca OSS ON OS.id_os = OSS.id_os
JOIN Matriz_Riscos_EPI MR ON OSS.id_risco = MR.id_risco
ORDER BY S.nome_setor, MA.tag_equipamento;


-- Exiba quais fabricantes e modelos específicos de equipamentos estão gerando o maior volume de ordens de serviço por falhas mecânicas/operacionais. 

SELECT 
    MM.fabricante_maquina,
    MM.nome_modelo,
    MM.potencia_especificacao,
    COUNT(OS.id_os) AS total_de_quebras_registradas
FROM Ordens_Servico OS
JOIN Maquinas_Ativos MA ON OS.tag_equipamento = MA.tag_equipamento
JOIN Modelos_Maquinas MM ON MA.id_modelo = MM.id_modelo
GROUP BY MM.id_modelo, MM.fabricante_maquina, MM.nome_modelo, MM.potencia_especificacao
ORDER BY total_de_quebras_registradas DESC;
