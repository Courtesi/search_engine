import os
import store_index, store_byte_index
from flask import Flask, render_template, request, redirect, url_for, flash
from invertindex import make_index, _parseDocIDMapping, findResults
import json

app = Flask(__name__)


@app.route('/')
def homePage():
    return render_template('homePage.html')

@app.route('/results', methods=["POST"])
def results():
    searchQuery = request.form.get("searchQuery")
    # if not searchQuery:
    #         break
    qWords = searchQuery.split()
    index = open("stored_index.json", "r")
    map = _parseDocIDMapping(os.path.join(os.getcwd(), "docID_mapping.txt"))
    resultsList = findResults(qWords, index, map)
    return render_template('resultsPage.html', results=resultsList)

if __name__ == 'main':
    buildIndex = False
    if buildIndex:
        if os.path.exists(os.path.join(os.getcwd(), "docID_mapping.txt")):
            os.remove(os.path.join(os.getcwd(), "docID_mapping.txt"))

        store_index.store(make_index(os.path.join(os.getcwd(), "DEV")))
        byte_index = store_byte_index.write_byte_index()
    else:
        with open("stored_byte_index.json") as f:
            byte_index = json.load(f)
