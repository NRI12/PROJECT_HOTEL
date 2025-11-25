-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: hotel_booking
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `amenities`
--

DROP TABLE IF EXISTS `amenities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `amenities` (
  `amenity_id` int NOT NULL AUTO_INCREMENT,
  `amenity_name` varchar(100) NOT NULL,
  `icon` varchar(100) DEFAULT NULL,
  `category` enum('hotel','room','both') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`amenity_id`),
  UNIQUE KEY `amenity_name` (`amenity_name`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `amenities`
--

LOCK TABLES `amenities` WRITE;
/*!40000 ALTER TABLE `amenities` DISABLE KEYS */;
INSERT INTO `amenities` VALUES (1,'WiFi miễn phí','wifi','both','2025-11-24 20:28:51'),(2,'Điều hòa','ac','room','2025-11-24 20:28:51'),(3,'Bể bơi','pool','hotel','2025-11-24 20:28:51'),(4,'Phòng gym','gym','hotel','2025-11-24 20:28:51'),(5,'Nhà hàng','restaurant','hotel','2025-11-24 20:28:51'),(6,'Bãi đỗ xe','parking','hotel','2025-11-24 20:28:51'),(7,'TV màn hình phẳng','tv','room','2025-11-24 20:28:51'),(8,'Minibar','minibar','room','2025-11-24 20:28:51'),(9,'Spa','spa','hotel','2025-11-24 20:28:51'),(10,'Két an toàn','safe','room','2025-11-24 20:28:51'),(11,'Ban công','balcony','room','2025-11-24 20:28:51'),(12,'Bồn tắm','bathtub','room','2025-11-24 20:28:51'),(13,'Dịch vụ phòng 24/7','room-service','hotel','2025-11-24 20:28:51'),(14,'Dịch vụ giặt ủi','laundry','hotel','2025-11-24 20:28:51'),(15,'Quầy bar','bar','hotel','2025-11-24 20:28:51'),(16,'Khu vui chơi trẻ em','playground','hotel','2025-11-24 20:28:51'),(17,'Phòng họp','meeting','hotel','2025-11-24 20:28:51'),(18,'Máy sấy tóc','hairdryer','room','2025-11-24 20:28:51'),(19,'Đồ vệ sinh miễn phí','toiletries','room','2025-11-24 20:28:51'),(20,'Tủ lạnh','fridge','room','2025-11-24 20:28:51');
/*!40000 ALTER TABLE `amenities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking_details`
--

DROP TABLE IF EXISTS `booking_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking_details` (
  `detail_id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int NOT NULL,
  `room_id` int NOT NULL,
  `quantity` int NOT NULL,
  `price_per_night` decimal(10,2) NOT NULL,
  `num_nights` int NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`detail_id`),
  KEY `booking_id` (`booking_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `booking_details_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`) ON DELETE CASCADE,
  CONSTRAINT `booking_details_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking_details`
--

LOCK TABLES `booking_details` WRITE;
/*!40000 ALTER TABLE `booking_details` DISABLE KEYS */;
INSERT INTO `booking_details` VALUES (1,1,1,1,1500000.00,2,3000000.00,'2025-11-24 20:28:51'),(2,2,3,1,3000000.00,3,9000000.00,'2025-11-24 20:28:51'),(3,3,5,1,1000000.00,2,2000000.00,'2025-11-24 20:28:51'),(4,4,8,1,1200000.00,3,3600000.00,'2025-11-24 20:28:51'),(5,5,11,1,1300000.00,3,3900000.00,'2025-11-24 20:28:51'),(6,6,1,1,1500000.00,2,3000000.00,'2025-11-24 20:28:51'),(7,7,14,1,900000.00,3,2700000.00,'2025-11-24 20:28:51'),(8,8,6,1,1200000.00,3,3600000.00,'2025-11-24 20:28:51'),(9,9,1,1,1500000.00,2,3000000.00,'2025-11-24 20:28:51'),(10,10,10,1,2200000.00,3,6600000.00,'2025-11-24 20:28:51'),(11,11,5,1,1000000.00,3,3000000.00,'2025-11-24 20:28:51'),(12,12,11,1,1100000.00,3,3300000.00,'2025-11-24 20:28:51'),(13,13,3,1,3000000.00,4,12000000.00,'2025-11-24 20:28:51'),(14,14,14,1,900000.00,2,1800000.00,'2025-11-24 20:28:51'),(15,15,8,1,1200000.00,2,2400000.00,'2025-11-24 20:28:51');
/*!40000 ALTER TABLE `booking_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `booking_code` varchar(50) NOT NULL,
  `user_id` int NOT NULL,
  `hotel_id` int NOT NULL,
  `check_in_date` date NOT NULL,
  `check_out_date` date NOT NULL,
  `num_guests` int NOT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `discount_amount` decimal(10,2) DEFAULT NULL,
  `final_amount` decimal(12,2) NOT NULL,
  `status` enum('pending','confirmed','checked_in','checked_out','cancelled','refunded') DEFAULT NULL,
  `payment_status` enum('unpaid','partial','paid','refunded') DEFAULT NULL,
  `special_requests` text,
  `cancellation_reason` text,
  `cancelled_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  UNIQUE KEY `ix_bookings_booking_code` (`booking_code`),
  KEY `ix_bookings_check_in_date` (`check_in_date`),
  KEY `ix_bookings_check_out_date` (`check_out_date`),
  KEY `ix_bookings_hotel_id` (`hotel_id`),
  KEY `ix_bookings_status` (`status`),
  KEY `ix_bookings_user_id` (`user_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`),
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (1,'BK2025110001',4,1,'2025-11-25','2025-11-27',2,3000000.00,0.00,3000000.00,'confirmed','paid','Phòng tầng cao, view đẹp',NULL,NULL,'2025-11-18 10:30:00','2025-11-18 10:30:00'),(2,'BK2025110002',5,1,'2025-11-26','2025-11-29',4,9000000.00,450000.00,8550000.00,'confirmed','paid','Yêu cầu giường phụ cho trẻ em',NULL,NULL,'2025-11-19 14:20:00','2025-11-19 14:20:00'),(3,'BK2025110003',6,2,'2025-11-28','2025-11-30',2,2000000.00,300000.00,1700000.00,'confirmed','paid',NULL,NULL,NULL,'2025-11-20 09:15:00','2025-11-20 09:15:00'),(4,'BK2025110004',4,3,'2025-12-01','2025-12-04',2,3600000.00,0.00,3600000.00,'pending','unpaid','Check-in sớm nếu được',NULL,NULL,'2025-11-21 16:45:00','2025-11-21 16:45:00'),(5,'BK2025110005',8,4,'2025-12-05','2025-12-08',2,3900000.00,0.00,3900000.00,'confirmed','partial','Phòng yên tĩnh',NULL,NULL,'2025-11-22 11:00:00','2025-11-22 11:00:00'),(6,'BK2025110006',5,1,'2025-12-10','2025-12-12',2,3000000.00,600000.00,2400000.00,'confirmed','paid',NULL,NULL,NULL,'2025-11-22 15:30:00','2025-11-22 15:30:00'),(7,'BK2025110007',6,5,'2025-12-15','2025-12-18',2,2700000.00,0.00,2700000.00,'pending','unpaid','Cần taxi đưa đón sân bay',NULL,NULL,'2025-11-23 08:20:00','2025-11-23 08:20:00'),(8,'BK2025110008',4,2,'2025-12-20','2025-12-23',3,3600000.00,0.00,3600000.00,'confirmed','paid',NULL,NULL,NULL,'2025-11-23 13:45:00','2025-11-23 13:45:00'),(9,'BK2025100001',5,1,'2025-10-15','2025-10-17',2,3000000.00,0.00,3000000.00,'checked_out','paid',NULL,NULL,NULL,'2025-10-10 10:00:00','2025-10-17 11:00:00'),(10,'BK2025100002',6,3,'2025-10-20','2025-10-23',4,6600000.00,0.00,6600000.00,'checked_out','paid','Phòng liền kề',NULL,NULL,'2025-10-15 14:30:00','2025-10-23 10:30:00'),(11,'BK2025090001',4,2,'2025-09-10','2025-09-13',2,3000000.00,0.00,3000000.00,'cancelled','refunded',NULL,NULL,NULL,'2025-09-01 09:00:00','2025-09-05 15:00:00'),(12,'BK2025080001',8,4,'2025-08-15','2025-08-18',2,3300000.00,0.00,3300000.00,'checked_out','paid','Phòng không hút thuốc',NULL,NULL,'2025-08-10 11:20:00','2025-08-18 11:00:00'),(13,'BK2025070001',5,1,'2025-07-20','2025-07-24',4,12000000.00,2400000.00,9600000.00,'checked_out','paid',NULL,NULL,NULL,'2025-07-15 16:00:00','2025-07-24 10:30:00'),(14,'BK2025060001',6,5,'2025-06-10','2025-06-12',2,1800000.00,0.00,1800000.00,'checked_out','paid',NULL,NULL,NULL,'2025-06-05 10:15:00','2025-06-12 11:00:00'),(15,'BK2025050001',4,3,'2025-05-15','2025-05-17',2,2400000.00,0.00,2400000.00,'checked_out','paid','Check-out muộn',NULL,NULL,'2025-05-10 13:30:00','2025-05-17 14:00:00');
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cancellation_policies`
--

DROP TABLE IF EXISTS `cancellation_policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cancellation_policies` (
  `policy_id` int NOT NULL AUTO_INCREMENT,
  `hotel_id` int NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text,
  `hours_before_checkin` int NOT NULL,
  `refund_percentage` decimal(5,2) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`policy_id`),
  KEY `hotel_id` (`hotel_id`),
  CONSTRAINT `cancellation_policies_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cancellation_policies`
--

LOCK TABLES `cancellation_policies` WRITE;
/*!40000 ALTER TABLE `cancellation_policies` DISABLE KEYS */;
INSERT INTO `cancellation_policies` VALUES (1,1,'Hủy miễn phí 7 ngày','Hủy miễn phí nếu hủy trước 7 ngày',168,100.00,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(2,1,'Hủy trước 3 ngày','Hoàn 50% nếu hủy trước 3 ngày',72,50.00,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(3,2,'Hủy miễn phí 3 ngày','Hủy miễn phí nếu hủy trước 3 ngày',72,100.00,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(4,2,'Hủy trước 1 ngày','Hoàn 30% nếu hủy trước 1 ngày',24,30.00,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(5,3,'Hủy miễn phí 5 ngày','Hủy miễn phí nếu hủy trước 5 ngày',120,100.00,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(6,4,'Hủy miễn phí 2 ngày','Hủy miễn phí nếu hủy trước 2 ngày',48,100.00,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(7,5,'Hủy miễn phí 3 ngày','Hủy miễn phí nếu hủy trước 3 ngày',72,100.00,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(8,6,'Hủy miễn phí 7 ngày','Hủy miễn phí nếu hủy trước 7 ngày',168,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(9,7,'Hủy miễn phí 5 ngày','Hủy miễn phí nếu hủy trước 5 ngày',120,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(10,8,'Hủy miễn phí 3 ngày','Hủy miễn phí nếu hủy trước 3 ngày',72,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(11,9,'Hủy miễn phí 2 ngày','Hủy miễn phí nếu hủy trước 2 ngày',48,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(12,10,'Hủy miễn phí 7 ngày','Hủy miễn phí nếu hủy trước 7 ngày',168,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(13,11,'Hủy miễn phí 3 ngày','Hủy miễn phí nếu hủy trước 3 ngày',72,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(14,12,'Hủy miễn phí 5 ngày','Hủy miễn phí nếu hủy trước 5 ngày',120,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(15,13,'Hủy miễn phí 3 ngày','Hủy miễn phí nếu hủy trước 3 ngày',72,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(16,14,'Hủy miễn phí 7 ngày','Hủy miễn phí nếu hủy trước 7 ngày',168,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(17,15,'Hủy miễn phí 5 ngày','Hủy miễn phí nếu hủy trước 5 ngày',120,100.00,'2025-11-24 20:33:59','2025-11-24 20:33:59');
/*!40000 ALTER TABLE `cancellation_policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discount_codes`
--

DROP TABLE IF EXISTS `discount_codes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discount_codes` (
  `code_id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `description` text,
  `discount_type` enum('percentage','fixed') NOT NULL,
  `discount_value` decimal(10,2) NOT NULL,
  `min_order_amount` decimal(10,2) DEFAULT NULL,
  `max_discount_amount` decimal(10,2) DEFAULT NULL,
  `usage_limit` int DEFAULT NULL,
  `used_count` int DEFAULT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `owner_id` int DEFAULT NULL,
  PRIMARY KEY (`code_id`),
  UNIQUE KEY `ix_discount_codes_code` (`code`),
  UNIQUE KEY `uq_owner_code` (`owner_id`,`code`),
  CONSTRAINT `fk_discount_codes_owner_id` FOREIGN KEY (`owner_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discount_codes`
--

LOCK TABLES `discount_codes` WRITE;
/*!40000 ALTER TABLE `discount_codes` DISABLE KEYS */;
INSERT INTO `discount_codes` VALUES (1,'WELCOME2025','Mã giảm giá chào mừng năm 2025','percentage',15.00,1000000.00,500000.00,100,5,'2025-01-01 00:00:00','2025-12-31 23:59:59',1,'2025-11-24 20:28:51','2025-11-24 20:28:51',2),(2,'SUMMER500','Giảm 500k cho đơn hàng mùa hè','fixed',500000.00,3000000.00,500000.00,50,3,'2025-06-01 00:00:00','2025-08-31 23:59:59',1,'2025-11-24 20:28:51','2025-11-24 20:28:51',2),(3,'WEEKEND20','Giảm 20% đặt phòng cuối tuần','percentage',20.00,1500000.00,1000000.00,200,12,'2025-01-01 00:00:00','2025-12-31 23:59:59',1,'2025-11-24 20:28:51','2025-11-24 20:28:51',3),(4,'VIP1000','Mã VIP giảm 1 triệu','fixed',1000000.00,5000000.00,1000000.00,20,1,'2025-01-01 00:00:00','2025-12-31 23:59:59',1,'2025-11-24 20:28:51','2025-11-24 20:28:51',2);
/*!40000 ALTER TABLE `discount_codes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `discount_usage`
--

DROP TABLE IF EXISTS `discount_usage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discount_usage` (
  `usage_id` int NOT NULL AUTO_INCREMENT,
  `code_id` int NOT NULL,
  `user_id` int NOT NULL,
  `booking_id` int NOT NULL,
  `discount_amount` decimal(10,2) NOT NULL,
  `used_at` datetime DEFAULT NULL,
  PRIMARY KEY (`usage_id`),
  KEY `booking_id` (`booking_id`),
  KEY `code_id` (`code_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `discount_usage_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`),
  CONSTRAINT `discount_usage_ibfk_2` FOREIGN KEY (`code_id`) REFERENCES `discount_codes` (`code_id`),
  CONSTRAINT `discount_usage_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discount_usage`
--

LOCK TABLES `discount_usage` WRITE;
/*!40000 ALTER TABLE `discount_usage` DISABLE KEYS */;
INSERT INTO `discount_usage` VALUES (1,1,5,2,450000.00,'2025-11-19 14:20:00'),(2,2,6,3,300000.00,'2025-11-20 09:15:00'),(3,3,5,6,600000.00,'2025-11-22 15:30:00'),(4,1,5,13,2400000.00,'2025-07-15 16:00:00');
/*!40000 ALTER TABLE `discount_usage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_verifications`
--

DROP TABLE IF EXISTS `email_verifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_verifications` (
  `verification_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `token` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `is_used` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`verification_id`),
  UNIQUE KEY `token` (`token`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `email_verifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_verifications`
--

LOCK TABLES `email_verifications` WRITE;
/*!40000 ALTER TABLE `email_verifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_verifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favorites`
--

DROP TABLE IF EXISTS `favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favorites` (
  `favorite_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `hotel_id` int NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`favorite_id`),
  UNIQUE KEY `unique_favorite` (`user_id`,`hotel_id`),
  KEY `hotel_id` (`hotel_id`),
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE,
  CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favorites`
--

LOCK TABLES `favorites` WRITE;
/*!40000 ALTER TABLE `favorites` DISABLE KEYS */;
INSERT INTO `favorites` VALUES (1,4,1,'2025-11-24 20:28:51'),(2,4,3,'2025-11-24 20:28:51'),(3,5,1,'2025-11-24 20:28:51'),(4,5,2,'2025-11-24 20:28:51'),(5,6,1,'2025-11-24 20:28:51'),(6,6,4,'2025-11-24 20:28:51'),(7,6,5,'2025-11-24 20:28:51'),(8,8,1,'2025-11-24 20:28:51'),(9,8,4,'2025-11-24 20:28:51');
/*!40000 ALTER TABLE `favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hotel_amenities`
--

DROP TABLE IF EXISTS `hotel_amenities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotel_amenities` (
  `hotel_id` int NOT NULL,
  `amenity_id` int NOT NULL,
  PRIMARY KEY (`hotel_id`,`amenity_id`),
  KEY `amenity_id` (`amenity_id`),
  CONSTRAINT `hotel_amenities_ibfk_1` FOREIGN KEY (`amenity_id`) REFERENCES `amenities` (`amenity_id`) ON DELETE CASCADE,
  CONSTRAINT `hotel_amenities_ibfk_2` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hotel_amenities`
--

LOCK TABLES `hotel_amenities` WRITE;
/*!40000 ALTER TABLE `hotel_amenities` DISABLE KEYS */;
INSERT INTO `hotel_amenities` VALUES (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),(13,1),(14,1),(15,1),(1,3),(3,3),(5,3),(6,3),(7,3),(9,3),(10,3),(12,3),(14,3),(15,3),(1,4),(2,4),(4,4),(6,4),(8,4),(10,4),(14,4),(15,4),(1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),(13,5),(14,5),(15,5),(1,6),(2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),(13,6),(14,6),(15,6),(1,9),(6,9),(10,9),(12,9),(14,9),(1,13),(2,13),(3,13),(4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),(11,13),(12,13),(13,13),(14,13),(15,13),(1,14),(2,14),(3,14),(4,14),(5,14),(6,14),(7,14),(8,14),(9,14),(10,14),(11,14),(12,14),(13,14),(14,14),(15,14),(1,15),(2,15),(4,15),(6,15),(7,15),(8,15),(10,15),(12,15),(14,15),(3,16),(7,16),(13,16),(15,16),(1,17),(2,17),(10,17),(14,17);
/*!40000 ALTER TABLE `hotel_amenities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hotel_images`
--

DROP TABLE IF EXISTS `hotel_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotel_images` (
  `image_id` int NOT NULL AUTO_INCREMENT,
  `hotel_id` int NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `is_primary` tinyint(1) DEFAULT NULL,
  `caption` varchar(255) DEFAULT NULL,
  `display_order` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`image_id`),
  KEY `hotel_id` (`hotel_id`),
  CONSTRAINT `hotel_images_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hotel_images`
--

LOCK TABLES `hotel_images` WRITE;
/*!40000 ALTER TABLE `hotel_images` DISABLE KEYS */;
INSERT INTO `hotel_images` VALUES (18,1,'/uploads/hotels/0d682a915d924d51a43715c5847dd8c8.jpeg',1,NULL,0,'2025-11-24 13:30:24'),(19,1,'/uploads/hotels/c232c65a703a4dd4a983347ba6d1c97f.webp',0,NULL,1,'2025-11-24 13:30:24'),(20,1,'/uploads/hotels/274e1fde5e364a6db7abd1dde7db46d6.jpeg',0,NULL,2,'2025-11-24 13:30:24'),(21,1,'/uploads/hotels/c6e59168431e493e8b10a172c6b61908.jpeg',0,NULL,3,'2025-11-24 13:30:24'),(22,1,'/uploads/hotels/b26fb6fe4b354dc2b984c7052db1a8b7.webp',0,NULL,4,'2025-11-24 13:30:24'),(23,1,'/uploads/hotels/ebad1422f00e4b05864e10b29e81ff4e.jpeg',0,NULL,5,'2025-11-24 13:30:24'),(24,1,'/uploads/hotels/5f61a4f7a1174473bc5e74cdf96f7759.webp',0,NULL,6,'2025-11-24 13:30:24'),(25,1,'/uploads/hotels/b728ff0f3f434a7a86a30ef17731e825.webp',0,NULL,7,'2025-11-24 13:30:24'),(26,1,'/uploads/hotels/fe0ccea3e15a46bb8d4c19b7b74a2aa6.webp',0,NULL,8,'2025-11-24 13:30:24'),(27,1,'/uploads/hotels/d27e0a86ea874e3face76706dc2d8943.jpeg',0,NULL,9,'2025-11-24 13:30:24'),(28,1,'/uploads/hotels/4e0dd1fe654d4708b54ff766ddf73e25.jpeg',0,NULL,10,'2025-11-24 13:30:24'),(29,1,'/uploads/hotels/1b7a0e096b594629a38ca7e524fe0b51.webp',0,NULL,11,'2025-11-24 13:30:24'),(30,1,'/uploads/hotels/282b4becd7394db79d04c4e1ce2c0f46.jpeg',0,NULL,12,'2025-11-24 13:30:24'),(31,1,'/uploads/hotels/821eb4fa062449e283bebb5726a8b8e9.jpeg',0,NULL,13,'2025-11-24 13:30:24'),(32,2,'/uploads/hotels/e30ff01ec6ac4f0594e1c99e33eb0fe8.jpeg',1,NULL,0,'2025-11-24 13:31:36'),(33,2,'/uploads/hotels/574ccb7d8fc348eb824215dbab62da00.webp',0,NULL,1,'2025-11-24 13:31:36'),(34,2,'/uploads/hotels/e81eafcfdfd247bdaa585f556a17e9df.jpeg',0,NULL,2,'2025-11-24 13:31:36'),(35,2,'/uploads/hotels/b56decabf7ef4ecdb2404eb3156c75a5.jpeg',0,NULL,3,'2025-11-24 13:31:36'),(36,2,'/uploads/hotels/341b09d9c580454eb321b2dfc4ef4dde.webp',0,NULL,4,'2025-11-24 13:31:36'),(37,2,'/uploads/hotels/cf609147df2b4b049e577a67cae48b0d.jpeg',0,NULL,5,'2025-11-24 13:31:36'),(38,2,'/uploads/hotels/54453b0c50a949ca97c34fe19201fd56.webp',0,NULL,6,'2025-11-24 13:31:36'),(39,2,'/uploads/hotels/dfa08a2a84a042c1917f9822e9dd7f48.webp',0,NULL,7,'2025-11-24 13:31:36'),(40,2,'/uploads/hotels/4ef6a721b877467486a5d88ccfb4ab5d.webp',0,NULL,8,'2025-11-24 13:31:36'),(41,2,'/uploads/hotels/c0574f43b558406baa0c28dc1e018858.jpeg',0,NULL,9,'2025-11-24 13:31:36'),(42,2,'/uploads/hotels/51aad6a19f914e46b7b0cdc0ffcbba00.jpeg',0,NULL,10,'2025-11-24 13:31:36'),(43,2,'/uploads/hotels/a7e4eed49a874659b8e7fedfe410ea9a.webp',0,NULL,11,'2025-11-24 13:31:36'),(44,2,'/uploads/hotels/770fb1b373ff457583aae43165aef82f.jpeg',0,NULL,12,'2025-11-24 13:31:36'),(45,2,'/uploads/hotels/d1e7c7e27efe4ed2b42363e88082d5b2.jpeg',0,NULL,13,'2025-11-24 13:31:36'),(71,6,'/uploads/hotels/f0e77a76536846a696793aeca79fe04f.webp',1,NULL,0,'2025-11-24 13:35:48'),(72,6,'/uploads/hotels/bb349620c68e4b5db157c7e0a50c07a4.webp',0,NULL,1,'2025-11-24 13:35:48'),(73,6,'/uploads/hotels/4a6f73992c734492bd4ff379be82f59e.webp',0,NULL,2,'2025-11-24 13:35:48'),(74,6,'/uploads/hotels/4ace3e6aa3be42ddb6a97d9b079e246c.webp',0,NULL,3,'2025-11-24 13:35:48'),(75,6,'/uploads/hotels/8777bf226137433b87b5ce0eebc6b9b3.webp',0,NULL,4,'2025-11-24 13:35:48'),(76,6,'/uploads/hotels/710d1e5d2729473ea81d6920b64eed13.webp',0,NULL,5,'2025-11-24 13:35:48'),(77,6,'/uploads/hotels/7fa5a398bd074320b0698c014f757ad2.jpeg',0,NULL,6,'2025-11-24 13:35:48'),(78,6,'/uploads/hotels/6779766f690e443f88ae1f8b3143dadd.webp',0,NULL,7,'2025-11-24 13:35:48'),(79,6,'/uploads/hotels/9e18c77c603e4059aca020fca631b19b.webp',0,NULL,8,'2025-11-24 13:35:48'),(80,6,'/uploads/hotels/b08a0467064d4895bc78522c37115652.webp',0,NULL,9,'2025-11-24 13:35:48'),(81,6,'/uploads/hotels/f557643d5c604795b90526656a9815cd.webp',0,NULL,10,'2025-11-24 13:35:48'),(82,6,'/uploads/hotels/57dd6506265a4ab7a8f534bc567e2da8.webp',0,NULL,11,'2025-11-24 13:35:48'),(83,6,'/uploads/hotels/01429bd69e30464796f31277d9fc9f8a.webp',0,NULL,12,'2025-11-24 13:35:48');
/*!40000 ALTER TABLE `hotel_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hotels`
--

DROP TABLE IF EXISTS `hotels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hotels` (
  `hotel_id` int NOT NULL AUTO_INCREMENT,
  `owner_id` int NOT NULL,
  `hotel_name` varchar(200) NOT NULL,
  `description` text,
  `address` text NOT NULL,
  `city` varchar(100) NOT NULL,
  `district` varchar(100) DEFAULT NULL,
  `ward` varchar(100) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `star_rating` int DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `check_in_time` time DEFAULT NULL,
  `check_out_time` time DEFAULT NULL,
  `status` enum('pending','active','suspended','rejected') DEFAULT NULL,
  `is_featured` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`hotel_id`),
  KEY `owner_id` (`owner_id`),
  KEY `ix_hotels_city` (`city`),
  KEY `ix_hotels_status` (`status`),
  CONSTRAINT `hotels_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hotels`
--

LOCK TABLES `hotels` WRITE;
/*!40000 ALTER TABLE `hotels` DISABLE KEYS */;
INSERT INTO `hotels` VALUES (1,2,'Sunrise Beach Resort','Resort 5 sao view biển tuyệt đẹp với đầy đủ tiện nghi cao cấp, bể bơi vô cực, spa sang trọng','123 Trần Phú, Vũng Tàu','Vũng Tàu','Thành phố Vũng Tàu','Phường 1',10.35622400,107.08426200,5,'02543856789','info@sunriseresort.vn','14:00:00','12:00:00','active',1,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(2,2,'City Center Hotel','Khách sạn 4 sao ngay trung tâm thành phố, gần sân bay, thuận tiện di chuyển','456 Nguyễn Văn Linh, Q7','TP.HCM','Quận 7','Phường Tân Phú',10.73339600,106.71843200,4,'02838475869','booking@citycenter.vn','14:00:00','12:00:00','active',1,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(3,3,'Mountain View Resort','Resort nghỉ dưỡng view núi tuyệt đẹp, không khí trong lành, phù hợp gia đình','789 Trần Hưng Đạo, Đà Lạt','Đà Lạt','Thành phố Đà Lạt','Phường 1',11.93862400,108.43802600,4,'02633827456','contact@mountainview.vn','14:00:00','11:00:00','active',0,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(4,2,'Riverside Hotel','Khách sạn ven sông với view đẹp, phòng rộng rãi, dịch vụ chu đáo','321 Bạch Đằng, Đà Nẵng','Đà Nẵng','Quận Hải Châu','Phường Hải Châu 1',16.06778900,108.22265500,4,'02363754829','info@riverside.vn','14:00:00','12:00:00','active',1,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(5,3,'Garden Plaza Hotel','Khách sạn với khu vườn xanh mát, phòng tiện nghi, gần chợ và bãi biển','654 Võ Nguyên Giáp, Nha Trang','Nha Trang','Thành phố Nha Trang','Phường Vĩnh Hòa',12.23864700,109.19637700,3,'02583746592','booking@gardenplaza.vn','14:00:00','12:00:00','active',0,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(6,2,'Paradise Bay Hotel','Khách sạn 5 sao view vịnh tuyệt đẹp, spa cao cấp, nhà hàng hải sản tươi sống','88 Trường Sa, Hạ Long','Quảng Ninh','TP. Hạ Long','Phường Bãi Cháy',20.95373200,107.04392800,5,'02033856234','info@paradisebay.vn','14:00:00','12:00:00','active',1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(7,3,'Golden Sand Resort','Resort 4 sao ngay bãi biển, hồ bơi ngoài trời, khu vui chơi trẻ em','234 Nguyễn Đình Chiểu, Mũi Né','Bình Thuận','TP. Phan Thiết','Phường Hàm Tiến',10.93156700,108.10149300,4,'02523746281','booking@goldensand.vn','14:00:00','12:00:00','active',1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(8,2,'Highland Coffee Hotel','Khách sạn 4 sao phong cách Pháp, view hồ Xuân Hương, gần chợ đêm','456 Phan Đình Phùng, Đà Lạt','Đà Lạt','TP. Đà Lạt','Phường 2',11.93426800,108.43988400,4,'02633847562','contact@highlandcoffee.vn','14:00:00','11:00:00','active',0,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(9,3,'Coastal Breeze Hotel','Khách sạn 3 sao ven biển, phòng view biển, giá cả hợp lý','567 Trần Phú, Quy Nhơn','Bình Định','TP. Quy Nhơn','Phường Nguyễn Văn Cừ',13.77648300,109.22367900,3,'02563829471','info@coastalbreeze.vn','14:00:00','12:00:00','active',0,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(10,2,'Royal Palace Hotel','Khách sạn 5 sao sang trọng, phòng rộng, dịch vụ đẳng cấp quốc tế','789 Lê Thánh Tông, Huế','Huế','TP. Huế','Phường Phú Hội',16.46381500,107.59063700,5,'02343826394','reservation@royalpalace.vn','14:00:00','12:00:00','active',1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(11,3,'Lotus Lake Hotel','Khách sạn 3 sao view hồ sen, yên tĩnh, phù hợp nghỉ ngơi','123 Hồ Xuân Hương, Đà Lạt','Đà Lạt','TP. Đà Lạt','Phường 3',11.94028600,108.44156900,3,'02633856172','booking@lotuslake.vn','14:00:00','11:00:00','active',0,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(12,2,'Sunset Beach Resort','Resort 4 sao view hoàng hôn tuyệt đẹp, bãi biển riêng, bar ngoài trời','345 Hùng Vương, Phú Quốc','Kiên Giang','Phú Quốc','Dương Đông',10.22759400,103.96637200,4,'02973845621','info@sunsetbeach.vn','14:00:00','12:00:00','active',1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(13,3,'Bamboo Garden Hotel','Khách sạn 3 sao với khu vườn tre xanh mát, phong cách rustic','678 Trần Quốc Toản, Hội An','Quảng Nam','TP. Hội An','Phường Minh An',15.87969400,108.33510400,3,'02353847293','contact@bamboogarden.vn','14:00:00','12:00:00','active',0,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(14,2,'Ocean Pearl Hotel','Khách sạn 5 sao cao cấp, spa, phòng gym, rooftop bar view biển','901 Võ Nguyên Giáp, Đà Nẵng','Đà Nẵng','Quận Sơn Trà','Phường Phước Mỹ',16.05569200,108.24263700,5,'02363829475','reservation@oceanpearl.vn','14:00:00','12:00:00','active',1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(15,3,'Pine Hill Resort','Resort 4 sao trên đồi thông, view thung lũng, không gian trong lành','234 Khe Sanh, Đà Lạt','Đà Lạt','TP. Đà Lạt','Phường 10',11.92847300,108.41726900,4,'02633865374','info@pinehill.vn','14:00:00','11:00:00','active',0,'2025-11-24 20:33:59','2025-11-24 20:33:59');
/*!40000 ALTER TABLE `hotels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_history`
--

DROP TABLE IF EXISTS `login_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_history` (
  `history_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `ip_address` varchar(50) DEFAULT NULL,
  `user_agent` text,
  `login_at` datetime DEFAULT NULL,
  PRIMARY KEY (`history_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `login_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_history`
--

LOCK TABLES `login_history` WRITE;
/*!40000 ALTER TABLE `login_history` DISABLE KEYS */;
INSERT INTO `login_history` VALUES (1,4,'171.224.180.123','Mozilla/5.0 (Windows NT 10.0; Win64; x64)','2025-11-18 10:25:00'),(2,5,'113.161.84.56','Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)','2025-11-19 14:15:00'),(3,6,'14.241.229.78','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)','2025-11-20 09:10:00'),(4,2,'27.72.98.145','Mozilla/5.0 (Windows NT 10.0; Win64; x64)','2025-11-20 15:30:00'),(5,4,'171.224.180.123','Mozilla/5.0 (Windows NT 10.0; Win64; x64)','2025-11-21 16:40:00'),(6,8,'118.71.224.89','Mozilla/5.0 (Windows NT 10.0; Win64; x64)','2025-11-22 10:55:00'),(7,5,'113.161.84.56','Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)','2025-11-22 15:25:00'),(8,3,'42.115.94.72','Mozilla/5.0 (Windows NT 10.0; Win64; x64)','2025-11-23 08:00:00'),(9,6,'14.241.229.78','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)','2025-11-23 08:15:00'),(10,4,'171.224.180.123','Mozilla/5.0 (Windows NT 10.0; Win64; x64)','2025-11-23 13:40:00');
/*!40000 ALTER TABLE `login_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(200) NOT NULL,
  `message` text NOT NULL,
  `type` enum('booking','payment','promotion','system','review') NOT NULL,
  `related_id` int DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`notification_id`),
  KEY `ix_notifications_is_read` (`is_read`),
  KEY `ix_notifications_user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,4,'Đặt phòng thành công','Đặt phòng BK2025110001 đã được xác nhận. Check-in: 25/11/2025','booking',1,1,'2025-11-18 10:30:00'),(2,5,'Thanh toán thành công','Thanh toán cho đặt phòng BK2025110002 đã hoàn tất','payment',2,1,'2025-11-19 14:25:00'),(3,4,'Khuyến mãi mới','Giảm 20% mùa hè 2025 cho Sunrise Beach Resort','promotion',1,0,'2025-11-20 09:00:00'),(4,8,'Nhắc nhở check-in','Đặt phòng BK2025110005 sắp đến ngày check-in (05/12/2025)','booking',5,0,'2025-12-04 09:00:00');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_resets`
--

DROP TABLE IF EXISTS `password_resets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `password_resets` (
  `reset_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `token` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `is_used` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`reset_id`),
  UNIQUE KEY `token` (`token`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `password_resets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_resets`
--

LOCK TABLES `password_resets` WRITE;
/*!40000 ALTER TABLE `password_resets` DISABLE KEYS */;
/*!40000 ALTER TABLE `password_resets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int NOT NULL,
  `payment_method` enum('credit_card','bank_transfer','momo','zalopay','vnpay','cash') NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `transaction_id` varchar(100) DEFAULT NULL,
  `payment_status` enum('pending','completed','failed','refunded') DEFAULT NULL,
  `payment_date` datetime DEFAULT NULL,
  `refund_amount` decimal(10,2) DEFAULT NULL,
  `refund_date` datetime DEFAULT NULL,
  `notes` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`payment_id`),
  KEY `ix_payments_booking_id` (`booking_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,1,'vnpay',3000000.00,'VNP20251118001','completed','2025-11-18 10:35:00',NULL,NULL,NULL,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(2,2,'momo',8550000.00,'MOMO20251119001','completed','2025-11-19 14:25:00',NULL,NULL,NULL,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(3,3,'credit_card',1700000.00,'CC20251120001','completed','2025-11-20 09:20:00',NULL,NULL,NULL,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(4,5,'bank_transfer',2000000.00,'BT20251122001','completed','2025-11-22 11:30:00',NULL,NULL,'Đã chuyển khoản 50%','2025-11-24 20:28:51','2025-11-24 20:28:51');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promotions`
--

DROP TABLE IF EXISTS `promotions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promotions` (
  `promotion_id` int NOT NULL AUTO_INCREMENT,
  `hotel_id` int DEFAULT NULL,
  `room_id` int DEFAULT NULL,
  `title` varchar(200) NOT NULL,
  `description` text,
  `discount_type` enum('percentage','fixed') NOT NULL,
  `discount_value` decimal(10,2) NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `applicable_days` varchar(50) DEFAULT NULL,
  `min_nights` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`promotion_id`),
  KEY `hotel_id` (`hotel_id`),
  KEY `room_id` (`room_id`),
  KEY `ix_promotions_end_date` (`end_date`),
  KEY `ix_promotions_start_date` (`start_date`),
  CONSTRAINT `promotions_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE,
  CONSTRAINT `promotions_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promotions`
--

LOCK TABLES `promotions` WRITE;
/*!40000 ALTER TABLE `promotions` DISABLE KEYS */;
INSERT INTO `promotions` VALUES (1,1,NULL,'Ưu đãi mùa hè 2025','Giảm 20% cho tất cả các phòng','percentage',20.00,'2025-06-01 00:00:00','2025-08-31 23:59:59','all',2,1,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(2,2,5,'Khuyến mãi phòng Standard','Giảm 300k cho phòng Standard','fixed',300000.00,'2025-01-01 00:00:00','2025-12-31 23:59:59','mon,tue,wed,thu',1,1,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(3,3,NULL,'Ưu đãi cuối tuần','Giảm 15% đặt phòng cuối tuần','percentage',15.00,'2025-01-01 00:00:00','2025-12-31 23:59:59','fri,sat,sun',2,1,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(4,4,12,'Giảm giá phòng Deluxe','Giảm 25% phòng Deluxe River View','percentage',25.00,'2025-02-01 00:00:00','2025-04-30 23:59:59','all',3,1,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(5,5,NULL,'Ưu đãi đặt sớm','Giảm 10% khi đặt trước 30 ngày','percentage',10.00,'2025-01-01 00:00:00','2025-12-31 23:59:59','all',2,1,'2025-11-24 20:28:51','2025-11-24 20:28:51'),(6,6,NULL,'Ưu đãi Hạ Long','Giảm 25% tất cả phòng tại Hạ Long','percentage',25.00,'2025-01-01 00:00:00','2025-03-31 23:59:59','all',2,1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(7,7,NULL,'Khuyến mãi mùa hè','Giảm 20% nghỉ dưỡng tại Mũi Né','percentage',20.00,'2025-06-01 00:00:00','2025-08-31 23:59:59','all',3,1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(8,10,30,'Giảm giá Suite','Giảm 30% phòng Royal Suite','percentage',30.00,'2025-02-01 00:00:00','2025-04-30 23:59:59','all',2,1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(9,12,NULL,'Ưu đãi Phú Quốc','Giảm 500k đặt phòng tại Phú Quốc','fixed',500000.00,'2025-01-01 00:00:00','2025-12-31 23:59:59','all',3,1,'2025-11-24 20:33:59','2025-11-24 20:33:59'),(10,14,NULL,'Ưu đãi cuối tuần','Giảm 18% đặt phòng cuối tuần','percentage',18.00,'2025-01-01 00:00:00','2025-12-31 23:59:59','fri,sat,sun',2,1,'2025-11-24 20:33:59','2025-11-24 20:33:59');
/*!40000 ALTER TABLE `promotions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `review_id` int NOT NULL AUTO_INCREMENT,
  `booking_id` int NOT NULL,
  `user_id` int NOT NULL,
  `hotel_id` int NOT NULL,
  `rating` int NOT NULL,
  `cleanliness_rating` int DEFAULT NULL,
  `service_rating` int DEFAULT NULL,
  `facilities_rating` int DEFAULT NULL,
  `location_rating` int DEFAULT NULL,
  `comment` text,
  `hotel_response` text,
  `response_date` datetime DEFAULT NULL,
  `is_reported` tinyint(1) DEFAULT NULL,
  `report_reason` text,
  `status` enum('active','hidden','removed') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`review_id`),
  UNIQUE KEY `unique_booking_review` (`booking_id`),
  KEY `ix_reviews_hotel_id` (`hotel_id`),
  KEY `ix_reviews_user_id` (`user_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`),
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,9,5,1,5,5,5,5,5,'Resort tuyệt vời! View đẹp, phòng sạch sẽ, nhân viên nhiệt tình. Sẽ quay lại lần sau.',NULL,NULL,NULL,NULL,'active','2025-10-18 15:30:00','2025-10-18 15:30:00'),(2,10,6,3,4,4,4,4,5,'Khách sạn đẹp, không gian yên tĩnh. View núi rất đẹp. Thức ăn ngon. Chỉ có điều wifi hơi yếu.',NULL,NULL,NULL,NULL,'active','2025-10-24 10:00:00','2025-10-24 10:00:00'),(3,12,8,4,5,5,5,4,5,'Vị trí tuyệt vời, gần bãi biển. Phòng rộng rãi, view sông đẹp. Nhân viên phục vụ chu đáo.',NULL,NULL,NULL,NULL,'active','2025-08-19 14:20:00','2025-08-19 14:20:00'),(4,13,5,1,5,5,5,5,5,'Kỳ nghỉ tuyệt vời cùng gia đình! Bể bơi đẹp, bãi biển sạch. Trẻ em rất thích. Đáng tiền!',NULL,NULL,NULL,NULL,'active','2025-07-25 09:45:00','2025-07-25 09:45:00'),(5,14,6,5,3,3,3,3,4,'Khách sạn tạm ổn, giá cả hợp lý. Phòng hơi nhỏ nhưng sạch sẽ. Vị trí khá thuận tiện.',NULL,NULL,NULL,NULL,'active','2025-06-13 16:00:00','2025-06-13 16:00:00'),(6,15,4,3,4,4,4,4,4,'Resort yên tĩnh, không gian đẹp. Phù hợp để nghỉ ngơi. Nhân viên thân thiện.',NULL,NULL,NULL,NULL,'active','2025-05-18 11:30:00','2025-05-18 11:30:00');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin','Quản trị viên hệ thống','2025-11-18 18:04:10'),(2,'hotel_owner','Chủ khách sạn','2025-11-18 18:04:10'),(3,'customer','Khách hàng','2025-11-18 18:04:10');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_amenities`
--

DROP TABLE IF EXISTS `room_amenities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_amenities` (
  `room_id` int NOT NULL,
  `amenity_id` int NOT NULL,
  PRIMARY KEY (`room_id`,`amenity_id`),
  KEY `amenity_id` (`amenity_id`),
  CONSTRAINT `room_amenities_ibfk_1` FOREIGN KEY (`amenity_id`) REFERENCES `amenities` (`amenity_id`) ON DELETE CASCADE,
  CONSTRAINT `room_amenities_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_amenities`
--

LOCK TABLES `room_amenities` WRITE;
/*!40000 ALTER TABLE `room_amenities` DISABLE KEYS */;
INSERT INTO `room_amenities` VALUES (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),(13,1),(14,1),(15,1),(16,1),(17,1),(18,1),(19,1),(20,1),(21,1),(22,1),(23,1),(24,1),(25,1),(26,1),(27,1),(28,1),(29,1),(30,1),(31,1),(32,1),(33,1),(34,1),(35,1),(36,1),(37,1),(38,1),(39,1),(40,1),(41,1),(42,1),(43,1),(44,1),(45,1),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),(13,2),(14,2),(15,2),(16,2),(17,2),(18,2),(19,2),(20,2),(21,2),(22,2),(23,2),(24,2),(25,2),(26,2),(27,2),(28,2),(29,2),(30,2),(31,2),(32,2),(33,2),(34,2),(35,2),(36,2),(37,2),(38,2),(39,2),(40,2),(41,2),(42,2),(43,2),(44,2),(45,2),(1,7),(2,7),(3,7),(4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),(13,7),(14,7),(15,7),(16,7),(17,7),(18,7),(19,7),(20,7),(21,7),(22,7),(23,7),(24,7),(25,7),(26,7),(27,7),(28,7),(29,7),(30,7),(31,7),(32,7),(33,7),(34,7),(35,7),(36,7),(37,7),(38,7),(39,7),(40,7),(41,7),(42,7),(43,7),(44,7),(45,7),(2,8),(3,8),(4,8),(6,8),(7,8),(9,8),(10,8),(12,8),(13,8),(15,8),(17,8),(18,8),(19,8),(21,8),(22,8),(24,8),(25,8),(27,8),(29,8),(30,8),(31,8),(33,8),(35,8),(36,8),(38,8),(40,8),(41,8),(42,8),(44,8),(45,8),(1,10),(2,10),(3,10),(4,10),(5,10),(6,10),(7,10),(8,10),(9,10),(10,10),(11,10),(12,10),(13,10),(14,10),(15,10),(16,10),(17,10),(18,10),(19,10),(20,10),(21,10),(22,10),(23,10),(24,10),(25,10),(26,10),(27,10),(28,10),(29,10),(30,10),(31,10),(32,10),(33,10),(34,10),(35,10),(36,10),(37,10),(38,10),(39,10),(40,10),(41,10),(42,10),(43,10),(44,10),(45,10),(2,11),(3,11),(6,11),(7,11),(9,11),(10,11),(12,11),(13,11),(15,11),(17,11),(18,11),(21,11),(22,11),(24,11),(25,11),(27,11),(29,11),(30,11),(31,11),(33,11),(35,11),(36,11),(38,11),(40,11),(41,11),(42,11),(44,11),(45,11),(3,12),(7,12),(13,12),(18,12),(25,12),(30,12),(31,12),(36,12),(41,12),(42,12),(1,18),(2,18),(3,18),(4,18),(5,18),(6,18),(7,18),(8,18),(9,18),(10,18),(11,18),(12,18),(13,18),(14,18),(15,18),(16,18),(17,18),(18,18),(19,18),(20,18),(21,18),(22,18),(23,18),(24,18),(25,18),(26,18),(27,18),(28,18),(29,18),(30,18),(31,18),(32,18),(33,18),(34,18),(35,18),(36,18),(37,18),(38,18),(39,18),(40,18),(41,18),(42,18),(43,18),(44,18),(45,18),(1,19),(2,19),(3,19),(4,19),(5,19),(6,19),(7,19),(8,19),(9,19),(10,19),(11,19),(12,19),(13,19),(14,19),(15,19),(16,19),(17,19),(18,19),(19,19),(20,19),(21,19),(22,19),(23,19),(24,19),(25,19),(26,19),(27,19),(28,19),(29,19),(30,19),(31,19),(32,19),(33,19),(34,19),(35,19),(36,19),(37,19),(38,19),(39,19),(40,19),(41,19),(42,19),(43,19),(44,19),(45,19),(2,20),(3,20),(4,20),(6,20),(7,20),(9,20),(10,20),(12,20),(13,20),(15,20),(17,20),(18,20),(19,20),(21,20),(22,20),(24,20),(25,20),(27,20),(29,20),(30,20),(31,20),(33,20),(35,20),(36,20),(38,20),(40,20),(41,20),(42,20),(44,20),(45,20);
/*!40000 ALTER TABLE `room_amenities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_images`
--

DROP TABLE IF EXISTS `room_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_images` (
  `image_id` int NOT NULL AUTO_INCREMENT,
  `room_id` int NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `is_primary` tinyint(1) DEFAULT NULL,
  `caption` varchar(255) DEFAULT NULL,
  `display_order` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`image_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `room_images_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_images`
--

LOCK TABLES `room_images` WRITE;
/*!40000 ALTER TABLE `room_images` DISABLE KEYS */;
INSERT INTO `room_images` VALUES (1,1,'/uploads/rooms/room_1_main.jpg',1,'Phòng tiêu chuẩn',1,'2025-11-24 20:28:51'),(2,1,'/uploads/rooms/room_1_bathroom.jpg',0,'Phòng tắm',2,'2025-11-24 20:28:51'),(3,2,'/uploads/rooms/room_2_main.jpg',1,'Phòng Deluxe',1,'2025-11-24 20:28:51'),(4,2,'/uploads/rooms/room_2_balcony.jpg',0,'Ban công',2,'2025-11-24 20:28:51'),(5,3,'/uploads/rooms/room_3_main.jpg',1,'Suite',1,'2025-11-24 20:28:51'),(6,3,'/uploads/rooms/room_3_living.jpg',0,'Phòng khách',2,'2025-11-24 20:28:51'),(7,4,'/uploads/rooms/room_4_main.jpg',1,'Phòng gia đình',1,'2025-11-24 20:28:51'),(8,5,'/uploads/rooms/room_5_main.jpg',1,'Standard City',1,'2025-11-24 20:28:51'),(9,6,'/uploads/rooms/room_6_main.jpg',1,'Deluxe City',1,'2025-11-24 20:28:51'),(10,7,'/uploads/rooms/room_7_main.jpg',1,'Executive Suite',1,'2025-11-24 20:28:51'),(11,8,'/uploads/rooms/room_8_main.jpg',1,'Standard Mountain',1,'2025-11-24 20:28:51'),(12,9,'/uploads/rooms/room_9_main.jpg',1,'Deluxe Mountain',1,'2025-11-24 20:28:51'),(13,10,'/uploads/rooms/room_10_main.jpg',1,'Family Mountain',1,'2025-11-24 20:28:51'),(14,11,'/uploads/rooms/room_11_main.jpg',1,'Standard River',1,'2025-11-24 20:28:51'),(15,12,'/uploads/rooms/room_12_main.jpg',1,'Deluxe River',1,'2025-11-24 20:28:51'),(16,13,'/uploads/rooms/room_13_main.jpg',1,'River Suite',1,'2025-11-24 20:28:51'),(17,14,'/uploads/rooms/room_14_main.jpg',1,'Standard Garden',1,'2025-11-24 20:28:51'),(18,15,'/uploads/rooms/room_15_main.jpg',1,'Deluxe Garden',1,'2025-11-24 20:28:51'),(19,16,'/uploads/rooms/room_16_main.jpg',1,'Standard Bay View',1,'2025-11-24 20:33:59'),(20,17,'/uploads/rooms/room_17_main.jpg',1,'Deluxe Bay View',1,'2025-11-24 20:33:59'),(21,18,'/uploads/rooms/room_18_main.jpg',1,'Bay Suite',1,'2025-11-24 20:33:59'),(22,19,'/uploads/rooms/room_19_main.jpg',1,'Family Bay View',1,'2025-11-24 20:33:59'),(23,20,'/uploads/rooms/room_20_main.jpg',1,'Standard Beach View',1,'2025-11-24 20:33:59'),(24,21,'/uploads/rooms/room_21_main.jpg',1,'Deluxe Beach View',1,'2025-11-24 20:33:59'),(25,22,'/uploads/rooms/room_22_main.jpg',1,'Family Bungalow',1,'2025-11-24 20:33:59'),(26,23,'/uploads/rooms/room_23_main.jpg',1,'Standard Lake View',1,'2025-11-24 20:33:59'),(27,24,'/uploads/rooms/room_24_main.jpg',1,'Deluxe Lake View',1,'2025-11-24 20:33:59'),(28,25,'/uploads/rooms/room_25_main.jpg',1,'Executive Suite',1,'2025-11-24 20:33:59'),(29,26,'/uploads/rooms/room_26_main.jpg',1,'Standard Sea View',1,'2025-11-24 20:33:59'),(30,27,'/uploads/rooms/room_27_main.jpg',1,'Deluxe Sea View',1,'2025-11-24 20:33:59'),(31,28,'/uploads/rooms/room_28_main.jpg',1,'Standard Palace',1,'2025-11-24 20:33:59'),(32,29,'/uploads/rooms/room_29_main.jpg',1,'Deluxe Palace',1,'2025-11-24 20:33:59'),(33,30,'/uploads/rooms/room_30_main.jpg',1,'Royal Suite',1,'2025-11-24 20:33:59'),(34,31,'/uploads/rooms/room_31_main.jpg',1,'Executive Palace',1,'2025-11-24 20:33:59'),(35,32,'/uploads/rooms/room_32_main.jpg',1,'Standard Lotus',1,'2025-11-24 20:33:59'),(36,33,'/uploads/rooms/room_33_main.jpg',1,'Deluxe Lotus',1,'2025-11-24 20:33:59'),(37,34,'/uploads/rooms/room_34_main.jpg',1,'Standard Sunset',1,'2025-11-24 20:33:59'),(38,35,'/uploads/rooms/room_35_main.jpg',1,'Deluxe Sunset',1,'2025-11-24 20:33:59'),(39,36,'/uploads/rooms/room_36_main.jpg',1,'Sunset Villa',1,'2025-11-24 20:33:59'),(40,37,'/uploads/rooms/room_37_main.jpg',1,'Standard Garden',1,'2025-11-24 20:33:59'),(41,38,'/uploads/rooms/room_38_main.jpg',1,'Deluxe Bamboo',1,'2025-11-24 20:33:59'),(42,39,'/uploads/rooms/room_39_main.jpg',1,'Standard Ocean',1,'2025-11-24 20:33:59'),(43,40,'/uploads/rooms/room_40_main.jpg',1,'Deluxe Ocean',1,'2025-11-24 20:33:59'),(44,41,'/uploads/rooms/room_41_main.jpg',1,'Ocean Pearl Suite',1,'2025-11-24 20:33:59'),(45,42,'/uploads/rooms/room_42_main.jpg',1,'Presidential Suite',1,'2025-11-24 20:33:59'),(46,43,'/uploads/rooms/room_43_main.jpg',1,'Standard Pine',1,'2025-11-24 20:33:59'),(47,44,'/uploads/rooms/room_44_main.jpg',1,'Deluxe Valley',1,'2025-11-24 20:33:59'),(48,45,'/uploads/rooms/room_45_main.jpg',1,'Family Cottage',1,'2025-11-24 20:33:59');
/*!40000 ALTER TABLE `room_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_types`
--

DROP TABLE IF EXISTS `room_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room_types` (
  `type_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(100) NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`type_id`),
  UNIQUE KEY `type_name` (`type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_types`
--

LOCK TABLES `room_types` WRITE;
/*!40000 ALTER TABLE `room_types` DISABLE KEYS */;
INSERT INTO `room_types` VALUES (1,'Standard','Phòng tiêu chuẩn','2025-11-24 20:28:51'),(2,'Deluxe','Phòng cao cấp','2025-11-24 20:28:51'),(3,'Suite','Phòng Suite sang trọng','2025-11-24 20:28:51'),(4,'Family','Phòng gia đình','2025-11-24 20:28:51'),(5,'Executive','Phòng hạng thương gia','2025-11-24 20:28:51');
/*!40000 ALTER TABLE `room_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rooms` (
  `room_id` int NOT NULL AUTO_INCREMENT,
  `hotel_id` int NOT NULL,
  `room_type_id` int NOT NULL,
  `room_number` varchar(50) DEFAULT NULL,
  `room_name` varchar(200) NOT NULL,
  `description` text,
  `area` decimal(6,2) DEFAULT NULL,
  `max_guests` int NOT NULL,
  `num_beds` int DEFAULT NULL,
  `bed_type` varchar(100) DEFAULT NULL,
  `base_price` decimal(10,2) NOT NULL,
  `weekend_price` decimal(10,2) DEFAULT NULL,
  `status` enum('available','occupied','maintenance') DEFAULT 'available',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`room_id`),
  KEY `room_type_id` (`room_type_id`),
  KEY `ix_rooms_hotel_id` (`hotel_id`),
  CONSTRAINT `rooms_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`hotel_id`) ON DELETE CASCADE,
  CONSTRAINT `rooms_ibfk_2` FOREIGN KEY (`room_type_id`) REFERENCES `room_types` (`type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rooms`
--

LOCK TABLES `rooms` WRITE;
/*!40000 ALTER TABLE `rooms` DISABLE KEYS */;
INSERT INTO `rooms` VALUES (1,1,1,'101','Standard Ocean View','Phòng tiêu chuẩn view biển với đầy đủ tiện nghi',28.00,2,1,'Giường đôi',1200000.00,1500000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(2,1,2,'201','Deluxe Ocean View','Phòng cao cấp view biển, rộng rãi thoáng mát',35.00,2,1,'Giường King',1800000.00,2200000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(3,1,3,'301','Ocean Suite','Suite sang trọng với phòng khách riêng và ban công rộng',55.00,4,2,'1 King + 1 Sofa bed',3500000.00,4000000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(4,1,4,'102','Family Ocean View','Phòng gia đình view biển với 2 giường lớn',45.00,4,2,'2 Giường đôi',2500000.00,3000000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(5,2,1,'201','Standard City View','Phòng tiêu chuẩn view thành phố',25.00,2,1,'Giường đôi',800000.00,1000000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(6,2,2,'301','Deluxe City View','Phòng cao cấp view thành phố, tầng cao',32.00,2,1,'Giường King',1200000.00,1500000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(7,2,5,'401','Executive Suite','Suite hạng thương gia với phòng làm việc',48.00,3,1,'Giường King',2000000.00,2400000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(8,3,1,'101','Standard Mountain View','Phòng tiêu chuẩn view núi',30.00,2,1,'Giường đôi',900000.00,1200000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(9,3,2,'201','Deluxe Mountain View','Phòng cao cấp với ban công view núi',38.00,2,1,'Giường King',1400000.00,1800000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(10,3,4,'102','Family Mountain View','Phòng gia đình rộng rãi view núi',50.00,5,2,'1 King + 2 Single',2200000.00,2600000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(11,4,1,'301','Standard River View','Phòng tiêu chuẩn view sông',28.00,2,1,'Giường đôi',850000.00,1100000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(12,4,2,'401','Deluxe River View','Phòng cao cấp view sông Hàn',35.00,2,1,'Giường King',1300000.00,1600000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(13,4,3,'501','River Suite','Suite sang trọng với view sông tuyệt đẹp',52.00,4,2,'1 King + 1 Sofa bed',2800000.00,3200000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(14,5,1,'101','Standard Garden View','Phòng tiêu chuẩn view vườn',26.00,2,1,'Giường đôi',700000.00,900000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(15,5,2,'201','Deluxe Garden View','Phòng cao cấp view vườn xanh mát',32.00,2,1,'Giường King',1000000.00,1300000.00,'available','2025-11-24 20:28:51','2025-11-24 20:28:51'),(16,6,1,'101','Standard Bay View','Phòng tiêu chuẩn view vịnh Hạ Long',30.00,2,1,'Giường đôi',1500000.00,1800000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(17,6,2,'201','Deluxe Bay View','Phòng cao cấp với ban công riêng view vịnh',38.00,2,1,'Giường King',2200000.00,2600000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(18,6,3,'301','Bay Suite','Suite sang trọng view toàn cảnh vịnh',60.00,4,2,'1 King + 1 Sofa bed',4000000.00,4500000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(19,6,4,'102','Family Bay View','Phòng gia đình với 2 giường lớn',48.00,4,2,'2 Giường đôi',2800000.00,3200000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(20,7,1,'101','Standard Beach View','Phòng tiêu chuẩn view biển Mũi Né',28.00,2,1,'Giường đôi',1100000.00,1400000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(21,7,2,'201','Deluxe Beach View','Phòng cao cấp với ban công riêng',35.00,2,1,'Giường King',1600000.00,2000000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(22,7,4,'301','Family Beach Bungalow','Bungalow gia đình gần bãi biển',50.00,5,2,'1 King + 2 Single',2400000.00,2800000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(23,8,1,'201','Standard Lake View','Phòng tiêu chuẩn view hồ Xuân Hương',26.00,2,1,'Giường đôi',950000.00,1200000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(24,8,2,'301','Deluxe Lake View','Phòng cao cấp phong cách Pháp',34.00,2,1,'Giường King',1450000.00,1800000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(25,8,5,'401','Executive Lake Suite','Suite hạng thương gia view hồ',50.00,3,1,'Giường King',2100000.00,2500000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(26,9,1,'101','Standard Sea View','Phòng tiêu chuẩn view biển',25.00,2,1,'Giường đôi',750000.00,950000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(27,9,2,'201','Deluxe Sea View','Phòng cao cấp gần bãi biển',32.00,2,1,'Giường King',1050000.00,1350000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(28,10,1,'101','Standard Palace View','Phòng tiêu chuẩn phong cách hoàng gia',32.00,2,1,'Giường đôi',1300000.00,1600000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(29,10,2,'201','Deluxe Palace View','Phòng cao cấp sang trọng',40.00,2,1,'Giường King',1900000.00,2300000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(30,10,3,'301','Royal Suite','Suite hoàng gia đẳng cấp',70.00,4,2,'1 King + 1 Sofa bed',4500000.00,5000000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(31,10,5,'401','Executive Palace','Phòng hạng thương gia',45.00,2,1,'Giường King',2600000.00,3000000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(32,11,1,'101','Standard Lotus View','Phòng tiêu chuẩn view hồ sen',24.00,2,1,'Giường đôi',800000.00,1000000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(33,11,2,'201','Deluxe Lotus View','Phòng cao cấp yên tĩnh',30.00,2,1,'Giường King',1200000.00,1500000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(34,12,1,'101','Standard Sunset View','Phòng tiêu chuẩn view hoàng hôn',30.00,2,1,'Giường đôi',1400000.00,1700000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(35,12,2,'201','Deluxe Sunset View','Phòng cao cấp với ban công riêng',38.00,2,1,'Giường King',2000000.00,2400000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(36,12,3,'301','Sunset Villa','Villa riêng biệt view hoàng hôn',65.00,4,2,'1 King + 1 Sofa bed',3800000.00,4200000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(37,13,1,'101','Standard Garden View','Phòng tiêu chuẩn view vườn tre',26.00,2,1,'Giường đôi',850000.00,1050000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(38,13,2,'201','Deluxe Bamboo View','Phòng cao cấp phong cách rustic',32.00,2,1,'Giường King',1250000.00,1550000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(39,14,1,'501','Standard Ocean View','Phòng tiêu chuẩn view biển Đà Nẵng',32.00,2,1,'Giường đôi',1600000.00,1900000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(40,14,2,'601','Deluxe Ocean View','Phòng cao cấp tầng cao',40.00,2,1,'Giường King',2300000.00,2700000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(41,14,3,'701','Ocean Pearl Suite','Suite sang trọng view biển',65.00,4,2,'1 King + 1 Sofa bed',4200000.00,4700000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(42,14,5,'801','Presidential Suite','Phòng tổng thống đẳng cấp',80.00,4,2,'1 King + 1 Sofa bed',6000000.00,6500000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(43,15,1,'101','Standard Pine View','Phòng tiêu chuẩn view đồi thông',28.00,2,1,'Giường đôi',1050000.00,1350000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(44,15,2,'201','Deluxe Valley View','Phòng cao cấp view thung lũng',36.00,2,1,'Giường King',1550000.00,1950000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59'),(45,15,4,'301','Family Pine Cottage','Cottage gia đình trên đồi thông',52.00,5,2,'1 King + 2 Single',2600000.00,3000000.00,'available','2025-11-24 20:33:59','2025-11-24 20:33:59');
/*!40000 ALTER TABLE `rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `search_history`
--

DROP TABLE IF EXISTS `search_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `search_history` (
  `search_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `destination` varchar(200) DEFAULT NULL,
  `check_in_date` date DEFAULT NULL,
  `check_out_date` date DEFAULT NULL,
  `num_guests` int DEFAULT NULL,
  `search_date` datetime DEFAULT NULL,
  PRIMARY KEY (`search_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `search_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `search_history`
--

LOCK TABLES `search_history` WRITE;
/*!40000 ALTER TABLE `search_history` DISABLE KEYS */;
INSERT INTO `search_history` VALUES (1,4,'Vũng Tàu','2025-11-25','2025-11-27',2,'2025-11-18 10:00:00'),(2,5,'Đà Lạt','2025-12-01','2025-12-03',2,'2025-11-19 09:30:00'),(3,6,'TP.HCM','2025-11-28','2025-11-30',2,'2025-11-20 08:45:00'),(4,4,'Nha Trang','2025-12-15','2025-12-18',4,'2025-11-21 14:20:00'),(5,8,'Đà Nẵng','2025-12-05','2025-12-08',2,'2025-11-22 10:15:00'),(6,5,'Vũng Tàu','2025-12-10','2025-12-12',2,'2025-11-22 15:00:00'),(7,6,'Phú Quốc','2025-12-20','2025-12-23',3,'2025-11-23 11:30:00');
/*!40000 ALTER TABLE `search_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text,
  `id_card` varchar(50) DEFAULT NULL,
  `avatar_url` varchar(255) DEFAULT NULL,
  `role_id` int NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `email_verified` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin@hotel.com','$2b$12$UYCdl1JyGTns3xBkOqC9euCqjo3FK3nnWHG1I3gai3bYEM8.mWUPW','Nguyễn Văn Admin','0901234567','123 Lê Lợi, Q1, TP.HCM','001234567890',NULL,1,1,1,'2025-11-18 18:04:10','2025-11-18 18:04:10'),(2,'owner1@hotel.com','$2b$12$UYCdl1JyGTns3xBkOqC9euCqjo3FK3nnWHG1I3gai3bYEM8.mWUPW','Trần Thị Lan','0912345678','456 Nguyễn Huệ, Q1, TP.HCM','001234567891','/uploads/users/user_2_Capture.PNG',2,1,1,'2025-11-18 18:04:10','2025-11-24 06:48:09'),(3,'owner2@hotel.com','$2b$12$UYCdl1JyGTns3xBkOqC9euCqjo3FK3nnWHG1I3gai3bYEM8.mWUPW','Lê Văn Hùng','0923456789','789 Trần Hưng Đạo, Q5, TP.HCM','001234567892',NULL,2,1,1,'2025-11-18 18:04:10','2025-11-18 18:04:10'),(4,'customer1@gmail.com','$2b$12$UYCdl1JyGTns3xBkOqC9euCqjo3FK3nnWHG1I3gai3bYEM8.mWUPW','Phạm Minh Tuấn','0934567890','12 Võ Văn Tần, Q3, TP.HCM','001234567893',NULL,3,1,1,'2025-11-18 18:04:10','2025-11-18 18:04:10'),(5,'customer2@gmail.com','$2b$12$UYCdl1JyGTns3xBkOqC9euCqjo3FK3nnWHG1I3gai3bYEM8.mWUPW','Hoàng Thị Mai','0945678901','34 Hai Bà Trưng, Q3, TP.HCM','001234567894',NULL,3,1,1,'2025-11-18 18:04:10','2025-11-18 18:04:10'),(6,'customer3@gmail.com','$2b$12$UYCdl1JyGTns3xBkOqC9euCqjo3FK3nnWHG1I3gai3bYEM8.mWUPW','Đỗ Văn Nam','0956789012','56 Lý Tự Trọng, Q1, TP.HCM','001234567895',NULL,3,1,1,'2025-11-18 18:04:10','2025-11-18 18:04:10'),(8,'ctv55342@gmail.com','$2b$12$A8Ex70hJZNL8Q83cA9mcoOOZvz0iNww1pqTIYIR2x1Rg7x.IqY0.S','nguyen van bka','03928182733','','','/uploads/users/user_8_1.png',3,1,1,'2025-11-18 12:47:22','2025-11-23 06:16:38');
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

-- Dump completed on 2025-11-24 21:40:18
