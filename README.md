# dameng-mcp-server
达梦8数据库的MCP服务

## 项目简介

`dameng-mcp-server` 是一个基于 MCP (Model Context Protocol) 协议的达梦8数据库服务，提供了与达梦数据库交互的能力，支持执行SQL查询、列出数据库表资源和读取表内容等功能。

## 功能特性

- 执行SQL查询：支持在达梦数据库上执行SQL语句并返回结果
- 列出数据库表：将数据库表作为资源列出
- 读取表内容：支持读取表的内容数据
- 基于MCP协议：通过MCP协议与客户端进行通信
- 环境变量配置：支持通过环境变量配置数据库连接信息

## 项目结构

```
dameng-mcp-server/
├── dameng/
│   ├── __init__.py    # 包初始化文件，提供main入口
│   ├── client.py      # MCP客户端实现
│   └── server.py      # MCP服务器实现
└── README.md          # 项目说明文档
```

## 依赖要求

- Python 3.7+
- dmPython（达梦数据库驱动）
- mcp（MCP协议库）
- pydantic
- openai（客户端使用）
- dotenv（加载环境变量）

## 安装方法

1. 克隆项目到本地

```bash
git clone <repository-url>
cd dameng-mcp-server
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量配置

在项目根目录创建 `.env` 文件，配置以下环境变量：

```env
# 数据库连接信息
DAMENG_USER=SYSDBA        # 数据库用户名
DAMENG_PASSWORD=SYSDBA    # 数据库密码
DAMENG_HOST=localhost     # 数据库主机
DAMENG_DATABASE=IDP_JH    # 数据库名

# OpenAI API配置（客户端使用）
DASHSCOPE_API_KEY=<your-api-key>  # OpenAI API Key
BASE_URL=<api-base-url>           # API基础URL
MODEL=<model-name>                # 使用的模型名称
```

## 使用方法

### 启动服务器

```bash
python -m dameng.server
```

### 运行客户端

```bash
python -m dameng.client
```

## 示例

### 执行SQL查询

客户端启动后，可以输入SQL查询语句，例如：

```
你: execute_sql {"query": "SELECT * FROM TABLE_NAME LIMIT 10"}
```

### 列出数据库表

服务器会自动列出数据库中的所有表作为资源。

## 注意事项

- 确保已安装达梦数据库驱动 `dmPython`
- 确保数据库服务已启动并可访问
- 配置正确的环境变量信息

## 许可证

MIT License

## 更新日志

- 初始版本：实现基本的MCP服务功能，支持执行SQL查询、列出表资源和读取表内容
