'''TODO'''

import string
import pycountry
import statistics
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from covit19.covid19indiaorg import Covid19indiaorg

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

def get_data():
    '''TODO'''

    total_counter = 0
    ignored_counter = 0
    covid19indiaorg = Covid19indiaorg()

    # Create Database
    database = {
        "Summary" : {
            "total_count": 0,
            "transmition_types": {},
            "increments": {},
            "outcome": {
                "avg_recovered_days": 0,
                "avg_deceased_days": 0,
                "tmp_all_recovered_days": [],
                "tmp_all_deceased_days": []
            }
        }
    }

    # False positive counters
    false_positives_counter_transmission_types = 0

    for item in covid19indiaorg.get_raw_data():
        # Ignore the in-correct data
        if item["detectedstate"] == "":
            ignored_counter += 1
            continue

        total_counter += 1

        # Get more data for transition types from notes and backupnotes
        transmition_type = item["typeoftransmission"]
        if transmition_type == "":
            if item["notes"] != "":
                transmition_type = item["notes"]
            elif item["backupnotes"] != "":
                transmition_type = item["backupnotes"]
            else:
                transmition_type = "Unknown"

            # Imported
            for country in list(pycountry.countries):
                if country.name.lower() in transmition_type.lower():
                    transmition_type = "Possible Imported"
            if ("Dubai").lower() in transmition_type.lower():
                transmition_type = "Possible Imported"
            if ("Iran").lower() in transmition_type.lower():
                transmition_type = "Possible Imported"
            if ("Foreign").lower() in transmition_type.lower():
                transmition_type = "Possible Imported"
            
            # Delhi Religious Conference
            if ("Delhi Religious Conference").lower() in transmition_type.lower():
                transmition_type = "NTJ Religious Conference"
            if ("Congregation").lower() in transmition_type.lower():
                transmition_type = "NTJ Religious Conference"
            if ("Religious").lower() in transmition_type.lower():
                transmition_type = "NTJ Religious Conference"
            
            # Local
            if ("Local").lower() in transmition_type.lower():
                transmition_type = "Local"
            if ("Contact").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Father").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Mother").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Husband").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Wife").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Daughter").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Son").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Family").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Friend").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Roommate").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("Domestic").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            if ("No").lower() in transmition_type.lower() and ("Travel").lower() in transmition_type.lower() and ("History").lower() in transmition_type.lower():
                transmition_type = "Possible Local"
            for subdivision in pycountry.subdivisions.get(country_code='IN'):
                if subdivision.name.lower() in transmition_type.lower():
                    transmition_type = "Possible Local"

            # Unknown
            if ("Details Awaited").lower() in transmition_type.lower():
                transmition_type = "Unknown"
            if ("Not Known").lower() in transmition_type.lower():
                transmition_type = "Unknown"

        # More high level groupping on transmition types
        if transmition_type == "NTJ Religious Conference":
            transmition_type = "Local"
        elif transmition_type == "Local":
            transmition_type = "Local"
        elif transmition_type == "Possible Local":
            transmition_type = "Local"
        elif transmition_type == "Imported":
            transmition_type = "Imported"
        elif transmition_type == "Possible Imported":
            transmition_type = "Imported"
        elif transmition_type == "TBD":
            transmition_type = "Unknown"
        elif transmition_type == "Unknown":
            transmition_type = "Unknown"
        else:
            transmition_type = "Unknown"
            false_positives_counter_transmission_types += 1

        # Get the avg days of outcome
        if item["currentstatus"] == "Recovered" or item["currentstatus"] == "Deceased":
            dateannounced = datetime.strptime(item["dateannounced"], "%d/%m/%Y")
            statuschangedate = datetime.strptime(item["statuschangedate"], "%d/%m/%Y")
            delta_days = (statuschangedate - dateannounced).days
            if item["currentstatus"] == "Recovered":
                database["Summary"]["outcome"]["tmp_all_recovered_days"].append(delta_days)
            if item["currentstatus"] == "Deceased":
                database["Summary"]["outcome"]["tmp_all_deceased_days"].append(delta_days)

        # Create state wise transmition types DB
        if item["detectedstate"] not in database:
            database[item["detectedstate"]] = {
                "total_count": 0,
                "transmition_types": {}
            }
        if transmition_type not in database[item["detectedstate"]]["transmition_types"]:
            database[item["detectedstate"]]["transmition_types"][transmition_type] = {
                "total_count": 0
            }
        database[item["detectedstate"]]["total_count"] += 1
        database[item["detectedstate"]]["transmition_types"][transmition_type]["total_count"] += 1
        if item["currentstatus"] not in database[item["detectedstate"]]["transmition_types"][transmition_type]:
            database[item["detectedstate"]]["transmition_types"][transmition_type][item["currentstatus"]] = 0
        database[item["detectedstate"]]["transmition_types"][transmition_type][item["currentstatus"]] += 1
        
        # Create a summary transmition types DB
        if transmition_type not in database["Summary"]["transmition_types"]:
            database["Summary"]["transmition_types"][transmition_type] = {
                "total_count": 0
            }
        database["Summary"]["total_count"] += 1
        database["Summary"]["transmition_types"][transmition_type]["total_count"] += 1
        if item["currentstatus"] not in database["Summary"]["transmition_types"][transmition_type]:
            database["Summary"]["transmition_types"][transmition_type][item["currentstatus"]] = 0
        database["Summary"]["transmition_types"][transmition_type][item["currentstatus"]] += 1

        # Create a summary transmition types increments DB by date
        if transmition_type not in database["Summary"]["increments"]:
            database["Summary"]["increments"][transmition_type] = {}
        if item["dateannounced"] not in database["Summary"]["increments"][transmition_type]:
            database["Summary"]["increments"][transmition_type][item["dateannounced"]] = {
                "count": 0,
                "states": {}
            }
        database["Summary"]["increments"][transmition_type][item["dateannounced"]]["count"] += 1
        if item["detectedstate"] not in database["Summary"]["increments"][transmition_type][item["dateannounced"]]["states"]:
            database["Summary"]["increments"][transmition_type][item["dateannounced"]]["states"][item["detectedstate"]] = 0
        database["Summary"]["increments"][transmition_type][item["dateannounced"]]["states"][item["detectedstate"]] += 1


    # Renders the average
    database["Summary"]["outcome"]["avg_recovered_days"] = round(statistics.mean(database["Summary"]["outcome"]["tmp_all_recovered_days"]))
    database["Summary"]["outcome"]["avg_deceased_days"] = round(statistics.mean(database["Summary"]["outcome"]["tmp_all_deceased_days"]))
    del database["Summary"]["outcome"]["tmp_all_recovered_days"]
    del database["Summary"]["outcome"]["tmp_all_deceased_days"]

    # Database is ready now analyze
    #print("[DEBUG]: Ignored Count - %d" % ignored_counter)
    #print("[DEBUG]: Summary Count - %d" % total_counter)
    #error_tramission_type_detection = (false_positives_counter_transmission_types / total_counter) * 100
    #print("[DEBUG]: Error in Tramission Type Detection - %.2f percent" % error_tramission_type_detection)

    # Create recovered and deceased Database
    recovered_data = {}
    for row in covid19indiaorg.get_recovered_data():
        if row[0] == "date":
            continue
        recovered_data[row[0]] = int(row[1])
    deceased_data = {}
    for row in covid19indiaorg.get_deceased_data():
        if row[0] == "date":
            continue
        deceased_data[row[0]] = int(row[1])

    return {"database": database, "recovered_data": recovered_data, "deceased_data": deceased_data}

