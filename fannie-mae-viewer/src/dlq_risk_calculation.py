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
        self.plot_tb = plot_tb
        
        # Generate the scale plot
        source = pd.DataFrame()
        source['x'] = [self.risk_score]
        source['y'] = [0]
        axis_label_expr = """
            datum.value == -1 ? '<-------------- Very Safe -------------->' : 
            datum.value == -0.5 ? '<---------------- Safe ---------------->' : 
            datum.value == 0 ? '<------------ Moderate ------------>':
            datum.value == 0.5 ? '<--------------- Risky --------------->':
            datum.value == 1 ? '<------------ Very Risky ------------>'
            :''
            """
        self.risk_score_scale_chart = alt.Chart(source,title='Delinquency Risk').mark_circle(size=120).encode(
            x=alt.X('x', title='Risk Level', scale=alt.Scale(domain=[-1.25,1.25]), axis=alt.Axis(labelExpr=axis_label_expr, values=[-1.25, -1, -0.75, -0.5, -0.25, 0 ,0.25, 0.5, 0.75, 1, 1.25])),
            y=alt.Y('y', title='', scale=alt.Scale(domain=[-0.01,0.01]), axis=alt.Axis(labels=False)),
        ).properties(
            width=800,
            height=25
        )

        # Generate the descriptive plot
        if self.risk_score<0:
            temp_plottb = self.plot_tb[self.plot_tb.directions==True]
            temp_plottb['value_direc'] = temp_plottb['values'].apply(lambda x: 'higher' if x>0 else 'lower') 
            temp_plottb['des'] = temp_plottb['value_direc'] + ' ' + temp_plottb['labels']
            description_str = ', '.join(temp_plottb['des'].values)
            subtitle = f"""
            This loan is rated as {self.risk_cat} because it has {description_str} comparing to loans from the same area
            """
        else:
            temp_plottb = self.plot_tb[self.plot_tb.directions==False]
            temp_plottb['value_direc'] = temp_plottb['values'].apply(lambda x: 'higher' if x>0 else 'lower') 
            temp_plottb['des'] = temp_plottb['value_direc'] + ' ' + temp_plottb['labels']
            description_str = ', '.join(temp_plottb['des'].values)
            subtitle = f"""
            This loan is rated as {self.risk_cat} because it has {description_str} comparing to loans from the same area
            """

        chart_title = alt.TitleParams(
            f"Why is this loan catagorized as {self.risk_cat}?",
            subtitle=[subtitle],
        )

        descriptive_chart = alt.Chart(
            self.plot_tb[self.plot_tb.directions==(self.risk_score<0)], title=chart_title
        ).mark_bar(
        ).encode(
            x=alt.X('labels', 
                    title='Loan Attributes',
                    axis=alt.Axis(labelAngle=0)
            ),
            y=alt.Y(
                'values:Q', 
                title='Percentage Delta Vs Area Average',
                axis=alt.Axis(format='%')
                # scale=alt.Scale(domain=[-1,1])
            ),
            color=alt.condition(
                alt.datum.directions,
                alt.value("green"),  # The positive color
                alt.value("red")  # The negative color
            )
        ).properties(
            width=800,
            height=300
        )

        self.descriptive_chart = descriptive_chart
        self.final_chart = alt.vconcat(self.risk_score_scale_chart, self.descriptive_chart)
        return self