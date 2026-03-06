-- ============================================================
-- Smart Complaint Management System - Database Setup
-- Run this file in MySQL to create all required tables
-- ============================================================

-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS smart_complaint_db;

-- Step 2: Select the database
USE smart_complaint_db;

-- ============================================================
-- Table 1: users
-- Stores registered users of the complaint system
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,           -- Unique user ID
    name VARCHAR(100) NOT NULL,                  -- Full name
    email VARCHAR(150) UNIQUE NOT NULL,          -- Email (used for login)
    password_hash VARCHAR(256) NOT NULL,         -- Hashed password (never store plain text)
    phone VARCHAR(15),                           -- Optional phone number
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Registration date
);

-- ============================================================
-- Table 2: admins
-- Stores admin credentials (separate from users)
-- ============================================================
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,       -- Admin username
    password_hash VARCHAR(256) NOT NULL          -- Hashed password
);

-- ============================================================
-- Table 3: departments
-- Stores department names for assigning complaints
-- ============================================================
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL                   -- Department name
);

-- ============================================================
-- Table 4: complaints
-- Main table storing all submitted complaints
-- ============================================================
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(20) UNIQUE NOT NULL,    -- Unique ID like CMP-XXXX
    user_id INT NOT NULL,                        -- FK → users.id
    title VARCHAR(200) NOT NULL,                 -- Complaint title
    description TEXT NOT NULL,                   -- Detailed description
    category VARCHAR(50) NOT NULL,               -- Road, Water, Electricity, etc.
    photo VARCHAR(300),                          -- Filename of uploaded photo (optional)
    location TEXT,                               -- Location/GPS coordinates
    status ENUM('Pending','In Progress','Resolved') DEFAULT 'Pending',
    department_id INT,                           -- FK → departments.id (assigned by admin)
    admin_notes TEXT,                            -- Admin comments on the complaint
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- ============================================================
-- Seed Data: Insert default departments
-- ============================================================
INSERT INTO departments (name) VALUES
    ('Road & Infrastructure'),
    ('Water Supply'),
    ('Electricity'),
    ('Sanitation & Waste'),
    ('Education / College'),
    ('Health & Medical'),
    ('Public Safety'),
    ('General Administration');

-- ============================================================
-- Admin Account Setup
-- !! IMPORTANT: Do NOT insert admin here. Run this instead: !!
--
--    python create_admin.py
--
-- This script generates a proper Werkzeug-hashed password for
-- "admin123" and inserts it into the admins table correctly.
-- Running the script is required because Werkzeug uses a
-- dynamic salt, so a static hash cannot be pre-baked here.
-- ============================================================
