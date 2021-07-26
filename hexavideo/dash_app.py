import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import n_colors
from skimage import io
import flask
import glob
import os


result = pd.read_csv("data/result.csv", index_col=0)
result["frame"] = result.index
df = result.melt(id_vars="frame", value_vars=["car","person"], var_name="class", value_name="number")
df["difference"] = df["number"].diff()
df["number"] = df["number"].astype(int)
notif = df[df["difference"] > 0]
notif = notif.sort_values(by="frame")
notif = notif[["frame", "class", "number"]]
notif["frame"] = "[" + notif["frame"].astype(str) + "]" 

notif_message = "[" + notif["frame"].astype(str) + "]" + " " +  notif["number"].astype(str) + " " + notif["class"]
notif_message = notif_message.to_frame("Message").to_dict("records")

img = io.imread("data/notif_images/57.jpg")
fig = px.imshow(img)
fig.update_layout(coloraxis_showscale=False)
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)

image_directory = 'data/notif_images/'
list_of_images = [os.path.basename(x) for x in glob.glob('{}*.jpg'.format(image_directory))]
static_image_route = '/static/'

def generate_notif_table():
    return dash_table.DataTable(
                id="notif-table",
                data=notif.to_dict("records"),
                columns=[{'id': c, 'name': c} for c in notif.columns],
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{class} contains "person"'
                        },
                        'backgroundColor': 'rgb(255,190,134)',
                        'color': 'rgb(255,127,14)'
                    },
                    {
                        'if': {
                            'filter_query': '{class} contains "car"'
                        },
                        'backgroundColor': 'rgb(142,186,217)',
                        'color': 'rgb(31,119,180)'
                    }
                ], style_header = {'display': 'none'}
                , style_as_list_view=True,
            )
    

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1("Video Analysis"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Event Notifications"),
                        dbc.Container([generate_notif_table()])
                    ])
                ,width=3),
                dbc.Col([
                    dbc.Row(
                        dcc.Graph(
                        id='example-graph',
                        figure= px.area(df, x="frame", y="number", color="class", template="simple_white"))
                    ),
                    dbc.Row(
                        dbc.Card(
                            [
                                dbc.CardBody(html.P("Event Review", className="card-text")),
                                dbc.CardImg(id="image", bottom=True),
                            ]
                        ), align="center"
                    )
                ], width=8),
            ],
            justify="around"
        ),
    ],
    style={"margin": "auto"},
)

@app.callback(Output('image', 'src'),
              [Input('notif-table', 'active_cell'),
               Input('notif-table', 'data')])
def get_active_letter(active_cell, data):
    if not active_cell:
        return " "
    if active_cell:
        s = str(data[active_cell['row']]["frame"])
        s = s[s.find("[")+1:s.find("]")]
        return static_image_route + s + ".jpg"

@app.server.route('{}<image_path>.jpg'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.jpg'.format(image_path)
    if image_name not in list_of_images:
        raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(image_directory, image_name)

if __name__ == '__main__':
    app.run_server(debug=True)
