-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: saia
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administrador`
--

DROP TABLE IF EXISTS `administrador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administrador` (
  `id_admin` int NOT NULL AUTO_INCREMENT,
  `num_doc` bigint NOT NULL,
  PRIMARY KEY (`id_admin`),
  UNIQUE KEY `num_doc` (`num_doc`),
  CONSTRAINT `administrador_ibfk_1` FOREIGN KEY (`num_doc`) REFERENCES `persona` (`num_doc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrador`
--

LOCK TABLES `administrador` WRITE;
/*!40000 ALTER TABLE `administrador` DISABLE KEYS */;
/*!40000 ALTER TABLE `administrador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cuenta`
--

DROP TABLE IF EXISTS `cuenta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cuenta` (
  `id_cuenta` int NOT NULL AUTO_INCREMENT,
  `id_rol` int NOT NULL,
  `num_doc` bigint NOT NULL,
  `estado` tinyint(1) DEFAULT '1',
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `password` varchar(255) NOT NULL,
  `id_ficha` int DEFAULT NULL,
  `id_programa` int DEFAULT NULL,
  `id_centro` int DEFAULT NULL,
  `imagen` varchar(150) DEFAULT NULL,
  `sesion_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_cuenta`),
  UNIQUE KEY `num_doc` (`num_doc`),
  KEY `id_rol` (`id_rol`),
  CONSTRAINT `cuenta_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`),
  CONSTRAINT `cuenta_ibfk_2` FOREIGN KEY (`num_doc`) REFERENCES `persona` (`num_doc`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuenta`
--

