from flask import Flask, request, jsonify
import requests
import json
import os
import re
import time
import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)


# MySQL 数据库配置 - 从环境变量读取
def get_mysql_config():
    """从环境变量获取MySQL配置"""
    required_vars = ["MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

    return {
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
    }


MYSQL_CONFIG = get_mysql_config()

db_conn = None


def get_db():
    global db_conn
    if db_conn is None:
        db_conn = pymysql.connect(**MYSQL_CONFIG)
    return db_conn


def close_db():
    global db_conn
    if db_conn:
        db_conn.close()
        db_conn = None


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            user_alias VARCHAR(255) NOT NULL,
            msg TEXT NOT NULL,
            attribute TEXT,
            send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type VARCHAR(50) NOT NULL
        )
    """
    )
    conn.commit()


def main():
    init_db()


@app.route("/add", methods=["POST"])
def add():
    data = request.get_data(as_text=True)
    print(data)

    return {"status": "ok"}, 200


if __name__ == "__main__":
    try:
        main()
        app.run(debug=True)
    except KeyboardInterrupt:
        print("正在退出...")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        close_db()
        print("数据库连接已关闭")
