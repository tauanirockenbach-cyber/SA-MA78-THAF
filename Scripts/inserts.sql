INSERT INTO Setores (id_setor, nome_setor, descricao_setor) VALUES
(1, 'Laboratório CNC', 'Setor responsável por usinagem computorizada'),
(2, 'Laboratório de Ajustagem', 'Setor de ajustagem mecânica e furação'),
(3, 'Laboratório de Ferramentaria', 'Manutenção e fabricação de matrizes/ferramentas'),
(4, 'Caldeiraria', 'Setor de soldagem, corte e conformação de chapas'),
(5, 'Laboratório de Manutenção II', 'Setor focado em manutenção corretiva e preventiva pesada'),
(6, 'Química', 'Análises químicas e controle de fluidos');

INSERT INTO Usuarios (nome_usuario, email_usuario, senha_hash, perfil_usuario, status_usuario, id_setor) VALUES
('Tauani', 'tauani@empresa.com', 'hash_senha_1', 'CEO', 'Ativo', 1), -- ID 1
('FelipeM', 'felipem@empresa.com', 'hash_senha_2', 'Diretor', 'Ativo', 2), -- ID 2
('Henrique', 'henrique@empresa.com', 'hash_senha_3', 'Gerente', 'Ativo', 5), -- ID 3
('Ana', 'ana@empresa.com', 'hash_senha_4', 'Coordenador', 'Ativo', 6), -- ID 4
('Carlos Silva', 'carlos.cnc@empresa.com', 'hash_tec_6', 'Supervisor', 'Ativo', 1), -- ID 5
('Marcos Souza', 'marcos.cnc@empresa.com', 'hash_tec_7', 'Tecnico', 'Ativo', 1), -- ID 6
('Julia Costa', 'julia.cnc@empresa.com', 'hash_tec_8', 'Tecnico', 'Ativo', 1), -- ID 7
('Lucas Pereira', 'lucas.cnc@empresa.com', 'hash_tec_9', 'Tecnico', 'Ativo', 1), -- ID 8
('Fernanda Lima', 'fernanda.cnc@empresa.com', 'hash_tec_10', 'Tecnico', 'Ativo', 1), -- ID 9
('Roberto Alves', 'roberto.cnc@empresa.com', 'hash_tec_11', 'Tecnico', 'Ativo', 1), -- ID 10
('Amanda Rocha', 'amanda.cnc@empresa.com', 'hash_tec_12', 'Tecnico', 'Ativo', 1), -- ID 11
('Bruno Melo', 'bruno.melo@empresa.com', 'hash_tec_13', 'Supervisor', 'Ativo', 1), -- ID 12
('Camila Dias', 'camila.cnc@empresa.com', 'hash_tec_14', 'Tecnico', 'Ativo', 1), -- ID 13
('Diego Martins', 'diego.cnc@empresa.com', 'hash_tec_15', 'Tecnico', 'Ativo', 1), -- ID 14
('Edson Ribeiro', 'edson.aju@empresa.com', 'hash_tec_16', 'Supervisor', 'Ativo', 2), -- ID 15
('Fabio Santos', 'fabio.aju@empresa.com', 'hash_tec_17', 'Tecnico', 'Ativo', 2), -- ID 16
('Gustavo Lima', 'gustavo.aju@empresa.com', 'hash_tec_18', 'Tecnico', 'Ativo', 2), -- ID 17
('Igor Gomes', 'igor.aju@empresa.com', 'hash_tec_19', 'Tecnico', 'Ativo', 2), -- ID 18
('Juliana Ramos', 'juliana.aju@empresa.com', 'hash_tec_20', 'Tecnico', 'Ativo', 2), -- ID 19
('Leonardo Cruz', 'leonardo.cruz@empresa.com', 'hash_tec_21', 'Tecnico', 'Inativo', 2), -- ID 20
('Marcelo Vieira', 'marcelo.aju@empresa.com', 'hash_tec_22', 'Tecnico', 'Ativo', 2), -- ID 21
('Nadia Souza', 'nadia.aju@empresa.com', 'hash_tec_23', 'Tecnico', 'Ativo', 2), -- ID 22
('Otavio Reis', 'otavio.aju@empresa.com', 'hash_tec_24', 'Tecnico', 'Ativo', 2), -- ID 23
('Patricia Cruz', 'patricia.aju@empresa.com', 'hash_tec_25', 'Tecnico', 'Ativo', 2), -- ID 24
('Ricardo Oliveira', 'ricardo.fer@empresa.com', 'hash_tec_26', 'Tecnico', 'Inativo', 3), -- ID 25
('Samuel Filho', 'samuel.fer@empresa.com', 'hash_tec_27', 'Tecnico', 'Ativo', 3), -- ID 26
('Thiago Cardoso', 'thiago.fer@empresa.com', 'hash_tec_28', 'Supervisor', 'Ativo', 3), -- ID 27
('Vitor Barbosa', 'vitor.fer@empresa.com', 'hash_tec_29', 'Tecnico', 'Ativo', 3), -- ID 28
('Alexandre Silva', 'alexandre.fer@empresa.com', 'hash_tec_30', 'Tecnico', 'Ativo', 3), -- ID 29
('Daniela Nunes', 'daniela.fer@empresa.com', 'hash_tec_31', 'Tecnico', 'Ativo', 3), -- ID 30
('Eduardo Jorge', 'eduardo.fer@empresa.com', 'hash_tec_32', 'Tecnico', 'Ativo', 3), -- ID 31
('Felipe Augusto', 'felipe.fer@empresa.com', 'hash_tec_33', 'Tecnico', 'Ativo', 3), -- ID 32
('Gabriel Neves', 'gabriel.neves@empresa.com', 'hash_tec_34', 'Tecnico', 'Ativo', 3), -- ID 33
('Helena Paschoal', 'helena.fer@empresa.com', 'hash_tec_35', 'Tecnico', 'Ativo', 3), -- ID 34
('Jonas Batista', 'jonas.cal@empresa.com', 'hash_tec_36', 'Tecnico', 'Ativo', 4), -- ID 35
('Kevin Rodrigues', 'kevin.cal@empresa.com', 'hash_tec_37', 'Tecnico', 'Ativo', 4), -- ID 36
('Luiz Fernando', 'luiz.cal@empresa.com', 'hash_tec_38', 'Tecnico', 'Ativo', 4), -- ID 37
('Mauricio Assis', 'mauricio.cal@empresa.com', 'hash_tec_39', 'Supervisor', 'Ativo', 4), -- ID 38
('Nelson Moura', 'nelson.cal@empresa.com', 'hash_tec_40', 'Tecnico', 'Ativo', 4), -- ID 39
('Orlando Neto', 'orlando.cal@empresa.com', 'hash_tec_41', 'Tecnico', 'Ativo', 4), -- ID 40
('Pedro Henrique', 'pedro.cal@empresa.com', 'hash_tec_42', 'Tecnico', 'Ativo', 4), -- ID 41
('Renan Silveira', 'renan.cal@empresa.com', 'hash_tec_43', 'Tecnico', 'Ativo', 4), -- ID 42
('Sandro Facchini', 'sandro.cal@empresa.com', 'hash_tec_44', 'Tecnico', 'Ativo', 4), -- ID 43
('William Santos', 'william.cal@empresa.com', 'hash_tec_45', 'Tecnico', 'Ativo', 4), -- ID 44
('Arthur Vinicius', 'arthur.man@empresa.com', 'hash_tec_46', 'Tecnico', 'Ativo', 5), -- ID 45
('Caio Cesar', 'caio.man@empresa.com', 'hash_tec_47', 'Tecnico', 'Ativo', 5), -- ID 46
('Douglas Pinheiro', 'douglas.man@empresa.com', 'hash_tec_48', 'Tecnico', 'Inativo', 5), -- ID 47
('Erick Andrade', 'erick.man@empresa.com', 'hash_tec_49', 'Supervisor', 'Ativo', 5), -- ID 48
('Guilherme Augusto', 'guilherme.man@empresa.com', 'hash_tec_50', 'Tecnico', 'Ativo', 5), -- ID 49
('Hudson Carvalho', 'hudson.man@empresa.com', 'hash_tec_51', 'Tecnico', 'Inativo', 5), -- ID 50
('Jean Carlos', 'jean.man@empresa.com', 'hash_tec_52', 'Tecnico', 'Ativo', 5), -- ID 51
('Kaique Oliveira', 'kaique.man@empresa.com', 'hash_tec_53', 'Tecnico', 'Ativo', 5), -- ID 52
('Leandro Prado', 'leandro.man@empresa.com', 'hash_tec_54', 'Tecnico', 'Inativo', 5), -- ID 53
('Murilo Benicio', 'murilo.man@empresa.com', 'hash_tec_55', 'Tecnico', 'Ativo', 5), -- ID 54
('Marcos Almoxarife', 'marcos.almox@empresa.com', 'hash_user_55', 'Entregador', 'Ativo', 5), -- ID 55
('Fabiana Costa', 'fabiana.man@empresa.com', 'hash_user_56', 'Tecnico', 'Ativo', 5),         -- ID 56
('Reginaldo Leme', 'reginaldo.cal@empresa.com', 'hash_user_57', 'Tecnico', 'Ativo', 4),       -- ID 57
('Rogerio Dias', 'rogerio.cnc@empresa.com', 'hash_user_58', 'Tecnico', 'Ativo', 1),           -- ID 58
('Silvia Moura', 'silvia.fer@empresa.com', 'hash_user_59', 'Tecnico', 'Ativo', 3),            -- ID 59
('Wellington Jr', 'wellington.aju@empresa.com', 'hash_user_60', 'Tecnico', 'Ativo', 2),       -- ID 60
('Gisele Ramos', 'gisele.man@empresa.com', 'hash_user_61', 'Entregador', 'Ativo', 5),         -- ID 61
('Tatiane Souza', 'tatiane.cnc@empresa.com', 'hash_user_62', 'Tecnico', 'Ativo', 1),          -- ID 62
('Valter Filho', 'valter.cal@empresa.com', 'hash_user_63', 'Tecnico', 'Ativo', 4),            -- ID 63
('Nair Antunes', 'nair.man@empresa.com', 'hash_user_64', 'Administrador', 'Ativo', 5);        -- ID 64

