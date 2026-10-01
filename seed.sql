-- Online Examination and Result Management System Seed Data
USE online_exam_db;

-- 1. Departments
INSERT INTO departments (id, dept_name, dept_code) VALUES
(1, 'Computer Science', 'CS'),
(2, 'Software Engineering', 'SE'),
(3, 'Information Technology', 'IT');

-- 2. Courses
INSERT INTO courses (id, dept_id, course_code, course_name, description) VALUES
(1, 1, 'CS101', 'Programming Fundamentals', 'Introduction to procedural and object-oriented programming concepts.'),
(2, 1, 'CS201', 'Data Structures & Algorithms', 'Arrays, linked lists, trees, graphs, sorting, and searching algorithms.'),
(3, 2, 'SE301', 'Software Testing & QA', 'Software testing methodologies, black-box, white-box, and Selenium automation.'),
(4, 2, 'SE302', 'Modern Web Development', 'Building dynamic web apps with HTML, CSS, JavaScript, and REST APIs.'),
(5, 3, 'IT202', 'Database Management Systems', 'Relational database design, SQL queries, normalization, and ACID properties.'),
(6, 3, 'IT401', 'Cybersecurity Essentials', 'Network security, encryption, authentication, OWASP top 10 vulnerabilities.');

-- 3. Users (Admins and Students)
-- Note: Passwords are Werkzeug hashes.
-- 'Admin@123' -> pbkdf2:sha256:600000$vQ3X6Z9L$605a96860bc87db3bb7b98ec342b5cce87b322c317e0821b0eec86ad60c1d6ff
-- 'Admin@456' -> pbkdf2:sha256:600000$kP7Y2M1W$724b1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab
-- 'Student@123' -> pbkdf2:sha256:600000$sT9U8V7W$11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff

INSERT INTO users (id, full_name, student_id, email, phone, username, password, status, role, dept_id, course_id, dob) VALUES
(1, 'System Administrator', NULL, 'admin@exam.com', '9876543210', 'admin', 'scrypt:32768:8:1$yS3T0X4U$148d4dbbd4770248ad68579cfeb159ef4e877c862bc2b545d7f3ff7c24458df8a2133bfbf7cbf7eefbf1bdcaefbd9bc0ecf0f29ce9716e257ebc8dbecb0c4bf4', 'active', 'admin', 2, 3, '1985-05-15'),
(2, 'Academic Controller', NULL, 'subadmin@exam.com', '9876543211', 'subadmin', 'scrypt:32768:8:1$yS3T0X4U$148d4dbbd4770248ad68579cfeb159ef4e877c862bc2b545d7f3ff7c24458df8a2133bfbf7cbf7eefbf1bdcaefbd9bc0ecf0f29ce9716e257ebc8dbecb0c4bf4', 'active', 'admin', 1, 1, '1988-08-20'),

(3, 'Alice Smith', 'STU001', 'alice@student.com', '9812345671', 'alice1', 'scrypt:32768:8:1$yS3T0X4U$148d4dbbd4770248ad68579cfeb159ef4e877c862bc2b545d7f3ff7c24458df8a2133bfbf7cbf7eefbf1bdcaefbd9bc0ecf0f29ce9716e257ebc8dbecb0c4bf4', 'active', 'student', 2, 3, '2001-04-10'),
(4, 'Bob Johnson', 'STU002', 'bob@student.com', '9812345672', 'bob2', 'scrypt:32768:8:1$yS3T0X4U$148d4dbbd4770248ad68579cfeb159ef4e877c862bc2b545d7f3ff7c24458df8a2133bfbf7cbf7eefbf1bdcaefbd9bc0ecf0f29ce9716e257ebc8dbecb0c4bf4', 'active', 'student', 2, 3, '2000-09-15'),
(5, 'Charlie Brown', 'STU003', 'charlie@student.com', '9812345673', 'charlie3', 'scrypt:32768:8:1$yS3T0X4U$148d4dbbd4770248ad68579cfeb159ef4e877c862bc2b545d7f3ff7c24458df8a2133bfbf7cbf7eefbf1bdcaefbd9bc0ecf0f29ce9716e257ebc8dbecb0c4bf4', 'blocked', 'student', 3, 5, '2002-01-22'),
(6, 'Diana Prince', 'STU004', 'diana@student.com', '9812345674', 'diana4', 'scrypt:32768:8:1$yS3T0X4U$148d4dbbd4770248ad68579cfeb159ef4e877c862bc2b545d7f3ff7c24458df8a2133bfbf7cbf7eefbf1bdcaefbd9bc0ecf0f29ce9716e257ebc8dbecb0c4bf4', 'active', 'student', 1, 1, '2001-11-05'),
(7, 'Edward Elric', 'STU005', 'edward@student.com', '9812345675', 'edward5', 'scrypt:32768:8:1$yS3T0X4U$148d4dbbd4770248ad68579cfeb159ef4e877c862bc2b545d7f3ff7c24458df8a2133bfbf7cbf7eefbf1bdcaefbd9bc0ecf0f29ce9716e257ebc8dbecb0c4bf4', 'active', 'student', 1, 2, '2000-03-30');

-- 4. Exams
INSERT INTO exams (id, course_id, title, description, duration_minutes, total_marks, pass_percentage, is_published, created_by) VALUES
(1, 3, 'Software Testing Fundamentals', 'Comprehensive quiz covering equivalence partitioning, boundary value analysis, and black-box testing techniques.', 15, 10, 40.00, 1, 1),
(2, 5, 'Database Systems Midterm', 'Exam testing relational database concepts, SQL joins, normalization, and ACID properties.', 20, 10, 40.00, 1, 1),
(3, 6, 'Advanced Cybersecurity Concepts', 'Assessment covering web security, XSS, SQL injection, and authorization controls.', 30, 10, 40.00, 0, 2);

