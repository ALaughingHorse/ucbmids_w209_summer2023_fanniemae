from flask import Flask, render_template, redirect
from dash import html
from dashcomponents.risk_analyzer import risk_app
import dash

app = Flask(__name__)
app_dash = dash.Dash(__name__, server=app, url_base_pathname='/dash_risk_calc/')
app_dash.layout = risk_app

@app.route("/test_dash")
def render_dashboard():
    return redirect('/dash_risk_calc')

@app.route("/")
def flaskapp():
    return render_template("fannie-mae-viewer.html")

@app.route("/riskanalyzer")
def riskanalyzer():
    return redirect('/dash_risk_calc')

@app.route("/exploration")
def exploration():
    return render_template("data-viz-exploration.html")
		
if __name__ == "__main__":
    app.run()
