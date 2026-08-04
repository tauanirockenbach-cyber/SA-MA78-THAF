-- Teste da role_admin_manutencao: 

-- User: tauani
-- Password: tauani123
-- Host: manutencao-thaf-samanutencao.b.aivencloud.com
-- Port: 16536

USE Manutencao;

SELECT * FROM Usuarios;

INSERT INTO Usuarios(nome_usuario, email_usuario, senha_hash, perfil_usuario, id_setor, data_cadastro)
VALUES ('Ivan Dahmer', 'ivan@empresa.com', 'hash_user_65', 'Entregador', 5, '2026-01-25');

UPDATE Usuarios
SET perfil_usuario = 'Supervisor'
WHERE email_usuario = 'ivan@empresa.com';

DELETE FROM Usuarios
WHERE email_usuario = 'ivan@empresa.com';