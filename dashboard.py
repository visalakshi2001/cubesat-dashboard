import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from datetime import datetime, timedelta

from issues import issuesinfo
import graphviz

COLORS = px.colors.qualitative.Plotly
more_colors = {
    "green": "#4bde9c",
    "red": "#fb8072",
    "amber": "#ffed6f"
}

# ########## TEST SCHEDULE VIEW FUNCTION
def dashschedule():
    # Make a heading of size H2
    st.subheader("Schedule", divider="orange")

    # create two columns of equal size
    top_columns = st.columns([0.7,0.3])

    # call the first column and design the view under
    with top_columns[0]:
        # this column will hold the number of tests scheduled, read data for test programs
        # programs = pd.read_csv("reports/TestPrograms.csv", index_col=0)
        testscheduling = pd.read_csv("reports/Query6_Scheduling 2 copy.csv", index_col=0)

        st.markdown("<h6>Scheduled Test Metrics</h6>", True)
        numTests = sum(pd.notnull(testscheduling['Site']))
        totalTests = len(testscheduling['Site'])
        unscheduledTests = totalTests - numTests
        metriccols = st.columns(3)
        metriccols[0].metric(label="Unscheduled Test Count", value=unscheduledTests, delta=f'Total Tests: {totalTests}')

        upcomingTests = np.asarray(np.where(pd.to_datetime(testscheduling['Start']).dt.date >= datetime.today().date())).size
        metriccols[1].metric(label="Upcoming Tests Count", value=upcomingTests, delta=f'Total Tests: {totalTests}')

        metriccols[2].metric(label="Successful Test Count", value=2, delta=f'Completed Tests: {totalTests-unscheduledTests-upcomingTests}')

        st.write('---')
        # make 4 sub-columns and display the data using col.metric()
        # for i,num in enumerate(testscheduling["num_Tests"]):
        #     metriccols[i].metric(label=programs.iloc[i]["TestProgram"], value=num, delta=f"{num-2} Scheduled")

    # call the second column and insert the issues section from issues.py
    with top_columns[1]:
        issuesinfo(500)
            
    # read the data for test schedule
    testscheduling = pd.read_csv("reports/Query6_Scheduling 2 copy.csv", index_col=0)
    testscheduling["Start"] = pd.to_datetime(testscheduling["Start"])
    testscheduling["End"] = pd.to_datetime(testscheduling["End"])

    # Define a function to extract the week of year
    testscheduling['Week'] = testscheduling['Start'].dt.strftime('%Y-W%U')

    # Creating the Plotly figure for timeline chart of test schedule
    fig = px.timeline(testscheduling, x_start="Start", x_end="End", y="Site", color="VMName", text="VMName", hover_name="VM",
                    category_orders={"Site": sorted(testscheduling['Site'].unique(), key=lambda x: str(x))})

    
    # Update layout to include a dropdown menu for week selection
    week_options = testscheduling['Week'].unique()

    # update the layout with options menu, time-axis scale, etc.
    fig.update_layout(
        title="Test Schedule",
        xaxis_title="Time",
        yaxis_title="Test Site",
        xaxis=dict(
            tickformat="%d %b %Y\n%H:%M",
            range=[testscheduling['Start'].min() - pd.Timedelta(days=1), testscheduling['End'].min() + pd.Timedelta(days=6)],
        ),
        # updatemenus=[{
        #     "buttons": [
        #         {
        #             "args": [
        #                 {"xaxis.range": [testscheduling[testscheduling['Week'] == week]['Start'].min(), testscheduling[testscheduling['Week'] == week]['End'].max()]}
        #             ],
        #             "label": week,
        #             "method": "relayout"
        #         }
        #         for week in week_options
        #     ],
        #     "direction": "down",
        #     "showactive": True,
        #     "x": 0.17,
        #     "xanchor": "left",
        #     "y": 1.15,
        #     "yanchor": "top"
        # }],
        legend=dict(xanchor="left", x=0, y=-0.5, yanchor="bottom", orientation="h"),
    )
    vlinedate = datetime.today().date()
    fig.add_vline(x=datetime(vlinedate.year, vlinedate.month, vlinedate.day).timestamp() * 1000, annotation_text= f"today {vlinedate.month}/{vlinedate.day}")
    
    # insert the figure in the view using streamlit
    top_columns[0].plotly_chart(fig, use_container_width=True)

    

