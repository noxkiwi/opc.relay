DROP TABLE `relay`;

CREATE TABLE `relay` (
	`relay_id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`relay_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`relay_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`relay_flags` TINYINT(3) UNSIGNED NOT NULL DEFAULT '0',
	`relay_name` VARCHAR(64) NOT NULL COMMENT 'I am the readable name of this relais.' COLLATE 'utf8_general_ci',
	`relay_enable` INT(10) UNSIGNED NOT NULL COMMENT 'I am the 433MHz command to send to turn relais ON',
	`relay_disable` INT(10) UNSIGNED NOT NULL COMMENT 'I am the 433MHz command to send to turn the relais OFF',
	`opc_item_setpoint` INT(10) UNSIGNED NOT NULL COMMENT 'I am the OPC address that is read to fetch the command.',
	`opc_item_current` INT(10) UNSIGNED NOT NULL COMMENT 'I am the OPC address that is read to publish the current status.',
	PRIMARY KEY (`relay_id`) USING BTREE,
	UNIQUE INDEX `relay_enable` (`relay_enable`) USING BTREE,
	UNIQUE INDEX `relay_disable` (`relay_disable`) USING BTREE,
	UNIQUE INDEX `relay_name` (`relay_name`) USING BTREE,
	UNIQUE INDEX `opc_item_current_unique` (`opc_item_current`) USING BTREE,
	INDEX `relay_opc_item_setpoint` (`opc_item_setpoint`) USING BTREE,
	INDEX `opc_item_current` (`opc_item_current`) USING BTREE,
	CONSTRAINT `relay_opc_item_current` FOREIGN KEY (`opc_item_current`) REFERENCES `opc_item` (`opc_item_id`) ON UPDATE NO ACTION ON DELETE NO ACTION,
	CONSTRAINT `relay_opc_item_setpoint` FOREIGN KEY (`opc_item_setpoint`) REFERENCES `opc_item` (`opc_item_id`) ON UPDATE NO ACTION ON DELETE NO ACTION
) COLLATE='utf8_general_ci' ENGINE=INNODB;
