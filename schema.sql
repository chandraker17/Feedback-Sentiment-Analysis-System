CREATE DATABASE IF NOT EXISTS openfeedback;
USE openfeedback;

-- tables here

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_name VARCHAR(100),
    feedback_text TEXT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

CREATE TABLE sentiment_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    feedback_id INT,
    sentiment_label VARCHAR(20),
    sentiment_score FLOAT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id)
) ENGINE=InnoDB;

CREATE TABLE feedback_summary (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) UNIQUE,
    average_rating FLOAT,
    total_feedback INT,
    positive_feedback INT,
    negative_feedback INT,
    neutral_feedback INT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
