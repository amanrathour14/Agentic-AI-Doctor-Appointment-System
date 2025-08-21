-- Seed sample data for testing the doctor appointment system

-- Insert sample doctors
INSERT INTO doctors (name, email, specialization, phone) VALUES
('Dr. Rajesh Ahuja', 'dr.ahuja@hospital.com', 'General Medicine', '+1-555-0101'),
('Dr. Sarah Johnson', 'dr.johnson@hospital.com', 'Cardiology', '+1-555-0102'),
('Dr. Michael Chen', 'dr.chen@hospital.com', 'Pediatrics', '+1-555-0103'),
('Dr. Emily Davis', 'dr.davis@hospital.com', 'Dermatology', '+1-555-0104')
ON CONFLICT (email) DO NOTHING;

-- Insert sample patients
INSERT INTO patients (name, email, phone, date_of_birth) VALUES
('John Smith', 'john.smith@email.com', '+1-555-1001', '1985-03-15'),
('Jane Doe', 'jane.doe@email.com', '+1-555-1002', '1990-07-22'),
('Robert Wilson', 'robert.wilson@email.com', '+1-555-1003', '1978-11-08'),
('Lisa Brown', 'lisa.brown@email.com', '+1-555-1004', '1992-05-30')
ON CONFLICT (email) DO NOTHING;

-- Insert doctor availability (Monday to Friday, 9 AM to 5 PM)
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time) VALUES
-- Dr. Ahuja (ID: 1)
(1, 1, '09:00:00', '17:00:00'), -- Monday
(1, 2, '09:00:00', '17:00:00'), -- Tuesday
(1, 3, '09:00:00', '17:00:00'), -- Wednesday
(1, 4, '09:00:00', '17:00:00'), -- Thursday
(1, 5, '09:00:00', '17:00:00'), -- Friday
-- Dr. Johnson (ID: 2)
(2, 1, '10:00:00', '16:00:00'), -- Monday
(2, 2, '10:00:00', '16:00:00'), -- Tuesday
(2, 3, '10:00:00', '16:00:00'), -- Wednesday
(2, 4, '10:00:00', '16:00:00'), -- Thursday
(2, 5, '10:00:00', '16:00:00'), -- Friday
-- Dr. Chen (ID: 3)
(3, 1, '08:00:00', '16:00:00'), -- Monday
(3, 2, '08:00:00', '16:00:00'), -- Tuesday
(3, 3, '08:00:00', '16:00:00'), -- Wednesday
(3, 4, '08:00:00', '16:00:00'), -- Thursday
(3, 5, '08:00:00', '16:00:00'), -- Friday
-- Dr. Davis (ID: 4)
(4, 2, '11:00:00', '19:00:00'), -- Tuesday
(4, 3, '11:00:00', '19:00:00'), -- Wednesday
(4, 4, '11:00:00', '19:00:00'), -- Thursday
(4, 5, '11:00:00', '19:00:00'), -- Friday
(4, 6, '09:00:00', '13:00:00')  -- Saturday
ON CONFLICT DO NOTHING;

-- Insert some sample appointments for testing
INSERT INTO appointments (doctor_id, patient_id, appointment_date, appointment_time, status, symptoms) VALUES
(1, 1, CURRENT_DATE - INTERVAL '1 day', '10:00:00', 'completed', 'Fever, headache'),
(1, 2, CURRENT_DATE - INTERVAL '2 days', '14:00:00', 'completed', 'Cough, sore throat'),
(2, 3, CURRENT_DATE + INTERVAL '1 day', '11:00:00', 'scheduled', 'Chest pain'),
(1, 4, CURRENT_DATE + INTERVAL '2 days', '15:00:00', 'scheduled', 'Regular checkup')
ON CONFLICT (doctor_id, appointment_date, appointment_time) DO NOTHING;

-- Insert corresponding visit history for completed appointments
INSERT INTO visit_history (appointment_id, doctor_id, patient_id, visit_date, diagnosis, symptoms, treatment) VALUES
(1, 1, 1, CURRENT_DATE - INTERVAL '1 day', 'Viral fever', 'Fever, headache', 'Rest, paracetamol, plenty of fluids'),
(2, 1, 2, CURRENT_DATE - INTERVAL '2 days', 'Upper respiratory infection', 'Cough, sore throat', 'Antibiotics, throat lozenges, rest')
ON CONFLICT DO NOTHING;
