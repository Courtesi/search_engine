import json, os, re
from bs4 import BeautifulSoup
import nltk

os.chdir(os.getcwd() + "/DEV")
print(f"MAIN DIRECTORY: {os.getcwd()}")

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
            content = json.load(f)["content"]
            soup = BeautifulSoup(content, features="xml")
            # pattern = r'var elementorFrontendConfig\s*=\s*({.*});'
            # script_tag = soup.find('script', string=lambda text: text and "elementorFrontendConfig" in text)
            # script_tag.string = re.sub(pattern, '', script_tag.string)
            # soup.prettify()
            print(soup.get_text())
            
            # NEXT STEPS
            # tokenize (including stemming) soup.gettext()
            # create dictionary with reference to docIDs

      print("----------\n")
      os.chdir("..")
    except Exception as e:
      print(e)