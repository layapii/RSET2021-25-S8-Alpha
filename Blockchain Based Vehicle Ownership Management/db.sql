/*
SQLyog Community v13.1.6 (64 bit)
MySQL - 5.7.9 : Database - online_vehicle_shop_rajagiri
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`online_vehicle_shop_rajagiri` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `online_vehicle_shop_rajagiri`;

/*Table structure for table `allotvehicle` */

DROP TABLE IF EXISTS `allotvehicle`;

CREATE TABLE `allotvehicle` (
  `allotvehicle_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) DEFAULT NULL,
  `chasisnumber` varchar(255) DEFAULT NULL,
  `modelnumber` varchar(255) DEFAULT NULL,
  `details` varchar(255) DEFAULT NULL,
  `regusternumber` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`allotvehicle_id`),
  KEY `booking_id` (`booking_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

/*Data for the table `allotvehicle` */

insert  into `allotvehicle`(`allotvehicle_id`,`booking_id`,`chasisnumber`,`modelnumber`,`details`,`regusternumber`) values 
(2,3,'34545','54535353','dvdxdd','555555555'),
(3,5,'242432242442','24f22332','fsdfdsfdsf','pending'),
(4,4,'242432242442','24f22332','fsdfdsfdsf','pending');

/*Table structure for table `bank` */

DROP TABLE IF EXISTS `bank`;

CREATE TABLE `bank` (
  `bank_id` int(11) NOT NULL AUTO_INCREMENT,
  `login_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `place` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`bank_id`),
  KEY `login_id` (`login_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

/*Data for the table `bank` */

insert  into `bank`(`bank_id`,`login_id`,`name`,`place`,`phone`,`email`,`image`) values 
(1,7,'bank','asdsds','3333333','adasdsd',NULL),
(2,10,'gfjhf','ddds','06789368498','kstores@gmail.com',NULL);

/*Table structure for table `booking` */

DROP TABLE IF EXISTS `booking`;

CREATE TABLE `booking` (
  `booking_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `vehicle_id` int(11) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`booking_id`),
  KEY `user_id` (`user_id`),
  KEY `vehicle_id` (`vehicle_id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;

/*Data for the table `booking` */

insert  into `booking`(`booking_id`,`user_id`,`vehicle_id`,`date`,`status`) values 
(5,1,1,'2025-03-22','alloted'),
(4,1,1,'2025-03-06','alloted'),
(3,1,1,'2025-03-04','alloted'),
(6,1,1,'2025-03-22','Accepted'),
(7,1,1,'2025-03-25','Accepted');

/*Table structure for table `brand` */

DROP TABLE IF EXISTS `brand`;

CREATE TABLE `brand` (
  `brand_id` int(11) NOT NULL AUTO_INCREMENT,
  `brand` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`brand_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `brand` */

insert  into `brand`(`brand_id`,`brand`) values 
(1,'hero');

/*Table structure for table `company` */

DROP TABLE IF EXISTS `company`;

CREATE TABLE `company` (
  `company_id` int(11) NOT NULL AUTO_INCREMENT,
  `login_id` int(11) DEFAULT NULL,
  `shopname` varchar(255) DEFAULT NULL,
  `place` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `image` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`company_id`),
  KEY `login_id` (`login_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

/*Data for the table `company` */

insert  into `company`(`company_id`,`login_id`,`shopname`,`place`,`phone`,`email`,`image`) values 
(1,1,'kstores','kochi','06789368498','benjames@gmail.com','static/cd6f97af-7ab8-4574-b297-0a2f29d649c7Screenshot (61).png'),
(2,11,'hkltores','angamaly','34567890','asd@df','static/2fb7b258-0149-472a-908f-c534ce44e734Salford Carpark (1).png');

/*Table structure for table `complaint` */

DROP TABLE IF EXISTS `complaint`;

CREATE TABLE `complaint` (
  `complaint_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL,
  `complaint` varchar(255) DEFAULT NULL,
  `reply` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`complaint_id`),
  KEY `user_id` (`user_id`),
  KEY `shop_id` (`company_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `complaint` */

insert  into `complaint`(`complaint_id`,`user_id`,`company_id`,`complaint`,`reply`,`date`) values 
(1,1,1,'trdtfuyyfuyuf','pending','2025-03-06');

/*Table structure for table `complaints` */

DROP TABLE IF EXISTS `complaints`;

CREATE TABLE `complaints` (
  `complaint_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL,
  `complaint` varchar(255) DEFAULT NULL,
  `reply` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`complaint_id`),
  KEY `user_id` (`user_id`),
  KEY `company_id` (`company_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/*Data for the table `complaints` */

/*Table structure for table `features` */

DROP TABLE IF EXISTS `features`;

CREATE TABLE `features` (
  `feature_id` int(11) NOT NULL AUTO_INCREMENT,
  `vehicle_id` int(11) DEFAULT NULL,
  `features` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`feature_id`),
  KEY `vehicle_id` (`vehicle_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

/*Data for the table `features` */

insert  into `features`(`feature_id`,`vehicle_id`,`features`) values 
(1,1,'ddddd'),
(2,1,'ddd');

/*Table structure for table `feedback` */

DROP TABLE IF EXISTS `feedback`;

CREATE TABLE `feedback` (
  `feedback_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `feedback` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`feedback_id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `feedback` */

insert  into `feedback`(`feedback_id`,`user_id`,`feedback`,`date`) values 
(1,1,'asdfsefd','2025-03-06');

/*Table structure for table `insurancecompany` */

DROP TABLE IF EXISTS `insurancecompany`;

CREATE TABLE `insurancecompany` (
  `insurance_id` int(11) NOT NULL AUTO_INCREMENT,
  `login_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `place` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`insurance_id`),
  KEY `login_id` (`login_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

/*Data for the table `insurancecompany` */

insert  into `insurancecompany`(`insurance_id`,`login_id`,`name`,`place`,`phone`,`email`,`image`) values 
(1,6,'joo','dasfesd','asaas','asaS',NULL),
(2,9,'sdfghjk dfghjkl','kochi','02345678906','sdfghjkl@ghj',NULL);

/*Table structure for table `loanrequest` */

DROP TABLE IF EXISTS `loanrequest`;

CREATE TABLE `loanrequest` (
  `loanrequest_id` int(11) NOT NULL AUTO_INCREMENT,
  `allotvehicle_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `bank_id` int(11) DEFAULT NULL,
  `details` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`loanrequest_id`),
  KEY `allotvehicle_id` (`allotvehicle_id`),
  KEY `bank_id` (`bank_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

/*Data for the table `loanrequest` */

insert  into `loanrequest`(`loanrequest_id`,`allotvehicle_id`,`user_id`,`bank_id`,`details`,`date`,`status`) values 
(3,2,1,1,'aaaaaaaaaaaaaaa','2025-03-25','accepted');

/*Table structure for table `login` */

DROP TABLE IF EXISTS `login`;

CREATE TABLE `login` (
  `login_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `usertype` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`login_id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

/*Data for the table `login` */

insert  into `login`(`login_id`,`username`,`password`,`usertype`) values 
(1,'ben','ben','company'),
(2,'admin','admin','admin'),
(4,'jithu','jithu','user'),
(6,'joo','joo','insurance'),
(7,'bank','bank','bank'),
(12,'kollamrto','kollamrto','mvd'),
(9,'sdfghj','sdfgh','insurance'),
(10,'ffffff','fdd','bank'),
(11,'kstore','kstore','pending'),
(13,'aluvarto','aluvarto','mvd'),
(14,'joyalwilson','joyalwilson','user');

/*Table structure for table `mvd` */

DROP TABLE IF EXISTS `mvd`;

CREATE TABLE `mvd` (
  `mvd_id` int(11) NOT NULL AUTO_INCREMENT,
  `login_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `place` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`mvd_id`),
  KEY `login_id` (`login_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

/*Data for the table `mvd` */

insert  into `mvd`(`mvd_id`,`login_id`,`name`,`place`,`phone`,`email`) values 
(4,13,'Aluva Rto','Aluva','9472638272','aluvarto@gmail.com'),
(3,12,'kollam Rto','Kollam','9023818482','kollamrto@gmail.com');

/*Table structure for table `noccertificate` */

DROP TABLE IF EXISTS `noccertificate`;

CREATE TABLE `noccertificate` (
  `noccertificate_id` int(11) NOT NULL AUTO_INCREMENT,
  `loanrequest_id` int(11) DEFAULT NULL,
  `file` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`noccertificate_id`),
  KEY `loanrequest_id` (`loanrequest_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

/*Data for the table `noccertificate` */

insert  into `noccertificate`(`noccertificate_id`,`loanrequest_id`,`file`,`date`) values 
(1,1,'static/imagesc5aba791-8abe-424d-a160-a4ed56402e67Screenshot (66).png','2025-03-06'),
(2,1,'static/imagesc8735e04-951b-4fa8-91be-28df24d759dcScreenshot (64).png','2025-03-06'),
(3,2,'static/imagesafbae6d8-70ac-4270-92eb-8d80062e2be0Screenshot (65).png','2025-03-25');

/*Table structure for table `payment` */

DROP TABLE IF EXISTS `payment`;

CREATE TABLE `payment` (
  `payment_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) DEFAULT NULL,
  `amount` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`payment_id`),
  KEY `booking_id` (`booking_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

/*Data for the table `payment` */

insert  into `payment`(`payment_id`,`booking_id`,`amount`,`date`) values 
(1,4,'1099000','2025-03-06'),
(2,5,'1099000','2025-03-22');

/*Table structure for table `policy` */

DROP TABLE IF EXISTS `policy`;

CREATE TABLE `policy` (
  `policy_id` int(11) NOT NULL AUTO_INCREMENT,
  `insurance_id` int(11) DEFAULT NULL,
  `policydetails` varchar(255) DEFAULT NULL,
  `details` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`policy_id`),
  KEY `insurance_id` (`insurance_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

/*Data for the table `policy` */

insert  into `policy`(`policy_id`,`insurance_id`,`policydetails`,`details`,`date`) values 
(1,1,'asadsads','sadasdasds','asdsad');

/*Table structure for table `policyrequest` */

DROP TABLE IF EXISTS `policyrequest`;

CREATE TABLE `policyrequest` (
  `policyrequest_id` int(11) NOT NULL AUTO_INCREMENT,
  `policy_id` int(11) DEFAULT NULL,
  `allotvehicle_id` int(11) DEFAULT NULL,
  `policynumber` varchar(255) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`policyrequest_id`),
  KEY `policy_id` (`policy_id`),
  KEY `allotvehicle_id` (`allotvehicle_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `policyrequest` */

insert  into `policyrequest`(`policyrequest_id`,`policy_id`,`allotvehicle_id`,`policynumber`,`date`,`status`) values 
(1,1,2,'234','2025-03-04','Accepted');

/*Table structure for table `registerrequest` */

DROP TABLE IF EXISTS `registerrequest`;

CREATE TABLE `registerrequest` (
  `registerrequest_id` int(11) NOT NULL AUTO_INCREMENT,
  `mvd_id` int(11) DEFAULT NULL,
  `allotvehicle_id` int(11) DEFAULT NULL,
  `date` varchar(255) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`registerrequest_id`),
  KEY `mvd_id` (`mvd_id`),
  KEY `allotvehicle_id` (`allotvehicle_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

/*Data for the table `registerrequest` */

insert  into `registerrequest`(`registerrequest_id`,`mvd_id`,`allotvehicle_id`,`date`,`status`) values 
(2,1,2,'2025-03-04','registered'),
(3,1,2,'2025-03-22','registered');

/*Table structure for table `specification` */

DROP TABLE IF EXISTS `specification`;

CREATE TABLE `specification` (
  `specification_id` int(11) NOT NULL AUTO_INCREMENT,
  `vehicle_id` int(11) DEFAULT NULL,
  `specification` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`specification_id`),
  KEY `vehicle_id` (`vehicle_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `specification` */

insert  into `specification`(`specification_id`,`vehicle_id`,`specification`) values 
(1,1,'sdsds');

/*Table structure for table `user` */

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `login_id` int(11) DEFAULT NULL,
  `fname` varchar(255) DEFAULT NULL,
  `lname` varchar(255) DEFAULT NULL,
  `place` varchar(255) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `login_id` (`login_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

/*Data for the table `user` */

insert  into `user`(`user_id`,`login_id`,`fname`,`lname`,`place`,`phone`,`email`,`image`) values 
(1,4,'jithu','gf','angamaly','09767875459','jith23@gmail.com','static/cd6f97af-7ab8-4574-b297-0a2f29d649c7Screenshot (61).png'),
(2,14,'joyal','wilson','kochi','09803291923','anu123@gmail.com','static/cd6f97af-7ab8-4574-b297-0a2f29d649c7Screenshot (61).png');

/*Table structure for table `vehicle` */

DROP TABLE IF EXISTS `vehicle`;

CREATE TABLE `vehicle` (
  `vehicle_id` int(11) NOT NULL AUTO_INCREMENT,
  `company_id` int(11) DEFAULT NULL,
  `brand_id` int(11) DEFAULT NULL,
  `vehicles` varchar(255) DEFAULT NULL,
  `amt` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`vehicle_id`),
  KEY `company_id` (`company_id`),
  KEY `brand_id` (`brand_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `vehicle` */

insert  into `vehicle`(`vehicle_id`,`company_id`,`brand_id`,`vehicles`,`amt`) values 
(1,1,1,'dulxee','1099000');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
