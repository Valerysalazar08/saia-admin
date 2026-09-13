-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: sena
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
-- Table structure for table `aprendiz`
--

DROP TABLE IF EXISTS `aprendiz`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `aprendiz` (
  `id_aprendiz` int NOT NULL AUTO_INCREMENT,
  `num_doc` bigint NOT NULL,
  `id_ficha` int NOT NULL,
  `estado` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_aprendiz`),
  UNIQUE KEY `num_doc` (`num_doc`),
  KEY `id_ficha` (`id_ficha`),
  CONSTRAINT `aprendiz_ibfk_1` FOREIGN KEY (`id_ficha`) REFERENCES `ficha` (`id_ficha`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aprendiz`
--

LOCK TABLES `aprendiz` WRITE;
/*!40000 ALTER TABLE `aprendiz` DISABLE KEYS */;
INSERT INTO `aprendiz` VALUES (1,9999999999,1,1),(2,1005980488,1,1),(3,1005978154,1,1),(4,1008095147,1,1);
/*!40000 ALTER TABLE `aprendiz` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `centro_formacion`
--

DROP TABLE IF EXISTS `centro_formacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `centro_formacion` (
  `id_centro` int NOT NULL AUTO_INCREMENT,
  `nombre_centro` varchar(100) DEFAULT NULL,
  `descripcion_centro` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_centro`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `centro_formacion`
--

LOCK TABLES `centro_formacion` WRITE;
/*!40000 ALTER TABLE `centro_formacion` DISABLE KEYS */;
INSERT INTO `centro_formacion` VALUES (1,'CEAI','Centro de Electricidad y Automatizacion Industrial'),(2,'CGTS','Centro de Gestión Tecnológica de Servicios'),(3,'CDTI','Centro de Diseño Tecnológico Industrial'),(4,'ASTIN','Centro Nacional de la Asistencia Técnica a la Industria');
/*!40000 ALTER TABLE `centro_formacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ficha`
--

DROP TABLE IF EXISTS `ficha`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ficha` (
  `id_ficha` int NOT NULL AUTO_INCREMENT,
  `id_programa` int NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_finalizacion` date DEFAULT NULL,
  PRIMARY KEY (`id_ficha`),
  KEY `id_programa` (`id_programa`),
  CONSTRAINT `ficha_ibfk_1` FOREIGN KEY (`id_programa`) REFERENCES `programa_formacion` (`id_programa`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ficha`
--

LOCK TABLES `ficha` WRITE;
/*!40000 ALTER TABLE `ficha` DISABLE KEYS */;
INSERT INTO `ficha` VALUES (1,1,'2025-01-15','2026-12-15');
/*!40000 ALTER TABLE `ficha` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `programa_formacion`
--

DROP TABLE IF EXISTS `programa_formacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `programa_formacion` (
  `id_programa` int NOT NULL AUTO_INCREMENT,
  `id_centro` int NOT NULL,
  `descripcion_programa` varchar(250) DEFAULT NULL,
  `nombre_programa` varchar(250) DEFAULT NULL,
  `carrera` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_programa`),
  KEY `id_centro` (`id_centro`),
  CONSTRAINT `programa_formacion_ibfk_1` FOREIGN KEY (`id_centro`) REFERENCES `centro_formacion` (`id_centro`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `programa_formacion`
--

LOCK TABLES `programa_formacion` WRITE;
/*!40000 ALTER TABLE `programa_formacion` DISABLE KEYS */;
INSERT INTO `programa_formacion` VALUES (1,1,'Formación en diseño, montaje y mantenimiento de sistemas automáticos basados en PLC, neumática, hidráulica y control de procesos industriales.','Tecnólogo en Automatización Industrial.','TECNOLOGO'),(2,1,'Enfocado en el montaje, operación y mantenimiento de instalaciones eléctricas industriales, tableros de control y sistemas de distribución de media tensión.','Tecnólogo en Electricidad Industrial','TECNOLOGO'),(3,1,'Capacita en el diagnóstico, calibración y reparación de tarjetas electrónicas, sensores e instrumentos de medición utilizados en plantas de producción.','Tecnólogo en Mantenimiento Electrónico e Instrumental Industrial','TECNOLOGO'),(4,1,'Desarrolla habilidades para el montaje, mantenimiento y reparación de acometidas, redes de iluminación y tomacorrientes en viviendas según el reglamento RETIE.','Técnico en Instalaciones Eléctricas Residenciales','TECNICO'),(5,1,'Formación en ensamble, mantenimiento preventivo y correctivo de computadores, instalación de sistemas operativos y diagnóstico de redes básicas de datos.','Técnico en Mantenimiento de Equipos de Cómputo','TECNICO'),(6,2,'Capacita en la recolección, registro, análisis y presentación de estados financieros en empresas, aplicando la normativa tributaria y comercial vigente.','Tecnólogo en Gestión Contable y de Información Financiera','TECNOLOGO'),(7,2,'Enfocado en el ciclo de vida del software: diseño de bases de datos, codificación en múltiples lenguajes de programación, pruebas y despliegue de aplicaciones.','Tecnólogo en Análisis y Desarrollo de Software','TECNOLOGO'),(8,2,'Formación en optimización de procesos de oficina, gestión documental, organización de eventos empresariales y soporte estratégico a la gerencia.','Tecnólogo en Gestión Administrativa','TECNOLOGO'),(9,2,'Prepara para coordinar procesos de selección, contratación, nómina, inducción y programas de bienestar laboral en organizaciones del sector público o privado.','Tecnólogo en Gestión del Talento Humano','TECNOLOGO'),(10,2,'Capacita en atención al cliente, operaciones de caja, asesoría de microcréditos y portafolio de servicios financieros en bancos y entidades comerciales.','Técnico en Servicios Comerciales y Financieros','TECNICO'),(11,3,'Integración de mecánica, electrónica y sistemas computarizados para el diagnóstico, reparación y puesta a punto de vehículos modernos y motocicletas.','Tecnólogo en Mantenimiento Mecatrónico de Automotores','TECNOLOGO'),(12,3,'Desarrollo de proyectos de animación en 2D y 3D, abarcando modelado, rigging, texturizado, iluminación y composición de escenas para la industria del entretenimiento.','Tecnólogo en Animación Digital','TECNOLOGO'),(13,3,'Enfocado en el diseño de piezas gráficas publicitarias, identidad corporativa, diagramación editorial y creación de interfaces digitales interactivas.','Tecnólogo en Desarrollo de Medios Gráficos Visuales','TECNOLOGO'),(14,3,'Formación práctica en procesos de soldadura por arco eléctrico (SMAW y GMAW) sobre platinas de acero al carbono, bajo normas internacionales de calidad.','Técnico en Soldadura de Productos Metálicos en Platina','TECNICO'),(15,3,'Capacita en la interpretación de diseños, elaboración de patrones base, escalado industrial y trazo técnico de prendas según requerimientos de producción textil.','Técnico en Patronaje Industrial de Prendas de Vestir','TECNICO'),(16,4,'Formación en análisis de laboratorio químico, control de calidad de materias primas, preparación de soluciones y manejo de equipos analíticos complejos.','Tecnólogo en Química Aplicada a la Industria','TECNOLOGO'),(17,4,'Enfocado en la parametrización de maquinaria industrial para procesos de inyección, soplado y extrusión de plásticos para empaques y componentes.','Tecnólogo en Transformación de Materiales Termoplásticos','TECNOLOGO'),(18,4,'Diseño asistido por computador (CAD/CAM) de moldes metálicos complejos y herramentales especializados para la fabricación de productos plásticos.','Tecnólogo en Diseño de Moldes para Inyección de Plásticos','TECNOLOGO'),(19,4,'Programación y operación de maquinaria convencional y de control numérico computarizado (CNC) para el mecanizado de precisión de piezas metálicas.','Tecnólogo en Fabricación de Productos Metalmecánicos','TECNOLOGO'),(20,4,'Capacita en la manipulación segura de reactivos químicos, monitoreo de reactores industriales, plantas de tratamiento de aguas y control de procesos en planta.','Técnico en Operación de Procesos Químicos Industriales','TECNICO');
/*!40000 ALTER TABLE `programa_formacion` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-14 17:00:00
