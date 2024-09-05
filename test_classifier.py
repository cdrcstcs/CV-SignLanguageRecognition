import pickle
import cv2
import mediapipe as mp
import numpy as np
import time
import nltk
from nltk.corpus import words
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
labels_dict = {0: 'A', 1: 'B', 2: 'L'}
data_aux = []
x_ = []
y_ = []
predicted_characters = []
taken_words = []
start_time = time.time()
nltk.download('words')
english_words = set(word.lower() for word in words.words())
def is_english_word(word):
    return word.lower() in english_words and len(word) >=3
from spellchecker import SpellChecker
spell = SpellChecker()
img_display = np.zeros((100, 600, 3), np.uint8)
img_display[:] = (0, 0, 0)  
while True:
    ret, frame = cap.read()
    if time.time() - start_time >= 3:
        H, W, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,  
                    hand_landmarks,  
                    mp_hands.HAND_CONNECTIONS,  
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))
        start_time = time.time()
        if data_aux:  
            prediction = model.predict([np.asarray(data_aux)])
            predicted_character = labels_dict[int(prediction[0])]
            predicted_characters.append(predicted_character)
            data_aux = []  
            formed_word = ''.join(predicted_characters)
            print(formed_word)  
            if is_english_word(formed_word):
                taken_words.append(formed_word)
                predicted_characters = [] 
                taken_words_str = ', '.join(taken_words)  
                cv2.putText(img_display, taken_words_str, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                words = []  
    cv2.imshow('frame', frame)
    cv2.imshow('taken_words', img_display)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()