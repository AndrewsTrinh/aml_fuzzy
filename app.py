import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import skfuzzy.membership as mf
import skfuzzy as fuzz
import math

st.set_page_config(layout='wide')
st.title('Fuzzy Logic rule')
credit_filter = st.sidebar.slider('Deposit Amount', min_value= 1000.00, max_value=100000.00,value=10000.0,step=0.1)
debit_filter = st.sidebar.slider('Withdrawal Amount', min_value= credit_filter*.8, max_value=credit_filter*1.2,value=credit_filter,step=0.1)
date_diff = st.sidebar.slider('Date difference', min_value= 0.00, max_value=3.00,value=1.00,step=1.00)
st.markdown('### Fuzzy rule: The AML scenario is as follows. An account is suspicious if:')
st.markdown('- large value received(>= 10000) and \n - immediate withdraw (within 1-3 days)')

rules = pd.DataFrame(data=[["Low","Low","Very Low",True]],columns=['Credit Amount','Match Score','AML Score',"active"])
rules_select = st.sidebar.data_editor(rules,num_rows="dynamic", column_config={\
    "Credit Amount":st.column_config.SelectboxColumn(options=["Low","Medium","High"]),\
    "Match Score":st.column_config.SelectboxColumn(options=["Low","Medium","High"]),\
    "AML Score":st.column_config.SelectboxColumn(options=["Very Low","Low","Medium","High"])\
})

col1, col2, col3 = st.columns(3)

x_cr = np.arange(0,7.1,0.1)

cr_low = mf.trapmf(x_cr,[0,0,3.7,3.9])
cr_med = mf.trimf(x_cr,[3.7,3.9,4.2])
cr_high = mf.trapmf(x_cr,[3.9,4.2,7,7])

x_m_score = np.arange(0,1.1,0.001)
m_low   = mf.trimf(x_m_score,[0,0,0.5])
m_med   = mf.trimf(x_m_score,[0,0.5,1])
m_high  = mf.trimf(x_m_score,[0.5,1,1])


x_aml = np.arange(0,1,0.001)
x_aml_vl = mf.trimf(x_aml,[0,0,0.25])
x_aml_l = mf.trimf(x_aml,[0,0.25,0.5])
x_aml_m = mf.trimf(x_aml,[0.25,0.5,0.75])
x_aml_h = mf.trimf(x_aml,[0.5,0.75,1])

#Fuzzification
x=math.log(credit_filter,10)

cr_fit = {
    'low':fuzz.interp_membership(x_cr,cr_low,x),
    'medium':fuzz.interp_membership(x_cr,cr_med,x),
    'high':fuzz.interp_membership(x_cr,cr_high,x)
}

abs_change = abs((credit_filter-debit_filter)/credit_filter)
match_factor = ((1-date_diff/3))/0.9+1
    
# x_score = 0.9(1-abs_change/0.2)*(match_factor-1)
if abs_change > 0.2:
    x_score = 0
else:
    x_score = 0.9*(1-abs_change/0.2)*(match_factor-1)
    
m_fit = {
    'low':fuzz.interp_membership(x_m_score,m_low,x_score),
    'med':fuzz.interp_membership(x_m_score,m_med,x_score),
    'high':fuzz.interp_membership(x_m_score,m_high,x_score)
}



with col1:
    y=max([
        fuzz.interp_membership(x_cr,cr_low,x),
        fuzz.interp_membership(x_cr,cr_med,x),
        fuzz.interp_membership(x_cr,cr_high,x)])
    fig = go.Figure()

    # Set axes ranges
    fig.update_xaxes(range=[3, 5])
    fig.update_yaxes(range=[0, 1])
    fig.add_trace(go.Scatter(x=x_cr, y=cr_low,fill='tozeroy',name='Low'))
    fig.add_trace(go.Scatter(x=x_cr, y=cr_med,fill='tozeroy',name='Medium'))
    fig.add_trace(go.Scatter(x=x_cr, y=cr_high,fill='tozeroy',name='High'))
    fig.add_shape(type="line",x0=x,y0=0,x1=x,y1=y,line= dict(width=3))
    fig.update_shapes(dict(xref='x', yref='y'))
    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=0.0,
        xanchor="right",
        x=0.99
    ),title='Log10 of amount received in $ value')
 
    st.plotly_chart(fig,use_container_width=True,)
    
    st.write('Low: {:.2f} Medium: {:.2f} High: {:.2f}'.format(\
                    fuzz.interp_membership(x_cr,cr_low,x),
                    fuzz.interp_membership(x_cr,cr_med,x),
                    fuzz.interp_membership(x_cr,cr_high,x)
                ))
    
    st.write(f'Credit Value: {str(credit_filter)}')
    st.write(f'Credit log value: {x:.2f}')
    
    
with col2:
    y_score = max([
        fuzz.interp_membership(x_m_score,m_low,x_score),
        fuzz.interp_membership(x_m_score,m_med,x_score),
        fuzz.interp_membership(x_m_score,m_high,x_score)
    ])
    
    fig1 = go.Figure()
    # Set axes ranges
    fig1.update_xaxes(range=[0, 1])
    fig1.update_yaxes(range=[0, 1])
    fig1.add_trace(go.Scatter(x=x_m_score, y=m_low,fill='tozeroy',name='Low'))
    fig1.add_trace(go.Scatter(x=x_m_score, y=m_med,fill='tozeroy',name='Medium'))
    fig1.add_trace(go.Scatter(x=x_m_score, y=m_high,fill='tozeroy',name='High'))
    fig1.add_shape(type="line",x0=x_score,y0=0,x1=x_score,y1=y_score,line= dict(width=3))
    fig1.update_shapes(dict(xref='x', yref='y'))
    fig1.update_layout(legend=dict(
        yanchor="bottom",
        y=0.0,
        xanchor="right",
        x=1
    ))

    st.plotly_chart(fig1,use_container_width=True,)
    
    st.write('Low: {:.2f} Medium: {:.2f} High: {:.2f}'.format(\
                    fuzz.interp_membership(x_m_score,m_low,x_score),
                    fuzz.interp_membership(x_m_score,m_med,x_score),
                    fuzz.interp_membership(x_m_score,m_high,x_score)
                ))
    
    st.write('Absolute change: {:.2f} Match factor: {:.2f}'.format(abs_change,match_factor))
    st.write(f'x_score: {x_score:.2f}')
    

with col3:
    fig2 = go.Figure()
        # Set axes ranges
    fig2.update_xaxes(range=[0, 1])
    fig2.update_yaxes(range=[0, 1])
    fig2.add_trace(go.Scatter(x=x_aml, y=x_aml_vl,fill='tozeroy',name='Very Low'))
    fig2.add_trace(go.Scatter(x=x_aml, y=x_aml_l,fill='tozeroy',name='Low'))
    fig2.add_trace(go.Scatter(x=x_aml, y=x_aml_m,fill='tozeroy',name='Medium'))
    fig2.add_trace(go.Scatter(x=x_aml, y=x_aml_h,fill='tozeroy',name='High'))
    # fig2.add_shape(type="line",x0=x_score,y0=0,x1=x_score,y1=y_score,line= dict(width=3))
    fig2.update_shapes(dict(xref='x', yref='y'))
    fig2.update_layout(legend=dict(
        yanchor="bottom",
        y=0.0,
        xanchor="right",
        x=0.99
    ))
    st.plotly_chart(fig2,use_container_width=True,)