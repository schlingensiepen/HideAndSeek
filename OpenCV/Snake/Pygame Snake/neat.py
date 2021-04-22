import random
import time



def ai_output(vector):
    richtung = [0, 0]
    print("von ai_output:", vector)
    wert = random.randrange(-1, 2)
    xy = random.randrange(0, 2)
    richtung[xy] = wert 
    return richtung
