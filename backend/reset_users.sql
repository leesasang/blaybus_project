UPDATE users
SET hashed_password = '$2b$12$Zgxj.qKv0JebIaJ2a2OTgOHSqUrYOwMW6SCqZBnpUN9usH63pdZpS'
WHERE email IN ('test1@example.com', 'test2@example.com');
