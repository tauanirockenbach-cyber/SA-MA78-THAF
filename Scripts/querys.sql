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

