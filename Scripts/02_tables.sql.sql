<<<<<<< HEAD:Scripts/02_tables.sql.sql
	TABLE Setores (
=======
-- TABELA 1: Setores da Fábrica
CREATE TABLE Setores (
>>>>>>> d3f437afe9817c07c6dfd889346b3ecbf62baf9b:Scripts/02_tables.sql
    id_setor INT AUTO_INCREMENT PRIMARY KEY,
    nome_setor VARCHAR(50) NOT NULL UNIQUE,
    descricao_setor VARCHAR(150)
);

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

CREATE TABLE Logs_Acesso (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acao_acesso VARCHAR(100) NOT NULL,
    ip_origem VARCHAR(45),
    sucesso_acesso BOOLEAN NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

CREATE TABLE Modelos_Maquinas (
    id_modelo INT AUTO_INCREMENT PRIMARY KEY,
<<<<<<< HEAD:Scripts/02_tables.sql.sql
    nome_maquina VARCHAR(50) NOT NULL,
=======
    nome_maquina varchar(50) not null,
>>>>>>> d3f437afe9817c07c6dfd889346b3ecbf62baf9b:Scripts/02_tables.sql
    fabricante_maquina VARCHAR(50) NOT NULL,
    nome_modelo VARCHAR(100) NOT NULL,
    descricao_tecnica TEXT,
    potencia_especificacao VARCHAR(50),
    CONSTRAINT unique_modelo_nome UNIQUE (id_modelo, nome_maquina) -- Permite a FK composta da Tabela 5
);

CREATE TABLE Maquinas_Ativos (
    tag_equipamento VARCHAR(20) PRIMARY KEY, 
    id_modelo INT NOT NULL,
    nome_maquina VARCHAR(50) NOT NULL,
    numero_serie VARCHAR(50) NOT NULL UNIQUE,
    localizacao_maquina VARCHAR(100) NOT NULL,       
    tipo_manutencao_padrao ENUM('Preventiva', 'Corretiva', 'Preditiva') NOT NULL,
    status_operacional ENUM('Operando', 'Parado', 'Em Manutenção') DEFAULT 'Operando',
    ultima_manutencao DATE,
    id_setor INT NOT NULL,
    FOREIGN KEY (id_modelo) REFERENCES Modelos_Maquinas(id_modelo),
    FOREIGN KEY (id_setor) REFERENCES Setores(id_setor),
<<<<<<< HEAD:Scripts/02_tables.sql.sql
    CONSTRAINT fk_ativos_modelo_nome 
    FOREIGN KEY (id_modelo, nome_maquina) 
    REFERENCES Modelos_Maquinas(id_modelo, nome_maquina)
    ON UPDATE CASCADE
=======
	CONSTRAINT fk_ativos_modelo_nome 
	FOREIGN KEY (id_modelo, nome_maquina) 
	REFERENCES Modelos_Maquinas(id_modelo, nome_maquina)
	ON UPDATE CASCADE
>>>>>>> d3f437afe9817c07c6dfd889346b3ecbf62baf9b:Scripts/02_tables.sql
);

CREATE TABLE Almoxarifado_Pecas (
    id_peca INT AUTO_INCREMENT PRIMARY KEY,
    nome_peca VARCHAR(100) NOT NULL UNIQUE, 
    quantidade_estoque INT NOT NULL DEFAULT 0,
    unidade_medida VARCHAR(20) DEFAULT 'Unidade',
    custo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE Almoxarifado_Ferramentas (
    id_ferramenta INT AUTO_INCREMENT PRIMARY KEY,
    nome_ferramenta VARCHAR(100) NOT NULL UNIQUE, 
    status_ferramenta ENUM('Disponível', 'Em Uso', 'Manutenção/Calibração') DEFAULT 'Disponível'
);

CREATE TABLE Matriz_Riscos_EPI (
    id_risco INT AUTO_INCREMENT PRIMARY KEY,
    risco_nr01 VARCHAR(100) NOT NULL UNIQUE,
    epis_obrigatorios VARCHAR(255) NOT NULL
);

CREATE TABLE Ordens_Servico (
    id_os INT PRIMARY KEY,
    tag_equipamento VARCHAR(20) NOT NULL,
    descricao_falha TEXT NOT NULL, 
    data_abertura DATE NOT NULL, 
    hh_inicio TIME NOT NULL,
    hh_fim TIME, 
    status_os ENUM('Aberto', 'Em andamento', 'Concluído') DEFAULT 'Aberto',
    id_tecnico_responsavel INT,
    FOREIGN KEY (tag_equipamento) REFERENCES Maquinas_Ativos(tag_equipamento),
    FOREIGN KEY (id_tecnico_responsavel) REFERENCES Usuarios(id_usuario)
);

CREATE TABLE OS_Materiais (
    id_os_material INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_peca INT NOT NULL,
    quantidade_utilizada INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_peca) REFERENCES Almoxarifado_Pecas(id_peca)
);

CREATE TABLE OS_Ferramentas (
    id_os_ferramenta INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_ferramenta INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_ferramenta) REFERENCES Almoxarifado_Ferramentas(id_ferramenta)
);

CREATE TABLE OS_Seguranca (
    id_os_seguranca INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_risco INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_risco) REFERENCES Matriz_Riscos_EPI(id_risco)
);
<<<<<<< HEAD:Scripts/02_tables.sql.sql
=======

-- ÍNDICES DE PERFORMANCE
CREATE INDEX idx_os_datas ON Ordens_Servico(data_abertura);
CREATE INDEX idx_os_status_atual ON Ordens_Servico(status_os);
CREATE INDEX idx_ativos_setor ON Maquinas_Ativos(id_setor);
CREATE INDEX idx_usuarios_login ON Usuarios(email_usuario, status_usuario);
CREATE INDEX idx_logs_data ON Logs_Acesso(data_hora);
>>>>>>> d3f437afe9817c07c6dfd889346b3ecbf62baf9b:Scripts/02_tables.sql
