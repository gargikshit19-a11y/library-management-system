USE library_management;

INSERT INTO books (title, author, isbn, category, total_copies, available_copies) VALUES
('Database System Concepts', 'Abraham Silberschatz', '9780073523323', 'Computer Science', 5, 3),
('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 'Computer Science', 4, 2),
('Fundamentals of Database Systems', 'Ramez Elmasri', '9780133970777', 'Computer Science', 3, 1),
('Operating System Concepts', 'Abraham Silberschatz', '9781118063330', 'Computer Science', 3, 3),
('Data Structures and Algorithms', 'Alfred Aho', '9780201000238', 'Computer Science', 2, 0);

INSERT INTO members (name, email, phone, join_date) VALUES
('Alice Johnson', 'alice@example.com', '9876543210', '2025-01-15'),
('Bob Smith', 'bob@example.com', '9876543211', '2025-02-20'),
('Charlie Brown', 'charlie@example.com', '9876543212', '2025-03-10'),
('Diana Wilson', 'diana@example.com', '9876543213', '2025-04-05');

INSERT INTO loans (book_id, member_id, issue_date, due_date, return_date) VALUES
(1, 1, '2025-09-01', '2025-09-15', '2025-09-10'),
(2, 2, '2025-09-05', '2025-09-19', NULL),
(3, 3, '2025-09-10', '2025-09-24', NULL),
(5, 1, '2025-09-20', '2025-10-04', NULL);
