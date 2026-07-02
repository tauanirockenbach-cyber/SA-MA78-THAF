CREATE TABLE Setores (
    id_setor INT AUTO_INCREMENT PRIMARY KEY,
    nome_setor VARCHAR(50) NOT NULL UNIQUE,
    descricao_setor VARCHAR(150)
);
CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_usuario VARCHAR(100) NOT NULL,
    email_usuario VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    cargo_usuario ENUM('Administrador', 'Sistema', 'Tecnico', 'Entregador', 'CEO', 'Diretor', 'Gerente', 'Coordenador', 'Supervisor') NOT NULL,
    status_usuario ENUM('Ativo', 'Inativo') NOT NULL DEFAULT 'Ativo',
    telefone_usuario VARCHAR(20) NOT NULL UNIQUE,
    data_nasc_usuario DATE,
    id_setor INT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_setor)
        REFERENCES Setores (id_setor)
        ON DELETE SET NULL
);

CREATE TABLE Tecnicos (
    id_tecnico INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    email_usuario VARCHAR(100) NOT NULL UNIQUE,
    telefone_usuario VARCHAR(20) NOT NULL UNIQUE,
    id_setor INT,
    cargo_tecnico VARCHAR(50) NOT NULL,
    nivel_experiencia ENUM('Junior', 'Pleno', 'Senior', 'Master') DEFAULT 'Junior',
    disponibilidade_tecnico ENUM('Disponível', 'Em Campo', 'Férias', 'Afastado') DEFAULT 'Disponível',
    FOREIGN KEY (id_setor)
        REFERENCES Setores (id_setor)
        ON DELETE SET NULL,
    FOREIGN KEY (id_usuario)
        REFERENCES Usuarios (id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (email_usuario)
        REFERENCES Usuarios (email_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (telefone_usuario)
        REFERENCES Usuarios (telefone_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Logs_Acesso (
    id_log BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acao_acesso VARCHAR(100) NOT NULL,
    ip_origem VARCHAR(45),
    sucesso_acesso BOOLEAN NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE SET NULL
);

CREATE TABLE Modelos_Maquinas (
    id_maquina INT AUTO_INCREMENT PRIMARY KEY,
    nome_maquina VARCHAR(50) NOT NULL,       
    fabricante_maquina VARCHAR(50) NOT NULL,  
    nome_modelo VARCHAR(100) NOT NULL,    
    descricao_tecnica TEXT,
    potencia_especificacao VARCHAR(50)
);

CREATE TABLE Maquinas (
    tag_equipamento VARCHAR(20) PRIMARY KEY, 
    id_maquina INT NOT NULL,               
    numero_serie VARCHAR(50) NOT NULL UNIQUE,
    localizacao_maquina VARCHAR(100) NOT NULL,       
    tipo_manutencao_padrao ENUM('Preventiva', 'Corretiva', 'Preditiva') NOT NULL,
    status_operacional ENUM('Operando', 'Parado', 'Em Manutenção') DEFAULT 'Operando',
    ultima_manutencao DATE,
    id_setor INT NOT NULL,
    FOREIGN KEY (id_setor) REFERENCES Setores(id_setor) ON DELETE RESTRICT,
    CONSTRAINT fk_maquinas_modelo
        FOREIGN KEY (id_maquina) 
        REFERENCES Modelos_Maquinas(id_maquina)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Almoxarifado_Pecas (
    id_peca INT AUTO_INCREMENT PRIMARY KEY,
    nome_peca VARCHAR(100) NOT NULL UNIQUE, 
    quantidade_estoque INT NOT NULL DEFAULT 0,
    unidade_medida VARCHAR(20) DEFAULT 'Unidade',
    custo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT chk_quantidade_estoque CHECK (quantidade_estoque >= 0),
    CONSTRAINT chk_custo_unitario CHECK (custo_unitario >= 0.00)
);

CREATE TABLE Almoxarifado_Ferramentas (
    id_ferramenta INT AUTO_INCREMENT PRIMARY KEY,
    nome_ferramenta VARCHAR(100) NOT NULL , 
    status_ferramenta ENUM('Disponível', 'Solicitada', 'Em Uso', 'Manutenção/Calibração', 'Extraviada') DEFAULT 'Disponível'
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
    FOREIGN KEY (tag_equipamento) REFERENCES Maquinas(tag_equipamento) ON DELETE RESTRICT,
    FOREIGN KEY (id_tecnico_responsavel) REFERENCES Tecnicos(id_tecnico) ON DELETE SET NULL,
    CONSTRAINT chk_horario_os CHECK (hh_fim IS NULL OR hh_fim >= hh_inicio)
);

CREATE TABLE OS_Materiais (
    id_os_material INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_peca INT NOT NULL,
    quantidade_utilizada INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_peca) REFERENCES Almoxarifado_Pecas(id_peca) ON DELETE RESTRICT,
    CONSTRAINT chk_qtd_utilizada CHECK (quantidade_utilizada > 0)
);

CREATE TABLE OS_Ferramentas (
    id_os_ferramenta INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_ferramenta INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_ferramenta) REFERENCES Almoxarifado_Ferramentas(id_ferramenta) ON DELETE RESTRICT
);

CREATE TABLE OS_Seguranca (
    id_os_seguranca INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    id_risco INT NOT NULL,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE CASCADE,
    FOREIGN KEY (id_risco) REFERENCES Matriz_Riscos_EPI(id_risco) ON DELETE RESTRICT
);

CREATE TABLE Movimentacao_Ferramentas (
    id_movimentacao INT AUTO_INCREMENT PRIMARY KEY,
    id_ferramenta INT NOT NULL,
    id_os INT,
    id_tecnico_solicitante INT NOT NULL, -- Corrigido para apontar para Técnicos (regra operacional)
    id_almoxarife_entregador INT,       -- Corrigido de "Usuario geral" para a função clara no nome do campo
    data_retirada TIMESTAMP NULL DEFAULT NULL, 
    data_devolucao_prevista DATETIME NOT NULL,
    data_devolucao_real TIMESTAMP NULL,
    status_movimentacao ENUM('Solicitado', 'Em Uso', 'Devolvido', 'Atrasado', 'Extraviado') DEFAULT 'Solicitado',
    observacoes TEXT,
    FOREIGN KEY (id_ferramenta) REFERENCES Almoxarifado_Ferramentas(id_ferramenta) ON DELETE RESTRICT,
    FOREIGN KEY (id_os) REFERENCES Ordens_Servico(id_os) ON DELETE SET NULL,
    FOREIGN KEY (id_tecnico_solicitante) REFERENCES Tecnicos(id_tecnico) ON DELETE RESTRICT,
    FOREIGN KEY (id_almoxarife_entregador) REFERENCES Usuarios(id_usuario) ON DELETE SET NULL,
    CONSTRAINT chk_datas_movimentacao CHECK (data_devolucao_real IS NULL OR data_devolucao_real >= data_retirada)
);