INSERT INTO Tecnicos (id_usuario, id_setor, email_tecnico, telefone_tecnico, data_nasc_tecnico, cargo_tecnico, nivel_experiencia, disponibilidade_tecnico) VALUES
(5, 1, 'carlos.silva@manutencao.com', '(47) 99111-0001', '1992-05-14', 'Técnico em Mecatrônica', 'Junior', 'Disponível'),
(6, 1, 'marcos.souza@manutencao.com', '(47) 99111-0002', '1988-11-23', 'Técnico em CNC', 'Pleno', 'Em Campo'),
(7, 1, 'julia.costa@manutencao.com', '(47) 99111-0003', '1995-03-02', 'Técnico Eletrônico', 'Senior', 'Disponível'),
(8, 1, 'lucas.pereira@manutencao.com', '(47) 99111-0004', '1990-07-19', 'Programador de Manutenção', 'Pleno', 'Disponível'),
(9, 1, 'fernanda.lima@manutencao.com', '(47) 99111-0005', '1983-12-30', 'Técnico de Manutenção CNC', 'Master', 'Afastado'),
(10, 1, 'roberto.alves@manutencao.com', '(47) 99111-0006', '1996-01-15', 'Mecânico de Usinagem', 'Junior', 'Férias'),
(11, 1, 'amanda.rocha@manutencao.com', '(47) 99111-0007', '1989-08-22', 'Eletricista de Manutenção', 'Pleno', 'Disponível'),
(12, 1, 'bruno.melo@manutencao.com', '(47) 99111-0008', '1986-04-11', 'Técnico Mecatrônico', 'Senior', 'Em Campo'),
(13, 1, 'camila.dias@manutencao.com', '(47) 99111-0009', '1981-09-05', 'Especialista em Fusos', 'Master', 'Afastado'),
(14, 1, 'diego.martins@manutencao.com', '(47) 99111-0010', '1998-10-25', 'Técnico de Campo CNC', 'Junior', 'Disponível'),
(15, 2, 'edson.ribeiro@manutencao.com', '(47) 99222-0011', '1991-02-17', 'Mecânico Ajustador', 'Pleno', 'Disponível'),
(16, 2, 'fabio.santos@manutencao.com', '(47) 99222-0012', '1997-06-28', 'Mecânico Industrial', 'Junior', 'Em Campo'),
(17, 2, 'gustavo.lima@manutencao.com', '(47) 99222-0013', '1985-03-14', 'Técnico de Manutenção', 'Senior', 'Disponível'),
(18, 2, 'igor.gomes@manutencao.com', '(47) 99222-0014', '1999-11-03', 'Mecânico Ajustador', 'Junior', 'Disponível'),
(19, 2, 'juliana.ramos@manutencao.com', '(47) 99222-0015', '1993-07-21', 'Técnico Mecânico', 'Pleno', 'Disponível'),
(20, 2, 'leonardo.cruz@manutencao.com', '(47) 99222-0016', '1984-05-19', 'Líder de Ajustagem', 'Senior', 'Férias'),
(21, 2, 'marcelo.vieira@manutencao.com', '(47) 99222-0017', '1996-12-08', 'Auxiliar de Mecânico', 'Junior', 'Disponível'),
(22, 2, 'nadia.souza@manutencao.com', '(47) 99222-0018', '1980-01-24', 'Inspetor de Equipamentos', 'Master', 'Disponível'),
(23, 2, 'otavio.reis@manutencao.com', '(47) 99222-0019', '1988-09-12', 'Mecânico Industrial', 'Pleno', 'Em Campo'),
(24, 2, 'patricia.cruz@manutencao.com', '(47) 99222-0020', '1987-04-05', 'Técnico Mecânico', 'Senior', 'Disponível'),
(25, 3, 'ricardo.oliveira@manutencao.com', '(47) 99333-0021', '1983-08-16', 'Ferramenteiro de Matrizes', 'Senior', 'Afastado'),
(26, 3, 'samuel.filho@manutencao.com', '(47) 99333-0022', '1990-10-22', 'Ferramenteiro de Moldes', 'Pleno', 'Disponível'),
(27, 3, 'thiago.cardoso@manutencao.com', '(47) 99333-0023', '1982-05-11', 'Técnico em Ferramentaria', 'Master', 'Em Campo'),
(28, 3, 'vitor.barbosa@manutencao.com', '(47) 99333-0024', '1998-03-19', 'Mecânico Ferramenteiro', 'Junior', 'Disponível'),
(29, 3, 'alexandre.silva@manutencao.com', '(47) 99333-0025', '1989-07-07', 'Ferramenteiro Industrial', 'Pleno', 'Disponível'),
(30, 3, 'daniela.nunes@manutencao.com', '(47) 99333-0026', '1995-12-14', 'Técnico de Matrizes', 'Junior', 'Afastado'),
(31, 3, 'eduardo.jorge@manutencao.com', '(47) 99333-0027', '1986-02-27', 'Retificador / Ferramenteiro', 'Senior', 'Disponível'),
(32, 3, 'felipe.augusto@manutencao.com', '(47) 99333-0028', '1991-04-09', 'Mecânico de Precisão', 'Pleno', 'Em Campo'),
(33, 3, 'gabriel.neves@manutencao.com', '(47) 99333-0029', '1985-06-18', 'Ferramenteiro Modelista', 'Senior', 'Afastado'),
(34, 3, 'helena.paschoal@manutencao.com', '(47) 99333-0030', '1979-11-25', 'Líder de Ferramentaria', 'Master', 'Disponível'),
(35, 4, 'jonas.batista@manutencao.com', '(47) 99444-0031', '1987-03-31', 'Soldador RX / Argonista', 'Senior', 'Afastado'),
(36, 4, 'kevin.rodrigues@manutencao.com', '(47) 99444-0032', '1992-09-14', 'Caldeireiro Industrial', 'Pleno', 'Em Campo'),
(37, 4, 'luiz.fernando@manutencao.com', '(47) 99444-0033', '1999-05-20', 'Soldador Mig/Mag', 'Junior', 'Disponível'),
(38, 4, 'mauricio.assis@manutencao.com', '(47) 99444-0034', '1981-01-12', 'Técnico em Soldagem', 'Master', 'Disponível'),
(39, 4, 'nelson.moura@manutencao.com', '(47) 99444-0035', '1990-06-25', 'Caldeireiro Montador', 'Pleno', 'Afastado'),
(40, 4, 'orlando.neto@manutencao.com', '(47) 99444-0036', '1996-11-08', 'Soldador de Manutenção', 'Junior', 'Férias'),
(41, 4, 'pedro.henrique@manutencao.com', '(47) 99444-0037', '1997-07-16', 'Operador de Jato/Pintura', 'Junior', 'Disponível'),
(42, 4, 'renan.silveira@manutencao.com', '(47) 99444-0038', '1986-02-03', 'Caldeireiro Traçador', 'Senior', 'Em Campo'),
(43, 4, 'sandro.facchini@manutencao.com', '(47) 99444-0039', '1983-12-19', 'Técnico de Inspeção de Solda', 'Senior', 'Disponível'),
(44, 4, 'william.santos@manutencao.com', '(47) 99444-0040', '1989-10-30', 'Serralheiro Industrial', 'Pleno', 'Disponível'),
(45, 5, 'arthur.vinicius@manutencao.com', '(47) 99555-0041', '1984-04-13', 'Mecânico de Manutenção Pesada', 'Senior', 'Disponível'),
(46, 5, 'caio.cesar@manutencao.com', '(47) 99555-0042', '1992-01-27', 'Técnico Hidráulico', 'Pleno', 'Em Campo'),
(47, 5, 'douglas.pinheiro@manutencao.com', '(47) 99555-0043', '1988-06-08', 'Eletricista Industrial', 'Senior', 'Afastado'),
(48, 5, 'erick.andrade@manutencao.com', '(47) 99555-0044', '1998-11-12', 'Técnico em Lubrificação', 'Junior', 'Disponível'),
(49, 5, 'guilherme.augusto@manutencao.com', '(47) 99555-0045', '1982-07-23', 'Mecânico de Pontes Rolantes', 'Master', 'Disponível'),
(50, 5, 'hudson.carvalho@manutencao.com', '(47) 99555-0046', '1991-05-19', 'Técnico de Manutenção Preventiva', 'Pleno', 'Férias'),
(51, 5, 'jean.carlos@manutencao.com', '(47) 99555-0047', '1997-03-02', 'Auxiliar de Manutenção', 'Junior', 'Disponível'),
(52, 5, 'kaique.oliveira@manutencao.com', '(47) 99555-0048', '1993-09-14', 'Eletromecânico', 'Pleno', 'Em Campo'),
(53, 5, 'leandro.prado@manutencao.com', '(47) 99555-0049', '1985-12-01', 'Mecânico de Fluídos', 'Senior', 'Afastado'),
(54, 5, 'murilo.benicio@manutencao.com', '(47) 99555-0050', '1978-08-11', 'Supervisor de Manutenção II', 'Master', 'Disponível'),
(56, 5, 'fabiana.costa@manutencao.com', '(47) 99555-0056', '1994-02-11', 'Técnico de Manutenção Preditiva', 'Senior', 'Disponível'),
(57, 4, 'reginaldo.leme@manutencao.com', '(47) 99444-0057', '1980-05-19', 'Caldeireiro Master', 'Master', 'Em Campo'),
(58, 1, 'rogerio.cnc@manutencao.com', '(47) 99111-0058', '1988-04-03', 'Metrologista de CNC', 'Pleno', 'Disponível'),
(59, 3, 'silvia.fer@manutencao.com', '(47) 99333-0059', '1993-09-12', 'Ferramenteira Especialista', 'Senior', 'Disponível'),
(60, 2, 'wellington.aju@manutencao.com', '(47) 99222-0060', '1985-11-20', 'Mecânico de Linha Pesada', 'Pleno', 'Em Campo'),
(62, 1, 'tatiane.cnc@manutencao.com', '(47) 99111-0062', '1991-01-14', 'Preparadora de Máquinas CNC', 'Senior', 'Disponível'),
(63, 4, 'valter.cal@manutencao.com', '(47) 99444-0063', '1978-06-25', 'Forjador Industrial', 'Master', 'Disponível');

