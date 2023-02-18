import json, os, pickle, sys
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

stemmer = PorterStemmer()

def get_index(path: str): #  -> dict(str, tuple(int, list))
    inverted_index = dict()
    docCount = 0
    for domain in os.listdir(path):
      try:
        print(f"DOMAIN: {domain}")
        # if this following line runs without raising an exception, the directory is valid
        os.chdir(domain)
        for file in os.listdir(os.getcwd()):
          docCount += 1
          with open(file, 'r') as f:
              #gets raw_content from json and gets a string containing all text content
              all_content = json.load(f)
              raw_content = all_content["content"]
              docID = hash(all_content["url"])
              soup = BeautifulSoup(raw_content, features="xml")
              p_tags = soup.find_all('p')
              text = ""
              for p_tag in p_tags:
                text += p_tag.get_text().replace("\n\n", "")

              #tokenizes and stems all words in text
              tokens = word_tokenize(text)
              tokens = [stemmer.stem(token).lower() for token in tokens if token.isalnum()]
# --dictionary format: {token -> [[docA, freqA], [docB, freqB],...for all tokens in all documents])}
              # for every token...
              for token in tokens:
                # and every index pair,
                for item in inverted_index.items():
                  # if the token already exists...
                  if token in item[0]:
                    # and it was already found in this specific document,
                    if item[1][0] == docID:
                      # increase the frequency by one
                      inverted_index[item[0]][1] += 1
                    # or it was found in a previous document but it is appearing first in this document,
                    elif item[1][0] != docID:
                      # add the docID to the token value and give it an initial frequency of 1
                      inverted_index[item[0]].append([docID, 1])
                # otherwise, if the token does not exist, create a new index entry with the token --> (docID, 1)
                else:
                  inverted_index[token] = [docID, 1]
        print(inverted_index)
        print("-------------------------------\n")
        os.chdir("..")
      except Exception as e:
        #this will likely be hit when the for-loop hits hidden non-directories in the /DEV folder when iterating
        pass
    print(f"# OF DOCUMENTS: {docCount}")
    print(f"# OF UNIQUE WORDS {len(inverted_index)}")
    index_in_bytes = pickle.dumps(inverted_index)
    print(f"SIZE IN KILOBYTES: {round(sys.getsizeof(index_in_bytes)/1000, 2)}")
    return inverted_index # returns empty dictionary for now

if __name__ == "__main__":
  get_index(os.chdir(os.getcwd() + "/DEV"))
