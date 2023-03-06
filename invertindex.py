import json
import os
import pickle
import sys
import time
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
def process_file(file_path, docID):
    with open(file_path, 'r') as f:
        # loads json file and extracts text content and url
        all_content = json.load(f)
        raw_content = all_content["content"]
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

    with open("docID_mapping.txt", "a") as f:
        f.write(f"{docID} {all_content['url']} {len(tokens)}\n")
    return (docID, Counter(tokens), map)

def make_index(path: str):
    inverted_index = {chr(i): {} for i in range(97, 123)}
    docCount = 0
    docID = 0
    counter = 1
    totalTokens = 0
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
            # returns (docID, Counter{token: freq})
            results = pool.starmap(process_file, zip(file_paths, [i for i in range(counter,len(file_paths)+counter+1)]))
            counter += len(file_paths)

            for result in results:
                docID += 1
                token_counts = result[1]
                for token, count in token_counts.items():
                    totalTokens += 1
                    first_letter = token[0].lower()
                    # if token starts with a non-letter, it will be put in the "z" section
                    if first_letter not in abc:
                        first_letter = "z"
                    # index structure: { a: { token: [[docID, count], [docID,count]], b: ... }
                    #                  dict(letter -> dict(tokenStartingWithLetter -> list of docId, count pair lists))
                    inverted_index[first_letter].setdefault(token, []).append([docID, count])
            docCount += len(results)
            print(docCount)
            print("INDEX UPDATED\n")
            os.chdir("..")
        except NotADirectoryError:
            print("** Successfully skipped an invalid directory in DEV folder **\n")
    print(f"# OF DOCUMENTS: {docCount}")
    print(f"# OF UNIQUE WORDS {totalTokens}")
    index_in_bytes = pickle.dumps(inverted_index)
    print(f"SIZE IN KILOBYTES: {round(sys.getsizeof(index_in_bytes)/1000, 2)}")
    os.chdir("..")
    return inverted_index

def _parseDocIDMapping(file):
    map = {}
    with open(file, "r") as f:
        for line in f:
            idUrlTotal = line.split()
            map[int(idUrlTotal[0])] = (idUrlTotal[1], idUrlTotal[2])
    return map


def findResults(qWords: list, index: dict):
    #Creating local dictionary with docID -> (urlString, totalTokens) from text file made while parsing
    map = _parseDocIDMapping(os.path.join(os.getcwd(), "docID_mapping.txt"))
    matched_docs = []
    firstWord = True
    qWords = [stemmer.stem(word).lower() for word in qWords]

    start_time = time.perf_counter()
    # For each word in the query
    for word in qWords:
        current_docs = []
        # Determing which of the 26 sections of the index to start at based on first char of token
        if word[0] in abc:
            category = word[0]
        else:
            category = "z"
        # If word is in the index at that letter section
        if word in index[category]:
            # Key is token and data is a list(docID, tokenFrequency)
            for key, data in index[category].items():
                if word == key:
                    for doc in data:
                        if firstWord:
                            matched_docs.append(doc)
                        current_docs.append(doc)
        # Intersects current query word documents with all those of previous query words
        matched_docs = [doc for doc in matched_docs if doc in current_docs]
        firstWord = False
        # Search is complete
    end_time = time.perf_counter()
    # Where ranking should be implemented: (For now, it is ranked based on token occurence frequency)
    matched_docs.sort(key=lambda x: -1 * x[1])
    for x in range(0,min(5, len(matched_docs))):
        print(f"{x+1}) {map[matched_docs[x][0]][0]} with {matched_docs[x][1]} occurences")
    print(f"SEARCH TIME: {end_time-start_time:.3f} seconds")
    print()
    return matched_docs

if __name__ == "__main__":
    # !!!
    # SET TRUE IF YOU ARE RUNNING FOR THE FIRST TIME AND NEED TO BUILD THE INDEX
    # SET FALSE IF INDEX IS ALREADY BUILT AND YOU ARE READY TO SEARCH ONLY
    buildIndex = False
    if buildIndex:
        if os.path.exists(os.path.join(os.getcwd(), "docID_mapping.txt")):
            os.remove(os.path.join(os.getcwd(), "docID_mapping.txt"))
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
