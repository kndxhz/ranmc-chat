# RanMC Chat

一个基于Flask的聊天应用程序。

## 环境配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 文件为 `.env` 并填入真实的配置信息：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入您的MySQL数据库配置：

```
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name
MYSQL_CHARSET=utf8mb4
```

### 3. 运行应用

```bash
python main.py
```

## 安全注意事项

- `.env` 文件包含敏感信息，已添加到 `.gitignore` 中，不会被提交到版本控制系统
- 请确保在生产环境中妥善保管环境变量
- 建议定期更换数据库密码

## 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| MYSQL_HOST | MySQL服务器地址 | localhost | 是 |
| MYSQL_PORT | MySQL端口 | 3306 | 否 |
| MYSQL_USER | MySQL用户名 | - | 是 |
| MYSQL_PASSWORD | MySQL密码 | - | 是 |
| MYSQL_DATABASE | 数据库名称 | - | 是 |
| MYSQL_CHARSET | 字符编码 | utf8mb4 | 否 |