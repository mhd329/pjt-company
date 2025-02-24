import os
import modules
from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    return Response()

if __name__ == "__main__":
    app.run(port=8080, debug=os.getenv("DEBUG") == "True") # 내부 run 코드를 보니 threaded 옵션이 기본으로 되어 있어 인자에서 뺐음.