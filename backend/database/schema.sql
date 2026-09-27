-- ============================================================
-- SATHI / SIH26001 - MySQL 8+ Database DDL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS `sathi` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `sathi`;

-- 1. Monitored Locations
CREATE TABLE IF NOT EXISTS `monitored_locations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `latitude` DOUBLE NOT NULL,
    `longitude` DOUBLE NOT NULL,
    `is_active` TINYINT(1) DEFAULT 1 NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX `idx_mon_loc_coords` (`latitude`, `longitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. IoT Sensors
CREATE TABLE IF NOT EXISTS `sensors` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `sensor_id` VARCHAR(100) NOT NULL UNIQUE,
    `name` VARCHAR(255) NULL,
    `latitude` DOUBLE NOT NULL,
    `longitude` DOUBLE NOT NULL,
    `sensor_type` VARCHAR(100) DEFAULT 'rain_gauge' NOT NULL,
    `is_active` TINYINT(1) DEFAULT 1 NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Sensor Readings
CREATE TABLE IF NOT EXISTS `sensor_readings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `sensor_id` VARCHAR(100) NOT NULL,
    `rainfall_mm` DOUBLE NULL,
    `soil_moisture` DOUBLE NULL,
    `temperature` DOUBLE NULL,
    `humidity` DOUBLE NULL,
    `recorded_at` DATETIME NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (`sensor_id`) REFERENCES `sensors`(`sensor_id`) ON DELETE CASCADE,
    INDEX `idx_sensor_reading_time` (`sensor_id`, `recorded_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Weather Observations
CREATE TABLE IF NOT EXISTS `weather_observations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `latitude` DOUBLE NOT NULL,
    `longitude` DOUBLE NOT NULL,
    `rain_1h` DOUBLE DEFAULT 0.0 NOT NULL,
    `rain_24h` DOUBLE DEFAULT 0.0 NOT NULL,
    `rain_3d` DOUBLE DEFAULT 0.0 NOT NULL,
    `rain_7d` DOUBLE DEFAULT 0.0 NOT NULL,
    `rain_14d` DOUBLE DEFAULT 0.0 NOT NULL,
    `temperature` DOUBLE NULL,
    `humidity` DOUBLE NULL,
    `soil_moisture` DOUBLE NULL,
    `observed_at` DATETIME NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    INDEX `idx_weather_coords_time` (`latitude`, `longitude`, `observed_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Citizen Reports
CREATE TABLE IF NOT EXISTS `citizen_reports` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `latitude` DOUBLE NOT NULL,
    `longitude` DOUBLE NOT NULL,
    `severity` INT DEFAULT 1 NOT NULL,
    `description` TEXT NULL,
    `image_url` VARCHAR(500) NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    INDEX `idx_citizen_report_coords` (`latitude`, `longitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Risk Predictions
CREATE TABLE IF NOT EXISTS `risk_predictions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `location_id` INT NULL,
    `latitude` DOUBLE NOT NULL,
    `longitude` DOUBLE NOT NULL,
    `landslide_probability` DOUBLE NOT NULL,
    `risk_score` INT NOT NULL,
    `risk_level` VARCHAR(50) NOT NULL,
    `model_version` VARCHAR(50) DEFAULT 'xgb-v1' NOT NULL,
    `prediction_timestamp` DATETIME NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (`location_id`) REFERENCES `monitored_locations`(`id`) ON DELETE SET NULL,
    INDEX `idx_risk_pred_loc_time` (`location_id`, `prediction_timestamp`),
    INDEX `idx_risk_pred_coords` (`latitude`, `longitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. District Risk Summaries
CREATE TABLE IF NOT EXISTS `district_risk_summaries` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `district` VARCHAR(255) NOT NULL UNIQUE,
    `state` VARCHAR(255) NULL,
    `flood_risk_pct` DOUBLE DEFAULT 0.0 NOT NULL,
    `landslide_risk_pct` DOUBLE DEFAULT 0.0 NOT NULL,
    `status` VARCHAR(50) DEFAULT 'Moderate' NOT NULL,
    `people_at_risk` INT DEFAULT 0 NOT NULL,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. System Alerts
CREATE TABLE IF NOT EXISTS `system_alerts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `alert_type` VARCHAR(50) NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `severity` VARCHAR(50) NOT NULL,
    `time_ago` VARCHAR(100) DEFAULT 'Just now' NOT NULL,
    `is_active` TINYINT(1) DEFAULT 1 NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Risk Trends
CREATE TABLE IF NOT EXISTS `risk_trends` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `day_label` VARCHAR(10) NOT NULL,
    `day_order` INT NOT NULL,
    `risk_value` DOUBLE NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Action Recommendations
CREATE TABLE IF NOT EXISTS `action_recommendations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `recommendation_text` TEXT NOT NULL,
    `priority` INT DEFAULT 1 NOT NULL,
    `is_active` TINYINT(1) DEFAULT 1 NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Dashboard Stats
CREATE TABLE IF NOT EXISTS `dashboard_stats` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `stat_key` VARCHAR(100) NOT NULL UNIQUE,
    `label` VARCHAR(255) NOT NULL,
    `value` VARCHAR(100) NOT NULL,
    `delta` VARCHAR(255) NOT NULL,
    `tone` VARCHAR(50) NOT NULL,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

