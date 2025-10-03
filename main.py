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
            send_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()


def main():
    init_db()


def save_message(username, user_alias, msg, attribute):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO messages (username, user_alias, msg, attribute)
        VALUES (%s, %s, %s, %s)
    """,
        (username, user_alias, msg, attribute),
    )
    conn.commit()


@app.route("/")
def index():
    return "<a href='https://github.com/kndxhz/ranmc-chat'>本项目已在github开源,没必要试探了</a>"


@app.route("/getdata")
def getdata():
    username = request.args.get("id", "")
    msg_pattern = request.args.get("filter", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM messages"
    params = []
    conditions = []

    if username:
        conditions.append("username = %s")
        params.append(username)
    if start_date:
        conditions.append("UNIX_TIMESTAMP(send_time) >= %s")
        params.append(int(start_date))
    if end_date:
        conditions.append("UNIX_TIMESTAMP(send_time) <= %s")
        params.append(int(end_date))
    if msg_pattern:
        conditions.append("msg REGEXP %s")
        params.append(msg_pattern)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    print(query, params)
    cursor.execute(query, params)
    rows = cursor.fetchall()

    result = [
        {
            "username": row[1],
            "user_alias": row[2],
            "message": row[3],
            "attribute": row[4] if row[4] else "",
            "send_time": row[5].timestamp(),
        }
        for row in rows
    ]

    return jsonify({"status": "ok", "chats": result}), 200


@app.route("/getid")
def getid():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM messages;")
    usernames = [row[0] for row in cursor.fetchall()]
    return {"status": "ok", "ids": usernames}, 200


@app.route("/add", methods=["POST"])
def add():
    data = request.get_data(as_text=True)
    data_list = data.split("\r\n")
    print(data_list)
    # ['[弦月柚子] <youzi> 展示物品[14伤]', '[装备强化] 6 / 6', '物理伤害: 2', '真实伤害: 4', '真实伤害: 3', '流血几率: 3', '物理伤害: 5', '虚弱几率: 4']

    match = re.search(r"\[(.*?)\] <(.*?)>(.*)", data_list[0])
    user_alias = match.group(1) if match else ""
    username = match.group(2) if match else ""
    msg = match.group(3).strip() if match else ""
    attribute = "|".join(data_list[1:]) if len(data_list) > 1 else ""
    send_time = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    print(
        f"头衔: {user_alias}, 用户名: {username}, 消息: {msg}, 属性: {attribute}, 发送时间: {send_time}"
    )
    save_message(username, user_alias, msg, attribute)

    return {"status": "ok"}, 200


if __name__ == "__main__":
    try:
        main()
        app.run(debug=True)
    except SystemExit:
        print("系统退出")
    except KeyboardInterrupt:
        print("正在退出...")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        close_db()
        print("数据库连接已关闭")
