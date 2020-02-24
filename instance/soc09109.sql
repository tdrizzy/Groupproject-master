SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;


DROP TABLE IF EXISTS academic_year;
CREATE TABLE IF NOT EXISTS academic_year (
  `year` varchar(10) COLLATE utf8_bin NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL,
  PRIMARY KEY (`year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS admin;
CREATE TABLE IF NOT EXISTS admin (
  last_notification_check datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS alert_queue;
CREATE TABLE IF NOT EXISTS alert_queue (
  alert_id int(11) NOT NULL AUTO_INCREMENT,
  user_id int(11) NOT NULL,
  email varchar(30) COLLATE utf8_bin NOT NULL,
  created_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sent_date timestamp NULL DEFAULT NULL,
  `subject` varchar(50) COLLATE utf8_bin NOT NULL,
  `message_text` varchar(1024) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (alert_id)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=484 ;

DROP TABLE IF EXISTS faq;
CREATE TABLE IF NOT EXISTS faq (
  faq_id int(11) NOT NULL AUTO_INCREMENT,
  question varchar(200) COLLATE utf8_bin NOT NULL,
  answer varchar(700) COLLATE utf8_bin NOT NULL,
  rank int(11) NOT NULL DEFAULT '0',
  external tinyint(4) NOT NULL DEFAULT '0',
  student tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (faq_id)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=13 ;

DROP TABLE IF EXISTS interest;
CREATE TABLE IF NOT EXISTS interest (
  project_id int(11) NOT NULL DEFAULT '0',
  user_id int(11) NOT NULL DEFAULT '0',
  created_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (project_id,user_id),
  KEY user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS programme;
CREATE TABLE IF NOT EXISTS programme (
  programme_code varchar(10) COLLATE utf8_bin NOT NULL,
  title varchar(50) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (programme_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS project;
CREATE TABLE IF NOT EXISTS project (
  project_id int(11) NOT NULL AUTO_INCREMENT,
  project_title varchar(100) COLLATE utf8_bin NOT NULL,
  client_id int(11) NOT NULL,
  created_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_date timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `year` varchar(10) COLLATE utf8_bin NOT NULL,
  overview text COLLATE utf8_bin NOT NULL,
  deliverables varchar(800) COLLATE utf8_bin NOT NULL,
  resources varchar(800) COLLATE utf8_bin NOT NULL,
  `status` int(11) NOT NULL DEFAULT '5',
  PRIMARY KEY (project_id),
  KEY project_client_idx (project_id) USING BTREE,
  KEY project_year_idx (`year`),
  KEY project_user_ix (client_id)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=52 ;

DROP TABLE IF EXISTS project_flag;
CREATE TABLE IF NOT EXISTS project_flag (
  project_id int(11) NOT NULL,
  user_id int(11) NOT NULL,
  message text COLLATE utf8_bin,
  PRIMARY KEY (project_id,user_id),
  KEY user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS skill;
CREATE TABLE IF NOT EXISTS skill (
  skill_id int(11) NOT NULL AUTO_INCREMENT,
  skill_name varchar(30) COLLATE utf8_bin NOT NULL,
  description varchar(200) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (skill_id),
  UNIQUE KEY skill_name (skill_name)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=74 ;

DROP TABLE IF EXISTS skills_offered;
CREATE TABLE IF NOT EXISTS skills_offered (
  user_id int(11) NOT NULL,
  skill_id int(11) NOT NULL,
  PRIMARY KEY (user_id,skill_id),
  KEY skill_id (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS skills_required;
CREATE TABLE IF NOT EXISTS skills_required (
  project_id int(11) NOT NULL DEFAULT '0',
  skill_id int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (project_id,skill_id),
  KEY skill_id (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS status;
CREATE TABLE IF NOT EXISTS `status` (
  `status` int(11) NOT NULL AUTO_INCREMENT,
  status_text varchar(20) COLLATE utf8_bin NOT NULL,
  domain varchar(10) COLLATE utf8_bin NOT NULL,
  action_text varchar(10) COLLATE utf8_bin DEFAULT NULL,
  css_class varchar(10) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`status`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=11 ;

DROP TABLE IF EXISTS status_transition;
CREATE TABLE IF NOT EXISTS status_transition (
  from_status int(11) NOT NULL DEFAULT '0',
  to_status int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (from_status,to_status),
  KEY transition_from (from_status),
  KEY transition_to (to_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS team;
CREATE TABLE IF NOT EXISTS team (
  team_id int(11) NOT NULL AUTO_INCREMENT,
  project_id int(11) NOT NULL,
  created_by int(11) NOT NULL,
  created_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_date timestamp NULL DEFAULT NULL,
  `status` int(20) NOT NULL DEFAULT '1',
  `comment` text COLLATE utf8_bin,
  vacancies text COLLATE utf8_bin,
  PRIMARY KEY (team_id),
  KEY team_project_idx (project_id) USING BTREE,
  KEY team_created_idx (created_by) USING BTREE,
  KEY team_status_idx (`status`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=65 ;

DROP TABLE IF EXISTS team_member;
CREATE TABLE IF NOT EXISTS team_member (
  team_id int(11) NOT NULL DEFAULT '0',
  user_id int(11) NOT NULL DEFAULT '0',
  created_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (team_id,user_id),
  KEY user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
  user_id int(11) NOT NULL AUTO_INCREMENT,
  username varchar(40) COLLATE utf8_bin NOT NULL,
  phash varchar(100) COLLATE utf8_bin NOT NULL,
  admin tinyint(4) NOT NULL DEFAULT '0',
  external tinyint(4) NOT NULL DEFAULT '0',
  created_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  first_name varchar(25) COLLATE utf8_bin DEFAULT NULL,
  last_name varchar(25) COLLATE utf8_bin DEFAULT NULL,
  email varchar(50) COLLATE utf8_bin DEFAULT NULL,
  company varchar(50) COLLATE utf8_bin DEFAULT NULL,
  telephone varchar(20) COLLATE utf8_bin DEFAULT NULL,
  programme_code varchar(10) COLLATE utf8_bin DEFAULT NULL,
  `comment` varchar(800) COLLATE utf8_bin DEFAULT NULL,
  web varchar(100) COLLATE utf8_bin DEFAULT NULL,
  notify_new tinyint(4) NOT NULL DEFAULT '0',
  notify_interest tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (user_id),
  UNIQUE KEY username (username),
  KEY users_programme_idx (programme_code)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=2495 ;


ALTER TABLE interest
  ADD CONSTRAINT interest_ibfk_1 FOREIGN KEY (project_id) REFERENCES project (project_id),
  ADD CONSTRAINT interest_ibfk_2 FOREIGN KEY (user_id) REFERENCES `users` (user_id);

ALTER TABLE project
  ADD CONSTRAINT project_ibfk_1 FOREIGN KEY (client_id) REFERENCES `users` (user_id),
  ADD CONSTRAINT project_ibfk_2 FOREIGN KEY (`year`) REFERENCES academic_year (`year`);

ALTER TABLE project_flag
  ADD CONSTRAINT project_flag_ibfk_1 FOREIGN KEY (project_id) REFERENCES project (project_id),
  ADD CONSTRAINT project_flag_ibfk_2 FOREIGN KEY (user_id) REFERENCES `users` (user_id);

ALTER TABLE skills_offered
  ADD CONSTRAINT skills_offered_ibfk_1 FOREIGN KEY (user_id) REFERENCES `users` (user_id),
  ADD CONSTRAINT skills_offered_ibfk_2 FOREIGN KEY (skill_id) REFERENCES skill (skill_id);

ALTER TABLE skills_required
  ADD CONSTRAINT skills_required_ibfk_1 FOREIGN KEY (project_id) REFERENCES project (project_id),
  ADD CONSTRAINT skills_required_ibfk_2 FOREIGN KEY (skill_id) REFERENCES skill (skill_id);

ALTER TABLE status_transition
  ADD CONSTRAINT status_transition_ibfk_1 FOREIGN KEY (from_status) REFERENCES status (`status`),
  ADD CONSTRAINT status_transition_ibfk_2 FOREIGN KEY (to_status) REFERENCES status (`status`);

ALTER TABLE team
  ADD CONSTRAINT team_ibfk_1 FOREIGN KEY (project_id) REFERENCES project (project_id),
  ADD CONSTRAINT team_ibfk_2 FOREIGN KEY (created_by) REFERENCES `users` (user_id);

ALTER TABLE team_member
  ADD CONSTRAINT team_member_ibfk_1 FOREIGN KEY (team_id) REFERENCES team (team_id),
  ADD CONSTRAINT team_member_ibfk_2 FOREIGN KEY (user_id) REFERENCES `users` (user_id);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
