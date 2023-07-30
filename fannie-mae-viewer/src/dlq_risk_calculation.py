import pandas as pd
import numpy as np
import altair as alt

def sigmoid(x):
    """Calculate the sigmoid of x."""
    return 1 / (1 + math.exp(-x))

class LoanDlqRisks:
    def __init__(self, interest_rate, upb, ltv, credit_score, dti, zipcode):
        """
        Obtain the loan information
        ------Parameters
        interest_rate: interest rate at loan
        upb: Unpaid Priciple Balance (loan amount)
        ltv: Loan to Value ratio
        credit_score: credit_score
        dti: Debt to income
        zipcode: First 3 digits of the zip
        """
        self.int_rate = interest_rate
        self.upb = upb
        self.ltv = ltv
        self.credit_score = credit_score
        self.dti = dti
        self.zipcode = zipcode
    
    def get_relative_stats(self, ref_table):
        """
        Given a reference table of all the available loan data, calculate the relative percentage delta between
        the target loan and the loans of the same zip code
        """
        # Filter the reference table for a specific zipcode
        filtered_ref_table = ref_table[ref_table['Zip Code Short']==self.zipcode]
        
        # If we have less than 50 records in the same area, use all data instead
        if filtered_ref_table.shape[0]<50:
            filtered_ref_table = ref_table
            print(f'Too few samples for zipcode starting {self.zipcode}, using all data instead')
        
        # Calculate the average values
        self.zip_avg_int_rate = np.mean(filtered_ref_table['Original Interest Rate'])
        self.zip_avg_upb = np.mean(filtered_ref_table['Original UPB'])
        self.zip_avg_ltv = np.mean(filtered_ref_table['Original Loan to Value Ratio (LTV)'])
        self.zip_avg_credit_score = np.mean(filtered_ref_table['Borrower Credit Score At Issuance'])
        self.zip_avg_dti = np.mean(filtered_ref_table['Debt-To-Income (DTI)'])
        
        # calculate the percentage delta between the input value and the average
        self.pct_d_int_rate = (self.int_rate - self.zip_avg_int_rate)/self.zip_avg_int_rate
        self.pct_d_upb = (self.upb - self.zip_avg_upb)/self.zip_avg_upb
        self.pct_d_ltv = (self.ltv - self.zip_avg_ltv)/self.zip_avg_ltv
        self.pct_d_credit_score = (self.credit_score - self.zip_avg_credit_score)/self.zip_avg_credit_score
        self.pct_d_dti = (self.dti - self.zip_avg_dti)/self.zip_avg_dti
        
        return self
    
    def generate_risk_summary(self, weight_params):
        if self.pct_d_int_rate is None:
            print('Percentage delta not found, run .get_relative_stats() first')
            return self
        
        # # Calculate the weighted sum of the scores
        self.risk_score = np.sum(
            [
                self.pct_d_int_rate * weight_params['Original Interest Rate'],
                self.pct_d_upb * weight_params['Original UPB'],
                self.pct_d_ltv * weight_params['Original Loan to Value Ratio (LTV)'],
                self.pct_d_credit_score * weight_params['Borrower Credit Score At Issuance'],
                self.pct_d_dti * weight_params['Debt-To-Income (DTI)']
            ]
        )/abs(sum(list(weight_params.values())))
        
        # self.risk_score = sigmoid(self.risk_score_weighted_sum)
        # self.risk_score = np.mean([
        #     self.pct_d_credit_score,
        #     self.pct_d_dti,
        #     self.pct_d_int_rate,
        #     self.pct_d_ltv,
        #     self.pct_d_upb
        # ])

        # transform the score into categories
        if self.risk_score <= -0.75:
            self.risk_cat = 'Very Safe'
        elif self.risk_score <= -0.25:
            self.risk_cat = 'Safe'
        elif self.risk_score <= 0.25:
            self.risk_cat = 'Moderate'
        elif self.risk_score <= 0.75:
            self.risk_cat = 'Risky'
        else:
            self.risk_cat = 'Very Risky'
        
        # Create the plot
        plot_tb = pd.DataFrame()
        
        # Need to Ensure same order as the values in the weights parameter
        plot_tb['labels'] = ['Interest Rate', 'Loan Amount', 'LTV', 'FICO', 'DTI']
        plot_tb['values'] = [
            self.pct_d_int_rate,
            self.pct_d_upb,
            self.pct_d_ltv,
            self.pct_d_credit_score,
            self.pct_d_dti
        ]
        
        # The model predicts the probability of delinquent, thus different direction compared to the weight is good
        plot_tb['directions'] = (plot_tb['values'] * np.array(list(weight_params.values())))<0
        
        # Plot
        self.diag_chart = alt.Chart(
            plot_tb, title=f'Loan Attributes Compared to Local Avearge (Shortzip:{self.zipcode})'
        ).mark_bar(
        ).encode(
            x=alt.Y(
                'values:Q', 
                title='Percentage Delta Vs Area Average',
                axis=alt.Axis(format='%'),
                scale=alt.Scale(domain=[-1,1])
            ),
            y=alt.X('labels', 
                    title='Loan Attributes'
            ),
            color=alt.condition(
                alt.datum.directions,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            )
        )
        return self