import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
MYSQLDATABASE = os.environ.get("MYSQLDATABASE")
MYSQLHOST = os.environ.get("MYSQLHOST")
MYSQLPASSWORD = os.environ.get("MYSQLPASSWORD")
MYSQLPORT = os.environ.get("MYSQLPORT")
MYSQLUSER = os.environ.get("MYSQLUSER")


# Create config dictionary


def connection():
    config = {
        "user": MYSQLUSER,
        "password": MYSQLPASSWORD,
        "host": MYSQLHOST,
        "database": MYSQLDATABASE,
        "port": MYSQLPORT,
        "raise_on_warnings": False,
    }

    return mysql.connector.connect(**config)


def initDB():
    conn = connection()
    cursor = conn.cursor()

    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
      );
    """
    )

    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS projects (
        project_id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        created_at VARCHAR(30) NOT NULL,
        deadline VARCHAR(30) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
      );
      """
    )

    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS tasks (
        task_id VARCHAR(36) PRIMARY KEY,
        project_id VARCHAR(36) NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date VARCHAR(30) NOT NULL,
        priority INT NOT NULL,
        completed INT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
      );
      """
    )

    conn.commit()
    cursor.close()
    conn.close()