INSERT INTO Modelos_Maquinas (nome_maquina, fabricante_maquina, nome_modelo, descricao_tecnica, potencia_especificacao) VALUES
('Centro de Usinagem', 'Hyundai Wia', 'I-Cut 380Ti', 'Centro de usinagem de alta velocidade', '15 kW'),
('Torno CNC', 'Hyundai', 'E 160 LA', 'Torno CNC para barramento inclinado', '11 kW'),
('Furadeira de Coluna', 'Joinville', 'Furadeira de Coluna Joinville', 'Furadeira mecânica de coluna', '2 HP'),
('Furadeira de Bancada', 'Mello', 'Furadeira de Bancada Mello', 'Furadeira de bancada para pequenos furos', '1 HP'),
('Furadeira de Bancada', 'MotoMil', 'Furadeira de Bancada MotoMil', 'Equipamento de furação hobby/oficina', '0.5 HP'),
('Furadeira de Bancada', 'Schulz', 'Furadeira de Bancada Schulz', 'Furadeira robusta para oficina', '0.75 HP'),
('Furadeira de Coluna', 'Newton', 'Furadeira de Coluna Newton', 'Furadeira industrial pesada', '3 HP'),
('Furadeira de Coluna', 'S.A Yadoya', 'Furadeira de Coluna S.A Yadoya', 'Furadeira de coluna de alta precisão', '2.5 HP'),
('Furadeira de Coluna', 'Kone', 'KM 25', 'Furadeira de coluna engrenada', '2 HP'),
('Lixadeira Combinada', 'Razi', 'Lixadeira Combinada Razi', 'Lixadeira de disco e cinta integrados', '1.5 HP'),
('Motoesmeril', 'Somar', 'Motoesmeril Somar', 'Esmeril bifásico/trifásico para desbaste', '1 HP'),
('Máquina Eletrodo Revestido', 'Sumig', 'Fox 200', 'Inversora de solda para eletrodo', '200A'),
('Máquina Mig/Mag', 'Sumig', 'HAWK 305', 'Equipamento de solda industrial MIG/MAG', '300A'),
('Jato de Granalha', 'CMV', 'GS-9075 X CMV', 'Cabine de jateamento por ar comprimido', '5 HP'),
('Furadeira de Coluna', 'Sem modelo definido', 'Padrão', 'Furadeira genérica de caldeiraria', '1.5 HP'),
('Policorte', 'Bosch', 'GCO 2000 Bosch', 'Serra rápida para cortar metais', '2000W'),
('Paleteira', 'TM2220', 'Paleteira TM2220', 'Transpalete manual hidráulico', '2.2 TON'),
('Guincho Hidráulico (girafa)', 'Guincho Hidráulico 2 TON', 'G2000', 'Guincho mecânico para movimentação de motores', '2 TON'),
('Prensa Hidraúlica', 'Prensa Hidraúlica 15 TON', 'ST', 'Prensa hidráulica tipo H', '15 TON'),
('Lavador de Peça', 'Fabricação WEG', 'Sob medida', 'Lavadora de peças por circulação de fluido', '0.5 HP'),
('Prensa Hidráulica 200T', 'Schuler', 'PE-200T', 'Prensa industrial para conformação', '200 Ton'),
('Compressor de Parafuso', 'Atlas Copco', 'GA37', 'Compressor estacionário de ar comprimido', '50 HP'),
('Forno de Têmpera', 'Combustol', 'FT-1200', 'Forno elétrico para ferramentaria', '35 kW'),
('Exaustor de Ar Industrial', 'TecnoVent', 'EX-400', 'Sistema de exaustão e filtragem de pó', '12 kW'),
('Projetor de Perfil Óptico', 'Mitutoyo', 'PH-A14', 'Equipamento de medição para metrologia', '110V'),
('Ponte Rolante Suspensa', 'Vastec', 'PR-05TON', 'Equipamento de elevação de carga', '5 TON'),
('Retificadora Cilíndrica', 'Romi', 'RUL 400', 'Retífica industrial mecânica', '7.5 kW'),
('Dobradeira de Chapas', 'Newton', 'PPC 135', 'Dobradeira de chapas grossas de aço', '15 HP'),
('Braço Robotizado', 'KUKA', 'KR 16', 'Braço de solda robótica integrada', '8 kW'),
('Misturador de Fluidos', 'ProQuim', 'MQ-500', 'Misturador de fluidos industriais e solúvel', '3 HP');

