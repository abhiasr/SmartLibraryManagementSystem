# User activity log
CREATE TABLE IF NOT EXISTS user_activity (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_db(member_id) ON DELETE CASCADE
);
-- Notifications table for in-app notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES member_db(member_id) ON DELETE CASCADE
);
-- This schema is compatible with both SQLite and PostgreSQL.
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

CREATE TABLE IF NOT EXISTS wishlist (
    wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    added_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES member_db(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_db(book_id) ON DELETE CASCADE,
    UNIQUE (member_id, book_id)
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    reserved_date TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active', -- active, fulfilled, cancelled
    FOREIGN KEY (member_id) REFERENCES member_db(member_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_db(book_id) ON DELETE CASCADE
);

-- New Chatbot Table
CREATE TABLE IF NOT EXISTS chatbot_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,
    response TEXT NOT NULL
);

-- Seed some initial data for the chatbot
INSERT OR IGNORE INTO chatbot_responses (keyword, response) VALUES
('hours', 'Our library is open from 9:00 AM to 8:00 PM, Monday to Saturday. We are closed on Sundays.'),
('fine', 'The fine for an overdue book is ₹5 per day.'),
('renew', 'You can renew a book by visiting the library counter. Online renewal is not yet available.'),
('borrow', 'You can borrow up to 3 books at a time.'),
('thank you', 'You''re welcome! Let me know if you need anything else.'),
('hello', 'Hello there! How can I assist you today?'),
('hi', 'Hi! What can I help you with?'),
('bye', 'Goodbye! Have a great day!'),
('good morning', 'Good morning! Wishing you a productive day at the library.'),
('good afternoon', 'Good afternoon! How can I help you today?'),
('good evening', 'Good evening! The library is open until 8:00 PM.'),
('welcome', 'Welcome to our library! Let me know if you need any assistance.'),
('who are you', 'I am your library assistant chatbot.'),
('help', 'I can answer questions about library hours, fines, borrowing, and more.'),
('books', 'We have a wide range of books, including self-development titles.'),
('self development', 'Looking for self-development books? We have over 100 titles available!'),
('recommend', 'I recommend "Atomic Habits" and "The 7 Habits of Highly Effective People" for self-development.'),
('thanks', 'Happy to help!'),
('thank you so much', 'You''re very welcome!'),
('library', 'This is the library chatbot. How can I assist you?');

-- Seed 100 self-development books
INSERT OR IGNORE INTO book_db (title, category, publisher, year, edition, total_stock, author_name) VALUES
('Atomic Habits', 'Self Development', 'Penguin', '2018', '1st', 0, 'James Clear'),
('The 7 Habits of Highly Effective People', 'Self Development', 'Free Press', '1989', '1st', 0, 'Stephen R. Covey'),
('Think and Grow Rich', 'Self Development', 'The Ralston Society', '1937', '1st', 0, 'Napoleon Hill'),
('Awaken the Giant Within', 'Self Development', 'Simon & Schuster', '1991', '1st', 10, 'Tony Robbins'),
('Deep Work', 'Self Development', 'Grand Central Publishing', '2016', '1st', 0, 'Cal Newport'),
('Mindset', 'Self Development', 'Random House', '2006', '1st', 10, 'Carol S. Dweck'),
('The Power of Now', 'Self Development', 'New World Library', '1997', '1st', 10, 'Eckhart Tolle'),
('Make Your Bed', 'Self Development', 'Grand Central Publishing', '2017', '1st', 10, 'William H. McRaven'),
('The Miracle Morning', 'Self Development', 'Hal Elrod', '2012', '1st', 0, 'Hal Elrod'),
('Grit', 'Self Development', 'Scribner', '2016', '1st', 10, 'Angela Duckworth'),
('Drive', 'Self Development', 'Riverhead Books', '2009', '1st', 10, 'Daniel H. Pink'),
('The Four Agreements', 'Self Development', 'Amber-Allen Publishing', '1997', '1st', 0, 'Don Miguel Ruiz'),
('The Subtle Art of Not Giving a F*ck', 'Self Development', 'HarperOne', '2016', '1st', 0, 'Mark Manson'),
('Can''t Hurt Me', 'Self Development', 'Lioncrest Publishing', '2018', '1st', 0, 'David Goggins'),
('The Alchemist', 'Self Development', 'HarperCollins', '1988', '1st', 0, 'Paulo Coelho'),
('The Magic of Thinking Big', 'Self Development', 'Simon & Schuster', '1959', '1st', 10, 'David J. Schwartz'),
('The One Thing', 'Self Development', 'Bard Press', '2013', '1st', 0, 'Gary Keller'),
('Start With Why', 'Self Development', 'Portfolio', '2009', '1st', 10, 'Simon Sinek'),
('Unlimited Power', 'Self Development', 'Simon & Schuster', '1986', '1st', 10, 'Tony Robbins'),
('The Success Principles', 'Self Development', 'HarperCollins', '2005', '1st', 10, 'Jack Canfield'),
('Tools of Titans', 'Self Development', 'Houghton Mifflin Harcourt', '2016', '1st', 10, 'Tim Ferriss'),
('The Compound Effect', 'Self Development', 'Vanguard Press', '2010', '1st', 10, 'Darren Hardy'),
('Essentialism', 'Self Development', 'Crown Business', '2014', '1st', 10, 'Greg McKeown'),
('The War of Art', 'Self Development', 'Black Irish Entertainment LLC', '2002', '1st', 10, 'Steven Pressfield'),
('Eat That Frog!', 'Self Development', 'Berrett-Koehler Publishers', '2001', '1st', 10, 'Brian Tracy'),
('The Monk Who Sold His Ferrari', 'Self Development', 'HarperSanFrancisco', '1997', '1st', 10, 'Robin Sharma'),
('The Slight Edge', 'Self Development', 'Greenleaf Book Group', '2005', '1st', 0, 'Jeff Olson'),
('The Art of Happiness', 'Self Development', 'Riverhead Books', '1998', '1st', 0, 'Dalai Lama'),
('The Gifts of Imperfection', 'Self Development', 'Hazelden', '2010', '1st', 10, 'Brené Brown'),
('Daring Greatly', 'Self Development', 'Gotham Books', '2012', '1st', 0, 'Brené Brown'),
('Man''s Search for Meaning', 'Self Development', 'Beacon Press', '1946', '1st', 0, 'Viktor E. Frankl'),
('The Road Less Traveled', 'Self Development', 'Simon & Schuster', '1978', '1st', 0, 'M. Scott Peck'),
('How to Win Friends and Influence People', 'Self Development', 'Simon & Schuster', '1936', '1st', 0, 'Dale Carnegie'),
('The Happiness Advantage', 'Self Development', 'Crown Business', '2010', '1st', 0, 'Shawn Achor'),
('The 5 Second Rule', 'Self Development', 'Savage Press', '2017', '1st', 0, 'Mel Robbins'),
('The Confidence Code', 'Self Development', 'HarperBusiness', '2014', '1st', 0, 'Katty Kay'),
('The Untethered Soul', 'Self Development', 'New Harbinger Publications', '2007', '1st', 10, 'Michael A. Singer'),
('The Obstacle Is the Way', 'Self Development', 'Portfolio', '2014', '1st', 0, 'Ryan Holiday'),
('The Daily Stoic', 'Self Development', 'Portfolio', '2016', '1st', 0, 'Ryan Holiday'),
('Mastery', 'Self Development', 'Viking Adult', '2012', '1st', 10, 'Robert Greene'),
('Mindfulness for Beginners', 'Self Development', 'Sounds True', '2012', '1st', 10, 'Jon Kabat-Zinn'),
('The Power of Habit', 'Self Development', 'Random House', '2012', '1st', 0, 'Charles Duhigg'),
('The Courage to Be Disliked', 'Self Development', 'Allen & Unwin', '2013', '1st', 0, 'Ichiro Kishimi'),
('The Science of Getting Rich', 'Self Development', 'Elizabeth Towne', '1910', '1st', 10, 'Wallace D. Wattles'),
('The Motivation Manifesto', 'Self Development', 'Hay House', '2014', '1st', 0, 'Brendon Burchard'),
('The Success Equation', 'Self Development', 'Harvard Business Review Press', '2012', '1st', 0, 'Michael J. Mauboussin'),
('The Art of War', 'Self Development', 'Oxford University Press', '5th century BC', '1st', 10, 'Sun Tzu'),
('The Art of Thinking Clearly', 'Self Development', 'HarperCollins', '2013', '1st', 0, 'Rolf Dobelli'),
('The Magic of Believing', 'Self Development', 'Prentice Hall', '1948', '1st', 0, 'Claude M. Bristol'),
('The 80/20 Principle', 'Self Development', 'Nicholas Brealey Publishing', '1997', '1st', 10, 'Richard Koch'),
('The Power of Positive Thinking', 'Self Development', 'Prentice Hall', '1952', '1st', 10, 'Norman Vincent Peale'),
('The Richest Man in Babylon', 'Self Development', 'Penguin', '1926', '1st', 0, 'George S. Clason'),
('The Miracle Morning for Entrepreneurs', 'Self Development', 'Hal Elrod', '2016', '1st', 0, 'Hal Elrod'),
('The 12 Week Year', 'Self Development', 'Wiley', '2013', '1st', 0, 'Brian P. Moran'),
('The Productivity Project', 'Self Development', 'Crown Business', '2016', '1st', 0, 'Chris Bailey'),
('The Now Habit', 'Self Development', 'TarcherPerigee', '1988', '1st', 10, 'Neil Fiore'),
('The Slight Edge', 'Self Development', 'Greenleaf Book Group', '2011', '2nd', 0, 'Jeff Olson'),
('The Art of Learning', 'Self Development', 'Free Press', '2007', '1st', 10, 'Josh Waitzkin'),
('The Power of Intention', 'Self Development', 'Hay House', '2004', '1st', 10, 'Wayne W. Dyer'),
('The Motivation Myth', 'Self Development', 'Portfolio', '2018', '1st', 0, 'Jeff Haden'),
('The Power of Your Subconscious Mind', 'Self Development', 'Prentice Hall', '1963', '1st', 10, 'Joseph Murphy'),
('The Slight Edge', 'Self Development', 'Greenleaf Book Group', '2015', '3rd', 0, 'Jeff Olson'),
('The Art of Possibility', 'Self Development', 'Harvard Business Review Press', '2000', '1st', 0, 'Rosamund Stone Zander'),
('The Power of Self-Discipline', 'Self Development', 'Berrett-Koehler Publishers', '2012', '1st', 0, 'Brian Tracy'),
('The Power of Focus', 'Self Development', 'Grand Central Publishing', '2000', '1st', 0, 'Jack Canfield'),
('The Power of Less', 'Self Development', 'Hyperion', '2009', '1st', 0, 'Leo Babauta'),
('The Power of Full Engagement', 'Self Development', 'Free Press', '2003', '1st', 0, 'Jim Loehr'),
('The Power of Consistency', 'Self Development', 'Wiley', '2013', '1st', 0, 'Weldon Long'),
('The Power of Meaning', 'Self Development', 'Crown', '2017', '1st', 0, 'Emily Esfahani Smith'),
('The Power of Vulnerability', 'Self Development', 'Sounds True', '2013', '1st', 0, 'Brené Brown'),
('The Power of Intention', 'Self Development', 'Hay House', '2004', '2nd', 0, 'Wayne W. Dyer'),
('The Power of Awareness', 'Self Development', 'Hay House', '1952', '1st', 0, 'Neville Goddard'),
('The Power of Your Potential', 'Self Development', 'FaithWords', '2018', '1st', 0, 'John C. Maxwell'),
('The Power of Discipline', 'Self Development', 'Independently Published', '2020', '1st', 1, 'Daniel Walter'),
('The Power of Mindfulness', 'Self Development', 'Independently Published', '2019', '1st', 0, 'Emma J. Williams'),
('The Power of Self-Confidence', 'Self Development', 'Berrett-Koehler Publishers', '2012', '1st', 1, 'Brian Tracy'),
('The Power of Positive Leadership', 'Self Development', 'Wiley', '2017', '1st', 10, 'Jon Gordon'),
('The Power of Intention', 'Self Development', 'Hay House', '2004', '3rd', 10, 'Wayne W. Dyer'),
('The Power of Your Mind', 'Self Development', 'Independently Published', '2018', '1st', 10, 'Chris Oyakhilome'),
('The Power of Focus', 'Self Development', 'Grand Central Publishing', '2000', '2nd', 1, 'Jack Canfield'),
('The Power of Less', 'Self Development', 'Hyperion', '2009', '2nd', 1, 'Leo Babauta'),
('The Power of Full Engagement', 'Self Development', 'Free Press', '2003', '2nd', 1, 'Jim Loehr'),
('The Power of Consistency', 'Self Development', 'Wiley', '2013', '2nd', 1, 'Weldon Long'),
('The Power of Meaning', 'Self Development', 'Crown', '2017', '2nd', 0, 'Emily Esfahani Smith'),
('The Power of Vulnerability', 'Self Development', 'Sounds True', '2013', '2nd', 1, 'Brené Brown'),
('The Power of Awareness', 'Self Development', 'Hay House', '1952', '2nd', 0, 'Neville Goddard'),
('The Power of Your Potential', 'Self Development', 'FaithWords', '2018', '2nd', 10, 'John C. Maxwell'),
('The Power of Discipline', 'Self Development', 'Independently Published', '2020', '2nd', 1, 'Daniel Walter'),
('The Power of Mindfulness', 'Self Development', 'Independently Published', '2019', '2nd', 1, 'Emma J. Williams'),
('The Power of Self-Confidence', 'Self Development', 'Berrett-Koehler Publishers', '2012', '2nd', 10, 'Brian Tracy'),
('The Power of Positive Leadership', 'Self Development', 'Wiley', '2017', '2nd', 0, 'Jon Gordon'),
('The Power of Intention', 'Self Development', 'Hay House', '2004', '4th', 10, 'Wayne W. Dyer'),
('The Power of Your Mind', 'Self Development', 'Independently Published', '2018', '2nd', 10, 'Chris Oyakhilome'),
('The Power of Focus', 'Self Development', 'Grand Central Publishing', '2000', '3rd', 10, 'Jack Canfield'),
('The Power of Less', 'Self Development', 'Hyperion', '2009', '3rd', 0, 'Leo Babauta'),
('The Power of Full Engagement', 'Self Development', 'Free Press', '2003', '3rd', 0, 'Jim Loehr'),
('The Power of Consistency', 'Self Development', 'Wiley', '2013', '3rd', 0, 'Weldon Long'),
('The Power of Meaning', 'Self Development', 'Crown', '2017', '3rd', 10, 'Emily Esfahani Smith'),
('The Power of Vulnerability', 'Self Development', 'Sounds True', '2013', '3rd', 10, 'Brené Brown');


