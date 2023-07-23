from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def flaskapp():
    return render_template("fannie-mae-viewer.html")

@app.route("/riskanalyzer")
def riskanalyzer():
    return render_template("risk-analyzer.html")

@app.route("/getrisk", methods=["GET", "POST"])
def getrisk():
    return render_template("risk-analyzer-results.html")

@app.route("/exploration")
def exploration():
    return render_template("data-viz-exploration.html")
		
if __name__ == "__main__":
    app.run()
