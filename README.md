# BoggleSolver
Take a picture of a boggle board with this app and it will tell you all of the solutions!

## Development Setup
This app is still in development. To use this app, you must locally host the backend server, which is used to do the computer vision and apply the ML model to determine the letters, and
perform the algorithm to determine all of the Boggle words. Second, you must also locally host Expo, which sets up the frontend and allows you to use the BoggleSolver app through the Expo app. This setup is run through the following commands:

To launch backend server:

```
python3 server_app.py
```

To launch Expo:

```
cd Boggler
nxp expo start
```

## TODO

### Stage 1 - Fixing up logic & algorithm

1. Improve image recognition of R - the training data did not have enough images with R, and it can often mistake R for being H. We should redo the ML model with more training data.
2. Find a better dictionary - the current dictionaries in word_finder.py have too many weird complicated words.
3. Speed up algorithm - the algorithm is run in Python and can take up to a full minute to run. The algorithm should be re-written in C or another much faster language.

### Stage 2 - Making it shippable

1. Make mobile app much more user-friendly and easy to use
2. Host backend online (Render perhaps), removing requirement for local backend server
3. Export mobile app, removing requirement for Expo server

