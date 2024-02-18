-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS tomato_db;

-- 사용자 및 권한 설정
-- %는 와일드카드로 어떤 호스트든 접속을 허용한다는 뜻(나중에 ip할당되면 변경(혹은 local))
CREATE USER IF NOT EXISTS 'my_user'@'%' IDENTIFIED BY 'my_password';
GRANT ALL PRIVILEGES ON tomato_db.* TO 'my_user'@'%';

-- 테이블 생성
USE tomato_db;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation_files (
    file_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_path VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
