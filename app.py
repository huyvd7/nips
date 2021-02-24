import plotly.express as px
import plotly.graph_objs as go
import io
import PIL
import argparse

import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
import dash.dependencies as dd
from mysql.connector.constants import ClientFlag


import pandas as pd
import mysql.connector

from wordcloud import WordCloud, STOPWORDS

def plot_wc(text):
    stopwords = set(STOPWORDS)
    stopwords.update(['model', 'algorithm', 'algorithms', 'method', 'methods', 'problem', 'show', 'models', 'based', 'via', 'problems', 'propose', 'learning', 'using'])
    wordcloud = WordCloud(stopwords=stopwords,
                          background_color="white", max_words=30,  width=600, height=400 ).generate(text) 
    return wordcloud.to_image()

def make_image2(text):
    img = io.BytesIO()
    plot_wc(text).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)
app.layout = html.Div([dcc.RangeSlider(
        id='slider',
        min=1987,
        max=2019,
        step=1,
        value=[2019,2019],tooltip ={'always_visible':False}
    ),
    html.Img(id="image_wc"),
    html.Div(id='output-container-range-slider')
],
    style = {'display': 'inline-block', 'width': '25%', 'textAlign': 'center'}
)

#@app.callback(dd.Output('image_wc', 'src'), [dd.Input('image_wc', 'id')])
#def make_image(b):
#    img = io.BytesIO()
#    PIL.Image.open('t.png').save(img, format='PNG')
#    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

@app.callback(
    #dd.Output('output-container-range-slider', 'children'),
    dd.Output('image_wc', 'src'),
    [dd.Input('slider', 'value')])
def update_output(value):
    y1, y2= value[0], value[1]
    
    df = papers[(papers.year>=y1) &
               ( papers.year<=y2)]
    text = " ".join(t for t in df.title.astype(str))
    #return f'{y1}-{y2}', make_image2(text)
    return make_image2(text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--dbname", default="nips")
    args = parser.parse_args()

    config = {
    'user': args.user,
    'password': args.password,
    'host': args.host,
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': 'server-ca.pem',
    'ssl_cert': 'client-cert.pem',
    'ssl_key': 'client-key.pem',
    'database': 'nips'
    }
    mydb = mysql.connector.connect(**config)
    
    print('Check 1: DB connected')    
    mc = mydb.cursor()
    sql = "SELECT * FROM papers"
    mc.execute(sql)
    result = mc.fetchall()
    papers = pd.DataFrame(result)
    papers.columns =[i[0] for i in mc.description]

    app.run_server(debug=True)
