#Used this tutorial for inspiration: https://www.youtube.com/watch?v=-4v4A550K3w&ab_channel=MisbahMohammed 

import cv2
import tensorflow as tf
from matplotlib import pyplot as plt
import numpy as np

interpreter = tf.lite.Interpreter(model_path='lite-model_movenet_singlepose_lightning_3.tflite')
#interpreter = tf.lite.Interpreter(model_path='lite-model_movenet_singlepose_thunder_3.tflite')
interpreter.allocate_tensors()

def draw_keypoints(frame, keypoints, confidence):
        """
        Draws in the locations of the key joints
        """
        y, x, c = frame.shape #y coordinate, x, coordginate, the channel coordinate
        shaped = np.squeeze(np.multiply(keypoints, [y, x, 1])) #the third coordinate in our keypoints is the confidence value, so we multiply by one to maintain that coordinate
        
        for kp in shaped:
            ky, kx, kp_conf = kp #extracting our y, our x, 
            if kp_conf > confidence:
                cv2.circle(frame, (int(kx), int(ky)), 4, (0, 255, 0), -1) #last three parameters are size, color, fill
    
def draw_connections(frame, keypoints, edges, confidence_threshold):
    y, x, c = frame.shape #y coordinate, x, coordginate, the channel coordinate
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1])) #the third coordinate in our keypoints is the confidence value, so we multiply by one to maintain that coordinate
    
    for edge, color in edges.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]
        
        if (c1 > confidence_threshold) & (c2 > confidence_threshold):
            cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
def calculate_angle(a, b, c):
    """
    Given three keypoints, calculate the angle between them
    """
    #In the mediapipe implementation, the points needed to be converted into numpy.ndarray type
    #Here, the points from the keypoints are already in this type, so we don't need to convert
        #p[0] ->  y-coordinate
        #p[1] -> x-coordinate
    
    radians = np.arctan2(c[0] - b[0], c[1] - b[1]) - np.arctan2(a[0] - b[0], a[1] - b[1])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    
    return angle

EDGES = {
    (0, 1): 'm',
    (0, 2): 'c',
    (1, 3): 'm',
    (2, 4): 'c',
    (0, 5): 'm',
    (0, 6): 'c',
    (5, 7): 'm',
    (7, 9): 'm',
    (6, 8): 'c',
    (8, 10): 'c',
    (5, 6): 'y',
    (5, 11): 'm',
    (6, 12): 'c',
    (11, 12): 'y',
    (11, 13): 'm',
    (13, 15): 'm',
    (12, 14): 'c',
    (14, 16): 'c'
    }

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        ret, frame = self.video.read()
        img = frame.copy()
        #For MoveNet Lightning
        img = tf.image.resize_with_pad(np.expand_dims(img, axis=0), 192, 192)
        #For MoveNet Thunder
        #img = tf.image.resize_with_pad(np.expand_dims(img, axis=0), 256, 256)

        input_image = tf.cast(img, dtype=tf.float32)

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]['index'], np.array(input_image))
        interpreter.invoke()
        keypoints_with_scores = interpreter.get_tensor(output_details[0]['index'])

        #Bicep Curl Counter
        try:
            left_shoulder = keypoints_with_scores[0][0][5]
            left_elbow = keypoints_with_scores[0][0][7]
            left_wrist = keypoints_with_scores[0][0][9]
            
            angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            #print(angle)
        
            #Curl Counter Logic (this might need to be better lol)
            if angle > 160:
                print("DOWN")
                stage = "down"
                print("set stage")
            if angle < 30 and stage == "down":
                print("UP")
                stage = "up"
                counter += 1
                print("counter: ", counter)
        except:
            pass

        draw_connections(frame, keypoints_with_scores, EDGES, 0.5)
        draw_keypoints(frame, keypoints_with_scores, 0.5)


        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
    
    
        