# Get the Database
all_data = get_data()
database = all_data["database"]
recovered_data = all_data["recovered_data"]
deceased_data = all_data["deceased_data"]

# Create Summary Charts Data
summary_pie_chart_labels = []
summary_pie_chart_values = []
summary_table_chart_status_considered = ["Imported", "Local", "Unknown"]
summary_table_chart_status_values = {
    "Hospitalized" : [0, 0, 0, 0],
    "Recovered": [0, 0, 0, 0],
    "Deceased": [0, 0, 0, 0]
}
summary_line_chart_dates_raw = []
summary_line_chart_dates_iso = []
summary_line_chart_values = {
    "Total": [],
    "TotalHospitalized": [],
    "Imported": [],
    "Local": [],
    "Unknown": [],
    "StateWise": {}
}
for item in database["Summary"]["transmition_types"]:
    summary_pie_chart_labels.append(item)
    summary_pie_chart_values.append(database["Summary"]["transmition_types"][item]["total_count"])

    if item in summary_table_chart_status_considered:
        if "Hospitalized" in database["Summary"]["transmition_types"][item]:
            summary_table_chart_status_values["Hospitalized"][summary_table_chart_status_considered.index(item)] = database["Summary"]["transmition_types"][item]["Hospitalized"]
        if "Recovered" in database["Summary"]["transmition_types"][item]:
            summary_table_chart_status_values["Recovered"][summary_table_chart_status_considered.index(item)] = database["Summary"]["transmition_types"][item]["Recovered"]
        if "Deceased" in database["Summary"]["transmition_types"][item]:
            summary_table_chart_status_values["Deceased"][summary_table_chart_status_considered.index(item)] = database["Summary"]["transmition_types"][item]["Deceased"]
