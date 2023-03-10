import json
import os
import re
import pickle
import sys
import time
from collections import Counter
from multiprocessing import Pool
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import store_indices, store_byte_index
stemmer = PorterStemmer()


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

    return (docID, Counter(tokens))



def make_index(path: str) -> list:

    partial_index1 = {}
    partial_index2 = {}
    partial_index3 = {}

    counter = 1
    tokenNum = 0
    BUFFER_SIZE = 200000
    pool = Pool()

    # Iterates through all folders in DEV
    for domain in os.listdir(path):
        try:
            print(f"INDEXING DOMAIN: {domain}")
            # The following line will raise an error if the item in the DEV folder is not a domain folder
            # but will hop into that directory if it is valid
            os.chdir(os.path.join(path, domain))

            # The following line creates a list of all the webpages in the current domain
            file_paths = [os.path.join(os.getcwd(), file) for file in os.listdir(os.getcwd())]

            # The following line uses multithreading to parse multiple urls simultaneously with the process_file function.
            # The startmap function will return a list of tuples: (docID, Counter{token: freq})
            results = pool.starmap(process_file, zip(file_paths, [i for i in range(counter,len(file_paths)+counter+1)]))
            counter += len(file_paths)

            # For each result (data of a single web page), update the index
            for result in results:
                docID = result[0]
                token_counts = result[1]
                for token, count in token_counts.items():
                    tokenNum += 1
                    if tokenNum <= BUFFER_SIZE:
                        partial_index1.setdefault(token, []).append([docID, count])
                    elif tokenNum <= BUFFER_SIZE * 2:
                        partial_index2.setdefault(token, []).append([docID, count])
                    else:
                        partial_index3.setdefault(token, []).append([docID, count])

            docCount = len(results)
            
            print("INDEX UPDATED\n")
            os.chdir("..")
        except NotADirectoryError:
            print("** Successfully skipped an invalid directory in DEV folder **\n")
    print(f"# OF DOCUMENTS: {docCount}")
    print(f"# OF UNIQUE WORDS {tokenNum}")
    index1_in_bytes = pickle.dumps(partial_index1)
    index2_in_bytes = pickle.dumps(partial_index2)
    index3_in_bytes = pickle.dumps(partial_index3)
    print(f"SIZE IN KILOBYTES: {round((sys.getsizeof(index1_in_bytes) + sys.getsizeof(index2_in_bytes) + sys.getsizeof(index3_in_bytes))/1000, 2)}\n")
    print("Index creation is complete. To search, set Line 198 to False and re-launch.")
    os.chdir("..")

    return [partial_index1, partial_index2, partial_index3]



def _parseDocIDMapping(file):
    map = {}
    with open(file, "r") as f:
        for line in f:
            idUrlTotal = line.split()
            map[int(idUrlTotal[0])] = (idUrlTotal[1], idUrlTotal[2])
    return map



'''
findResults takes in:
    1) list of query words
    2) list of open partial index files
    3) docID to (docLink mapping, wordCount) dict
'''
def findResults(qWords: list, indices: list, map: dict):

    #Starting Search Timer
    start_time = time.perf_counter()

    # List which will contain all the documents matched by the query
    matched_docs = []
    firstWord = True

    # Stemming the qWords to allow for matching with stemmed index keys
    qWords = [stemmer.stem(word).lower() for word in qWords]

    # For each word in the query...
    for word in qWords:
        qSize = len(qWords)

        # List which will contain all the documents matched by the current word in the list of query words
        current_docs = []

        # If the word is no where to be found in the index, the search is over
        if word not in byte_index:
            print("No Results Found.\n")
            return
        
        partialIndex = "?"
        location = 0

        # Use the byte index to find where in the main index to start searching for the term
        for token, tokenLocation in byte_index.items():
            # Note: tokenLocation is a tuple: (partialIndexNumber, byte)
            if word == token:
                location = tokenLocation[1]
                break
        partialIndex = tokenLocation[0]
        index = indices[partialIndex-1]
        index.seek(location)    
        
        # Once seeking to the byte location in the main index open object, start reading lines
        #   (the first line read should be a match because the read starts at the proper byte location)
        data_string = index.readline()

        # To avoid loading the entire index onto memory with json.dump(), we will be reading the json index 
        # file as a string. The following code parses the string to get only the first key-value pair in the
        # file starting from the seeked byte location. tokenData will be a list of [docID, freq] lists.
        while data_string[-3:-1] != "]]":
            data_string += index.readline().strip()
        tokenData = []
        data = data_string.replace("],[", " ").replace("[", "").replace("]],", "").split()[1:]
        for doc in data:
            tokenData.append([int(doc.split(",")[0]), int(doc.split(",")[1])])
        current_docs = tokenData

        # The following code will only run if the query size is greater than 1.
        # Here is where optimized merging should be implemented.
        if qSize > 1:
            if firstWord:
                matched_docs = current_docs
                firstWord = False
            matched_docs = [doc for doc in matched_docs if doc in current_docs]
    
    if firstWord:
        matched_docs = current_docs

    # Search is complete
    end_time = time.perf_counter()
    index.close()

    # This is where ranking should be implemented. For now, it is ranked based on token frequency in the doc
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
    buildIndex = True
    if buildIndex:
        if os.path.exists(os.path.join(os.getcwd(), "docID_mapping.txt")):
            os.remove(os.path.join(os.getcwd(), "docID_mapping.txt"))

        store_indices.store(make_index(os.path.join(os.getcwd(), "DEV")))
        byte_index = store_byte_index.write_byte_index()
    else:
        with open("stored_byte_index.json") as f:
            byte_index = json.load(f)

        print("\n---------------------")
        print("Preparing Search...")

        while True:
            query = input("SEARCH QUERY (hit return/enter to quit): ")
            if not query:
                break
            qWords = query.split()
            indices = [open("partial_index1.json", "r"), open("partial_index2.json", "r"), open("partial_index3.json", "r")]
            map = _parseDocIDMapping(os.path.join(os.getcwd(), "docID_mapping.txt"))
            findResults(qWords, indices, map)