-- 5. Questions for Exam 1 (Software Testing Fundamentals)
INSERT INTO questions (id, exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks, difficulty_level, topic) VALUES
(1, 1, 'Which testing technique divides input domain into classes where test cases can be derived?', 'Boundary Value Analysis', 'Equivalence Partitioning', 'State Transition Testing', 'Decision Table Testing', 'B', 1, 'EASY', 'Black-Box Testing'),
(2, 1, 'In Boundary Value Analysis, if the valid range is 1 to 100, which values should be tested?', '0, 1, 100, 101', '50, 60, 70', '-1, 0, 50, 150', '1, 50, 100', 'A', 1, 'MEDIUM', 'Boundary Value Analysis'),
(3, 1, 'What is the primary goal of White-Box Testing?', 'Testing user interface responsiveness', 'Testing internal code structures and logic paths', 'Testing system integration with external APIs', 'Testing acceptance by end users', 'B', 1, 'EASY', 'White-Box Testing'),
(4, 1, 'Cyclomatic Complexity measures which attribute of software code?', 'Execution speed of the algorithm', 'Number of lines of code', 'Number of linearly independent paths through code', 'Memory consumption during runtime', 'C', 1, 'HARD', 'Cyclomatic Complexity'),
(5, 1, 'Which tool is used for automated browser UI testing in Python?', 'Pytest-Django', 'Selenium WebDriver', 'Requests', 'BeautifulSoup', 'B', 1, 'EASY', 'Selenium Automation'),
(6, 1, 'What does POM stand for in test automation design patterns?', 'Process Object Model', 'Page Object Model', 'Python Object Mapper', 'Program Output Module', 'B', 1, 'EASY', 'Page Object Model'),
(7, 1, 'Regression testing is primarily performed to:', 'Verify that new code changes did not break existing features', 'Check system performance under heavy load', 'Ensure security credentials are encrypted', 'Validate initial project requirements', 'A', 1, 'MEDIUM', 'Regression Testing'),
(8, 1, 'Which HTTP response status code indicates an Unauthorized access request?', '200 OK', '404 Not Found', '401 Unauthorized', '500 Internal Server Error', 'C', 1, 'EASY', 'API Security'),
(9, 1, 'In decision table testing, a table with 3 binary conditions will have how many combinations?', '3 combinations', '6 combinations', '8 combinations', '9 combinations', 'C', 1, 'MEDIUM', 'Decision Table'),
(10, 1, 'What is a defect report severity rating?', 'The business priority assigned by product manager', 'The technical impact of the defect on system operation', 'The time taken to fix the bug', 'The number of lines of code affected', 'B', 1, 'EASY', 'Defect Management');

-- 6. Questions for Exam 2 (Database Systems Midterm)
INSERT INTO questions (id, exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks, difficulty_level, topic) VALUES
(11, 2, 'Which SQL keyword is used to prevent SQL Injection when combined with prepared statements?', 'Parameterized Placeholders (?)', 'CONCAT()', 'EXECUTE IMMEDIATE', 'INTO OUTFILE', 'A', 1, 'EASY', 'Database Security'),
(12, 2, 'What does ACID stand for in database transactions?', 'Atomicity, Consistency, Isolation, Durability', 'Access, Control, Integrity, Data', 'Action, Command, Index, Delete', 'Aggregate, Count, Insert, Distinct', 'A', 1, 'EASY', 'Transactions'),
(13, 2, 'Which normal form eliminates partial key dependencies?', '1NF', '2NF', '3NF', 'BCNF', 'B', 1, 'MEDIUM', 'Normalization'),
(14, 2, 'A Primary Key constraint automatically enforces:', 'Foreign key relationship', 'Unique and NOT NULL constraints', 'Auto incrementing values only', 'Cascade deletion', 'B', 1, 'EASY', 'Constraints'),
(15, 2, 'Which JOIN returns all records from the left table and matched records from the right table?', 'INNER JOIN', 'RIGHT JOIN', 'LEFT JOIN', 'FULL OUTER JOIN', 'C', 1, 'EASY', 'SQL Joins'),
(16, 2, 'What is an Index in MySQL used for?', 'Compressing table storage space', 'Speeding up data retrieval operations', 'Encrypting sensitive passwords', 'Enforcing cascade deletes', 'B', 1, 'MEDIUM', 'Indexes'),
(17, 2, 'Which clause is used to filter group results after GROUP BY?', 'WHERE', 'HAVING', 'ORDER BY', 'LIMIT', 'B', 1, 'EASY', 'SQL Syntax'),
(18, 2, 'What type of key links two tables together in a relational schema?', 'Primary Key', 'Candidate Key', 'Foreign Key', 'Composite Key', 'C', 1, 'EASY', 'Relational Model'),
(19, 2, 'Which SQL command is used to modify existing rows in a table?', 'ALTER', 'UPDATE', 'MODIFY', 'INSERT', 'B', 1, 'EASY', 'DML'),
(20, 2, 'In MySQL, what is the default storage engine supporting transactions?', 'MyISAM', 'InnoDB', 'Memory', 'CSV', 'B', 1, 'MEDIUM', 'Storage Engines');

-- 7. Sample Historical Result (Student 3 - Alice Smith took Exam 1)
INSERT INTO results (id, student_id, exam_id, start_time, submit_time, score, total_possible_score, percentage, status, total_correct, total_wrong, total_unanswered, is_submitted) VALUES
(1, 3, 1, '2026-09-28 10:00:00', '2026-09-28 10:12:30', 8.00, 10.00, 80.00, 'PASS', 8, 2, 0, 1);
