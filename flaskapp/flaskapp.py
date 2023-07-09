from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def flaskapp():
    file="about9.jpg"
    return render_template("main_page.html",file=file)

@app.route("/riskanalyzer")
def riskanalyzer():
	return render_template("risk-analyzer.html")
	
if __name__ == "__main__":
    app.run()
