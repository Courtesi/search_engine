import math
from collections import defaultdict, Counter
from nltk.tokenize import word_tokenize
# from sklearn.metrics import cosine_similarity



""" The functions in this module are meant to be called in search_engine.py; use them as utilities"""

# calculates the tf-idf score given a term, document, inverted index, and doc_lengths (separate dict mapping each docID to the number of terms in that doc)

"""
DEFINITIONS:
    term frequency - tell us how frequent a term is in a given document
    inverse document frequency - tells us the rarity of a term across all the documents in a corpus
    tf-idf score - tell us the importance of a term relative to term frequency and inverse document frequency (essentially it is a weight)
    cosine similarity - tells us how relevant a document is to the query taking into account angle proximity rather than total euclidean distance
    normalized vector - a "pure" vector that removes the problem of different length documents which can heavily impact the weight of a term and lead to incorrect results
PROCESS:
    1. accept a query
    2. preprocess the query (remove stopwords, perform stemming, etc)
    3. generate the query vector using getQueryVector() to compare with docVectors later [see getQueryVector()]
    4. represent all documents as vectors in a large vector space[see getDocVector()]
        - SHORT EXPLANATION: the two functions above will return a vector (list) of the tf-idf scores of all the terms in the doc/query making use of calcTfIdf()
    
    5. compute the cosine similarity between the queryVector and EACH documentVector and store inside a dictionary 
    6. sort the dictionary by value in descending order [the higher a cosine similarity -> the more relevant the doc is]
    
    7. return the top k-docs in the dictionary 
THOUGHT: 
    - thinking of adding the docLengthDict as just an extra key value pair in our inverted index or a separate dict
"""

# This function calculates the tf-idf score for a term within a given document 
def calcTfIdf(term: str, docLengthDict: dict, termPostingDict: dict, docID=None):

    # dividing by the # of terms in the docID in order to normalize the size of a document for comparison
    
    #termFreq = invertedIndex[term][docID] / docLengthDict[docID] # see matched docs in invertIndex.py
    # print(termPostingDict)
    # print()
    # print(termPostingDict[term][1])
    # print()
    # print(docLengthDict)

    # termFreq = termPostingDict[term][1] / docLengthDict[docID]
    
    # # put termPosting in the IDf calculation
    # termPosting = termPostingDict[term]
    # #inverseDocFreq = math.log(len(docLengthDict) / len(invertedIndex[term])) #replace len invertedIndex[term] with lenCurrDoc
    # inverseDocFreq = math.log(len(docLengthDict) / len(termPosting))

    # # The tf-idf score is just the dot product of both tf and idf
    # score = termFreq * inverseDocFreq

    # return score
    if docID is not None:
        # Divide by the number of terms in the document in order to normalize the size of the document for comparison
        # print(termPostingDict[term])
        # print(docLengthDict[docID][1])
        termFreq = termPostingDict[term][1][0] / int(docLengthDict[docID][1])
        # Put termPosting in the IDF calculation
        termPosting = termPostingDict[term]
        # Inverse document frequency
        inverseDocFreq = math.log(len(docLengthDict) / len(termPosting))
    else:
        # Term frequency in the entire corpus
        termFreq = sum([posting[1] for posting in termPostingDict[term]])
        # Inverse document frequency
        inverseDocFreq = math.log(len(docLengthDict) / len(termPostingDict[term]))

    # The tf-idf score is just the dot product of both tf and idf
    score = termFreq * inverseDocFreq

    return score
