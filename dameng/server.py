import asyncio
import logging
import os
import sys
from dmPython import connect
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dameng_mcp_server")

def get_db_config():
    """Get database configuration from environment variables."""
    config = {
        "user": os.getenv("DAMENG_USER","SYSDBA"),
        "password": os.getenv("DAMENG_PASSWORD","SYSDBA"),
        "server": os.getenv("DAMENG_HOST", "localhost"),
        "port": 5236,
        "schema": os.getenv("DAMENG_DATABASE","IDP_JH")
    }
    
    if not all([config["user"], config["password"]]):
        logger.error("Missing required database configuration. Please check environment variables:")
        logger.error("DAMENG_USER and DAMENG_PASSWORD are required")
        raise ValueError("Missing required database configuration")
    
    return config

# Initialize server
app = Server("dameng_mcp_server")

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List Dameng tables as resources."""
    config = get_db_config()
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT TABLE_NAME FROM ALL_TABLES")
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")
                
                resources = []
                for table in tables:
                    resources.append(
                        Resource(
                            uri=f"dameng://{table[0]}/data",
                            name=f"Table: {table[0]}",
                            mimeType="text/plain",
                            description=f"Data in table: {table[0]}"
                        )
                    )
                return resources
    except Exception as e:
        logger.error(f"Failed to list resources: {str(e)}")
        return []

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read table contents."""
    config = get_db_config()
    uri_str = str(uri)
    logger.info(f"Reading resource: {uri_str}")
    
    if not uri_str.startswith("dm://"):
        raise ValueError(f"Invalid URI scheme: {uri_str}")
        
    parts = uri_str[9:].split('/')
    table = parts[0]
    
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)
                
    except Exception as e:
        logger.error(f"Schema error reading resource {uri}: {str(e)}")
        raise RuntimeError(f"Schema error: {str(e)}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Dameng tools."""
    logger.info("Listing tools...")
    return [
        Tool(
            name="execute_sql",
            description="Execute an SQL query on the Dameng server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute SQL commands."""
    config = get_db_config()
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    
    if name != "execute_sql":
        raise ValueError(f"Unknown tool: {name}")
    
    query = arguments.get("query")
    if not query:
        raise ValueError("Query is required")
    
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                
                # Handle all other queries that return result sets (SELECT, SHOW, DESCRIBE etc.)
                if cursor.description is not None:
                    columns = [desc[0] for desc in cursor.description]
                    try:
                        rows = cursor.fetchall()
                        result = [",".join(map(str, row)) for row in rows]
                        return [TextContent(type="text", text="\n".join([",".join(columns)] + result))]
                    except Exception as e:
                        logger.warning(f"Error fetching results: {str(e)}")
                        return [TextContent(type="text", text=f"Query executed but error fetching results: {str(e)}")]
                
                # Non-SELECT queries
                else:
                    conn.commit()
                    return [TextContent(type="text", text=f"Query executed successfully. Rows affected: {cursor.rowcount}")]
                
    except Exception as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        return [TextContent(type="text", text=f"Error executing query: {str(e)}")]

async def main():
    """Main entry point to run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    # Add additional debug output
    print("Starting Dameng MCP server with config:", file=sys.stderr)
    config = get_db_config()
    print(f"Server: {config['server']}", file=sys.stderr)
    print(f"Port: {config['port']}", file=sys.stderr)
    print(f"User: {config['user']}", file=sys.stderr)
    print(f"Schema: {config['schema']}", file=sys.stderr)
    
    logger.info("Starting Dameng MCP server...")
    logger.info(f"Schema config: {config['server']}/{config['schema']} as {config['user']}")
    
    async with stdio_server() as (read_stream, write_stream):
        try:
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    asyncio.run(main())
