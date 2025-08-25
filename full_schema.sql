-- Combined Library Database Schema and Utility SQL
-- ===============================================

-- 1. Main Tables
-- --------------

-- Members
CREATE TABLE IF NOT EXISTS member_db (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    address TEXT NOT NULL,
    mob_no TEXT UNIQUE NOT NULL,
    email_id TEXT NOT NULL,
    password BLOB NOT NULL,
    role TEXT NOT NULL,
    profile_pic TEXT
);

-- Books
CREATE TABLE IF NOT EXISTS book_db (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT,
    publisher TEXT,
    year TEXT,
    edition TEXT,
    total_stock INTEGER NOT NULL,
    author_name TEXT,
    read_count INTEGER DEFAULT 0
);

-- Issued Books
CREATE TABLE IF NOT EXISTS issued_books (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    return_date TEXT,
    FOREIGN KEY (member_id) REFERENCES member_db(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_db(book_id) ON DELETE CASCADE
);

-- Fines
CREATE TABLE IF NOT EXISTS fines (
    fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    fine_amount REAL NOT NULL,
    days_late INTEGER NOT NULL,
    status TEXT NOT NULL,
    fine_date TEXT NOT NULL,
    payment_date TEXT,
    FOREIGN KEY (issue_id) REFERENCES issued_books(issue_id) ON DELETE CASCADE
);

-- Wishlist
CREATE TABLE IF NOT EXISTS wishlist (
    wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    added_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES member_db(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_db(book_id) ON DELETE CASCADE,
    UNIQUE (member_id, book_id)
);

-- Reservations
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    reserved_date TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active', -- active, fulfilled, cancelled
    FOREIGN KEY (member_id) REFERENCES member_db(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_db(book_id) ON DELETE CASCADE
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_db(member_id) ON DELETE CASCADE
);

-- User Activity Log
CREATE TABLE IF NOT EXISTS user_activity (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_db(member_id) ON DELETE CASCADE
);

-- Chatbot Responses
CREATE TABLE IF NOT EXISTS chatbot_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,
    response TEXT NOT NULL
);

-- 2. Alter Table Statements (if needed)
-- -------------------------------------
-- (Already included profile_pic in member_db)

-- 3. Utility/Data Scripts
-- ----------------------

-- Remove duplicate books from book_db, keeping the lowest book_id for each (title, author_name)
-- (Run only if needed)
-- DELETE FROM book_db
-- WHERE book_id NOT IN (
--     SELECT MIN(book_id) FROM book_db GROUP BY title, author_name
-- );

-- Insert a test fine for demonstration
-- (Run only if needed)
-- INSERT INTO fines (issue_id, fine_amount, days_late, status, fine_date)
-- VALUES (1, 50.0, 10, 'Pending', DATE('now'));

-- 4. Seed Data
-- ------------
INSERT OR IGNORE INTO chatbot_responses (keyword, response) VALUES
('hours', 'Our library is open from 9:00 AM to 8:00 PM, Monday to Saturday. We are closed on Sundays.'),
('fine', 'The fine for an overdue book is ₹5 per day.'),
('renew', 'You can renew a book by visiting the library counter. Online renewal is not yet available.'),
('borrow', 'You can borrow up to 3 books at a time.'),
('thank you', 'You''re welcome! Let me know if you need anything else.'),
('hello', 'Hello there! How can I assist you today?');
