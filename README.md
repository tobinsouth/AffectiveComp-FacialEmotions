# Affective Computing Group Project - The Repo When GANs fail

Turns out GANs are hard. OpenCV is less hard. Here is a bunch of code to build out an emotion demo product as a backup.

Two key files currently:
- `emotion_lag.py`: is a simple script that will add your current expression to a queue and display a lagged face simulating delayed communication.
- `emotion_swap.py`: is a script that will swap your current expression with a set of pre-collected emotions provided by the user or an emoji. Designed to be an example of limited emotional expression range (or the use of a computer to show emotion).


# Local Setup
1) create virtual environment
2) pip install -r requirements.txt

# Deployment Notes
1) No environment variables needed (for now ... otherwise use dotenv and os)
2) [Procfile takes care of Heroku Deployment] --> not using Procfile since OpenCV has problems
2) Use heroku stack:set container and heroku.yml file instead
3) Dockerfile makes sure that deployment errors are resolved (especially w.r.t. OpenCV's cv2 Python library)
4) Push deploy branch to Heroku: '''git push heroku deploy:main'''
5) App runs on https://ganemon.herokuapp.com/