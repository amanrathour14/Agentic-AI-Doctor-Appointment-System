-- MySQL Database Schema for MedAI Doctor Appointment System
-- Run this script to create the database structure

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS doctor_appointments;
USE doctor_appointments;

-- Doctors table
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    license_number VARCHAR(50) UNIQUE NOT NULL,
    experience_years INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other') NOT NULL,
    address TEXT,
    emergency_contact VARCHAR(255),
    emergency_phone VARCHAR(20),
    medical_history TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Doctor availability table
CREATE TABLE IF NOT EXISTS doctor_availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week TINYINT NOT NULL, -- 1=Monday, 2=Tuesday, ..., 7=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    UNIQUE KEY unique_doctor_day (doctor_id, day_of_week)
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_minutes INT DEFAULT 30,
    status ENUM('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    symptoms TEXT,
    diagnosis TEXT,
    prescription TEXT,
    notes TEXT,
    google_calendar_event_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    UNIQUE KEY unique_appointment (doctor_id, appointment_date, appointment_time)
);

-- Visit history table
CREATE TABLE IF NOT EXISTS visit_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    visit_date DATE NOT NULL,
    symptoms TEXT,
    diagnosis TEXT,
    prescription TEXT,
    treatment_notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_type ENUM('doctor', 'patient') NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('appointment', 'reminder', 'system', 'alert') NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sessions table for chat/conversation management
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_type ENUM('doctor', 'patient', 'guest') NOT NULL,
    user_id INT,
    context JSON,
    conversation_history JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL
);

-- Create indexes for better performance
CREATE INDEX idx_doctors_specialty ON doctors(specialty);
CREATE INDEX idx_doctors_active ON doctors(is_active);
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_doctor_date ON appointments(doctor_id, appointment_date);
CREATE INDEX idx_availability_doctor_day ON doctor_availability(doctor_id, day_of_week);
CREATE INDEX idx_notifications_user ON notifications(user_id, user_type);
CREATE INDEX idx_notifications_unread ON notifications(is_read, created_at);
CREATE INDEX idx_sessions_active ON sessions(is_active, expires_at);

-- Create views for common queries
CREATE OR REPLACE VIEW active_appointments AS
SELECT 
    a.id,
    a.appointment_date,
    a.appointment_time,
    a.status,
    a.symptoms,
    d.name as doctor_name,
    d.specialty as doctor_specialty,
    p.name as patient_name,
    p.email as patient_email
FROM appointments a
JOIN doctors d ON a.doctor_id = d.id
JOIN patients p ON a.patient_id = p.id
WHERE a.status IN ('scheduled', 'confirmed')
AND a.appointment_date >= CURDATE()
ORDER BY a.appointment_date, a.appointment_time;

CREATE OR REPLACE VIEW doctor_schedule AS
SELECT 
    d.id as doctor_id,
    d.name as doctor_name,
    d.specialty,
    a.appointment_date,
    a.appointment_time,
    a.duration_minutes,
    a.status,
    p.name as patient_name
FROM doctors d
LEFT JOIN appointments a ON d.id = a.doctor_id 
    AND a.appointment_date = CURDATE()
    AND a.status IN ('scheduled', 'confirmed')
LEFT JOIN patients p ON a.patient_id = p.id
WHERE d.is_active = TRUE
ORDER BY d.name, a.appointment_time;

-- Insert sample data
INSERT INTO doctors (name, specialty, email, phone, license_number, experience_years) VALUES
('Dr. Sarah Johnson', 'Cardiology', 'sarah.johnson@medai.com', '+1-555-0101', 'MD12345', 15),
('Dr. Michael Chen', 'Neurology', 'michael.chen@medai.com', '+1-555-0102', 'MD12346', 12),
('Dr. Emily Rodriguez', 'Pediatrics', 'emily.rodriguez@medai.com', '+1-555-0103', 'MD12347', 8),
('Dr. David Kim', 'Orthopedics', 'david.kim@medai.com', '+1-555-0104', 'MD12348', 20),
('Dr. Lisa Thompson', 'Dermatology', 'lisa.thompson@medai.com', '+1-555-0105', 'MD12349', 10);

