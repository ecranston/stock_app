#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:36:22 2017

@author: Beth
"""

import pandas as pd
import datetime
import requests
import json
# from matplotlib import pyplot as pt
from bokeh.plotting import figure, output_file, save
from flask import Flask, render_template, request, redirect

StockPriceCranston = Flask(__name__)
StockPriceCranston.vars = {}

@StockPriceCranston.route('/', methods=['GET', 'POST'])
def initial():
    return redirect('/index')

@StockPriceCranston.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('FrontPage.html')
    else:
        StockPriceCranston.vars['stock_val'] = request.form['stock_val']

        if(request.form.get('Opening')):
            StockPriceCranston.vars['Columns'] = 'open'
            StockPriceCranston.vars['opening'] = True
        else:
            StockPriceCranston.vars['Columns'] = ''
            StockPriceCranston.vars['opening'] = False

        if(request.form.get('Closing')):
            StockPriceCranston.vars['closing'] = True
            if StockPriceCranston.vars['opening']:
                StockPriceCranston.vars['Columns'] = \
                    StockPriceCranston.vars['Columns'] + ',close'
            else:
                StockPriceCranston.vars['Columns'] = 'close'
        else:
            StockPriceCranston.vars['closing'] = False

        return redirect('/results')


@StockPriceCranston.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'GET':
        date = datetime.datetime.today()
        y = date.year
        m = date.month
        m = (m-1) % 12
        if m < 10:
            mstring = '0' + str(m)
        else:
            mstring = str(m)
        d = date.day
        if d < 10:
            dstring = '0' + str(d)
        else:
            dstring = str(d)
        querystring = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES' +\
            '.json?qopts.columns=ticker,date,' +\
            StockPriceCranston.vars['Columns'] +\
            '&date.gte=' + str(y) + mstring + dstring + \
            '&ticker=' + StockPriceCranston.vars['stock_val'] +\
            '&api_key=JHAyxi2U_djHjcxJeHUf'

        #f = open('debug.txt', 'a')
        #f.write(querystring)
        #f.close()
        #print(querystring)
        analyze(querystring)

        #filename = 'lines.html'
        filename = 'lines' + StockPriceCranston.vars['stock_val'] +\
            StockPriceCranston.vars['Columns'] + '.html'
        #f = open('debug.txt', 'a')
        #f.write(filename)
        #f.close()
        return render_template(filename)


def analyze(qstring):
    r = requests.get(qstring)
    data = json.loads(r.text)

    # Get the columns that were actually queried:
    columnList = []
    for i in range(len(data['datatable']['columns'])):
        columnList.append(data['datatable']['columns'][i]['name'])

    prices = pd.DataFrame(data=data['datatable']['data'],
                          columns=columnList)
    prices['date'] = pd.to_datetime(prices['date'])

    # output to static HTML file
    filename = 'templates/lines' + StockPriceCranston.vars['stock_val'] +\
        StockPriceCranston.vars['Columns'] + '.html'
    #filename = 'templates/lines.html'
    output_file(filename)

    # create a new plot with a title and axis labels
    p = figure(title=StockPriceCranston.vars['stock_val'],
               x_axis_type="datetime")

    # add a line renderer with legend and line thickness
    if(StockPriceCranston.vars['closing']):
        p.line(prices['date'], prices['close'],
               legend="Closing Prices", line_color='red', line_width=1)
    if(StockPriceCranston.vars['opening']):
        p.line(prices['date'], prices['open'],
               legend="Opening Prices", line_color='blue', line_width=1)

    # show the results
    save(p)


sampleQuery = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?' +\
              'qopts.columns=ticker,date,close,open' +\
              '&date.gte=20160102' +\
              '&ticker=GOOG' +\
              '&api_key=JHAyxi2U_djHjcxJeHUf'


if __name__ == "__main__":
    #analyze(sampleQuery)
    StockPriceCranston.run()
