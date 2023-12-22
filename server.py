from flask import Flask, send_file

app = Flask(__name__)


@app.route("/report")
def serve_report():
    return send_file("report.txt", as_attachment=True)


@app.route("/")
def serve_home():
    return send_file("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
