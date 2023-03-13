# seghegfa
<h1>Seghegfa search engine</h1>

The Seghegfa application is a python program using the flask library that is used to search for a specified word in uploaded text documents. 
Each document is uploaded on the server side and split into tokens. 
The processed data is stored in the session. 
Subsequently, all texts are tested for the presence of the searched word; if the word is found, the result is presented to the user in the form of an html page containing the word and its surroundings with an adjustable window size. 
The program finds all occurrences of the word in the document. Individual occurrences are clickable, and after clicking, the user will be shown the found word in the wider context of the document.