for item in database["Summary"]["increments"]:
    for date in database["Summary"]["increments"][item]:
        if date not in summary_line_chart_dates_raw:
            summary_line_chart_dates_raw.append(date)
for date in summary_line_chart_dates_raw:
    total_in_a_date = 0
    for item in summary_line_chart_values:
        if item == "Total" or item == "TotalHospitalized" or item == "StateWise":
            continue
        if date in database["Summary"]["increments"][item]:
            if len(summary_line_chart_values[item]) > 0:
                summary_line_chart_values[item].append(
                    summary_line_chart_values[item][-1] + database["Summary"]["increments"][item][date]["count"]
                )
                total_in_a_date += database["Summary"]["increments"][item][date]["count"]
            else:
                summary_line_chart_values[item].append(
                    database["Summary"]["increments"][item][date]["count"]
                )
            for state in database["Summary"]["increments"][item][date]["states"]:
                if state not in summary_line_chart_values["StateWise"]:
                    summary_line_chart_values["StateWise"][state] = {}
                if date not in summary_line_chart_values["StateWise"][state]:
                    summary_line_chart_values["StateWise"][state][date] = {}
                if item not in summary_line_chart_values["StateWise"][state][date]:
                    summary_line_chart_values["StateWise"][state][date][item] = 0
                summary_line_chart_values["StateWise"][state][date][item] += database["Summary"]["increments"][item][date]["states"][state]
        else:
            if len(summary_line_chart_values[item]) > 0:
                summary_line_chart_values[item].append(
                    summary_line_chart_values[item][-1]
                )
            else:
                summary_line_chart_values[item].append(
                    0
                )
    if len(summary_line_chart_values["Total"]) > 0:
        summary_line_chart_values["Total"].append(
            summary_line_chart_values["Total"][-1] + total_in_a_date
        )
    else:
        summary_line_chart_values["Total"].append(
            total_in_a_date
        )
    date_obj = datetime.strptime(date, "%d/%m/%Y")
    summary_line_chart_dates_iso.append(
        date_obj.isoformat()
    )

summary_line_chart_other_values = {
    "Recovered": [],
    "Deceased": [],
    "Active": []
}
# Create a merged data with total reported and recovered and deceased data
for date in recovered_data:
    date_formatted = datetime.strptime(date, "%d-%b-%y").strftime("%d/%m/%Y")
    if date_formatted not in summary_line_chart_dates_raw:
        print("Ignoring Date from Recovered: {}".format(date_formatted))
for date in deceased_data:
    date_formatted = datetime.strptime(date, "%d-%b-%y").strftime("%d/%m/%Y")
    if date_formatted not in summary_line_chart_dates_raw:
        print("Ignoring Date from Deceased: {}".format(date_formatted))
