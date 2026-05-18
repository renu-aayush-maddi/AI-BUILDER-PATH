from tools.web_search_tool import get_web_search_tool

tool = get_web_search_tool()

response = tool.run("latest AI regulations in US")

print("\n✅ WEB SEARCH RESPONSE:\n")
print(response)