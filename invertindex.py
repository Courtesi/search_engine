import json, os

os.chdir(os.getcwd() + "/DEV")
print(os.getcwd())
for domain in os.listdir(os.getcwd()):
  try:
    print(domain)
    os.chdir(domain)
    print(f"{len(os.listdir(os.getcwd()))} files")
    print("----------\n")
    os.chdir("..")
  except:
    print(f"Skipped non-directory: {domain}")