from flask import Flask, render_template, request, jsonify
import pickle
import cv2
import numpy as np
import base64
import mediapipe as mp
from flask_cors import CORS
import nltk
from nltk.corpus import words
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

# Load model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# Initialize OpenCV objects
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
labels_dict = {0: 'A', 1: 'B', 2: 'L'}

nltk.download('words')
english_words = set(word.lower() for word in words.words())
def is_english_word(word):
    return word.lower() in english_words and len(word) >=3

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.get_json()
    base64_data = data['image_data']
    # Convert base64 string to numpy array
    nparr = np.frombuffer(base64.b64decode(base64_data.split(',')[1]), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Process image and return predicted text
    predicted_text = predict_text_from_image(img)
    return jsonify({'text': predicted_text})

def predict_text_from_image(img):
    # Process image and predict text using model
    results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if results.multi_hand_landmarks:
        # Process hand landmarks and predict text
        for hand_landmarks in results.multi_hand_landmarks:
            data_aux = []
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x)
                data_aux.append(y)
        prediction = model.predict([np.asarray(data_aux)])
        predicted_character = labels_dict[int(prediction[0])]
        return predicted_character
    else:
        return ''

@app.route('/check_word',methods=['POST'])
def check_word():
    data = request.get_json()
    word = data['word']
    return jsonify({'check': is_english_word(word)})

    
if __name__ == '__main__':
    app.run(debug=True)
