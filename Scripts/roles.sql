-- Active: 1782931087954@@manutencao-thaf-samanutencao.b.aivencloud.com@16536@Manutencao

#Criação dos usuários
CREATE USER 'tauani'@'localhost' IDENTIFIED BY'tauani123';
CREATE USER 'felipe'@'localhost' IDENTIFIED BY'felipe123';
CREATE USER 'ana'@'localhost' IDENTIFIED BY'ana123';
CREATE USER 'henrique'@'localhost' IDENTIFIED BY'henrique123';


#Criação das Roles
CREATE ROLE 'role_admin_manutencao',
'role_supervisor_manutencao', 
'role_tecnico_manutencao', 
'role_auditor_manutencao';

-- 3. Atribuição de Privilégios para as Roles
-- Privilégio total
GRANT ALL PRIVILEGES ON Manutencao.* TO 'role_admin_manutencao';

-- Privilégios de CRUD padrão
GRANT SELECT, INSERT, UPDATE, DELETE ON Manutencao.* TO 'role_supervisor_manutencao';

-- Privilégios de leitura e inserção (criação de registros)
GRANT SELECT, INSERT ON Manutencao.* TO 'role_tecnico_manutencao';

-- Privilégio apenas de leitura
GRANT SELECT ON Manutencao.* TO 'role_auditor_manutencao';

-- 4. Associação das Roles aos Usuários (Exemplo de distribuição)
GRANT 'role_admin_manutencao' TO 'tauani'@'localhost';

GRANT 'role_supervisor_manutencao' TO 'felipe'@'localhost';

GRANT 'role_tecnico_manutencao' TO 'ana'@'localhost';

GRANT 'role_auditor_manutencao' TO 'henrique'@'localhost';


-- 5. Ativação das Roles (Para que as roles sejam ativas quando o usuário logar)
SET DEFAULT ROLE 'role_admin_manutencao' TO 'tauani'@'localhost';
SET DEFAULT ROLE 'role_supervisor_manutencao' TO 'felipe'@'localhost';
SET DEFAULT ROLE 'role_tecnico_manutencao' TO 'ana'@'localhost';
SET DEFAULT ROLE 'role_auditor_manutencao' TO 'henrique'@'localhost';

-- 6. Aplicação das mudanças
FLUSH PRIVILEGES;