INSERT INTO Maquinas_Ativos (tag_equipamento, id_modelo, nome_maquina, numero_serie, localizacao_maquina, tipo_manutencao_padrao, status_operacional, ultima_manutencao, id_setor) VALUES
('CNC-CU-01', 1, 'Centro de Usinagem', 'SN-CU001', 'Laboratório CNC', 'Preventiva', 'Operando', '2026-05-10', 1),
('CNC-TN-01', 2, 'Torno CNC', 'SN-TN001', 'Laboratório CNC', 'Preventiva', 'Operando', '2026-06-01', 1),
('AJU-FR-01', 3, 'Furadeira de Coluna', 'SN-FR01', 'Laboratório de Ajustagem', 'Preventiva', 'Em Manutenção', '2026-04-15', 2),
('AJU-FR-02', 4, 'Furadeira de Bancada', 'SN-FR02', 'Laboratório de Ajustagem', 'Preventiva', 'Em Manutenção', '2026-04-18', 2),
('AJU-FR-03', 5, 'Furadeira de Bancada', 'SN-FR03', 'Laboratório de Ajustagem', 'Preventiva', 'Parado', '2026-03-20', 2),
('AJU-FR-04', 6, 'Furadeira de Bancada', 'SN-FR04', 'Laboratório de Ajustagem', 'Preventiva', 'Em Manutenção', '2026-02-12', 2),
('AJU-FR-05', 6, 'Furadeira de Bancada', 'SN-FR05', 'Laboratório de Ajustagem', 'Preventiva', 'Em Manutenção', '2026-01-20', 2),
('AJU-FR-06', 7, 'Furadeira de Coluna', 'SN-FR06', 'Laboratório de Ajustagem', 'Preventiva', 'Em Manutenção', '2026-05-02', 2),
('FER-FR-01', 8, 'Furadeira de Coluna', 'SN-FER01', 'Laboratório de Ferramentaria', 'Preventiva', 'Operando', '2026-06-12', 3),
('FER-FR-02', 9, 'Furadeira de Coluna', 'SN-FER02', 'Laboratório de Ferramentaria', 'Preventiva', 'Operando', '2026-06-14', 3),
('FER-FR-03', 6, 'Furadeira de Bancada', 'SN-FER03', 'Laboratório de Ferramentaria', 'Preventiva', 'Operando', '2026-06-15', 3),
('FER-LX-01', 10, 'Lixadeira Combinada', 'SN-LX01', 'Laboratório de Ferramentaria', 'Preventiva', 'Parado', '2026-05-18', 3),
('FER-ES-01', 11, 'Motoesmeril', 'SN-ES01', 'Laboratório de Ferramentaria', 'Preventiva', 'Operando', '2026-06-11', 3),
('CAL-ER-01', 12, 'Máquina Eletrodo Revestido', 'SN-ER01', 'Caldeiraria', 'Preventiva', 'Operando', '2026-06-10', 4),
('CAL-MG-01', 13, 'Máquina Mig/Mag', 'SN-MG01', 'Caldeiraria', 'Preventiva', 'Operando', '2026-06-08', 4),
('CAL-JT-01', 14, 'Jato de Granalha', 'SN-JT01', 'Caldeiraria', 'Preventiva', 'Parado', '2026-04-22', 4),
('CAL-FR-01', 15, 'Furadeira de Coluna', 'SN-CALFR01', 'Caldeiraria', 'Preventiva', 'Operando', '2026-05-25', 4),
('CAL-PC-01', 16, 'Policorte', 'SN-PC01', 'Caldeiraria', 'Preventiva', 'Operando', '2026-06-13', 4),
('MAN-JC-01', 17, 'Paleteira', 'SN-JC01', 'Laboratório de Manutenção II', 'Preventiva', 'Em Manutenção', '2026-03-01', 5),
('MAN-JC-02', 17, 'Paleteira', 'SN-JC02', 'Laboratório de Manutenção II', 'Preventiva', 'Em Manutenção', '2026-03-05', 5),
('MAN-GH-01', 18, 'Guincho Hidráulico (girafa)', 'SN-GH01', 'Laboratório de Manutenção II', 'Preventiva', 'Operando', '2026-06-02', 5),
('MAN-PR-01', 19, 'Prensa Hidraúlica', 'SN-PR01', 'Laboratório de Manutenção II', 'Preventiva', 'Operando', '2026-06-04', 5),
('MAN-ES-02', 11, 'Motoesmeril', 'SN-ES02', 'Laboratório de Manutenção II', 'Preventiva', 'Operando', '2026-06-11', 5),
('MAN-LV-01', 20, 'Lavador de Peça', 'SN-LV01', 'Laboratório de Manutenção II', 'Preventiva', 'Parado', '2026-02-10', 5),
('MAN-PR-02', 21, 'Prensa Hidráulica 200T', 'SN-PR002', 'Laboratório de Manutenção II', 'Preventiva', 'Operando', '2026-05-20', 5),
('CNC-CP-01', 22, 'Compressor de Parafuso', 'SN-CNC50', 'Laboratório CNC', 'Preditiva', 'Operando', '2026-06-15', 1),
('FER-FN-01', 23, 'Forno de Têmpera', 'SN-FER10', 'Laboratório de Ferramentaria', 'Preventiva', 'Parado', '2026-04-10', 3),
('CAL-EX-01', 24, 'Exaustor de Ar Industrial', 'SN-CAL80', 'Caldeiraria', 'Preventiva', 'Operando', '2026-06-18', 4),
('CNC-PP-01', 25, 'Projetor de Perfil Óptico', 'SN-CNC51', 'Laboratório CNC', 'Preditiva', 'Operando', '2026-06-22', 1),
('MAN-PT-01', 26, 'Ponte Rolante Suspensa', 'SN-MAN90', 'Laboratório de Manutenção II', 'Preventiva', 'Em Manutenção', '2026-03-12', 5),
('FER-RT-01', 27, 'Retificadora Cilíndrica', 'SN-FER11', 'Laboratório de Ferramentaria', 'Preventiva', 'Operando', '2026-06-11', 3),
('CAL-DB-01', 28, 'Dobradeira de Chapas', 'SN-CAL81', 'Caldeiraria', 'Preventiva', 'Operando', '2026-05-30', 4),
('CNC-RB-01', 29, 'Braço Robotizado', 'SN-CNC99', 'Laboratório CNC', 'Preventiva', 'Operando', '2026-06-02', 1),
('QMI-MS-01', 30, 'Misturador de Fluidos', 'SN-QMI01', 'Química', 'Preventiva', 'Operando', '2026-06-10', 6);

