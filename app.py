# Author: Tobin South
# Date 30 Nov 2021

import dash
from dash import html, dcc
from dash.dependencies import Output
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


from flask import Flask, Response, request
import cv2
import imutils





# This VideoCamera class generates frames and does facial processing. It uses the helperFuncs.py file.
from helperFuncs import *

class VideoCamera(object):
    """This object will store all of the information about the app as it progresses. It will use that information to generate the next frame."""
    def __init__(self):
        self.video = cv2.VideoCapture(-1)

        # Variables for storing the current state of the emotions
        self.current_emotion = 'happy'
        self.emotions_list = [ 'happy', 'sad', 'angry', 'disgust', 'fear', 'surprise', 'neutral']
        self.emotion_index = 0
        self.faces = {}

        # Variables for the collection phase
        self.progress_flag = False
        self.phase = 'collection'

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        frame = imutils.resize(frame, width=450) # Resize for speed

        frame = self.update_emotion(frame)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def update_emotion(self, frame):
        # Get the faces or return an unchanged frame
        try: 
            (x, y, w, h), mask, face = get_facemask(frame)
        except ValueError: 
            # print('Missing face')
            return frame

         # Collection
        if self.phase == 'collection':
            if self.progress_flag == False:
                return frame
            else:
                # Save face
                just_prev_face = face[y:y+h, x:x+w, :]
                just_prev_mask = mask[y:y+h, x:x+w]
                self.faces[self.current_emotion] = (just_prev_face, just_prev_mask)  
                self.progress_flag = False

                # Progress to next emotion
                self.emotion_index += 1 
                if self.emotion_index >= len(self.emotions_list):
                    self.phase = 'replacement'
                    self.current_emotion = 'happy'
                    print('Phase: replacement')
                    return frame
                else:
                    self.current_emotion = self.emotions_list[self.emotion_index]
                return frame

        # Replacement
        elif self.phase == 'replacement':
            just_prev_face, just_prev_mask = self.faces[self.current_emotion]
            try:
                combined_frame = overlay_face(just_prev_face, just_prev_mask, frame, x, y, w, h)
                return combined_frame
            except ValueError:
                return frame
            

cameraObject = VideoCamera()




# This is the server setup. We will then add routes and html to the app & server.
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.CYBORG, 'style.css'])





# This generator will yield the edit frames of the video and show it on the route.
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@server.route('/video_feed')
def video_feed():
    request.form.get('username')
    return Response(gen(cameraObject),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



# This is the layout of the app.
app.layout = html.Div([
    html.H1("Emotion Obfuscation App"),
    html.Hr(style={'padding-top': '5pt', 'padding-bottom': '5pt'}),
    html.Div(id='collection_div', style = {'align-items': 'center', 'justify-content': 'center', 'width':'450pt'}, children=[
        html.Div("""This app will take snapshots of your face showing different emotions and then overlay them on the video feed later to hide your expression. To set this up you need to follow the instructions below and click the button to record each emotion."""),
        html.Div(dbc.Button('Next Step', id='progress_button', style={'width':'450pt', 'padding-top': '5pt', 'padding-bottom': '5pt'})),
        dcc.Markdown(id='collection_text', highlight_config={'theme':'dark'}),
    ]),

    html.Div(id='video_feed_container', children=html.Img(src="/video_feed"), style={'padding-top': '5pt', 'padding-bottom': '5pt'}),

    html.Div(id='replacement_div', style={'display': 'none'}, children=[
        html.Div([
            html.Div(id='replacement_text'),
            dbc.RadioItems(
                options=[
                    {'label':'happy', 'value':'happy'},
                    {'label':'sad', 'value':'sad'},
                    {'label':'angry', 'value':'angry'},
                    {'label':'disgust', 'value':'disgust'},
                    {'label':'fear', 'value':'fear'},
                    {'label':'surprise', 'value':'surprise'},
                    {'label':'neutral', 'value':'neutral'},
                ],
                value='happy',
                id='emotion_radio',
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",
                labelCheckedClassName="active",
                # labelStyle={'display': 'inline-block',}
            )],
            className="radio-group"
        )
    ]),
    html.Hr(style={'padding-top': '20pt', 'padding-bottom': '20pt'}),
# html.Markdown("""
# ### What is this?


# """)
],
style={'width': '100%', 'height': '100%', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center'}
)


## These callbacks allow for states to change in the app. They are used to update the VideoFeed object.
# Collection callbacks
@app.callback(Output('collection_div', 'style'), Input('progress_button', 'n_clicks'))
def hide_collection_section(n_clicks):
    if cameraObject.phase == 'collection':
        cameraObject.progress_flag = True
        raise PreventUpdate
    elif cameraObject.phase == 'replacement':
        return {'display': 'none'}

@app.callback(Output('replacement_div', 'style'), Input('progress_button', 'n_clicks'))
def show_replacement_section(emotion_radio):
    if cameraObject.phase == 'collection':
        raise PreventUpdate
    elif cameraObject.phase == 'replacement':
        return {'display': 'block'}
         

@app.callback(Output('collection_text', 'children'), [Input('progress_button', 'n_clicks')])
def update_collection_text(n_clicks):
    if cameraObject.phase == 'collection':
        return '##### Make a face that shows a **%s**  emotion.' % cameraObject.current_emotion
    elif cameraObject.phase == 'replacement':
        return '##### Click me one last time and you can change the emotions!'

# Replacement callbacks
@app.callback(Output('replacement_text', 'children'), Input('emotion_radio', 'value'))
def update_face_and_text(emotion_value):
    cameraObject.emotion_index = cameraObject.emotions_list.index(emotion_value)
    cameraObject.current_emotion = emotion_value
    return 'Showing %s face' % emotion_value


# Running everything.
if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=True)