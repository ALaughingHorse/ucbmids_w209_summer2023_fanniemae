import pandas as pd
import numpy as np
import altair as alt
from dlq_risk_calcuation import LoanDlqRisks
from panel.interact import interact
import streamlit as st
import pickle

from sqlalchemy import URL, create_engine, text
alt.data_transformers.disable_max_rows()

hostname = 'database-3.cluster-cgldqbnitk50.us-east-1.rds.amazonaws.com'
username = 'postgres'
password = 'cas_analytics'
database = 'postgres'

url_object = URL.create(
    "postgresql",
    username=username,
    password=password,  # plain (unescaped) text
    host=hostname,
    database=database,
)

engine = create_engine(url_object)
# load the data
query = f"""
WITH loan_stats AS (
    SELECT 
        "Loan Identifier",
        "Original Interest Rate",
        "Original UPB",
        "Original Loan to Value Ratio (LTV)",
        "Original Combined Loan to Value Ratio (CLTV)",
        "Borrower Credit Score At Issuance",
        "Debt-To-Income (DTI)",
        "Zip Code Short",
        ROUND(
            1.0*SUM(CASE WHEN "Current Loan Delinquency Status" > 0 THEN 1 ELSE 0 END)/COUNT("Monthly Reporting Period"),
        2
        ) AS pct_dlq_marks
    FROM Cas.ref  
    GROUP BY 
        "Loan Identifier",
        "Original Interest Rate",
        "Original UPB",
        "Original Loan to Value Ratio (LTV)",
        "Original Combined Loan to Value Ratio (CLTV)",
        "Borrower Credit Score At Issuance",
        "Debt-To-Income (DTI)",
        "Zip Code Short"
)

SELECT * FROM loan_stats
"""
@st.cache_data
def get_loan_data_from_db():
    return pd.DataFrame(engine.connect().execute(text(query)))
df = get_loan_data_from_db()

with open('outputs/weights.pkl', 'rb') as file:
    weights = pickle.load(file)

# Adding title
st.title('Risk Analyzer For Mortgage Delinquency')
interest_rate=st.number_input('What is the interest rate for this loan? Enter the percentage (e.g. 2% : 2.0)', value=3.5)
upb=st.number_input('What is the total loan amount in dollars?', value=20000)
ltv=st.number_input('What is the Loan-to-Value ratio? Enter percentage number (e.g. 45% -> 45)', value=80)
credit_score=st.number_input('What is the FICO score for the main borrower?',value=780)
dti=st.number_input('What is the Debt-To-Income ratio? Enter percentage (e.g. 20% -> 20)', value=22)
zipcode=st.selectbox('What is the short Zipcode where the property is located at?', set(df['Zip Code Short']))

if st.button('Analyze'):
    dlqr = LoanDlqRisks(
            interest_rate,
            upb,
            ltv,
            credit_score,
            dti,
            zipcode
        ).get_relative_stats(ref_table=df).generate_risk_summary(weight_params=weights)
    
    st.write(
        f"According to the calculation, the risk level of this loan going delinquent is: {dlqr.risk_cat}"
    )

    st.altair_chart(
        dlqr.diag_chart, 
        use_container_width=True
    )