INSERT INTO Almoxarifado_Pecas (nome_peca, quantidade_estoque, unidade_medida, custo_unitario) VALUES
('Béquer', 102, 'Unidade', 15.50),
('Balão volumétrico', 77, 'Unidade', 45.00),
('Erlenmeyer', 59, 'Unidade', 22.30),
('Tubo conectante', 8, 'Unidade', 12.00),
('Funil de cerâmica', 10, 'Unidade', 35.00),
('Funil de vidro', 14, 'Unidade', 18.00),
('Funil de separação', 8, 'Unidade', 65.00),
('Pipeta', 60, 'Unidade', 9.50),
('Proveta', 49, 'Unidade', 28.00),
('Motor W22 Plus (carcaça 63)', 6, 'Unidade', 450.00),
('Motor W22 Premium (carcaça 71)', 3, 'Unidade', 620.00),
('Motor W22 Premium (carcaça 80)', 1, 'Unidade', 850.00),
('Motor W21 (carcaça Alú 90S/L)', 1, 'Unidade', 780.00),
('Motor W22 Premium Carcaça (250S/M)', 1, 'Unidade', 3200.00),
('Motor W22 Premium Carcaça (132S)', 1, 'Unidade', 1450.00),
('Tarugo de bronze', 5, 'Unidade', 120.00),
('Macho máquina', 13, 'Unidade', 45.00),
('Macho manual', 6, 'Unidade', 35.00),
('Rolamento SKF 6204-2Z', 50, 'Unidade', 34.20),
('Contator Tripolar 24V Siemens', 12, 'Unidade', 189.90),
('Inversor de Frequência WEG CFW500', 0, 'Unidade', 1450.00),
('Óleo Hidráulico ISO VG 68', 200, 'Litro', 18.50),
('Sensor Indutivo Balluff M12', 0, 'Unidade', 220.00),
('Gaxeta de Vedação Nitrílica', 35, 'Unidade', 8.90),
('Filtro de Ar Regulador Festo', 8, 'Unidade', 310.00),
('Placa Eletrônica Controladora CNC', 1, 'Unidade', 4200.00),
('Graxa de Alta Temperatura SKF', 15, 'Kg', 75.00),
('Válvula Solenoide Pneumática 5/2v', 0, 'Unidade', 195.00);

