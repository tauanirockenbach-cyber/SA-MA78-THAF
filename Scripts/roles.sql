-- Criar os utilizadores corretamente com '%' (permitindo o acesso a partir do seu IP)
CREATE USER 'tauani'@'%' IDENTIFIED BY 'tauani123';
CREATE USER 'felipe'@'%' IDENTIFIED BY 'felipe123';
CREATE USER 'ana'@'%' IDENTIFIED BY 'ana123';
CREATE USER 'henrique'@'%' IDENTIFIED BY 'henrique123';

-- Criação das Roles
CREATE ROLE 'role_admin_manutencao',
'role_supervisor_manutencao', 
'role_tecnico_manutencao', 
'role_auditor_manutencao';

-- Privilégio total
GRANT ALL PRIVILEGES ON Manutencao.* TO 'role_admin_manutencao';

-- Privilégios de CRUD padrão
GRANT SELECT, INSERT, UPDATE, DELETE ON Manutencao.* TO 'role_supervisor_manutencao';

-- Privilégios de leitura e inserção (criação de registros)
GRANT SELECT, INSERT ON Manutencao.* TO 'role_tecnico_manutencao';

-- Privilégio apenas de leitura
GRANT SELECT ON Manutencao.* TO 'role_auditor_manutencao';

GRANT 'role_admin_manutencao' TO 'tauani'@'%';
GRANT 'role_supervisor_manutencao' TO 'felipe'@'%';
GRANT 'role_tecnico_manutencao' TO 'ana'@'%';
GRANT 'role_auditor_manutencao' TO 'henrique'@'%';

SET DEFAULT ROLE 'role_admin_manutencao' TO 'tauani'@'%';
SET DEFAULT ROLE 'role_supervisor_manutencao' TO 'felipe'@'%';
SET DEFAULT ROLE 'role_tecnico_manutencao' TO 'ana'@'%';
SET DEFAULT ROLE 'role_auditor_manutencao' TO 'henrique'@'%';

-- Aplicar todas as alterações
FLUSH PRIVILEGES;

-- SELECT * FROM mysql.user;
