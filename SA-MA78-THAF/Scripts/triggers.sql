
DELIMITER $$
CREATE TRIGGER trk_valida_somente_tecnico
BEFORE INSERT ON Ordens_Servico
FOR EACH ROW
BEGIN
    DECLARE v_cargo VARCHAR(20);
    SELECT cargo INTO v_cargo 
    FROM Usuarios 
    WHERE id_usuario = NEW.id_usuario;
    
    IF v_cargo <> 'Tecnico' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = "Erro: Apenas usuários com cargo Tecnico podem ser associados a uma OS.";
    END IF;
END$$
DELIMITER ;


DELIMITER $$

-- -----------------------------------------------------------------------------
-- 2) Almoxarifado_Pecas: impede estoque ou custo negativo no cadastro.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_pecas_valida_insert $$
CREATE TRIGGER trg_pecas_valida_insert
BEFORE INSERT ON Almoxarifado_Pecas
FOR EACH ROW
BEGIN
    IF NEW.quantidade_estoque < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantidade em estoque não pode ser negativa.';
    END IF;

    IF NEW.custo_unitario < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Custo unitário não pode ser negativo.';
    END IF;
END $$

-- -----------------------------------------------------------------------------
-- 3) Almoxarifado_Pecas: impede que uma atualização deixe o estoque negativo.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_pecas_valida_update $$
CREATE TRIGGER trg_pecas_valida_update
BEFORE UPDATE ON Almoxarifado_Pecas
FOR EACH ROW
BEGIN
    IF NEW.quantidade_estoque < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantidade em estoque não pode ficar negativa.';
    END IF;
END $$

-- -----------------------------------------------------------------------------
-- 4) OS_Materiais: valida a quantidade utilizada antes de vincular a peça à OS.
--    Garante também que não se utilize mais peças do que existe em estoque.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_os_materiais_valida $$
CREATE TRIGGER trg_os_materiais_valida
BEFORE INSERT ON OS_Materiais
FOR EACH ROW
BEGIN
    DECLARE v_estoque INT;

    IF NEW.quantidade_utilizada <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A quantidade utilizada deve ser maior que zero.';
    END IF;

    SELECT quantidade_estoque INTO v_estoque
    FROM Almoxarifado_Pecas
    WHERE id_peca = NEW.id_peca;

    IF v_estoque IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Peça informada não existe no Almoxarifado.';
    ELSEIF NEW.quantidade_utilizada > v_estoque THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantidade utilizada maior que o estoque disponível.';
    END IF;
END $$

-- -----------------------------------------------------------------------------
-- 5) OS_Materiais: dá baixa automática no estoque quando a peça é vinculada
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_os_materiais_baixa_estoque $$
CREATE TRIGGER trg_os_materiais_baixa_estoque
AFTER INSERT ON OS_Materiais
FOR EACH ROW
BEGIN
    UPDATE Almoxarifado_Pecas
    SET quantidade_estoque = quantidade_estoque - NEW.quantidade_utilizada
    WHERE id_peca = NEW.id_peca;
END $$

-- -----------------------------------------------------------------------------
-- 6) OS_Ferramentas: ao vincular uma ferramenta a uma OS, ela deixa de estar
--    "disponível" no almoxarifado (fica "solicitada" até ser retirada).
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_ferramenta_status_vinculo_os $$
CREATE TRIGGER trg_ferramenta_status_vinculo_os
AFTER INSERT ON OS_Ferramentas
FOR EACH ROW
BEGIN
    UPDATE Almoxarifado_Ferramentas
    SET status_ferramenta = 'solicitada'
    WHERE id_ferramenta = NEW.id_ferramenta
      AND status_ferramenta = 'disponível';
END $$

