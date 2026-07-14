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