for date in summary_line_chart_dates_raw:
    date_formatted = datetime.strptime(date, "%d/%m/%Y").strftime("%d-%b-%y")
    if date_formatted in recovered_data:
        if len(summary_line_chart_other_values["Recovered"]) > 0:
            summary_line_chart_other_values["Recovered"].append(
                summary_line_chart_other_values["Recovered"][-1] + recovered_data[date_formatted]
            )
        else:
            summary_line_chart_other_values["Recovered"].append(
                summary_line_chart_other_values["Recovered"][-1]
            )
    else:
        if len(summary_line_chart_other_values["Recovered"]) > 0:
            summary_line_chart_other_values["Recovered"].append(
                summary_line_chart_other_values["Recovered"][-1]
            )
        else:
            summary_line_chart_other_values["Recovered"].append(
                0
            )
    if date_formatted in deceased_data:
        if len(summary_line_chart_other_values["Deceased"]) > 0:
            summary_line_chart_other_values["Deceased"].append(
                summary_line_chart_other_values["Deceased"][-1] + deceased_data[date_formatted]
            )
        else:
            summary_line_chart_other_values["Deceased"].append(
                summary_line_chart_other_values["Deceased"][-1]
            )
    else:
        if len(summary_line_chart_other_values["Deceased"]) > 0:
            summary_line_chart_other_values["Deceased"].append(
                summary_line_chart_other_values["Deceased"][-1]
            )
        else:
            summary_line_chart_other_values["Deceased"].append(
                0
            )
    summary_line_chart_other_values["Active"].append(
        summary_line_chart_values["Total"][summary_line_chart_dates_raw.index(date)] - (
            summary_line_chart_other_values["Deceased"][-1] + summary_line_chart_other_values["Recovered"][-1]
        )
    )

# Create State wise Charts Data
all_state_dropdown = []
for item in database:
    if item == "Summary":
        continue
    all_state_dropdown.append(
        {'label': item, 'value': item}
    )
all_state_dropdown = sorted(all_state_dropdown, key = lambda i: i['label'])

# Create the figures to plot
summary_pie_fig = go.Figure(data=[go.Pie(labels=summary_pie_chart_labels, values=summary_pie_chart_values)])
summary_pie_fig.update_layout(title_text='Overall Transmition Types')
summary_column_fig = go.Figure()
summary_column_fig.add_trace(go.Bar(name='Hospitalized', x=summary_table_chart_status_considered, y=summary_table_chart_status_values["Hospitalized"]))
summary_column_fig.add_trace(go.Bar(name='Recovered', x=summary_table_chart_status_considered, y=summary_table_chart_status_values["Recovered"]))
summary_column_fig.add_trace(go.Bar(name='Deceased', x=summary_table_chart_status_considered, y=summary_table_chart_status_values["Deceased"]))
summary_column_fig.update_layout(title_text='Overall Status by Transmition Types', barmode='stack')
summary_historical_line = go.Figure()
summary_historical_line.add_trace(go.Scatter(name="Imported", x=summary_line_chart_dates_iso, y=summary_line_chart_values["Imported"], mode='lines+markers'))
summary_historical_line.add_trace(go.Scatter(name="Local", x=summary_line_chart_dates_iso, y=summary_line_chart_values["Local"], mode='lines+markers'))
summary_historical_line.add_trace(go.Scatter(name="Unknown", x=summary_line_chart_dates_iso, y=summary_line_chart_values["Unknown"], mode='lines+markers'))
summary_historical_line.update_layout(title_text='Overall History of Transmition Types')
summary_historical_line.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=7, label="7d", step="day", stepmode="backward"),
            dict(count=14, label="14d", step="day", stepmode="backward"),
            dict(count=21, label="21d", step="day", stepmode="backward"),
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=2, label="2m", step="month", stepmode="backward"),
            dict(count=3, label="3m", step="month", stepmode="backward"),
            dict(count=4, label="4m", step="month", stepmode="backward"),
            dict(label="R", step="all")
        ])
    )
)
summary_historical_total_line = go.Figure()
summary_historical_total_line.add_trace(go.Scatter(name="Total", x=summary_line_chart_dates_iso, y=summary_line_chart_values["Total"], mode='lines+markers'))
summary_historical_total_line.add_trace(go.Scatter(name="Deceased", x=summary_line_chart_dates_iso, y=summary_line_chart_other_values["Deceased"], mode='lines+markers'))
summary_historical_total_line.add_trace(go.Scatter(name="Recovered", x=summary_line_chart_dates_iso, y=summary_line_chart_other_values["Recovered"], mode='lines+markers'))
summary_historical_total_line.add_trace(go.Scatter(name="Active", x=summary_line_chart_dates_iso, y=summary_line_chart_other_values["Active"], mode='lines+markers'))
summary_historical_total_line.update_layout(title_text='Overall History')
summary_historical_total_line.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=7, label="7d", step="day", stepmode="backward"),
            dict(count=14, label="14d", step="day", stepmode="backward"),
            dict(count=21, label="21d", step="day", stepmode="backward"),
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=2, label="2m", step="month", stepmode="backward"),
            dict(count=3, label="3m", step="month", stepmode="backward"),
            dict(count=4, label="4m", step="month", stepmode="backward"),
            dict(label="R", step="all")
        ])
    )
)

