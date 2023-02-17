import json, os

os.chdir(os.getcwd() + "/DEV")
print(os.getcwd())
for domain in os.listdir(os.getcwd()):
  print(domain)
  os.chdir(domain)
  for page in os.listdir(os.getcwd()):
    print(page)
  print("----------\n")
  os.chdir("..")