import json
import os
import pickle
import sys
import time
import requests
from collections import Counter
from multiprocessing import Pool
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import store_index
stemmer = PorterStemmer()
abc = "abcdefghijklmnopqrstuvqxyz"

# takes in a webpage url (in json format) and returns a tuple: (docID, Counter dictionary of tokens --> freq)
def process_file(file_path):
    if file_path.startswith('http'):
        # Why is this if statement here??
        print("Is this ever being run?")
        response = requests.get(file_path)
        raw_content = response.text
        docID = file_path
    else:
        with open(file_path, 'r') as f:
            # loads json file and extracts text content and url
            all_content = json.load(f)
            raw_content = all_content["content"]
            docID = all_content["url"]
    # parsing html content with BeautifuLSoup
    soup = BeautifulSoup(raw_content, features="lxml")
    # using p-tags to find paragraph content
    p_tags = soup.find_all('p')
    text = ""
    # removing two-in-a-row blank lines to enhance readability speed up tokenizing
    for p_tag in p_tags:
        text += p_tag.get_text().replace("\n\n", "")
    # tokenizing and stemming
    tokens = word_tokenize(text)
    tokens = [stemmer.stem(token).lower() for token in tokens if token.isalnum()]
    return (docID, Counter(tokens))

def make_index(path: str):
    inverted_index = {chr(i): {} for i in range(97, 123)}
    docCount = 0
    pool = Pool()
    # iterates through all folders in DEV
    for domain in os.listdir(path):
        try:
            print(f"INDEXING DOMAIN: {domain}")
            # the following line will raise an error if the item in the DEV folder is not a domain folder
            # while also hopping into that directory if it is valid
            os.chdir(os.path.join(path, domain))
            # the following line creates a list of all the webpages in the domain
            file_paths = [os.path.join(os.getcwd(), file) for file in os.listdir(os.getcwd())]
            # the following line uses multithreading to parse each url with the process_file function
            results = pool.map(process_file, file_paths)
            # returns (docID, Counter{token: freq})
            for result in results:
                docID = result[0]
                token_counts = result[1]
                for token, count in token_counts.items():
                    # not sure how this works...
                    first_letter = token[0].lower()
                    # if token starts with a non-letter, it will be put in the "z" section
                    if first_letter not in abc:
                        first_letter = "z"
                    inverted_index[first_letter].setdefault(token, []).append([docID, count])
            docCount += len(results)
            print("INDEX COMPLETED\n")
            os.chdir("..")
        except Exception as e:
            print(e)
            #print("** Successfully skipped an invalid directory in DEV folder **")
    print(f"# OF DOCUMENTS: {docCount}")
    print(f"# OF UNIQUE WORDS {len(inverted_index)}")
    index_in_bytes = pickle.dumps(inverted_index)
    print(f"SIZE IN KILOBYTES: {round(sys.getsizeof(index_in_bytes)/1000, 2)}")
    os.chdir("..")
    return inverted_index

def findResults(qWords: list, index: dict):
    start_time = time.perf_counter()
    matched_docs = []
    firstWord = True
    # stemming query words
    qWords = [stemmer.stem(word).lower() for word in qWords]

    for word in qWords:
        current_docs = []
        if word[0] in abc:
            category = word[0]
        else:
            category = "z"
        if word in index[category]:
            for key, data in index[category].items():
                if word == key:
                    for doc in data:
                        if firstWord:
                            matched_docs.append(doc)
                        current_docs.append(doc)
        matched_docs = [doc for doc in matched_docs if doc in current_docs]
        firstWord = False
    end_time = time.perf_counter()
    matched_docs.sort(key=lambda x: -1 * x[1])
    for x in range(0,min(5, len(matched_docs))):
        print(f"{x+1}) {matched_docs[x][0]} with {matched_docs[x][1]} occurences")
    print(f"SEARCH TIME: {end_time-start_time:.3f} seconds")
    print()
    return matched_docs

if __name__ == "__main__":
    # CHANGE THIS TO TRUE IF YOU ARE RUNNING FOR THE FIRST TIME AND NEED TO BUILD THE INDEX
    buildIndex = False
    if buildIndex:
        store_index.store(make_index(os.path.join(os.getcwd(), "DEV")))

    print("\n---------------------")
    print("Preparing Search...")
    with open("stored_index.json", "r") as f:
        index = json.load(f)

    while True:
        query = input("SEARCH QUERY (hit return/enter to quit): ")
        if not query:
            break
        qWords = query.split()
        findResults(qWords, index)
