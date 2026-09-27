-- ============================================================
-- Shaheen Model Girls High School - Management System
-- Database Schema (MySQL 8+)
-- ============================================================

CREATE DATABASE IF NOT EXISTS shaheen_school_erp
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE shaheen_school_erp;

-- ============================================================
-- 1. ROLES  (Super Admin, Admin, Teacher, Student, Parent)
-- ============================================================
CREATE TABLE roles (
    role_id      INT AUTO_INCREMENT PRIMARY KEY,
    role_name    VARCHAR(50) NOT NULL UNIQUE,   -- super_admin, admin, teacher, student, parent
    description  VARCHAR(255),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO roles (role_name, description) VALUES
 ('super_admin', 'Full system access'),
 ('admin',       'School administration access'),
 ('teacher',     'Teacher access'),
 ('student',     'Student access'),
 ('parent',      'Parent access (future version)');

-- ============================================================
-- 2. USERS  (core auth table for every login-capable person)
-- ============================================================
CREATE TABLE users (
    user_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    role_id        INT NOT NULL,
    full_name      VARCHAR(150) NOT NULL,
    email          VARCHAR(150) UNIQUE,
    phone          VARCHAR(20) UNIQUE,
    username       VARCHAR(80) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    profile_image  VARCHAR(255) DEFAULT NULL,
    is_active      BOOLEAN DEFAULT TRUE,
    last_login_at  DATETIME DEFAULT NULL,
    reset_token        VARCHAR(255) DEFAULT NULL,
    reset_token_expiry DATETIME DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
) ENGINE=InnoDB;

CREATE INDEX idx_users_role ON users(role_id);

-- ============================================================
-- 3. CLASSES / SECTIONS / SUBJECTS
-- ============================================================
CREATE TABLE classes (
    class_id     INT AUTO_INCREMENT PRIMARY KEY,
    class_name   VARCHAR(50) NOT NULL,     -- e.g. "Class 9", "Nursery"
    class_order  INT DEFAULT 0,            -- for sorting
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE sections (
    section_id   INT AUTO_INCREMENT PRIMARY KEY,
    class_id     INT NOT NULL,
    section_name VARCHAR(20) NOT NULL,     -- A, B, C
    room_number  VARCHAR(20),
    capacity     INT DEFAULT 40,
    class_teacher_id BIGINT DEFAULT NULL,  -- FK to teachers, set after teachers table exists
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_class_section (class_id, section_name),
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE academic_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    session_name VARCHAR(50) NOT NULL,
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_session_name (session_name)
) ENGINE=InnoDB;



CREATE TABLE subjects (
    subject_id   INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) UNIQUE,
    class_id     INT NOT NULL,
    is_optional  BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 4. TEACHERS
-- ============================================================
CREATE TABLE teachers (
    teacher_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NOT NULL UNIQUE,
    employee_code   VARCHAR(30) UNIQUE,
    qualification   VARCHAR(255),
    specialization  VARCHAR(150),
    joining_date    DATE,
    cnic            VARCHAR(20),
    address         VARCHAR(255),
    salary          DECIMAL(10,2),
    status          ENUM('active','on_leave','resigned','terminated') DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

ALTER TABLE sections
  ADD CONSTRAINT fk_section_class_teacher
  FOREIGN KEY (class_teacher_id) REFERENCES teachers(teacher_id) ON DELETE SET NULL;

-- Which teacher teaches which subject in which section
CREATE TABLE teacher_subject_assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id    BIGINT NOT NULL,
    subject_id    INT NOT NULL,
    section_id    INT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_teacher_subject_section (teacher_id, subject_id, section_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 5. PARENTS
-- ============================================================
CREATE TABLE parents (
    parent_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT NOT NULL UNIQUE,
    cnic          VARCHAR(20),
    occupation    VARCHAR(100),
    address       VARCHAR(255),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 6. STUDENTS
-- ============================================================
CREATE TABLE students (
    student_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NOT NULL UNIQUE,
    registration_no VARCHAR(30) UNIQUE NOT NULL,
    section_id      INT DEFAULT NULL,
    parent_id       BIGINT DEFAULT NULL,
    date_of_birth   DATE,
    gender          ENUM('female','male','other') DEFAULT 'female',
    admission_date  DATE,
    address         VARCHAR(255),
    blood_group     VARCHAR(5),
    status          ENUM('active','inactive','graduated','expelled') DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    FOREIGN KEY (parent_id) REFERENCES parents(parent_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_students_section ON students(section_id);

-- ============================================================
-- 7. ATTENDANCE
-- ============================================================
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id    BIGINT NOT NULL,
    section_id    INT NOT NULL,
    marked_by     BIGINT NOT NULL,        -- teacher_id
    attendance_date DATE NOT NULL,
    status        ENUM('present','absent','late','leave') NOT NULL,
    remarks       VARCHAR(255),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_student_date (student_id, attendance_date),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    FOREIGN KEY (marked_by) REFERENCES teachers(teacher_id)
) ENGINE=InnoDB;

CREATE INDEX idx_attendance_date ON attendance(attendance_date);

-- ============================================================
-- 8. EXAMS / RESULTS
-- ============================================================
CREATE TABLE exams (
    exam_id      INT AUTO_INCREMENT PRIMARY KEY,
    exam_name    VARCHAR(100) NOT NULL,     -- Mid Term, Final Term
    class_id     INT NOT NULL,
    start_date   DATE,
    end_date     DATE,
    academic_year VARCHAR(20),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE exam_subject_schedule (
    schedule_id  INT AUTO_INCREMENT PRIMARY KEY,
    exam_id      INT NOT NULL,
    subject_id   INT NOT NULL,
    exam_date    DATE,
    start_time   TIME,
    end_time     TIME,
    total_marks  INT DEFAULT 100,
    passing_marks INT DEFAULT 40,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE results (
    result_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id    BIGINT NOT NULL,
    schedule_id   INT NOT NULL,
    marks_obtained DECIMAL(5,2) NOT NULL,
    grade         VARCHAR(5),
    remarks       VARCHAR(255),
    entered_by    BIGINT NOT NULL,      -- teacher_id
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_student_schedule (student_id, schedule_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES exam_subject_schedule(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (entered_by) REFERENCES teachers(teacher_id)
) ENGINE=InnoDB;

-- ============================================================
-- 9. HOMEWORK
-- ============================================================
CREATE TABLE homework (
    homework_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    section_id    INT NOT NULL,
    subject_id    INT NOT NULL,
    teacher_id    BIGINT NOT NULL,
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    attachment_path VARCHAR(255),
    assigned_date DATE NOT NULL,
    due_date      DATE NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Future: student homework submissions
CREATE TABLE homework_submissions (
    submission_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    homework_id    BIGINT NOT NULL,
    student_id     BIGINT NOT NULL,
    file_path      VARCHAR(255),
    submitted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status         ENUM('submitted','late','graded') DEFAULT 'submitted',
    grade_remarks  VARCHAR(255),
    UNIQUE KEY uq_homework_student (homework_id, student_id),
    FOREIGN KEY (homework_id) REFERENCES homework(homework_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 10. TIMETABLE
-- ============================================================
CREATE TABLE timetable (
    timetable_id  INT AUTO_INCREMENT PRIMARY KEY,
    section_id    INT NOT NULL,
    subject_id    INT NOT NULL,
    teacher_id    BIGINT NOT NULL,
    day_of_week   ENUM('monday','tuesday','wednesday','thursday','friday','saturday') NOT NULL,
    start_time    TIME NOT NULL,
    end_time      TIME NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 11. FEES
-- ============================================================
CREATE TABLE fee_structures (
    fee_structure_id INT AUTO_INCREMENT PRIMARY KEY,
    class_id      INT NOT NULL,
    fee_title     VARCHAR(100) NOT NULL,     -- Tuition Fee, Admission Fee
    amount        DECIMAL(10,2) NOT NULL,
    frequency     ENUM('monthly','quarterly','annual','one_time') DEFAULT 'monthly',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE fee_challans (
    challan_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id    BIGINT NOT NULL,
    fee_structure_id INT NOT NULL,
    challan_no    VARCHAR(40) UNIQUE NOT NULL,
    month_year    VARCHAR(20),        -- e.g. "August 2026"
    amount        DECIMAL(10,2) NOT NULL,
    fine_amount   DECIMAL(10,2) DEFAULT 0,
    due_date      DATE NOT NULL,
    paid_date     DATE DEFAULT NULL,
    status        ENUM('unpaid','paid','overdue','cancelled') DEFAULT 'unpaid',
    payment_method VARCHAR(50),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (fee_structure_id) REFERENCES fee_structures(fee_structure_id)
) ENGINE=InnoDB;

CREATE INDEX idx_fee_status ON fee_challans(status);

-- ============================================================
-- 12. NOTICES
-- ============================================================
CREATE TABLE notices (
    notice_id     INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    posted_by     BIGINT NOT NULL,          -- user_id
    audience      ENUM('all','teachers','students','parents','specific_class') DEFAULT 'all',
    class_id      INT DEFAULT NULL,
    attachment_path VARCHAR(255),
    publish_date  DATE NOT NULL,
    expiry_date   DATE DEFAULT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (posted_by) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- 13. NOTIFICATIONS (real-time, per-user)
-- ============================================================
CREATE TABLE notifications (
    notification_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    title         VARCHAR(200) NOT NULL,
    message       VARCHAR(500),
    type          ENUM('homework','attendance','exam','fee','notice','general') DEFAULT 'general',
    reference_id  BIGINT DEFAULT NULL,     -- id of related record (homework_id, exam_id, etc.)
    is_read       BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);

-- ============================================================
-- 14. SCHOOL EVENTS & GALLERY (for public website)
-- ============================================================
CREATE TABLE school_events (
    event_id      INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    event_date    DATE NOT NULL,
    image_path    VARCHAR(255),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE gallery (
    gallery_id    INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(150),
    image_path    VARCHAR(255) NOT NULL,
    category      VARCHAR(80),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE testimonials (
    testimonial_id INT AUTO_INCREMENT PRIMARY KEY,
    author_name   VARCHAR(150) NOT NULL,
    role          VARCHAR(100),          -- Parent, Alumni, Student
    message       TEXT NOT NULL,
    image_path    VARCHAR(255),
    is_published  BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 15. AUDIT / ACTIVITY LOG (security requirement)
-- ============================================================
CREATE TABLE activity_logs (
    log_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT DEFAULT NULL,
    action        VARCHAR(150) NOT NULL,
    ip_address    VARCHAR(45),
    details        VARCHAR(500),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;