# Create the Dashboard
app.layout = html.Div(children=[
    html.H1(children="COVID-19 India Detailed Analysis"),
    html.H2(children="Total Count: " + str(database["Summary"]["total_count"])),
    html.Div([
        html.Div([
            dcc.Graph(figure=summary_pie_fig)
        ], className="six columns"),
        html.Div([
            dcc.Graph(figure=summary_column_fig)
        ], className="six columns"),
    ], className="row"),
    html.Div(
        dcc.Graph(figure=summary_historical_line)
    ),
    html.Div(
        dcc.Graph(figure=summary_historical_total_line)
    ),
    html.H2(children="State Wise Analysis"),
    html.Div(
        html.Label([
            "Select State",
            dcc.Dropdown(
                id='state-filter',
                options=all_state_dropdown,
                value='Karnataka',
                clearable=False
            )
        ])
    ),
    html.Div([
        html.Div(id='state-transmition-summary-output', className="six columns"),
        html.Div(id='state-daily-summary-output', className="six columns"),
    ], className="row"),
    html.Footer("Based on data from api.covid19india.org")
], style={'textAlign': 'center'})

@app.callback(
    dash.dependencies.Output('state-transmition-summary-output', 'children'),
    [dash.dependencies.Input('state-filter', 'value')])
def state_transmition_summary(value):
    statewise_pie_chart_labels = []
    statewise_pie_chart_values = []
    for item in database[value]["transmition_types"]:
        statewise_pie_chart_labels.append(item)
        statewise_pie_chart_values.append(database[value]["transmition_types"][item]["total_count"])
    statewise_pie_fig = go.Figure(data=[go.Pie(labels=statewise_pie_chart_labels, values=statewise_pie_chart_values)])
    statewise_pie_fig.update_layout(title_text='{}: Transmition Types (Total: {})'.format(value, database[value]["total_count"]))
    
    return dcc.Graph(figure=statewise_pie_fig)

@app.callback(
    dash.dependencies.Output('state-daily-summary-output', 'children'),
    [dash.dependencies.Input('state-filter', 'value')])
def state_daily_summary(value):
    statewise_column_chart_dates_iso = []
    statewise_column_chart_values = {
        "Imported": [],
        "Local": [],
        "Unknown": []
    }
    statewise_transmition_types = [
        "Imported",
        "Local",
        "Unknown",
    ]
    for date in summary_line_chart_dates_raw:
        if date in summary_line_chart_values["StateWise"][value]:
            for transmition in statewise_transmition_types:
                statewise_column_chart_values[transmition].append(0)
            for transmition in summary_line_chart_values["StateWise"][value][date]:
                statewise_column_chart_values[transmition][-1] = summary_line_chart_values["StateWise"][value][date][transmition]
                date_obj = datetime.strptime(date, "%d/%m/%Y")
            statewise_column_chart_dates_iso.append(
                date_obj.isoformat()
            )
    statewise_column_fig = go.Figure()
    for transmition in statewise_transmition_types:
        statewise_column_fig.add_trace(go.Bar(name=transmition, x=statewise_column_chart_dates_iso, y=statewise_column_chart_values[transmition]))
    statewise_column_fig.update_layout(title_text='{}: Daily Increments'.format(value), barmode='stack')
    
    return dcc.Graph(figure=statewise_column_fig)

if __name__ == "__main__":
    # Run the application
    app.run_server(debug=True)