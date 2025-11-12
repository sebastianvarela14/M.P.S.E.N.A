-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: proyecto
-- ------------------------------------------------------
-- Server version	9.5.0

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '625c0673-bf35-11f0-aa35-00410ea36cd2:1-170';

--
-- Table structure for table `archivos`
--

DROP TABLE IF EXISTS `archivos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `archivos` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla archivos',
  `nombre_archivo` varchar(100) NOT NULL COMMENT 'nombre de la evidencia para su identificacion en carpetas',
  `fecha_entrega` date DEFAULT NULL COMMENT 'fecha limite de entrega de la evidencia',
  `idcarpetas` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla archivos con carpetas',
  PRIMARY KEY (`id`),
  KEY `idcarpetas` (`idcarpetas`),
  CONSTRAINT `archivos_ibfk_1` FOREIGN KEY (`idcarpetas`) REFERENCES `carpetas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `archivos`
--

LOCK TABLES `archivos` WRITE;
/*!40000 ALTER TABLE `archivos` DISABLE KEYS */;
INSERT INTO `archivos` VALUES (1,'taller','2025-09-11',1),(2,'python','2025-10-02',1),(3,'Taller resuelto Luara Camila','2025-10-07',2),(4,'Plan mejoramiento','2025-09-02',4),(5,'Plan concertado','2025-09-02',3);
/*!40000 ALTER TABLE `archivos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add archivos',7,'add_archivos'),(26,'Can change archivos',7,'change_archivos'),(27,'Can delete archivos',7,'delete_archivos'),(28,'Can view archivos',7,'view_archivos'),(29,'Can add carpetas',8,'add_carpetas'),(30,'Can change carpetas',8,'change_carpetas'),(31,'Can delete carpetas',8,'delete_carpetas'),(32,'Can view carpetas',8,'view_carpetas'),(33,'Can add documento',9,'add_documento'),(34,'Can change documento',9,'change_documento'),(35,'Can delete documento',9,'delete_documento'),(36,'Can view documento',9,'view_documento'),(37,'Can add evidencias aprendiz',10,'add_evidenciasaprendiz'),(38,'Can change evidencias aprendiz',10,'change_evidenciasaprendiz'),(39,'Can delete evidencias aprendiz',10,'delete_evidenciasaprendiz'),(40,'Can view evidencias aprendiz',10,'view_evidenciasaprendiz'),(41,'Can add evidencias ficha',11,'add_evidenciasficha'),(42,'Can change evidencias ficha',11,'change_evidenciasficha'),(43,'Can delete evidencias ficha',11,'delete_evidenciasficha'),(44,'Can view evidencias ficha',11,'view_evidenciasficha'),(45,'Can add evidencias instructor',12,'add_evidenciasinstructor'),(46,'Can change evidencias instructor',12,'change_evidenciasinstructor'),(47,'Can delete evidencias instructor',12,'delete_evidenciasinstructor'),(48,'Can view evidencias instructor',12,'view_evidenciasinstructor'),(49,'Can add ficha',13,'add_ficha'),(50,'Can change ficha',13,'change_ficha'),(51,'Can delete ficha',13,'delete_ficha'),(52,'Can view ficha',13,'view_ficha'),(53,'Can add ficha carpetas',14,'add_fichacarpetas'),(54,'Can change ficha carpetas',14,'change_fichacarpetas'),(55,'Can delete ficha carpetas',14,'delete_fichacarpetas'),(56,'Can view ficha carpetas',14,'view_fichacarpetas'),(57,'Can add ficha usuario',15,'add_fichausuario'),(58,'Can change ficha usuario',15,'change_fichausuario'),(59,'Can delete ficha usuario',15,'delete_fichausuario'),(60,'Can view ficha usuario',15,'view_fichausuario'),(61,'Can add jornada',16,'add_jornada'),(62,'Can change jornada',16,'change_jornada'),(63,'Can delete jornada',16,'delete_jornada'),(64,'Can view jornada',16,'view_jornada'),(65,'Can add material',17,'add_material'),(66,'Can change material',17,'change_material'),(67,'Can delete material',17,'delete_material'),(68,'Can view material',17,'view_material'),(69,'Can add material usuario',18,'add_materialusuario'),(70,'Can change material usuario',18,'change_materialusuario'),(71,'Can delete material usuario',18,'delete_materialusuario'),(72,'Can view material usuario',18,'view_materialusuario'),(73,'Can add nombre asignatura',19,'add_nombreasignatura'),(74,'Can change nombre asignatura',19,'change_nombreasignatura'),(75,'Can delete nombre asignatura',19,'delete_nombreasignatura'),(76,'Can view nombre asignatura',19,'view_nombreasignatura'),(77,'Can add programa',20,'add_programa'),(78,'Can change programa',20,'change_programa'),(79,'Can delete programa',20,'delete_programa'),(80,'Can view programa',20,'view_programa'),(81,'Can add rol',21,'add_rol'),(82,'Can change rol',21,'change_rol'),(83,'Can delete rol',21,'delete_rol'),(84,'Can view rol',21,'view_rol'),(85,'Can add tipo asignatura',22,'add_tipoasignatura'),(86,'Can change tipo asignatura',22,'change_tipoasignatura'),(87,'Can delete tipo asignatura',22,'delete_tipoasignatura'),(88,'Can view tipo asignatura',22,'view_tipoasignatura'),(89,'Can add usuario',23,'add_usuario'),(90,'Can change usuario',23,'change_usuario'),(91,'Can delete usuario',23,'delete_usuario'),(92,'Can view usuario',23,'view_usuario'),(93,'Can add usuario rol',24,'add_usuariorol'),(94,'Can change usuario rol',24,'change_usuariorol'),(95,'Can delete usuario rol',24,'delete_usuariorol'),(96,'Can view usuario rol',24,'view_usuariorol');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carpetas`
--

DROP TABLE IF EXISTS `carpetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carpetas` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla carpetas',
  `nombre` varchar(100) NOT NULL COMMENT 'nombre de la carpeta (ej: plan concertado, evidencias de aprendizaje, guias de aprendizajes,  etc.)',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carpetas`
--

LOCK TABLES `carpetas` WRITE;
/*!40000 ALTER TABLE `carpetas` DISABLE KEYS */;
INSERT INTO `carpetas` VALUES (1,'evidencias de aprendizaje'),(2,'guias de aprendizaje'),(3,'plan concertado'),(4,'planes de accion de mejora');
/*!40000 ALTER TABLE `carpetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(7,'pantallas','archivos'),(8,'pantallas','carpetas'),(9,'pantallas','documento'),(10,'pantallas','evidenciasaprendiz'),(11,'pantallas','evidenciasficha'),(12,'pantallas','evidenciasinstructor'),(13,'pantallas','ficha'),(14,'pantallas','fichacarpetas'),(15,'pantallas','fichausuario'),(16,'pantallas','jornada'),(17,'pantallas','material'),(18,'pantallas','materialusuario'),(19,'pantallas','nombreasignatura'),(20,'pantallas','programa'),(21,'pantallas','rol'),(22,'pantallas','tipoasignatura'),(23,'pantallas','usuario'),(24,'pantallas','usuariorol'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-11-11 20:08:31.076596'),(2,'auth','0001_initial','2025-11-11 20:08:31.617444'),(3,'admin','0001_initial','2025-11-11 20:08:31.769831'),(4,'admin','0002_logentry_remove_auto_add','2025-11-11 20:08:31.776687'),(5,'admin','0003_logentry_add_action_flag_choices','2025-11-11 20:08:31.785826'),(6,'contenttypes','0002_remove_content_type_name','2025-11-11 20:08:31.969633'),(7,'auth','0002_alter_permission_name_max_length','2025-11-11 20:08:32.031751'),(8,'auth','0003_alter_user_email_max_length','2025-11-11 20:08:32.049352'),(9,'auth','0004_alter_user_username_opts','2025-11-11 20:08:32.055211'),(10,'auth','0005_alter_user_last_login_null','2025-11-11 20:08:32.114086'),(11,'auth','0006_require_contenttypes_0002','2025-11-11 20:08:32.116444'),(12,'auth','0007_alter_validators_add_error_messages','2025-11-11 20:08:32.121438'),(13,'auth','0008_alter_user_username_max_length','2025-11-11 20:08:32.200085'),(14,'auth','0009_alter_user_last_name_max_length','2025-11-11 20:08:32.270015'),(15,'auth','0010_alter_group_name_max_length','2025-11-11 20:08:32.291131'),(16,'auth','0011_update_proxy_permissions','2025-11-11 20:08:32.299361'),(17,'auth','0012_alter_user_first_name_max_length','2025-11-11 20:08:32.377116'),(18,'sessions','0001_initial','2025-11-11 20:08:32.419049'),(19,'pantallas','0001_initial','2025-11-11 21:28:48.870070');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documento`
--

DROP TABLE IF EXISTS `documento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documento` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla documento',
  `tipo` varchar(20) NOT NULL COMMENT 'que tipo de documento tiene el usuario cedula, tarjeta de identidad, etc',
  `numero` bigint DEFAULT NULL COMMENT 'es el numero de identificacion',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documento`
--

LOCK TABLES `documento` WRITE;
/*!40000 ALTER TABLE `documento` DISABLE KEYS */;
INSERT INTO `documento` VALUES (1,'cédula',3118854578),(2,'tarjeta_identidad',9872345678);
/*!40000 ALTER TABLE `documento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencias_aprendiz`
--

DROP TABLE IF EXISTS `evidencias_aprendiz`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencias_aprendiz` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla evidencias_aprendiz',
  `archivo` varchar(50) NOT NULL COMMENT 'documentos evidencias, material de apoyo',
  `observaciones` varchar(300) DEFAULT NULL COMMENT ' observaciones del intructor',
  `fecha_entrega` date DEFAULT NULL COMMENT 'la fecha de la entrega de las evidencias',
  `idusuario` int DEFAULT NULL COMMENT ' esta es la llave foranea que conecta la tabla evidencias_aprendiz con usuario',
  `idevidencias_instructor` int DEFAULT NULL COMMENT ' esta es la llave foranea que conecta la tabla evidencias_aprendiz con evidencias_instructor',
  PRIMARY KEY (`id`),
  KEY `idusuario` (`idusuario`),
  KEY `idevidencias_instructor` (`idevidencias_instructor`),
  CONSTRAINT `evidencias_aprendiz_ibfk_1` FOREIGN KEY (`idusuario`) REFERENCES `usuario` (`id`),
  CONSTRAINT `evidencias_aprendiz_ibfk_2` FOREIGN KEY (`idevidencias_instructor`) REFERENCES `evidencias_instructor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencias_aprendiz`
--

LOCK TABLES `evidencias_aprendiz` WRITE;
/*!40000 ALTER TABLE `evidencias_aprendiz` DISABLE KEYS */;
INSERT INTO `evidencias_aprendiz` VALUES (1,'archivo.pdf','Muy buen trabajo!','2025-10-03',3,1),(2,'taller.jpg','Te falta el punto numero 11 y 12 y los puntos 13 y 14 falta el procedimiento','2025-11-28',4,2);
/*!40000 ALTER TABLE `evidencias_aprendiz` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencias_ficha`
--

DROP TABLE IF EXISTS `evidencias_ficha`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencias_ficha` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla evidencias_usuario',
  `idficha` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla evidenciasins_usuario con usuario',
  `idevidencias_instructor` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla evidenciasins_usuario con evidencias_instructor',
  PRIMARY KEY (`id`),
  KEY `idficha` (`idficha`),
  KEY `idevidencias_instructor` (`idevidencias_instructor`),
  CONSTRAINT `evidencias_ficha_ibfk_1` FOREIGN KEY (`idficha`) REFERENCES `ficha` (`id`),
  CONSTRAINT `evidencias_ficha_ibfk_2` FOREIGN KEY (`idevidencias_instructor`) REFERENCES `evidencias_instructor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencias_ficha`
--

LOCK TABLES `evidencias_ficha` WRITE;
/*!40000 ALTER TABLE `evidencias_ficha` DISABLE KEYS */;
/*!40000 ALTER TABLE `evidencias_ficha` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evidencias_instructor`
--

DROP TABLE IF EXISTS `evidencias_instructor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evidencias_instructor` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla evidenvias_instructor',
  `titulo` varchar(70) NOT NULL COMMENT 'titulo de la evidencia que el instructor crea',
  `instrucciones` varchar(200) DEFAULT NULL COMMENT 'instrucciones detalladas de la evidencia a entregar',
  `calificacion` varchar(20) NOT NULL COMMENT 'nota maxima o calificacion asignada a la evidencia',
  `fecha_de_entrega` date DEFAULT NULL COMMENT 'fecha limite en la que el aprendiz debe entregar la evidencia',
  `archivo` varchar(100) NOT NULL COMMENT 'nombre o ruta del archivo adjunto correspondiente a la evidencia',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evidencias_instructor`
--

LOCK TABLES `evidencias_instructor` WRITE;
/*!40000 ALTER TABLE `evidencias_instructor` DISABLE KEYS */;
INSERT INTO `evidencias_instructor` VALUES (1,'Taller funciones','desarrollar','100/100','2025-08-29','taller sentencias.pdf'),(2,'guia de aprendizaje','realizar los ejercicios correspondientes','90/100','2025-08-29','guia de aprendizaje pdf');
/*!40000 ALTER TABLE `evidencias_instructor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ficha`
--

DROP TABLE IF EXISTS `ficha`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ficha` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla ficha',
  `numero_ficha` int NOT NULL COMMENT 'aqui se define a cual ficha pertenece',
  `idjornada` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla ficha con jornada',
  `idprograma` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla ficha con programa',
  PRIMARY KEY (`id`),
  KEY `idjornada` (`idjornada`),
  KEY `idprograma` (`idprograma`),
  CONSTRAINT `ficha_ibfk_1` FOREIGN KEY (`idjornada`) REFERENCES `jornada` (`id`),
  CONSTRAINT `ficha_ibfk_2` FOREIGN KEY (`idprograma`) REFERENCES `programa` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ficha`
--

LOCK TABLES `ficha` WRITE;
/*!40000 ALTER TABLE `ficha` DISABLE KEYS */;
INSERT INTO `ficha` VALUES (1,3175010,1,1),(2,8234560,3,1),(3,6687667,2,2);
/*!40000 ALTER TABLE `ficha` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ficha_carpetas`
--

DROP TABLE IF EXISTS `ficha_carpetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ficha_carpetas` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla usuario_carpeta',
  `idficha` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla ficha_carpetas con ficha',
  `idcarpetas` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla usuario_carpeta con carpeta',
  PRIMARY KEY (`id`),
  KEY `idficha` (`idficha`),
  KEY `idcarpetas` (`idcarpetas`),
  CONSTRAINT `ficha_carpetas_ibfk_1` FOREIGN KEY (`idficha`) REFERENCES `ficha` (`id`),
  CONSTRAINT `ficha_carpetas_ibfk_2` FOREIGN KEY (`idcarpetas`) REFERENCES `carpetas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ficha_carpetas`
--

LOCK TABLES `ficha_carpetas` WRITE;
/*!40000 ALTER TABLE `ficha_carpetas` DISABLE KEYS */;
/*!40000 ALTER TABLE `ficha_carpetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ficha_usuario`
--

DROP TABLE IF EXISTS `ficha_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ficha_usuario` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla ficha_usuario',
  `idusuario` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla ficha_usuario con usuario',
  `idficha` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla ficha_usuario con ficha',
  PRIMARY KEY (`id`),
  KEY `idusuario` (`idusuario`),
  KEY `idficha` (`idficha`),
  CONSTRAINT `ficha_usuario_ibfk_1` FOREIGN KEY (`idusuario`) REFERENCES `usuario` (`id`),
  CONSTRAINT `ficha_usuario_ibfk_2` FOREIGN KEY (`idficha`) REFERENCES `ficha` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ficha_usuario`
--

LOCK TABLES `ficha_usuario` WRITE;
/*!40000 ALTER TABLE `ficha_usuario` DISABLE KEYS */;
INSERT INTO `ficha_usuario` VALUES (1,3,1),(2,4,2);
/*!40000 ALTER TABLE `ficha_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jornada`
--

DROP TABLE IF EXISTS `jornada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jornada` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla jornada',
  `nombre` varchar(50) NOT NULL COMMENT 'aqui va si es diurna, nocturna o mixta',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jornada`
--

LOCK TABLES `jornada` WRITE;
/*!40000 ALTER TABLE `jornada` DISABLE KEYS */;
INSERT INTO `jornada` VALUES (1,'diurna'),(2,'nocturna'),(3,'mixta');
/*!40000 ALTER TABLE `jornada` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `material`
--

DROP TABLE IF EXISTS `material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla material',
  `titulo` varchar(100) NOT NULL COMMENT 'titulo del material',
  `descripcion` varchar(500) DEFAULT NULL COMMENT 'instrucciones o descripcion del material de apoyo',
  `archivo` varchar(255) DEFAULT NULL COMMENT 'nombre o ruta del archivo de apoyo adjunto por el instructor',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material`
--

LOCK TABLES `material` WRITE;
/*!40000 ALTER TABLE `material` DISABLE KEYS */;
INSERT INTO `material` VALUES (1,'Ejercicio Sentencias SQL','Como crear base de datos para un sistema de control de hotel','Sentencias Ejemplos'),(2,'Ejercicio HV','Como crear hoja de vida en HTML','HV');
/*!40000 ALTER TABLE `material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `material_usuario`
--

DROP TABLE IF EXISTS `material_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_usuario` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla material_usuario',
  `idusuario` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla material_usuario con usuario',
  `idmaterial` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla material_usuario con material',
  PRIMARY KEY (`id`),
  KEY `idusuario` (`idusuario`),
  KEY `idmaterial` (`idmaterial`),
  CONSTRAINT `material_usuario_ibfk_1` FOREIGN KEY (`idusuario`) REFERENCES `usuario` (`id`),
  CONSTRAINT `material_usuario_ibfk_2` FOREIGN KEY (`idmaterial`) REFERENCES `material` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material_usuario`
--

LOCK TABLES `material_usuario` WRITE;
/*!40000 ALTER TABLE `material_usuario` DISABLE KEYS */;
INSERT INTO `material_usuario` VALUES (1,1,1),(2,1,2),(3,2,1),(4,2,2);
/*!40000 ALTER TABLE `material_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nombre_asignatura`
--

DROP TABLE IF EXISTS `nombre_asignatura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nombre_asignatura` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla nombre_asignatura',
  `idtipo_asignatura` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla nombre_asignatura con tipo_asignatura',
  `idficha` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla nombre_asignatura con ficha',
  `nombre` varchar(200) NOT NULL COMMENT 'aqui va el nombre que se le asigne a la competencia',
  PRIMARY KEY (`id`),
  KEY `idtipo_asignatura` (`idtipo_asignatura`),
  KEY `idficha` (`idficha`),
  CONSTRAINT `nombre_asignatura_ibfk_1` FOREIGN KEY (`idtipo_asignatura`) REFERENCES `tipo_asignatura` (`id`),
  CONSTRAINT `nombre_asignatura_ibfk_2` FOREIGN KEY (`idficha`) REFERENCES `ficha` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nombre_asignatura`
--

LOCK TABLES `nombre_asignatura` WRITE;
/*!40000 ALTER TABLE `nombre_asignatura` DISABLE KEYS */;
INSERT INTO `nombre_asignatura` VALUES (1,2,1,'Cultura de paz'),(2,1,2,'TPS'),(3,2,3,'Inglés');
/*!40000 ALTER TABLE `nombre_asignatura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `programa`
--

DROP TABLE IF EXISTS `programa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `programa` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla programa',
  `programa` varchar(150) NOT NULL COMMENT 'tecnico o tecnologo',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `programa`
--

LOCK TABLES `programa` WRITE;
/*!40000 ALTER TABLE `programa` DISABLE KEYS */;
INSERT INTO `programa` VALUES (1,'tecnico'),(2,'tecnologo');
/*!40000 ALTER TABLE `programa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla rol',
  `tipo` varchar(50) NOT NULL COMMENT 'aqui se define el rol del usuario que son (aprendiz, instructor, coordinacion y observador)',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'aprendiz'),(2,'instructor'),(3,'coordinacion'),(4,'observador');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_asignatura`
--

DROP TABLE IF EXISTS `tipo_asignatura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_asignatura` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla asignatura',
  `nombre` varchar(200) NOT NULL COMMENT 'Si la competencia es tecnica o transversal',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_asignatura`
--

LOCK TABLES `tipo_asignatura` WRITE;
/*!40000 ALTER TABLE `tipo_asignatura` DISABLE KEYS */;
INSERT INTO `tipo_asignatura` VALUES (1,'Técnica'),(2,'Transversal');
/*!40000 ALTER TABLE `tipo_asignatura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla nombre_asignatura',
  `nombres` varchar(100) NOT NULL COMMENT 'aqui van los nombre del usuario',
  `apellidos` varchar(100) NOT NULL COMMENT 'aqui van los apellidos del usuario',
  `correo` varchar(100) NOT NULL COMMENT 'aqui estara el correo del usuario',
  `telefono` bigint NOT NULL COMMENT 'aqui va el numero de telefono del usuario',
  `usuario` varchar(100) NOT NULL COMMENT 'aqui va el usuario de regristro de cada uno de los usuarios',
  `contrasena` varchar(20) NOT NULL COMMENT 'aca estara la contrasena para entrar al sistema de cada usuario',
  `iddocumento` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla usuario con documento',
  PRIMARY KEY (`id`),
  KEY `iddocumento` (`iddocumento`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`iddocumento`) REFERENCES `documento` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'luis alfonso','cardona perez','luiscardona@gmail.com',3124564453,'luisito429','123asdfg',1),(2,'tomas santiago','gomez gil','tomigomez@gmail.com',3245678913,'tomi9424','asdfg123',1),(3,'julia andrea','romero quiroga','andreju@gmail.com',31245643284,'jul29ana','2845gsi',2),(4,'santiago andres','padilla ortiz','santipa@gmail.com',3245295513,'sant844','jsfd936',1),(5,'andrea angie','zambrano cruz',' zambranocruz@gmail.com',3245297989,'andrea7877','Andre_890',1),(6,'lorena angel','camargo arias','ceciliacamargo@gmail.com',3245267788,'lorenaaa7889','Laut_08',1);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_rol`
--

DROP TABLE IF EXISTS `usuario_rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_rol` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'este es el identificador unico de la tabla usuario_rol',
  `idusuario` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla usuario_rol con usuario',
  `idrol` int DEFAULT NULL COMMENT 'esta es la llave foranea que une la tabla usuario_rol con rol',
  PRIMARY KEY (`id`),
  KEY `idusuario` (`idusuario`),
  KEY `idrol` (`idrol`),
  CONSTRAINT `usuario_rol_ibfk_1` FOREIGN KEY (`idusuario`) REFERENCES `usuario` (`id`),
  CONSTRAINT `usuario_rol_ibfk_2` FOREIGN KEY (`idrol`) REFERENCES `rol` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_rol`
--

LOCK TABLES `usuario_rol` WRITE;
/*!40000 ALTER TABLE `usuario_rol` DISABLE KEYS */;
INSERT INTO `usuario_rol` VALUES (1,1,2),(2,2,2),(3,3,1),(4,4,1),(5,5,3),(6,6,4);
/*!40000 ALTER TABLE `usuario_rol` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-11 16:39:36
