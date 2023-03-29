from flask import Flask, session
from flask import render_template, request, abort 
from werkzeug.utils import secure_filename
import os
from flask_session import Session
import string 

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.txt']
app.config['UPLOAD_PATH'] = 'uploads'
app.secret_key = '6318262as1328X1172630541das24674320c2'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def remove_punct(s: str) -> str:
    """
    Removes punctuation from given string s. Returns string.
    :param s: input string with punctuation
    :type s: str
    :return: string without punctuation
    """
    return s.translate(str.maketrans('', '', string.punctuation))


def process_data(files: list, processed_data: dict) -> dict:
    """
    Loops through given text files, splits them into words and returns them in given processed_data dictionary.
    Keys of dict - file names. Values - text tokens. Destructive func.
    :param files: input list containing text files
    :type files: list
    :param processed_data: input dictionary to store processed data
    :type processed_data: dict
    :return: modified given processed_data dict
    """

    for file in files:
        file_name = file.filename
        file_lines = file.readlines()
        for line in file_lines:
                line = line.decode("utf-8") 
                line_tokens = [remove_punct(word.lower().strip()) for word in line.split()] 
                if file_name in processed_data:
                    processed_data[file_name].extend(line_tokens)
                else:
                    processed_data[file_name] = line_tokens
    return processed_data



@app.route("/")
def index():
    return render_template("index.html")
    

@app.route("/", methods=["POST", "GET"])
def upload():
    """
    After post HTTP request method checks file extensions and sizes. If permitted uploads files and processes them.
    Processed data is then stored as value for session's processed_data key.
    :return: renders html template with listed uploaded files
    """
    if request.method == "POST":
        uploaded_files = request.files.getlist("file[]")
        processed_data = dict()
        for file in uploaded_files:
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)

        if uploaded_files:
            file_names = [file.filename for file in uploaded_files]
            processed_data = process_data(uploaded_files, processed_data)
            session["processed_data"] = processed_data
            return render_template("search_page.html", uploaded_files_names=file_names)


def search_texts(q_word: str, processed_data:dict, window_size:int, multiply_const=19) -> tuple:
    """
    Loops through all keys and values in processed_data dict and finds all occurences of q_word str.
    :param q_word: query word string
    :type q_word: str
    :param processed_data: dict with file names as keys and token lists as values
    :type processed_data: dict
    :param window_size: int number of displayed tokens left and right of given q_word
    :type window_size: int
    :param multiply_const: int multiplying window_size, used to set bigger window size
    :type multiply_const: int
    :return: tuple of: 0. snippets containing q_word occurances 1. bigger text chunks containing q_word
    """
    snippets = dict()
    
    for k, v in processed_data.items():
        q_word = q_word.lower()
        if q_word in v:
            indices = [i for i, x in enumerate(v) if x == q_word]
            for index in indices:
                window_size = int(window_size) if window_size else 3
                prevalue = " ".join(v[index - window_size:index])
                postvalue = " ".join(v[index + 1: index + window_size + 1])
                value = (prevalue, postvalue)
                if k in snippets:
                    snippets[k].append(value)
                    
                else:
                    snippets[k] = [value]
                    

    return snippets


@app.route("/search", methods=["POST", "GET"])
def search():
    """
    Searches all occurences of query word in texts saved in session and renders html template.
    """
    processed_data = session.get("processed_data", None)
    q_word = request.args.get("q_word")
    window_size = request.args.get("window_size")
    snippets = search_texts(q_word, processed_data, window_size)
    return render_template("search_results.html", snippets=snippets, q_word=q_word)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