INSERT INTO Almoxarifado_Ferramentas (nome_ferramenta, status_ferramenta) VALUES
('Paquímetro', 'Disponível'),
('Fita métrica 50m', 'Disponível'),
('Micrômetro', 'Disponível'),
('Nível de precisão', 'Disponível'),
('Régua 500mm', 'Disponível'),
('Trena 5m', 'Disponível'),
('Aquecedor indutivo de rolamento portátil', 'Disponível'),
('Rebitador', 'Disponível'),
('Macho', 'Disponível'),
('Pincel', 'Disponível'),
('Borda plástica', 'Disponível'),
('Calibrador de folga', 'Disponível'),
('Ocrílico (Acrílico)', 'Disponível'),
('Verificador de planeza', 'Disponível'),
('Verificador de raio', 'Disponível'),
('Lima triangular murça', 'Disponível'),
('Lima triangular bastarda', 'Disponível'),
('Caixa de broca', 'Disponível'),
('Serra copo', 'Disponível'),
('Furadeira diversas', 'Disponível'),
('Jogo de chaves Allen (mm)', 'Disponível'),
('Jogo de chaves Allen (pol)', 'Disponível'),
('Chave Allen em T', 'Disponível'),
('Chave Torx em T', 'Disponível'),
('Chave Grifo', 'Disponível'),
('Chave canhão', 'Disponível'),
('Chave Phillips', 'Disponível'),
('Chave de Fenda', 'Disponível'),
('Chave biela', 'Disponível'),
('Alicate para anéis externo', 'Disponível'),
('Eixo padrões', 'Disponível'),
('Morsa', 'Disponível'),
('Multímetro Fluke TrueRMS', 'Disponível'),
('Megômetro Digital', 'Disponível'),
('Torquímetro Estalo 1/2', 'Disponível'),
('Alicate Crimpador Hidráulico', 'Disponível'),
('Extrator de Rolamento de 3 Garras', 'Disponível'),
('Termovisor Flir', 'Disponível'),
('Caneta de Vibração Preditiva', 'Disponível'),
('Chave de Impacto Pneumática 3/4', 'Disponível'),
('Bloco Padrão de Calibração', 'Disponível'),
('Fresa de Topo Metal Duro 12mm', 'Disponível');

