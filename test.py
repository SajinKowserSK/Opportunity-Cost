
from flask import Flask, render_template, request

import pandas as pd
import numpy as np
import re
import operator
from fuzzywuzzy import fuzz
from datetime import datetime

def clean(sentence):

    cleaned = re.compile('[^a-zA-Z-"&"-" "]')
    cleaned = cleaned.sub('', sentence)
    cleaned = re.sub(' +', ' ', sentence)
    cleaned = ''.join([i for i in cleaned if not i.isdigit()])
    if "#" in cleaned:
        cleaned = cleaned.replace("#", "")

    elif "*" in cleaned:
        cleaned = cleaned.replace("*", "")

    return cleaned.rstrip().lstrip()

def days_between(d1, d2):
    d1 = datetime.strptime(d1, '%m/%d/%Y')
    d2 = datetime.strptime(d2, '%m/%d/%Y')
    return abs((d2 - d1).days)

def average (lst):
    avg = sum(lst) / len(lst)
    return round(avg, 2)

def main(filename):
    transactionList = []
    places_avg_price = {}

    df1 = pd.read_csv(filename, names=["Date", "Transaction", "Price", "NA1", "NA2"])
    df1 = df1.drop('NA1', axis=1)
    df1 = df1.drop('NA2', axis=1)
    for x in range(0, len(df1["Price"])):  # the problem
        df1 = df1[df1["Price"] > 0]

    df1 = df1.reset_index(drop=True)

    for places in df1["Transaction"]:
        df1["Transaction"] = [clean(places) for places in df1["Transaction"]]

    for entries in df1["Date"]:
        df1["Date"][entries] = datetime.strptime(entries, '%m/%d/%Y')

    days = days_between("08/15/2019", "07/23/2019")
    months = 1 + (days // 30)

    for places in range(0, len(df1["Transaction"])):
        for placesBelow in range(places, len(df1["Transaction"])):
            if fuzz.ratio(df1["Transaction"][places], df1["Transaction"][placesBelow]) > 50:
                df1["Transaction"][placesBelow] = df1["Transaction"][places]

    for places in range(0, len(df1["Transaction"])):
        transactionList.append(df1["Transaction"][places])

    transactionList = set(transactionList)

    for entries in transactionList:
        tmpValues = []
        tmpDF = df1[df1["Transaction"] == entries]

        for prices in tmpDF["Price"]:
            tmpValues.append(prices)

        avgVal = average(tmpValues)
        total_visits = len(tmpValues)
        places_avg_price[entries] = total_visits, avgVal


    places_avg_price = sorted(places_avg_price.items(), key=operator.itemgetter(1),
                              reverse=True)  # sorts dictionary in terms of bill frequency

    item = input("What are you thinking of buying?")
    item_price = float(input("What is the price?"))

    for entries in range(0, len(places_avg_price)):
        transaction = places_avg_price[entries]
        bill = transaction[0]

        avg_price = transaction[1][1]
        all_visits = transaction[1][0]

        monthly_visits = all_visits // months
        monthly_cost = monthly_visits * avg_price

        canAfford = item_price // monthly_cost
        total_times = item_price // avg_price
        print("For the price of %s($%d), you could pay for "
              "%s approximately %d times! That's an average of paying for %d months of %s!" % (
              item, item_price, bill, total_times, canAfford, bill))
        print("\n")

app = Flask(__name__)

@app.route("/profile/<name>")
def profile(name):
    return render_template("profile.html", name=name )

@app.route("/", methods = ['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        filename = request.form['filename'] # now we can use filename as a python variable
        main(filename)
        return render_template("homepage.html")

    else:
        return render_template("homepage.html")