LOCK TABLES `cuenta` WRITE;
/*!40000 ALTER TABLE `cuenta` DISABLE KEYS */;
INSERT INTO `cuenta` VALUES (1,1,1005978154,1,NULL,'$2b$10$.XOR9CraVw4/kTI8ykOF/uWDBnDrb1//uSIdOijwuLXh6M5JGIZQe',1,1,1,'/uploads/perfiles/perfil_1005978154_1786339371893.jpeg','cf34ebec-43f8-4038-ae9b-1913e1cad985'),(2,3,1005978456,1,'2026-08-07 19:19:21','$2b$10$fuWyucFe3NN9xr98xJNeEObg06RYz5uStqUVuHOs0Qynqyg3ZKwm2',NULL,NULL,NULL,NULL,'22988440-9d61-46df-8a31-172d4e543b3a'),(3,1,1005980488,1,'2026-08-09 22:25:00','$2b$10$VcfRONEjU8HqAO7IPD474.Evfpl63cB3YjKPrqS40wWVTf3hgg7.W',1,1,1,NULL,NULL);
/*!40000 ALTER TABLE `cuenta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial`
--

DROP TABLE IF EXISTS `historial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial` (
  `id_ingreso` int NOT NULL AUTO_INCREMENT,
  `id_guarda` int NOT NULL,
  `fecha_hora_ingreso` datetime NOT NULL,
  `fecha_hora_salida` datetime DEFAULT NULL,
  `estado_movimiento` varchar(20) DEFAULT NULL,
  `observacion` text,
  `num_doc` bigint NOT NULL,
  `codigo` varchar(20) DEFAULT NULL,
  `porteria` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_ingreso`),
  KEY `id_guarda` (`id_guarda`),
  KEY `fk_ingreso_persona` (`num_doc`),
  CONSTRAINT `fk_ingreso_persona` FOREIGN KEY (`num_doc`) REFERENCES `persona` (`num_doc`),
  CONSTRAINT `historial_ibfk_2` FOREIGN KEY (`id_guarda`) REFERENCES `personal_seguridad` (`id_guarda`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial`
--

LOCK TABLES `historial` WRITE;
/*!40000 ALTER TABLE `historial` DISABLE KEYS */;
INSERT INTO `historial` VALUES (1,1,'2026-08-08 17:43:54','2026-08-09 11:15:33','0',NULL,1005978154,NULL,NULL),(2,1,'2026-08-09 21:05:30',NULL,'1',NULL,1005978154,NULL,NULL),(3,1,'2026-08-09 23:07:25','2026-08-09 23:09:36','0',NULL,1005980488,NULL,NULL);
/*!40000 ALTER TABLE `historial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_turno_guarda`
--

DROP TABLE IF EXISTS `historial_turno_guarda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_turno_guarda` (
  `id_historial_turno` int NOT NULL AUTO_INCREMENT,
  `id_guarda` int NOT NULL,
  `fecha` date NOT NULL,
  `inicio_turno` datetime NOT NULL,
  `finalizacion_turno` datetime DEFAULT NULL,
  `turno` enum('Mañana','Tarde','Noche') NOT NULL,
  `empresa_seg` varchar(100) NOT NULL,
  `estado` enum('ACTIVO','FINALIZADO') NOT NULL DEFAULT 'ACTIVO',
  PRIMARY KEY (`id_historial_turno`),
  KEY `id_guarda` (`id_guarda`),
  CONSTRAINT `historial_turno_guarda_ibfk_1` FOREIGN KEY (`id_guarda`) REFERENCES `personal_seguridad` (`id_guarda`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_turno_guarda`
--

LOCK TABLES `historial_turno_guarda` WRITE;
/*!40000 ALTER TABLE `historial_turno_guarda` DISABLE KEYS */;
INSERT INTO `historial_turno_guarda` VALUES (1,1,'2026-08-08','2026-08-08 17:31:15','2026-08-08 17:33:37','Mañana','ATLAS','FINALIZADO'),(2,1,'2026-08-08','2026-08-08 17:36:14','2026-08-08 17:37:28','Tarde','ATLAS','FINALIZADO'),(3,1,'2026-08-08','2026-08-08 17:37:33','2026-08-08 17:45:02','Mañana','ATLAS','FINALIZADO'),(4,1,'2026-08-09','2026-08-09 11:15:22','2026-08-09 11:15:40','Tarde','ATLAS','FINALIZADO'),(5,1,'2026-08-09','2026-08-09 20:34:26','2026-08-10 01:19:22','Mañana','ATLAS','FINALIZADO'),(6,1,'2026-08-13','2026-08-13 21:30:17','2026-08-13 21:30:36','Tarde','ATLAS','FINALIZADO');
/*!40000 ALTER TABLE `historial_turno_guarda` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ingreso_insumo`
--

DROP TABLE IF EXISTS `ingreso_insumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingreso_insumo` (
  `id_ingreso` int NOT NULL,
  `id_insumo` int NOT NULL,
  `ingreso` tinyint(1) DEFAULT '1',
  `salida` tinyint(1) DEFAULT '1',
  `observacion` varchar(255) DEFAULT NULL,
  `estado` varchar(30) NOT NULL DEFAULT 'Registrado',
  PRIMARY KEY (`id_ingreso`,`id_insumo`),
  KEY `id_insumo` (`id_insumo`),
  CONSTRAINT `ingreso_insumo_ibfk_1` FOREIGN KEY (`id_ingreso`) REFERENCES `historial` (`id_ingreso`),
  CONSTRAINT `ingreso_insumo_ibfk_2` FOREIGN KEY (`id_insumo`) REFERENCES `insumo` (`id_insumo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingreso_insumo`
--

LOCK TABLES `ingreso_insumo` WRITE;
/*!40000 ALTER TABLE `ingreso_insumo` DISABLE KEYS */;
INSERT INTO `ingreso_insumo` VALUES (3,2,1,1,NULL,'Registrado'),(3,4,1,1,NULL,'Registrado'),(3,5,1,1,NULL,'Registrado');
/*!40000 ALTER TABLE `ingreso_insumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumo`
--

DROP TABLE IF EXISTS `insumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumo` (
  `id_insumo` int NOT NULL AUTO_INCREMENT,
  `nom_insumo` varchar(100) NOT NULL,
  `estado` tinyint(1) DEFAULT '1',
  `marca` varchar(100) DEFAULT NULL,
  `num_serie` varchar(100) DEFAULT NULL,
  `desc_insumo` text,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `imagen` varchar(150) DEFAULT NULL,
  `num_doc` bigint NOT NULL,
  PRIMARY KEY (`id_insumo`),
  UNIQUE KEY `num_serie` (`num_serie`),
  KEY `fk_insumo_persona` (`num_doc`),
  CONSTRAINT `fk_insumo_persona` FOREIGN KEY (`num_doc`) REFERENCES `persona` (`num_doc`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumo`
--

LOCK TABLES `insumo` WRITE;
/*!40000 ALTER TABLE `insumo` DISABLE KEYS */;
INSERT INTO `insumo` VALUES (1,'rasds',0,'HP','asdasdas','asdadada','2026-08-10 01:02:44',NULL,1005978154),(2,'Portátil ',1,'Lenovo','TFVHRRKGXH','Portátil casi nuevo con dos teclas malas','2026-08-10 03:48:59','uploads/img/1786333736963.jpeg',1005980488),(4,'Tttt',1,'Lenovo','VFFGJJ','Hehejejhejeje','2026-08-10 03:55:14','uploads/img/1786334114120.jpeg',1005980488),(5,'Jejejejjeje',1,'ASUS','JEJEJUE','Idkejeje','2026-08-10 03:57:55','uploads/img/1786334275907.jpeg',1005980488),(10,'Jejejejjejejejejw',0,'ASUS','JEJEJUEBSBE','Idkejeje','2026-08-10 04:00:01','uploads/img/1786334401867.jpeg',1005980488);
/*!40000 ALTER TABLE `insumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `persona`
--

DROP TABLE IF EXISTS `persona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `persona` (
  `num_doc` bigint NOT NULL,
  `tip_doc` varchar(20) NOT NULL,
  `nombres` varchar(50) NOT NULL,
  `p_ape` varchar(50) NOT NULL,
  `tel` varchar(20) DEFAULT NULL,
  `tip_sang` varchar(5) DEFAULT NULL,
  `sexo` varchar(20) DEFAULT NULL,
  `fecha_nac` date DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`num_doc`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `chk_doc` CHECK ((not((`num_doc` like _utf8mb4'% %'))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `persona`
--

LOCK TABLES `persona` WRITE;
/*!40000 ALTER TABLE `persona` DISABLE KEYS */;
INSERT INTO `persona` VALUES (1005978154,'Cédula de Ciudadanía','Hian Michel ','Osorio Andrade','3122288971','O+','Masculino','2002-04-16','mich344741@gmail.com'),(1005978456,'Cédula de Ciudadanía','Alice','Castillo','3200856245','O-','','1990-02-27','Alice578_@gmail.com'),(1005980488,'Cédula de Ciudadanía','Valery ','Salazar Cabrera','3175310689','B+','','2003-08-12','valerysalazar0812@gmail.com');
/*!40000 ALTER TABLE `persona` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `personal_seguridad`
--

DROP TABLE IF EXISTS `personal_seguridad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `personal_seguridad` (
  `id_guarda` int NOT NULL AUTO_INCREMENT,
  `num_doc` bigint NOT NULL,
  `turno` varchar(30) DEFAULT NULL,
  `empresa_seg` varchar(100) DEFAULT NULL,
  `inicio_turno` datetime DEFAULT NULL,
  `finalizacion_turno` datetime DEFAULT NULL,
  `observacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_guarda`),
  UNIQUE KEY `num_doc` (`num_doc`),
  CONSTRAINT `personal_seguridad_ibfk_1` FOREIGN KEY (`num_doc`) REFERENCES `persona` (`num_doc`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `personal_seguridad`
--

LOCK TABLES `personal_seguridad` WRITE;
/*!40000 ALTER TABLE `personal_seguridad` DISABLE KEYS */;
INSERT INTO `personal_seguridad` VALUES (1,1005978456,NULL,'ATLAS','2026-08-13 21:30:17','2026-08-13 21:30:36',NULL);
/*!40000 ALTER TABLE `personal_seguridad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recordatorio`
--

DROP TABLE IF EXISTS `recordatorio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recordatorio` (
  `id_recordatorio` int NOT NULL AUTO_INCREMENT,
  `num_doc` bigint NOT NULL,
  `titulo` varchar(150) NOT NULL,
  `descripcion` text,
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `fecha_limite` date NOT NULL,
  `hora_limite` time DEFAULT NULL,
  `prioridad` tinyint NOT NULL DEFAULT '2',
  `url` varchar(500) DEFAULT NULL,
  `estado` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_recordatorio`),
  KEY `num_doc` (`num_doc`),
  CONSTRAINT `recordatorio_ibfk_1` FOREIGN KEY (`num_doc`) REFERENCES `persona` (`num_doc`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recordatorio`
--

LOCK TABLES `recordatorio` WRITE;
/*!40000 ALTER TABLE `recordatorio` DISABLE KEYS */;
INSERT INTO `recordatorio` VALUES (1,1005980488,'Tarea Python Ciclos ','Tarea Ciclos 15 Ejercicios en Python acerca de Ciclos ','2026-08-09 22:29:03','2026-08-13','23:57:00',1,NULL,0),(2,1005978154,'Exposición piloto proyecto formativo ','El proyecto se expondrá el próximo lunes.','2026-08-09 22:30:06','2026-08-25','18:00:00',1,NULL,0),(3,1005980488,'Tarea Proyecto ','Hacer Prueba de Exposición para proyecto','2026-08-09 22:31:20','2026-08-25','12:30:00',2,'https://drive.google.com/drive/folders/17BkE9PJVOBQW_6z0aP8GLqkgJXtPVjTE',0),(4,1005980488,'Hola','Hofofk','2026-08-09 22:35:15','2026-08-18','22:34:35',2,NULL,0),(5,1005978154,'Eliminar ','Eliminar ','2026-08-09 22:37:27','2026-08-10','22:34:36',3,NULL,0);
/*!40000 ALTER TABLE `recordatorio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reporte`
--

DROP TABLE IF EXISTS `reporte`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reporte` (
  `id_reporte` int NOT NULL AUTO_INCREMENT,
  `id_insumo` int NOT NULL,
  `descripcion` text,
  `fecha_reporte` datetime DEFAULT CURRENT_TIMESTAMP,
  `num_doc` bigint NOT NULL,
  PRIMARY KEY (`id_reporte`),
  KEY `id_insumo` (`id_insumo`),
  KEY `fk_perdida_persona` (`num_doc`),
  CONSTRAINT `fk_perdida_persona` FOREIGN KEY (`num_doc`) REFERENCES `persona` (`num_doc`),
  CONSTRAINT `reporte_ibfk_2` FOREIGN KEY (`id_insumo`) REFERENCES `insumo` (`id_insumo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reporte`
--

LOCK TABLES `reporte` WRITE;
/*!40000 ALTER TABLE `reporte` DISABLE KEYS */;
/*!40000 ALTER TABLE `reporte` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nom_rol` varchar(50) NOT NULL,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `nom_rol` (`nom_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (2,'administrador'),(1,'aprendiz'),(3,'guarda');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-14 16:59:24