INSERT INTO Matriz_Riscos_EPI (risco_nr01, epis_obrigatorios) VALUES
('Mecânico / Projeção de Partículas', 'Óculos de proteção, Protetor auricular, Bota de segurança'),
('Químico / Manuseio de Produtos', 'Luvas nitrílicas, Óculos ampla visão, Avental impermeável'),
('Ergonômico / Movimentação de Carga', 'Cinta ergonômica, Sapato de segurança com biqueira'),
('Físico / Ruído e Vibração', 'Abafador de ruído tipo concha, Luvas antivibração'),
('Elétrico / Alta Tensão e Choque', 'Luvas isolantes de borracha, Sapato de segurança sem componentes metálicos, Protetor facial contra arco elétrico'),
('Térmico / Altas Temperatures', 'Luva de raspa de couro, Avental de raspa, Perneira de raspa'),
('Radiação Não Ionizante / Soldagem', 'Máscara de solda com filtro de escurecimento automático, Blusão de raspa, Luva de vaqueta para soldador'),
('Trabalho em Altura / Pontes mecânicas', 'Cinto de segurança tipo paraquedista, Talabarte duplo, Capacete com jugular'),
('Espaço Confinado / Tanques e Fornos', 'Exaustor de ar portátil, Detector de gases portátil, Tripé de resgate'),
('Corte e Desbaste / Policorte e Esmeril', 'Protetor facial incolor (Face Shield), Avental de raspa, Luva de raspa'),
('Laser Industrial / Alinhamento Óptico', 'Óculos de proteção contra radiação laser específica'),
('Riscos Biológicos / Troca de Solúvel', 'Máscara respiratória PFF2, Luvas de cano longo de PVC, Avental químico'),
('Manuseio de Vidrarias / Lab Química', 'Óculos de proteção policarbonato, Luvas de malha de kevlar anticorte'),
('Atmosferas Inflamáveis / Vapores', 'Vestimenta antiestática, Calçado condutivo, Lanterna intrinsecamente segura'),
('Queda de Objetos / Cargas Suspensas', 'Capacete de proteção industrial, Bota com biqueira de aço composto'),
('Poeiras Metálicas / Jateamento', 'Máscara facial inteira com filtro contra poeiras industriais'),
('Alta Pressão / Circuitos Hidráulicos', 'Óculos de segurança ampla visão impacto, Barreira física, Protetor auricular concha');

INSERT INTO Ordens_Servico (id_os, tag_equipamento, descricao_falha, data_abertura, hh_inicio, hh_fim, status_os, id_tecnico_responsavel) VALUES
(1001, 'AJU-FR-03', 'Desnivelamento da mesa, mandril solto e folga no eixo do mandril.', '2026-06-15', '08:00:00', NULL, 'Em andamento', 16),
(1002, 'MAN-JC-01', 'Vazamento na parte hidráulica e garfos descendo sozinhos.', '2026-06-16', '09:30:00', NULL, 'Em andamento', 46),
(1003, 'MAN-LV-01', 'A estrutura da grade possui um furo na solda, não sai fluido e máquina não liga.', '2026-06-17', '13:00:00', '17:00:00', 'Concluído', 51),
(1004, 'FER-LX-01', 'Lixadeira está com desalinhamento nas polias.', '2026-06-18', '07:45:00', NULL, 'Aberto', 26),
(1005, 'CAL-JT-01', 'Quebra do fecho do engate rápido.', '2026-06-19', '10:00:00', '11:30:00', 'Concluído', 36),
(1006, 'CNC-CU-01', 'Ruído excessivo no fuso (spindle) em altas rotações.', '2026-06-20', '08:00:00', '12:00:00', 'Concluído', 6),
(1007, 'AJU-FR-01', 'Motor superaquecendo após 15 minutes de uso contínuo.', '2026-06-20', '14:00:00', NULL, 'Em andamento', 17),
(1008, 'CAL-MG-01', 'Alimentador de arame travando intermitentemente durante a soldagem.', '2026-06-21', '09:00:00', '11:15:00', 'Concluído', 37),
(1009, 'MAN-GH-01', 'Gatilho de alívio da pressão hidráulica travado.', '2026-06-22', '10:30:00', NULL, 'Aberto', 45),
(1010, 'AJU-FR-04', 'Chave liga/desliga com mau contato elétrico.', '2026-06-22', '15:45:00', NULL, 'Aberto', 18),
(1011, 'CNC-TN-01', 'Vazamento de fluido refrigerante na base da máquina.', '2026-06-23', '08:30:00', '10:45:00', 'Concluído', 7),
(1012, 'AJU-FR-02', 'Substituição preventiva do rolamento do eixo principal.', '2026-06-24', '07:30:00', '11:30:00', 'Concluído', 19),
(1013, 'CNC-CU-01', 'Inversor de frequência queimado por pico elétrico na rede.', '2026-06-24', '08:00:00', '16:30:00', 'Concluído', 6),
(1014, 'CAL-JT-01', 'Trinca estrutural detectada na base de fixação traseira.', '2026-06-25', '07:30:00', NULL, 'Em andamento', 57),
(1015, 'FER-ES-01', 'Inspeção semestral periódica dos rebolos de desbaste.', '2026-06-25', '00:00:00', NULL, 'Aberto', 26),
(1016, 'MAN-PR-01', 'Vazamento crônico no cilindro de prensa principal.', '2026-06-25', '13:00:00', '17:45:00', 'Concluído', 46),
(1017, 'CNC-TN-01', 'Lubrificação das guias mecânicas e nível do barramento.', '2026-06-26', '09:00:00', '10:15:00', 'Concluído', 7),
(1018, 'MAN-PR-02', 'Martelo da prensa mecânica pesada travou no ponto morto inferior.', '2026-06-26', '06:15:00', '14:20:00', 'Concluído', 60),
(1019, 'CNC-CP-01', 'Falha no pressostato mecânico de corte do compressor.', '2026-06-26', '10:00:00', NULL, 'Em andamento', 62),
(1020, 'FER-FN-01', 'Resistência cerâmica interna queimada do forno de têmpera.', '2026-06-26', '11:30:00', NULL, 'Em andamento', 59),
(1021, 'CAL-EX-01', 'Verificação e teste do aterramento de carcaça do motor de exaustão.', '2026-06-26', '14:00:00', '15:30:00', 'Concluído', 57),
(1022, 'MAN-PT-01', 'Leitura preditiva e análise de vibração no mancal da ponte rolante.', '2026-06-26', '15:00:00', NULL, 'Em andamento', 56);

