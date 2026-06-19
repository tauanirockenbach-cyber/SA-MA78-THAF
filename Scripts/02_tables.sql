
-- TABELA 1: Setores da Fábrica
CREATE TABLE Setores (
    id_setor INT AUTO_INCREMENT PRIMARY KEY,
    nome_setor VARCHAR(50) NOT NULL UNIQUE,
    descricao_setor VARCHAR(150)
);

-- TABELA 2: Usuários e Técnicos
CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    email_usuario VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil_usuario ENUM('Administrador', 'Sistema', 'Tecnico', 'Entregador') NOT NULL,
    status_usuario ENUM('Ativo', 'Inativo') NOT NULL DEFAULT 'Ativo',
    id_setor INT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_setor) REFERENCES Setores(id_setor)
);

-- TABELA 3: Registro de Logs e Bloqueios
CREATE TABLE Logs_Acesso (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acao_acesso VARCHAR(100) NOT NULL,
    ip_origem VARCHAR(45),
    sucesso_acesso BOOLEAN NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- TABELA 4: Modelos de Máquinas
CREATE TABLE Modelos_Maquinas (
    id_modelo INT AUTO_INCREMENT PRIMARY KEY,
    nome_maquina varchar(50) not null,
    fabricante_maquina VARCHAR(50) NOT NULL,
    nome_modelo VARCHAR(100) NOT NULL,
    descricao_tecnica TEXT,
    potencia_especificacao VARCHAR(50),  
     CONSTRAINT uk_modelo_nome UNIQUE (id_modelo, nome_maquina)
);

-- TABELA 5: Máquinas / Ativos Físicos
CREATE TABLE Maquinas_Ativos (
    tag_equipamento VARCHAR(20) PRIMARY KEY,
    id_modelo INT NOT NULL,
    nome_maquina varchar(50) not null,
    numero_serie VARCHAR(50) NOT NULL UNIQUE,
    localizacao_maquina VARCHAR(100) NOT NULL,       
    tipo_manutencao_padrao ENUM('Preventiva', 'Corretiva', 'Preditiva') NOT NULL,
    status_operacional ENUM('Operando', 'Parado', 'Em Manutenção') DEFAULT 'Operando',
    ultima_manutencao DATE,
    id_setor INT NOT NULL,
    FOREIGN KEY (id_setor) REFERENCES Setores(id_setor),
	CONSTRAINT fk_ativos_modelo_nome 
	FOREIGN KEY (id_modelo, nome_maquina) 
	REFERENCES Modelos_Maquinas(id_modelo, nome_maquina)
	ON UPDATE CASCADE
);


-- TABELA 6: Almoxarifado de Peças e Insumos
CREATE TABLE Almoxarifado_Pecas (
    id_peca INT AUTO_INCREMENT PRIMARY KEY,
    nome_peca VARCHAR(100) NOT NULL UNIQUE, 
    quantidade_estoque INT NOT NULL DEFAULT 0,
    unidade_medida VARCHAR(20) DEFAULT 'Unidade',
    custo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0.00
);

-- TABELA 7: Almoxarifado de Ferramentas da Empresa
CREATE TABLE Almoxarifado_Ferramentas (
    id_ferramenta INT AUTO_INCREMENT PRIMARY KEY,
    nome_ferramenta VARCHAR(100) NOT NULL UNIQUE, 
    status_ferramenta ENUM('Disponível', 'Em Uso', 'Manutenção/Calibração') DEFAULT 'Disponível'
);

-- TABELA 8: Matriz de Riscos Ocupacionais e EPIs
CREATE TABLE Matriz_Riscos_EPI (
    id_risco INT AUTO_INCREMENT PRIMARY KEY,
    risco_nr01 VARCHAR(100) NOT NULL UNIQUE,
    epis_obrigatorios VARCHAR(255) NOT NULL
);

-- TABELA 9: Cabeçalho das Ordens de Serviço (OS)
CREATE TABLE Ordens_Servico (
    id_os INT PRIMARY KEY,
    tag_equipamento VARCHAR(20) NOT NULL,
    descricao_falha TEXT NOT NULL, 
    data_abertura DATE NOT NULL, 
    hh_inicio TIME NOT NULL,
    hh_fim TIME, 
    status_os ENUM('Aberto', 'Em andamento', 'Concluído ') DEFAULT 'Aberto',
    id_tecnico_responsavel INT,
    FOREIGN KEY (tag_equipamento) REFERENCES Maquinas_Ativos(tag_equipamento),
    FOREIGN KEY (id_tecnico_responsavel) REFERENCES Usuarios(id_usuario)
);

-- TABELA 10: Relacionamento OS e Peças Utilizadas
CREATE TABLE OS_Materiais (
    id_os_material INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_peca INT NOT NULL,
    quantidade_utilizada INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_peca) REFERENCES Almoxarifado_Pecas(id_peca)
);

-- TABELA 11: Relacionamento OS e Ferramentas Alocadas
CREATE TABLE OS_Ferramentas (
    id_os_ferramenta INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_ferramenta INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_ferramenta) REFERENCES Almoxarifado_Ferramentas(id_ferramenta)
);

-- TABELA 12: Relacionamento OS e Riscos/EPIs Aplicados
CREATE TABLE OS_Seguranca (
    id_os_seguranca INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_risco INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_risco) REFERENCES Matriz_Riscos_EPI(id_risco)
);

-- ÍNDICES DE PERFORMANCE
CREATE INDEX idx_os_datas ON Ordens_Servico(data_abertura);
CREATE INDEX idx_os_status_atual ON Ordens_Servico(status_os);
CREATE INDEX idx_ativos_setor ON Maquinas_Ativos(id_setor);
CREATE INDEX idx_usuarios_login ON Usuarios(email_usuario, status_usuario);
CREATE INDEX idx_logs_data ON Logs_Acesso(data_hora);