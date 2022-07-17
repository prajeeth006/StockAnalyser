from flask import Flask
from flask_restful import Api
import news_feed

app = Flask(__name__)
api = Api(app)

api.add_resource(news_feed.newsFeed, '/stocks-in-news')

if __name__ == '__main__':
    app.run(debug = True)