# ########## TEST SCHEDULE VIEW FUNCTION
def dashresults():
    # create a heading of size H2
    st.subheader("Performance", divider="violet")

    # create two columns of sizes 40% and 60%
    top_columns = st.columns([0.4,0.6])

    # call the second column and insert the issues section from issues.py
    with top_columns[1]:
        issuesinfo(150)
    
    # call the first column and design the view under
    with top_columns[0]:
        resultsdocument = pd.read_csv("reports/DocumentSearch.csv", index_col=0)
        verificationcheck = pd.read_csv("reports/Query7_VerificationCheck.csv", index_col=0)
        
        st.markdown("<h6>Test Data Results</h6>", True)

        metricchoice = st.selectbox("Select Test Data Document", 
                                    options=["Payload Test Data Report", "Verification Results"], index=0)

        if metricchoice == "Payload Test Data Report":
            metriccols = st.columns([1, 1.5, 1.5], gap="small") 
            for index,row in resultsdocument.iterrows():
                with metriccols[index]:
                    value = str(row["Value"]) + " " + str(row["Unit"]) if (pd.isna(row["Unit"]) != True) else str(row["Value"])
                    st.metric(label=row["TestData"], value=value, delta=row["TestDataSubject"], help="Test, followed by result value for given test subject")

        if metricchoice == "Verification Results":
            verificationcheck["UnitSymb"] = verificationcheck["Unit"].replace({"percentage": "%"})
            for index,row in verificationcheck.iterrows():
                value = str(row["Value"]) + " " + str(row["UnitSymb"]) if (pd.isna(row["UnitSymb"]) != True) else str(row["Value"])
                st.metric(label=row["MissionReqName"], value=value, delta="Minimum Value: " + str(row["MinValue"]) + str(row["UnitSymb"]),
                          help=f"Test Name: {row['TestName']} \n Test Output: {row['TestOutput']}")
        
        
        st.write(
            """
            <style>
            [data-testid="stMetricDelta"] svg {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    middle_columns = st.columns([0.7, 0.3])

    with middle_columns[0]:
        keycaprates = pd.read_csv("reports/Query5_KeyCapabilities 2.csv", index_col=0)
        keycaprates["UnitSymbols"] = keycaprates["Unit"].map({"percent": "%", "degrees": "deg", "second": "sec", "kilogram": "kg"})

        fig = go.Figure()
        for i in range(len(keycaprates["KCName"])):
            fig.add_trace(go.Scatter(
                x=[keycaprates["Threshold"][i], keycaprates["Objective"][i]],
                y=[keycaprates["KCName"][i], keycaprates["KCName"][i]],
                mode='lines',
                line=dict(color='gray'),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=[keycaprates["Threshold"][i]],
                y=[keycaprates["KCName"][i]],
                mode='markers+text',
                marker=dict(size=10, color="blue"),
                name="Threshold" if i==0 else "",
                showlegend=(i==0),
                text=[f"{keycaprates['Threshold'][i]} {keycaprates['UnitSymbols'][i]}"],
                textposition="bottom center",
                hovertemplate=f" <b> Satisfied by:</b> {keycaprates['SatisfiedBy'][i]}" + ""
            ))
            fig.add_trace(go.Scatter(
                x=[keycaprates["Objective"][i]],
                y=[keycaprates["KCName"][i]],
                mode='markers+text',
                marker=dict(size=10, color="red"),
                name="Objective" if i==0 else "",
                showlegend=(i==0),
                text=[f"{keycaprates['Objective'][i]} {keycaprates['UnitSymbols'][i]}"],
                textposition="top center",
                hovertemplate=f" <b> Satisfied by:</b> {keycaprates['SatisfiedBy'][i]}" + ""
            ))

        fig.update_layout(title="Threshold vs Objective for Each Key Capacities",
                            xaxis_title="Value",
                            yaxis_title="KCName",
                            yaxis=dict(tickmode='linear'),
                            legend=dict(orientation="h", x=0.3, y=10))

        st.plotly_chart(fig, use_container_width=True)
    
    with middle_columns[1]:
        keycaprates["VerificationStatus"] = np.where(pd.notnull(keycaprates["VerificationMethodName"]),  "Verified", "Unverified")
        
        fig = go.Figure(data=[
            go.Bar(name="Satisfied", y=keycaprates["KCName"], x=np.where(pd.notnull(keycaprates["SatisfiedBy"]), 1, 0),
                    orientation="h", marker=dict(color=COLORS[2]), text=keycaprates["SatisfiedBy"]),
            go.Bar(name="Verified", y=keycaprates["KCName"], x=np.where(pd.notnull(keycaprates["VerificationMethodName"]), 1, 0),
                    orientation="h",marker=dict(color=COLORS[0]), text=keycaprates["VerificationMethodName"])
        ])
        fig.update_layout(barmode="stack",
                            title="Key Capabilities Verification and Satisfaction Status")
        fig.update_traces(textposition="inside", textfont_size=16)
        fig.update_xaxes(showticklabels=False)
        st.plotly_chart(fig, True)



##########################################################################################################
# REFERENCES  # 
#  hover templates: https://plotly.com/python/hover-text-and-formatting/ #
#  scatterplot annotations: https://stackoverflow.com/questions/71875067/adding-text-labels-to-a-plotly-scatter-plot-for-a-subset-of-points #
##########################################################################################################

# ########## REQUIREMENTS VIEW FUNCTION
def dashreqs():
    st.subheader("Requirements Summary", divider="orange")
    breakdown = pd.read_csv("reports/cubesatrequirements.csv")
    # breakdown = 

    cols = st.columns([0.7,0.15])

    st.dataframe(breakdown.drop(columns=["Results"]).style. \
                 applymap(lambda x: f'background-color: {more_colors["green"]}' if x == "PASS" \
                           else (
                               f'background-color: {more_colors["red"]}' if x == "FAIL"   
                               else f'background-color: {more_colors["amber"]}'
                           ), 
                          subset=["Verification Status"]). \
                applymap(lambda x: 'color: black'), 
                 use_container_width=True, hide_index=True)
    
    cont = st.container(border=True)
    cont.subheader("Warnings")
    for _, row in breakdown.iterrows():
        req = row["Requirement Name"]
        verified = row["Verified By"]
        satisfied = row["Satisfied By"]
        result = row["Results"]
        status = row["Verification Status"]

        if pd.isna(verified):
            cont.warning(f"Requirement {req} is not verified by any analysis", icon="⚠️")
        if pd.isna(satisfied):
            cont.warning(f"Requirement {req} is not satisfied by any mission element", icon="⚠️")
        if pd.notna(verified) and status != "PASS":
            cont.error(f"Requirement {req} has not PASSED the analysis")

    req_choice = st.selectbox("Select Requirement by Name", options=breakdown["Requirement Name"], index=1)
    target_req = breakdown[breakdown["Requirement Name"] == req_choice]

    dot = graphviz.Digraph(comment='Hierarchy', strict=True)
    for _, row in target_req.iterrows():
            
        reqid = row["Requirement ID"]
        req = row["Requirement Name"]
        verified = row["Verified By"]
        satisfied = row["Satisfied By"]
        result = row["Results"]
        status = row["Verification Status"]

        if pd.notna(reqid):
            dot.node(reqid)
        if pd.notna(req):
            if req not in dot.body:
                dot.node(req)
            dot.edge(reqid, req, label="has name")

        if pd.notna(verified):
            if verified not in dot.body:
                dot.node(verified)
            dot.edge(req, verified, label="verified by")
        
        if pd.notna(satisfied):
            if satisfied not in dot.body:
                dot.node(satisfied)
            dot.edge(req, satisfied, label="satisfied by")
        if pd.notna(result):
            if result not in dot.body:
                dot.node(result)
            dot.edge(verified, result, label="analysis output")
        
        if pd.notna(result) and pd.notna(status):
            if status not in dot.body:
                dot.node(status, shape="box")
            dot.edge(result, status, label="verification status")
            
    cols = st.columns([0.23 ,0.5])
    cols[0].graphviz_chart(dot, True)

    cols[-1].dataframe(target_req.rename({0: "values", 1: "values", 2: "values", 3: "values", 4: "values"}).T.reset_index(). \
        style.applymap(lambda x: 'color: black'), use_container_width=True, hide_index=True)

   