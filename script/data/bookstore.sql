-- MySQL dump 10.15  Distrib 10.0.24-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: bookstore
-- ------------------------------------------------------
-- Server version	10.0.24-MariaDB-7

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `email` varchar(64) NOT NULL COMMENT '登录邮箱地址',
  `password` varchar(128) NOT NULL COMMENT '管理员登录密码',
  `sign_count` int(11) NOT NULL DEFAULT '0' COMMENT '登录次数',
  `is_effective` int(11) NOT NULL DEFAULT '1' COMMENT '是否有效',
  `last_signIn_time` date NOT NULL COMMENT '上次登录时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_email_uindex` (`email`),
  UNIQUE KEY `admin_id_uindex` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COMMENT='管理员';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'caisi1735@163.com','asdf',0,1,'2021-03-08');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned DEFAULT NULL,
  `book_id` varchar(100) DEFAULT NULL,
  `book_num` varchar(40) DEFAULT NULL,
  `is_effe` int(11) DEFAULT '1',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_cart_user` (`user_id`),
  CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (2,6,'5e927b251771c616ff7455ad','1',1,'2020-05-12 08:44:10','2020-05-12 08:44:10');
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(24) DEFAULT NULL,
  `tel` char(11) DEFAULT NULL,
  `email` varchar(64) DEFAULT NULL,
  `gender` char(1) DEFAULT NULL,
  `age` varchar(3) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `hobbies` text,
  `introduce` text,
  `identity` varchar(20) DEFAULT NULL,
  `password` varchar(128) NOT NULL,
  `createtime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `address_default` varchar(24) DEFAULT NULL COMMENT '默认收货地址',
  `avatar` varchar(60) DEFAULT NULL,
  `is_freezing` int(1) NOT NULL DEFAULT '0' COMMENT '1有效，0无效',
  `is_delete` int(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `tel` (`tel`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (5,'黄彩思','13481470145','caisi@163.com','M','20','2020-05-05','ka','kba','本科生','pbkdf2:sha256:150000$h5ogSUey$b97023a7bc1ea8e66b8edeca5d6573c481f1e0afb36413809609d307dc8ca5b4','2020-04-25 16:00:00','603723dff28f9bc870637d60','5.jpg',0,0),(6,NULL,'13557447351',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'pbkdf2:sha256:150000$Gdm9CRYV$e77a940d75d9090eb528f7882549ce99185758775b9bdd91c3a60beda323e080','2020-05-12 08:39:32','5eba611846b6a958611eb292',NULL,0,0),(7,NULL,'12312312312',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'pbkdf2:sha256:150000$NxYcbnHZ$1db49659e4db0748f6bb6f9f70e953063e2b96f59e361076cbc117a4b8e0b3c9','2020-05-12 08:45:46',NULL,NULL,1,0),(8,NULL,'89416315634',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'pbkdf2:sha256:150000$zGyXib7P$1df71b5bcc660cc087342f1f3af9fd6802de3149ed22f49746a0db67db713b56','2020-05-20 01:02:04',NULL,NULL,1,1),(9,NULL,'74846635413',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'pbkdf2:sha256:150000$mwE74VRd$423550b0216e3ef1e4eb61e94bcf4b4e0eeabbff63eef8ea73fe97ddc29d4d35','2020-05-20 01:02:19',NULL,NULL,1,1),(10,NULL,'78643464764',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'pbkdf2:sha256:150000$Hz66LRnI$56b105a9b5d95c236426f3b727a88ea1f50feea25d240f427443f3c6183b7836','2020-05-20 01:02:47',NULL,NULL,1,0),(11,NULL,'74635413126',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'pbkdf2:sha256:150000$wA2BRyXa$42896b5c6e8ac61fff307f1a8043e50969a38536d7c9b2b2714c02bce18c5d2a','2020-05-20 01:02:59',NULL,NULL,1,0),(12,NULL,'98798798798',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'pbkdf2:sha256:150000$aanr7BK9$269607e3d1cc5c306d822960c44f85cf96a85b38001e32411506a97343a763ba','2020-05-20 01:03:33',NULL,NULL,1,1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-03-08 10:14:49
