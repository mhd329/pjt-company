from settings import *
from modules import multi_thread_web_bp
from flask import Flask, render_template


app = Flask(__name__)
app.register_blueprint(multi_thread_web_bp)


@app.route("/")
def index():
    return render_template("index.html", cam_number=MAX_WORKERS)


if __name__ == "__main__":
    app.run(port=8080, debug=DEBUG) # 내부 run 코드를 보니 threaded 옵션이 기본으로 되어 있음.