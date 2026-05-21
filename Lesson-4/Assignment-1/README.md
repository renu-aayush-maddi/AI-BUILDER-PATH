source .venv/bin/activate
myenv\Scripts\activate


pip install -U mcp
pip install -U langchain-mcp-adapters


python mcp_servers/google_docs_server.py
python mcp_servers/rag_server.py
python mcp_servers/web_search_server.py