INSERT INTO OS_Materiais (id_os, id_peca, quantidade_utilizada) VALUES
(1002, 16, 1), 
(1003, 17, 1),
(1006, 10, 1), 
(1007, 11, 1), 
(1008, 17, 2),
(1011, 4, 3),  
(1012, 16, 1),
(1013, 21, 1), 
(1016, 22, 40),
(1016, 24, 2), 
(1017, 22, 5),  
(1018, 19, 2), 
(1018, 16, 1), 
(1019, 23, 1), 
(1020, 20, 1), 
(1021, 22, 1), 
(1022, 27, 1); 

INSERT INTO OS_Ferramentas (id_os, id_ferramenta) VALUES
(1001, 1),   
(1001, 12), 
(1002, 25), 
(1003, 9),
(1006, 3), 
(1006, 7), 
(1007, 21), 
(1008, 32), 
(1009, 25), 
(1011, 28), 
(1012, 1), 
(1012, 12),
(1013, 33), 
(1013, 21), 
(1014, 25), 
(1016, 12), 
(1016, 35), 
(1018, 37), 
(1018, 1),  
(1019, 33), 
(1020, 34), 
(1022, 39); 

INSERT INTO OS_Seguranca (id_os, id_risco) VALUES
(1001, 1), 
(1002, 3), 
(1003, 2), 
(1004, 4),
(1006, 1), 
(1007, 5),
(1008, 7), 
(1009, 3), 
(1010, 5),
(1011, 2),
(1012, 1),
(1013, 5),  
(1014, 7),  
(1015, 4),  
(1016, 3),  
(1018, 10), 
(1019, 5),  
(1020, 6),  
(1021, 5),  
(1022, 4),  
(1001, 3);  

INSERT INTO Movimentacao_Ferramentas (
    id_ferramenta, id_os, id_solicitante, id_entregador, data_retirada, data_devolucao_prevista, data_devolucao_real, status_movimentacao, observacoes
) VALUES
(1, 1001, 16, 55, '2026-06-15 08:05:00', '2026-06-15 17:00:00', NULL, 'Em Uso', 'Retirado por Fabio Santos para medição da folga do eixo do mandril.'),
(12, 1001, 16, 55, '2026-06-15 09:15:00', '2026-06-15 12:00:00', '2026-06-15 11:50:00', 'Devolvido', 'Utilizado na checagem do desnivelamento da mesa de ajustagem.'),
(25, 1002, 46, 55, '2026-06-16 09:40:00', '2026-06-16 16:00:00', NULL, 'Em Uso', 'Retirada para remoção da carenagem da bomba hidráulica.'),
(9, 1003, 51, 55, '2026-06-17 13:10:00', '2026-06-17 16:30:00', '2026-06-17 16:15:00', 'Devolvido', 'Utilizado para recuperar a rosca do furo da grade de fluidos.'),
(4, 1004, 26, NULL, NULL, '2026-06-26 08:00:00', NULL, 'Solicitado', 'Reserva programada no PCP para o alinhamento preventivo das polias.'),
(21, 1005, 36, 55, '2026-06-19 10:05:00', '2026-06-19 11:30:00', '2026-06-19 11:25:00', 'Devolvido', 'Troca rápida do fecho danificado da granalha concluída.'),
(3, 1006, 6, 55, '2026-06-20 08:15:00', '2026-06-20 11:30:00', '2026-06-20 11:45:00', 'Devolvido', 'Medição de excentricidade do fuso realizada com sucesso.'),
(6, 1007, 17, 55, '2026-06-20 14:10:00', '2026-06-20 17:00:00', NULL, 'Atrasado', 'O prazo de devolução expirou. Alerta emitido para o Laboratório de Ajustagem.'),
(32, 1008, 37, 55, '2026-06-21 09:10:00', '2026-06-21 11:15:00', '2026-06-21 11:00:00', 'Devolvido', 'Fixação temporária do guia de arame para soldagem em bancada.'),
(27, 1011, 7, 55, '2026-06-23 08:35:00', '2026-06-23 10:30:00', '2026-06-23 10:20:00', 'Devolvido', 'Abertura das calhas de proteção de fluido refrigerante.'),
(33, 1013, 6, 55, '2026-06-24 08:10:00', '2026-06-24 12:00:00', '2026-06-24 11:40:00', 'Devolvido', 'Multímetro retirado por Marcos Souza para teste de queima do inversor.'),
(25, 1014, 57, 55, '2026-06-25 07:45:00', '2026-06-26 17:00:00', NULL, 'Em Uso', 'Chave Grifo pesada em uso na base estrutural da caldeiraria.'),
(12, 1016, 46, 61, '2026-06-25 13:15:00', '2026-06-25 17:00:00', NULL, 'Atrasado', 'Calibrador de folga esquecido em campo pelo técnico Caio Cesar.'),
(35, 1016, 46, 61, '2026-06-25 13:20:00', '2026-06-25 16:30:00', '2026-06-25 16:15:00', 'Devolvido', 'Torquímetro devolvido limpo e calibrado.'),
(37, 1018, 60, 55, '2026-06-26 06:30:00', '2026-06-26 11:00:00', '2026-06-26 10:45:00', 'Devolvido', 'Extrator de garras usado para destravar o martelo da prensa.'),
(1, 1018, 60, 55, '2026-06-26 07:00:00', '2026-06-26 12:00:00', '2026-06-26 13:10:00', 'Devolvido', 'Paquímetro retornado com leve atraso por conta do ajuste fino.'),
(33, 1019, 62, 61, '2026-06-26 10:15:00', '2026-06-26 14:00:00', NULL, 'Em Uso', 'Multímetro alocado na bancada de eletrônica para testes lógicos.'),
(34, 1020, 59, 55, '2026-06-26 11:45:00', '2026-06-26 16:00:00', NULL, 'Em Uso', 'Megômetro retirado para teste de isolamento das resistências elétricas.'),
(39, 1022, 56, 61, '2026-06-26 15:10:00', '2026-06-26 17:30:00', NULL, 'Em Uso', 'Caneta de vibração acionada para rotina preditiva programada.'),
(3, 1013, 6, 55, '2026-06-24 14:00:00', '2026-06-24 16:00:00', '2026-06-24 15:50:00', 'Devolvido', 'Micrômetro usado para conferir o diâmetro do acoplamento do motor.');