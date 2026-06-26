INSERT INTO Setores (nome_setor, descricao_setor) VALUES
('Laboratório CNC', 'Setor responsável por usinagem computorizada'),
('Laboratório de Ajustagem', 'Setor de ajustagem mecânica e furação'),
('Laboratório de Ferramentaria', 'Manutenção e fabricação de matrizes/ferramentas'),
('Caldeiraria', 'Setor de soldagem, corte e conformação de chapas'),
('Laboratório de Manutenção II', 'Setor focado em manutenção corretiva e preventiva pesada'),
('Química', 'Análises químicas e controle de fluidos');

INSERT INTO Usuarios (nome_usuario, email_usuario, senha_hash, perfil_usuario, status_usuario, id_setor) VALUES
('Tauani', 'tauani@empresa.com', 'hash_senha_1', 'Tecnico', 'Ativo', 1),
('FelipeM', 'felipem@empresa.com', 'hash_senha_2', 'Tecnico', 'Ativo', 2),
('Henrique', 'henrique@empresa.com', 'hash_senha_3', 'Tecnico', 'Ativo', 5),
('Ana', 'ana@empresa.com', 'hash_senha_4', 'Tecnico', 'Ativo', 6),
('Admin Sistema', 'admin@empresa.com', 'hash_admin', 'Administrador', 'Ativo', NULL);

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
('Lavador de Peça', 'Fabricação WEG', 'Sob medida', 'Lavadora de peças por circulação de fluido', '0.5 HP');

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
('MAN-LV-01', 20, 'Lavador de Peça', 'SN-LV01', 'Laboratório de Manutenção II', 'Preventiva', 'Parado', '2026-02-10', 5);

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
('Macho manual', 6, 'Unidade', 35.00);

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
('Morsa', 'Disponível');

INSERT INTO Matriz_Riscos_EPI (risco_nr01, epis_obrigatorios) VALUES
('Mecânico / Projeção de Partículas', 'Óculos de proteção, Protetor auricular, Bota de segurança'),
('Químico / Manuseio de Produtos', 'Luvas nitrílicas, Óculos ampla visão, Avental impermeável'),
('Ergonômico / Movimentação de Carga', 'Cinta ergonômica, Sapato de segurança com biqueira'),
('Físico / Ruído e Vibração', 'Abafador de ruído tipo concha, Luvas antivibração')
('Elétrico / Alta Tensão e Choque', 'Luvas isolantes de borracha, Sapato de segurança sem componentes metálicos, Protetor facial contra arco elétrico'),
('Térmico / Altas Temperaturas', 'Luva de raspa de couro, Avental de raspa, Perneira de raspa'),
('Radiação Não Ionizante / Soldagem', 'Máscara de solda com filtro de escurecimento automático, Blusão de raspa, Luva de vaqueta para soldador');

INSERT INTO Ordens_Servico (id_os, tag_equipamento, descricao_falha, data_abertura, hh_inicio, hh_fim, status_os, id_tecnico_responsavel) VALUES
(1001, 'AJU-FR-03', 'Desnivelamento da mesa, mandril solto e folga no eixo do mandril.', '2026-06-15', '08:00:00', NULL, 'Em andamento', 2),
(1002, 'MAN-JC-01', 'Vazamento na parte hidráulica e garfos descendo sozinhos.', '2026-06-16', '09:30:00', NULL, 'Em andamento', 3),
(1003, 'MAN-LV-01', 'A estrutura da grade possui um furo na solda, não sai fluido e máquina não liga.', '2026-06-17', '13:00:00', '17:00:00', 'Concluído', 3),
(1004, 'FER-LX-01', 'Lixadeira está com desalinhamento nas polias.', '2026-06-18', '07:45:00', NULL, 'Aberto', 1),
(1005, 'CAL-JT-01', 'Quebra do fecho do engate rápido.', '2026-06-19', '10:00:00', '11:30:00', 'Concluído', 2),
(1006, 'CNC-CU-01', 'Ruído excessivo no fuso (spindle) em altas rotações.', '2026-06-20', '08:00:00', '12:00:00', 'Concluído', 1),
(1007, 'AJU-FR-01', 'Motor superaquecendo após 15 minutos de uso contínuo.', '2026-06-20', '14:00:00', NULL, 'Em andamento', 2),
(1008, 'CAL-MG-01', 'Alimentador de arame travando intermitentemente durante a soldagem.', '2026-06-21', '09:00:00', '11:15:00', 'Concluído', 2),
(1009, 'MAN-GH-01', 'Gatilho de alívio da pressão hidráulica travado.', '2026-06-22', '10:30:00', NULL, 'Aberto', 3),
(1010, 'AJU-FR-04', 'Chave liga/desliga com mau contato elétrico.', '2026-06-22', '15:45:00', NULL, 'Aberto', 2),
(1011, 'CNC-TN-01', 'Vazamento de fluido refrigerante na base da máquina.', '2026-06-23', '08:30:00', '10:45:00', 'Concluído', 1),
(1012, 'AJU-FR-02', 'Substituição preventiva do rolamento do eixo principal.', '2026-06-24', '07:30:00', '11:30:00', 'Concluído', 2);

INSERT INTO OS_Materiais (id_os, id_peca, quantidade_utilizada) VALUES
(1002, 16, 1), 
(1003, 17, 1),
(1006, 10, 1), 
(1007, 11, 1), 
(1008, 17, 2),
(1011, 4, 3),  
(1012, 16, 1); 

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
(1012, 12); 

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
(1012, 1); 