-- -----------------------------------------------------------------------------
-- 7) Movimentacao_Ferramentas: quando uma movimentação é criada, sincroniza
--    o status da ferramenta no almoxarifado (solicitado -> solicitada,
--    em uso -> em uso).
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_ferramenta_status_movimentacao_insert $$
CREATE TRIGGER trg_ferramenta_status_movimentacao_insert
AFTER INSERT ON Movimentacao_Ferramentas
FOR EACH ROW
BEGIN
    DECLARE v_id_ferramenta INT;

    SELECT id_ferramenta INTO v_id_ferramenta
    FROM OS_Ferramentas
    WHERE id_os_ferramenta = NEW.id_os_ferramenta;

    IF NEW.status_movimentacao = 'em uso' THEN
        UPDATE Almoxarifado_Ferramentas
        SET status_ferramenta = 'em uso'
        WHERE id_ferramenta = v_id_ferramenta;
    ELSEIF NEW.status_movimentacao = 'solicitado' THEN
        UPDATE Almoxarifado_Ferramentas
        SET status_ferramenta = 'solicitada'
        WHERE id_ferramenta = v_id_ferramenta;
    END IF;
END $$

-- -----------------------------------------------------------------------------
-- 8) Movimentacao_Ferramentas: quando o status muda para "devolvido"
--    (ver registrar_devolucao em mov_ferramentas.py), a ferramenta volta a
--    ficar "disponível" no almoxarifado automaticamente.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_ferramenta_status_devolucao $$
CREATE TRIGGER trg_ferramenta_status_devolucao
AFTER UPDATE ON Movimentacao_Ferramentas
FOR EACH ROW
BEGIN
    DECLARE v_id_ferramenta INT;

    IF NEW.status_movimentacao = 'devolvido' AND OLD.status_movimentacao <> 'devolvido' THEN
        SELECT id_ferramenta INTO v_id_ferramenta
        FROM OS_Ferramentas
        WHERE id_os_ferramenta = NEW.id_os_ferramenta;

        UPDATE Almoxarifado_Ferramentas
        SET status_ferramenta = 'disponível'
        WHERE id_ferramenta = v_id_ferramenta;
    END IF;
END $$

-- -----------------------------------------------------------------------------
-- 9) Ordens_Servico: ao encerrar a OS (encerrar_os), valida que hh_fim é
--    posterior a hh_inicio antes de gravar.
--    (referente ao erro "verifique se o horário de término é posterior ao de início")
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_os_valida_encerramento $$
CREATE TRIGGER trg_os_valida_encerramento
BEFORE UPDATE ON Ordens_Servico
FOR EACH ROW
BEGIN
    IF NEW.status_os = 'Concluído'
       AND NEW.hh_fim IS NOT NULL
       AND NEW.hh_inicio IS NOT NULL
       AND NEW.hh_fim <= NEW.hh_inicio THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'O horário de término deve ser posterior ao horário de início.';
    END IF;
END $$

-- -----------------------------------------------------------------------------
-- 10) Ordens_Servico: quando uma OS é concluída, a máquina volta a operar e
--    tem sua data de última manutenção atualizada automaticamente.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_maquina_pos_conclusao_os $$
CREATE TRIGGER trg_maquina_pos_conclusao_os
AFTER UPDATE ON Ordens_Servico
FOR EACH ROW
BEGIN
    IF NEW.status_os = 'Concluído' AND OLD.status_os <> 'Concluído' THEN
        UPDATE Maquinas
        SET status_operacional = 'operando',
            ultima_manutencao = CURDATE()
        WHERE tag_equipamento = NEW.tag_equipamento;
    END IF;
END $$

-- -----------------------------------------------------------------------------
-- 11) Ordens_Servico: ao abrir uma OS para uma máquina, ela passa para
--     "parado" (equipamento em intervenção). Ative apenas se essa for
--     realmente a regra do seu negócio, pois nem toda OS aberta implica
--     parada imediata do equipamento.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_maquina_parada_abertura_os $$
CREATE TRIGGER trg_maquina_parada_abertura_os
AFTER INSERT ON Ordens_Servico
FOR EACH ROW
BEGIN
    UPDATE Maquinas
    SET status_operacional = 'parado'
    WHERE tag_equipamento = NEW.tag_equipamento;
END $$

DELIMITER ;