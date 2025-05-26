from app.app import create_api, create_app

api = create_api()
app = create_app(api)
