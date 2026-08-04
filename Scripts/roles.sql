-- 1. Criação dos usuários com permissão de acesso externo
CREATE USER 'tauani'@'%' IDENTIFIED BY 'tauani123'; 
CREATE USER 'felipe'@'%' IDENTIFIED BY 'felipe123'; 
CREATE USER 'ana'@'%' IDENTIFIED BY 'ana123'; 
CREATE USER 'henrique'@'%' IDENTIFIED BY 'henrique123'; 

-- 2. Criação das Roles 
CREATE ROLE 'role_admin_manutencao', 
            'role_supervisor_manutencao', 
            'role_tecnico_manutencao', 
            'role_auditor_manutencao'; 

-- 3. Atribuição de privilégios para cada Role no banco 'Manutencao'
GRANT ALL PRIVILEGES ON Manutencao.* TO 'role_admin_manutencao'; 
GRANT SELECT, INSERT, UPDATE, DELETE ON Manutencao.* TO 'role_supervisor_manutencao'; 
GRANT SELECT, INSERT ON Manutencao.* TO 'role_tecnico_manutencao'; 
GRANT SELECT ON Manutencao.* TO 'role_auditor_manutencao'; 

-- 4. Vinculação das Roles aos respectivos usuários
GRANT 'role_admin_manutencao' TO 'tauani'@'%'; 
GRANT 'role_supervisor_manutencao' TO 'felipe'@'%'; 
GRANT 'role_tecnico_manutencao' TO 'ana'@'%'; 
GRANT 'role_auditor_manutencao' TO 'henrique'@'%'; 

-- 5. Definição das Roles padrão (obrigatório para ativar ao logar)
SET DEFAULT ROLE 'role_admin_manutencao' TO 'tauani'@'%'; 
SET DEFAULT ROLE 'role_supervisor_manutencao' TO 'felipe'@'%'; 
SET DEFAULT ROLE 'role_tecnico_manutencao' TO 'ana'@'%'; 
SET DEFAULT ROLE 'role_auditor_manutencao' TO 'henrique'@'%'; 

-- 6. Configuração do servidor para ativar automaticamente as Roles no login
SET GLOBAL activate_all_roles_on_login = ON;

-- 7. Atualização da tabela de permissões na memória
FLUSH PRIVILEGES; 
