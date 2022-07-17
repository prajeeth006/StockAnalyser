from flask_restful import Resource
import spacy
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import json

rss_link_default = 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms'

nlp = spacy.load("en_core_web_sm")

def extract_text_from_rss_link(rss_link):
    r = requests.get(rss_link if rss_link else rss_link_default)
    soup = BeautifulSoup(r.content, features='xml')
    headlines = soup.findAll('title')
    return headlines

def generate_stock_info(headlines):
    stock_info_dict = {
        'Org':[],
        'Symbol': [],
        'currentPrice' : [],
        'dayHigh': [],
        'dayLow':[],
        'forwardPE':[],
        'dividendYield':[]
    }
    stocks_df = pd.read_csv('./data/ind_nifty500list.csv')
    for title in headlines:
        doc = nlp(title.text)
        for ent in doc.ents:
            try:
                if stocks_df['Company Name'].str.contains(ent.text).sum() > 0:
                    chunk_df = stocks_df[stocks_df['Company Name'].str.contains(ent.text) == True]
                    symbol = chunk_df['Symbol'].values[0]
                    org_name = chunk_df['Company Name'].values[0]
                    stock_info = yf.Ticker(symbol+'.NS').info

                    if(all(item in list(stock_info.keys())) for item in ['currentPrice','dayHigh','dayLow','forwardPE','dividendYield']):
                        stock_info_dict['Org'].append(org_name)
                        stock_info_dict['Symbol'].append(symbol)
                        stock_info_dict['currentPrice'].append(stock_info['currentPrice'])
                        stock_info_dict['dayHigh'].append(stock_info['dayHigh'])
                        stock_info_dict['dayLow'].append(stock_info['dayLow'])
                        stock_info_dict['forwardPE'].append(stock_info['forwardPE'])
                        stock_info_dict['dividendYield'].append(stock_info['dividendYield'])
                    else:
                        pass
                else:
                    pass
            except:
                pass
    output_df = pd.DataFrame(stock_info_dict)
    output_df.drop_duplicates(inplace = True)    
    print(output_df)
    return output_df.to_json()

class newsFeed(Resource):
    def get(self):
        headlines = extract_text_from_rss_link(rss_link_default)
        stocks_in_news = generate_stock_info(headlines)
        return stocks_in_news