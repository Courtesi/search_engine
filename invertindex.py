import json, os
from bs4 import BeautifulSoup
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

stemmer = PorterStemmer()

def get_index(path: str): #  -> dict(str, tuple(int, list))
    inverted_index = dict()
    x = 1
    for domain in os.listdir(os.getcwd()):
      while x < 2: # while loop to get the for-loop to run only once for testing
        try:
          x += 1
          print(f"DOMAIN: {domain}")
          os.chdir(domain)
          for file in os.listdir(os.getcwd()):
            with open(file, 'r') as f:
                #gets raw_content from json and gets a string containing all text content
                raw_content = json.load(f)["content"]
                soup = BeautifulSoup(raw_content, features="xml")
                p_tags = soup.find_all('p')
                text = ""
                for p_tag in p_tags:
                  text += p_tag.get_text().replace("\n\n", "")

                #tokenizes and steams all words in text
                tokens = word_tokenize(text)
                stemmed_words = [stemmer.stem(token) for token in tokens if token.isalnum()]
                print(stemmed_words)

                # NEXT STEPS
                # create dictionary with reference to docIDs
                # --dictionary format: {key: token, value: (frequency, [docA, docB, docC...for all documents token appears in])}

          print("----------\n")
          os.chdir("..")
        except Exception as e:
          print(e) #this will likely be hit when the for-loop hits hidden non-directories in the /DEV folder when iterating
    return inverted_index # returns empty dictionary for now

if __name__ == "__main__":
  get_index(os.chdir(os.getcwd() + "/DEV"))