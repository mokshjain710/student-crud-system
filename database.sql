-- =======================================================
-- DBMS Mini Project: Student Records Management System
-- Database Setup Script (MySQL)
-- =======================================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS student_crud_db;
USE student_crud_db;

-- Step 2: Create Students Table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    cgpa DECIMAL(4, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Insert Sample Data for Demonstration
INSERT INTO students (roll_no, name, email, department, semester, cgpa) VALUES
('CS101', 'Aarav Sharma', 'aarav.sharma@example.com', 'Computer Science', 6, 8.85),
('CS102', 'Priya Patel', 'priya.patel@example.com', 'Computer Science', 6, 9.20),
('IT201', 'Rohan Verma', 'rohan.verma@example.com', 'Information Technology', 4, 7.90),
('EC301', 'Ananya Iyer', 'ananya.iyer@example.com', 'Electronics', 8, 8.40),
('ME401', 'Vikram Singh', 'vikram.singh@example.com', 'Mechanical', 2, 7.50)
ON DUPLICATE KEY UPDATE roll_no=roll_no;

-- Step 4: Verification Query
SELECT * FROM students;
