** All testing was done on MacOS, so there is a possibility of incompatibility with Windows systems

SET-UP REQUIREMENTS
     - DEV folder must be in the same directory as main.py
     - Ensure the following are installed on your system:
        1) bs4 (w/ lxml parser)
        2) nltk

BUILDING THE INDEX
     - To build the necessary indices and files to configure the search system,
       ensure the buildIndex boolean in the __name__== "__main__" block is set to True
     - Launch main.py and wait a few minutes for the indexing to complete

USING SEARCH
     - Once index is completed and execution stops on its own after a few seconds, 
       set buildIndex to False and relaunch main.py
     - Type your search query in the console followed by the return/enter key
     - If you want to stop execution, hit the return/enter key as the query
