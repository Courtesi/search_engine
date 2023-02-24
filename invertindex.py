import json
import math
import os
import pickle
import sys
import requests
import store_index
from collections import Counter
from multiprocessing import Pool
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
stemmer = PorterStemmer()

def process_file(file_path):
    if file_path.startswith('http'):
        response = requests.get(file_path)
        raw_content = response.text
        docID = file_path
    else:
        with open(file_path, 'r') as f:
            all_content = json.load(f)
            raw_content = all_content["content"]
            docID = all_content["url"]
    soup = BeautifulSoup(raw_content, features="lxml")
    p_tags = soup.find_all('p')
    text = ""
    for p_tag in p_tags:
        text += p_tag.get_text().replace("\n\n", "")
    tokens = word_tokenize(text)
    tokens = [stemmer.stem(token).lower() for token in tokens if token.isalnum()]
    return (docID, Counter(tokens))

def get_index(path: str):
    inverted_index = {}
    docCount = 0
    pool = Pool()
    for domain in os.listdir(path):
        try:
            print(f"DOMAIN: {domain}")
            os.chdir(os.path.join(path, domain))
            file_paths = [os.path.join(os.getcwd(), file) for file in os.listdir(os.getcwd())]
            results = pool.map(process_file, file_paths)
            for result in results:
                docID = result[0]
                token_counts = result[1]
                for token, count in token_counts.items():
                    inverted_index.setdefault(token, []).append([docID, count])
            docCount += len(results)
            print("-------------------------------\n")
            print(inverted_index)
            os.chdir("..")
        except Exception as e:
            print(e)
    print(f"# OF DOCUMENTS: {docCount}")
    print(f"# OF UNIQUE WORDS {len(inverted_index)}")
    index_in_bytes = pickle.dumps(inverted_index)
    print(f"SIZE IN KILOBYTES: {round(sys.getsizeof(index_in_bytes)/1000, 2)}")
    return inverted_index

def findResults(qWords: list, index: dict):
    with open(index, 'r') as f:
        index = json.load(f)
    #print("irvine" in index)

    matched_docs = []
    firstWord = True
    qWords = [stemmer.stem(word).lower() for word in qWords]
    for word in qWords:
        current_docs = []
        if word in index:
            for key, data in index.items():
                if word == key:
                    for doc in data:
                        if firstWord:
                            matched_docs.append(doc)
                        current_docs.append(doc)
        matched_docs = [doc for doc in matched_docs if doc in current_docs]
        firstWord = False
    matched_docs.sort(key=lambda x: -1 * x[1])
    for x in range(0,min(5, len(matched_docs))):
        print(f"{x+1}) {matched_docs[x]}")
    return matched_docs

if __name__ == "__main__":
    store_index.store(get_index(os.path.join(os.getcwd(), "DEV"))) #comment this out after the index file is created for the first time.
                                                                    #it is saved in the DEV folder
    query = input("SEARCH: ")
    qWords = query.split()
    findResults(qWords, "stored_index.json")
