-- Remove duplicate books from book_db, keeping the lowest book_id for each (title, author_name)
DELETE FROM book_db
WHERE book_id NOT IN (
    SELECT MIN(book_id) FROM book_db GROUP BY title, author_name
);
