import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import altair as alt
import pandas as pd
import dash_bootstrap_components as dbc
from src.dlq_risk_calculation import LoanDlqRisks
import pickle
df = pd.read_csv('dashcomponents/loan_data.csv')
with open('dashcomponents/weights.pkl', 'rb') as file:
    weights = pickle.load(file)

risk_app = \
    html.Div(children=[
    html.Header(children=[
        html.Title("Fannie Mae Viewer"),
        html.Meta(name="viewport", content="width=device-width, initial-scale=1"),
        html.Link(rel="stylesheet", href="/static/style.css"),
        html.Link(rel="preconnect", href="https://fonts.googleapis.com"),
        html.Link(rel="preconnect", href="https://fonts.gstatic.com"),
        html.Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Lato:wght@700&display=swap")
    ]),
    html.Div(children=[
        # HEADER SECTION
        html.Div(className="header", children=[
            html.Div(className="container", children=[
                html.Div(className="heading", children=[
                    html.Div(className="logo", children=[
                        html.H1(children=[
                            html.A("Fannie Mae Viewer", href="/fannie-mae-viewer/", title="Fannie Mae Viewer")
                        ], title="Fannie Mae Viewer")
                    ]),
                    html.Div(className="menu", children=[
                        html.Ul(children=[
                            html.Li(html.A("Analyze", href="#", title="Analyze")),
                            html.Li(html.A("Explore", href="/fannie-mae-viewer/exploration", title="Explore"))
                        ])
                    ])
                ])
            ])
        ]),

        # BANNER SECTION
        html.Div(className="banner row", children=[
            html.Div(className="container", children=[
                html.Div(className="content", children=[
                    html.Div(className="input-container", children=[
                        html.Div(className="two", children=[
                            html.H1("Risk Analyzer For Mortgage Delinquency")
                        ]),
                        html.Div(className="input-question", children=[
                            html.Label("Interest Rate (e.g. 2% : 2.0)"),
                            dcc.Input(type="text", className="input-field", name="question-1", id="interest_rate", value=2.0)
                        ]),
                        html.Div(className="input-question", children=[
                            html.Label("Loan Amount ($)"),
                            dcc.Input(type="text", className="input-field", name="question-2", id="loan_amount", value = 250000)
                        ]),
                        html.Div(className="input-question", children=[
                            html.Label("Loan-to-Value Ratio (e.g. 45% -> 45)"),
                            dcc.Input(type="text", className="input-field", name="question-3", id="ltv", value=45)
                        ]),
                        html.Div(className="input-question", children=[
                            html.Label("Main borrower FICO score"),
                            dcc.Input(type="text", className="input-field", name="question-4", id="fico", value=750)
                        ]),
                        html.Div(className="input-question", children=[
                            html.Label("Debt-To-Income ratio (e.g. 20% -> 20)"),
                            dcc.Input(type="text", className="input-field", name="question-5", id="dti", value=22)
                        ]),
                        html.Div(className="input-question", children=[
                            html.Label("ZipCode"),
                            dcc.Input(type="text", className="input-field", name="question-6", id="zipcodeshort", value=000)
                            # dcc.Dropdown(options=list(set(df['Zip Code Short'])),className="input-field", id="zipcodeshort", value=0)
                        ]),
                        
                        html.Div(className="btn", children=[
                            html.Button('Get Risk', id='get_risk', n_clicks=0)
                        ])
                    ])
                ]),
                html.Div([
                    html.Iframe(
                        id='risk-chart',
                        style={'border-width': '0', 'width': '1500px', 'height': '600px'}
                    )
                ])
            ])
        ]),

        # # RESULTS SECTION
        # html.Div(className="banner row", children=[
        #     html.Div(className="container", children=[
        #         html.Div(className="content", children=[
        #             html.Div(className='input-container', children=[
        #                 html.Iframe(
        #                     id='risk-chart',
        #                     style={'border-width': '0', 'width': '100%', 'height': '100%'}
        #                 )
        #             ])
        #         ])
        #     ])
        # ]),

        # FOOTER SECTION
        html.Div(className="footer row", children=[
            html.Div(className="container", children=[
                html.Div(className="footer-inner", children=[
                    html.P("Josh Fram • Andre Gigena • Marshal Ma • Sudhir Suvva")
                ])
            ])
        ])
    ])
])

"""
Callbacks
"""
@dash.callback(
    Output('risk-chart', 'srcDoc'),
    [Input('get_risk', 'n_clicks')],
    [dash.dependencies.State('interest_rate', 'value'),
     dash.dependencies.State('loan_amount', 'value'),
     dash.dependencies.State('ltv', 'value'),
     dash.dependencies.State('fico', 'value'),
     dash.dependencies.State('dti', 'value'),
     dash.dependencies.State('zipcodeshort', 'value')]
)
def update_chart(n_clicks, interest_rate, total_loan_amount, loan_to_value, fico_score, dti_ratio, zipcode):
    print('callback fired')
    dlqr = LoanDlqRisks(
            float(interest_rate),
            float(total_loan_amount),
            float(loan_to_value),
            float(fico_score),
            float(dti_ratio),
            zipcode
        ).get_relative_stats(ref_table=df).generate_risk_summary(weight_params=weights)
    return dlqr.final_chart.to_html()