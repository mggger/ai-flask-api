import time

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import base64
import os
import json
import dash_player

external_script = ["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], external_scripts=external_script,
                suppress_callback_exceptions=True,
                )
app.scripts.config.serve_locally = True

media_folder = 'medias'
media_files = [f for f in os.listdir(media_folder) if f.lower().endswith(('.mp3', '.wav', '.mp4'))]
transcripts = {}


current_words_info = None

for media_file in media_files:
    transcript_file = os.path.splitext(media_file)[0] + '.json'
    if transcript_file in os.listdir(media_folder):
        with open(os.path.join(media_folder, transcript_file), 'r') as f:
            transcripts[media_file] = json.load(f)



app.layout = html.Div(
    className="flex h-screen",
    children=[
        # 左侧边栏，显示Loaded Media Files
        html.Div(
            dbc.Card(
                [
                    dbc.CardHeader("Loaded Media Files", className="bg-gray-200"),
                    dbc.ListGroup(
                        [
                            html.Label(
                                media_file,
                                id=media_file.split(".")[0],
                                className="p-2 cursor-pointer hover:bg-gray-200"
                            )
                            for media_file in media_files
                        ]
                    ),
                ],
                color="light",
                className="h-full p-4"
            ),
            className="w-1/4"
        ),

        # 中间区域，显示Transcript
        html.Div(
            [
                html.H2("Transcript:", className="p-2 cursor-pointer hover:bg-gray-200"),
                dcc.Markdown(id='transcript-display', className="w-full p-2 border rounded max-h-[700px] overflow-y-auto",
                         dangerously_allow_html=True)
            ],
            className="w-1/4 p-4"
        ),

        # 右侧区域，显示媒体播放器
        html.Div(
            [
                html.H2("Media player:", className="p-2 cursor-pointer hover:bg-gray-200"),
                dash_player.DashPlayer(id='video-player', controls=True, className="bg-gray-200 h-full w-full")
            ],
            className="w-1/2 p-4"
        )
    ]
)

inputs = (Input(media_file.split(".")[0], 'n_clicks') for media_file in media_files)

@app.callback(
    [Output('transcript-display', 'children', allow_duplicate=True),
     Output('video-player', 'url')],
    *inputs,
    prevent_initial_call='initial_duplicate'
)
def update_media(*args):
    if (args[0]) is not None:
        global current_words_info

        media_file = media_files[args[0] - 1]
        transcript = transcripts[media_file]

        transcript_value = transcript['results']['channels'][0]['alternatives'][0]['transcript']
        words_info = transcript['results']['channels'][0]['alternatives'][0]['words']
        current_words_info = {(item['start'], item['end']): item['word'] for item in words_info}
        media_path = os.path.join(media_folder, media_file)
        url = f'data:video/mp4;base64,{base64.b64encode(open(media_path, "rb").read()).decode()}'
        return transcript_value, url
    else:
        return "", None

@app.callback(
    [Output("transcript-display", "children")],
    [Input("video-player", "currentTime")],
    [State("transcript-display", "children")]
)
def alter_transcript(currentTime, current_word):
    global current_words_info
    if current_words_info is not None and currentTime is not None:
        all_word = ""
        for (start, end), word_data in current_words_info.items():
            if start <= currentTime <= end:
                highlighted_word = f'<mark>{word_data}</mark>'
                all_word += f" {highlighted_word}"
            else:
                all_word += f" {word_data}"
        return [all_word]
    return [current_word]

if __name__ == '__main__':
    app.run_server(debug=True)
