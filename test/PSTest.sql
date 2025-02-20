CREATE SCHEMA `PSTest`;
CREATE USER 'PSTestUser'@'localhost' IDENTIFIED BY 'PSTestPassword';
GRANT ALL PRIVILEGES ON `PSTest`.* TO 'PSTestUser'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
USE `PSTest`;
CREATE TABLE `User`
	(`Name` VARCHAR(80) NOT NULL, 
   `PhoneNumber` VARCHAR(14), 
   `Age` INT DEFAULT 0,
   PRIMARY KEY (`Name`));
INSERT INTO `User`(`Name`, `PhoneNumber`, `Age`) VALUES('Aymeric', '06.83.34.04.93', 24);
INSERT INTO `User`(`Name`, `PhoneNumber`, `Age`) VALUES('Helene', '06.17.17.04.93', 32);
INSERT INTO `User`(`Name`, `PhoneNumber`, `Age`) VALUES('Marie', '06.83.17.04.93', 22);
INSERT INTO `User`(`Name`, `PhoneNumber`, `Age`) VALUES('Tata', '99.99.99.99.99', 88);
INSERT INTO `User`(`Name`, `PhoneNumber`, `Age`) VALUES('Toto', '77.77', 1);
COMMIT;