INSERT INTO patients (name, email, phone, date_of_birth, gender, address) VALUES
('John Smith', 'john.smith@email.com', '+1-555-0201', '1985-03-15', 'male', '123 Main St, City, State'),
('Maria Garcia', 'maria.garcia@email.com', '+1-555-0202', '1990-07-22', 'female', '456 Oak Ave, City, State'),
('Robert Wilson', 'robert.wilson@email.com', '+1-555-0203', '1978-11-08', 'male', '789 Pine Rd, City, State'),
('Jennifer Lee', 'jennifer.lee@email.com', '+1-555-0204', '1992-04-30', 'female', '321 Elm St, City, State'),
('Thomas Brown', 'thomas.brown@email.com', '+1-555-0205', '1983-09-12', 'male', '654 Maple Dr, City, State');

-- Insert doctor availability (Monday to Friday, 9 AM to 5 PM)
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time) VALUES
(1, 1, '09:00:00', '17:00:00'), -- Monday
(1, 2, '09:00:00', '17:00:00'), -- Tuesday
(1, 3, '09:00:00', '17:00:00'), -- Wednesday
(1, 4, '09:00:00', '17:00:00'), -- Thursday
(1, 5, '09:00:00', '17:00:00'), -- Friday
(2, 1, '09:00:00', '17:00:00'),
(2, 2, '09:00:00', '17:00:00'),
(2, 3, '09:00:00', '17:00:00'),
(2, 4, '09:00:00', '17:00:00'),
(2, 5, '09:00:00', '17:00:00'),
(3, 1, '09:00:00', '17:00:00'),
(3, 2, '09:00:00', '17:00:00'),
(3, 3, '09:00:00', '17:00:00'),
(3, 4, '09:00:00', '17:00:00'),
(3, 5, '09:00:00', '17:00:00'),
(4, 1, '09:00:00', '17:00:00'),
(4, 2, '09:00:00', '17:00:00'),
(4, 3, '09:00:00', '17:00:00'),
(4, 4, '09:00:00', '17:00:00'),
(4, 5, '09:00:00', '17:00:00'),
(5, 1, '09:00:00', '17:00:00'),
(5, 2, '09:00:00', '17:00:00'),
(5, 3, '09:00:00', '17:00:00'),
(5, 4, '09:00:00', '17:00:00'),
(5, 5, '09:00:00', '17:00:00');

-- Insert sample appointments
INSERT INTO appointments (doctor_id, patient_id, appointment_date, appointment_time, status, symptoms) VALUES
(1, 1, CURDATE() + INTERVAL 1 DAY, '10:00:00', 'scheduled', 'Chest pain and shortness of breath'),
(2, 2, CURDATE() + INTERVAL 2 DAY, '14:30:00', 'scheduled', 'Headaches and dizziness'),
(3, 3, CURDATE() + INTERVAL 1 DAY, '11:00:00', 'scheduled', 'Fever and cough'),
(4, 4, CURDATE() + INTERVAL 3 DAY, '15:00:00', 'scheduled', 'Knee pain after injury'),
(5, 5, CURDATE() + INTERVAL 2 DAY, '13:00:00', 'scheduled', 'Skin rash and itching');

-- Insert sample notifications
INSERT INTO notifications (user_id, user_type, title, message, type, priority) VALUES
(1, 'doctor', 'New Appointment', 'New appointment scheduled with John Smith for tomorrow at 10:00 AM', 'appointment', 'medium'),
(2, 'patient', 'Appointment Reminder', 'Reminder: Your appointment with Dr. Michael Chen is tomorrow at 2:30 PM', 'reminder', 'medium'),
(3, 'doctor', 'Patient Update', 'Patient Robert Wilson has updated their symptoms', 'system', 'low');

-- Show created tables
SHOW TABLES;

-- Show sample data
SELECT 'Doctors' as table_name, COUNT(*) as count FROM doctors
UNION ALL
SELECT 'Patients', COUNT(*) FROM patients
UNION ALL
SELECT 'Appointments', COUNT(*) FROM appointments
UNION ALL
SELECT 'Doctor Availability', COUNT(*) FROM doctor_availability
UNION ALL
SELECT 'Notifications', COUNT(*) FROM notifications;