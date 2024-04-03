from hackathon_ai_assistant.app import application
from aiohttp import web

if __name__ == "__main__":
    app = application()
    web.run_app(app, host="0.0.0.0", port=8083)
