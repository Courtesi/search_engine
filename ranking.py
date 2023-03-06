import math
from collections import defaultdict

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

# This function calculates the tf-idf score for a term within a given document and is meant to be passed every docID a term is mapped to in the Inverted Index.
def calcTfIdf(term: str, docID: int, invertedIndex: dict, docLengthDict: dict):

    # dividing by the # of terms in the docID in order to normalize the size of a document for comparison
    termFreq = index[term][docID] / docLengthDict[docID]
    
    inverseDocFreq = math.log(len(doc_lengths) / len(invertedIndex[term]))

    # The tf-idf score is just the dot product of both tf and idf
    score = termFreq * inverseDocFreq

    return score

# This function constructs a vector to represent a doc in a large dimensional vector space when provided a doc
def getDocVector(docID: int, invertedIndex: dict, docLengthDict: dict):

    # all the terms in the entire inverted index
    allTerms = list(invertedIndex.keys())

    # filtering out all the terms where the docID is not in it's posting list
    docTerms = [term for term in allTerms if docID in invertedIndex[term]]

    # Calculate TF-IDF score for each term in document
    docVector = list()
    for term in docTerms:
        score = calcTfIdf(term, docID, invertedIndex, docLengthDict)
        docVector.append(score)

    return docVector

# This function constructs a vector to represent a query in a large dimensional vector space
def getQueryVector(query: str, invertedIndex: dict, docLengthDict: dict):
    # Tokenize query into terms (QUERY PREPROCESSING HERE)
    query_terms = tokenize(query)

    # Calculate term frequencies in query
    query_tf = Counter(query_terms)

    # Calculate TF-IDF score for each term in query
    queryVector = list()
    for term in query_terms:
        if term not in invertedIndex:
            # term is not in any document, so skip it
            continue
        # pass in None instead of a docID since there is no specific docID to calculate the tf-idf of but rather just the term in the entire corpus
        score = calcTfIdf(term, None, invertedIndex, docLengthDict) * query_tf[term]
        queryVector.append(score)

    return queryVector
 

# This function takes in the queryVector and docVector and calculates the cosine similarity beteween the two
def calcCosineSim(qv: list, dv: list):
     # normalize the query vector by dividing by its L2 norm
    query_norm = math.sqrt(sum([x**2 for x in qv]))
    query_norm_vector = [x / query_norm for x in qv]

    # normalize documen vector by dividing by its L2 norm
    document_norm = math.sqrt(sum([x**2 for x in dv]))
    document_norm_vector = [x / document_norm for x in dv]

    # Calculate dot product of normalized vectors
    cosineSim = sum([x * y for x, y in zip(query_norm_vector, document_norm_vector)])

    return cosineSim

def getRankedDocs(query: str, invertedIndex: dict, docLengthDict: dict):

    # process: generate queryVector -> get all the docID's related -> generate their corresponding docVectors -> compute their cosine sims
    #  -> add the cosine sims to docs list -> sort docs list and return top K docs
    docScores = defaultdict(float)

    queryVector = getQueryVector(query, invertedINdex, docLengthDict)
    for docID in docLengthDict.keys(): # change this to be appropriate for the _keys_ key value pair in the invertedIndex
        docVector = getDocVector(docID, invertedIndex, docLengthDict)
        similarityScores[docID] = calcCosineSim(queryVector, docVector)
    
    # Sort documents by value in descending order
    rankedDocs = sorted(similarityScores.items(), key=lambda x: x[1], reverse=True)
    
    return rankedDocs[:5]

if __name__ == '__main__':
    print('running ranking.py in its own module space')
