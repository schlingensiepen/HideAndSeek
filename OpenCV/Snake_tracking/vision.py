import cv2 as cv
import numpy as np


class Vision:

    # properties
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None

    # constructor
    def __init__(self, needle_img_path, method=cv.TM_CCOEFF_NORMED):
        
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        self.last_rectangles = None
        self.new_rectangles = []

        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]

        #Methods:  TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method


    #funktioniert nicht
    '''
    def diffrerences(self, old_img, new_img):

        diffs = cv.subtract(old_img, new_img)

        result = not np.any(diffs)

        if result == True:
            print("Same Imgs")
        else:
            print("images are different")
            locations = np.where(diffs != 0)
            locations = locations[2:,...]
            print("locations", locations)
            locations = list(zip(*locations[::-1]))
            rectangles = []
            for loc in locations:
                rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
                rectangles.append(rect)
                rectangles.append(rect)
                rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

            points = []
            marker_color = (255, 0, 255)
            marker_type = cv.MARKER_CROSS

            for (x, y, w, h) in rectangles:

                
                center_x = x + int(w/2)
                center_y = y + int(h/2)
              
                points.append((center_x, center_y))

                cv.drawMarker(haystack_img, (center_x, center_y), 
                                color=marker_color, markerType=marker_type, 
                                markerSize=40, thickness=2)
    '''




    def find(self, haystack_img, threshold=0.5, debug_mode=None):
        
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
        #print("locations in find: ",locations)
        locations = list(zip(*locations[::-1]))
        #print(locations)

        # remove overlapping rectangles
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            
            rectangles.append(rect)
            rectangles.append(rect)
        
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        #print(rectangles)

        if np.any(rectangles != self.last_rectangles):

            #new_rectangles = np.where rectangles

            try:
                #print('rechtecke', rectangles)
                #print('letzte_rechtecke', self.last_rectangles)

                #new_rectangles = np.setdiff1d(rectangles, self.last_rectangles)
                #positions = np.where(rectangles != self.last_rectangles)
                #print(positions)
                #print('position', position)
                #new_rectangles.append(rectangles[position])
                #new_rectangles = np.where(rectangles != self.last_rectangles)
                self.new_rectangles.clear()
                

                for rect in rectangles:
                    #print (rect)
                    identisches_eck = np.where((self.last_rectangles == rect).all(axis = 1))
                    #print('identisch: ', identisches_eck)
                    if np.any(identisches_eck) == False:
                        print('neues Rechteck', rect)
                        self.new_rectangles.append(rect)
                print(self.new_rectangles)
                              
            except Exception as e: print(e)


        else:
            print("nichts neues")


        points = []
        if len(rectangles):
            #print('Found needle.')

            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            marker_color = (255, 0, 255)
            marker_type = cv.MARKER_CROSS

            # Loop over all the rectangles
            for (x, y, w, h) in rectangles:

                # Determine the center position
                center_x = x + int(w/2)
                center_y = y + int(h/2)
                # Save the points
                points.append((center_x, center_y))

                if debug_mode == 'rectangles':
                    # Determine the box position
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    # Draw the box
                    cv.rectangle(haystack_img, top_left, bottom_right, color=line_color, 
                                lineType=line_type, thickness=2)
                elif debug_mode == 'points':
                    # Draw the center point
                    cv.drawMarker(haystack_img, (center_x, center_y), 
                                color=marker_color, markerType=marker_type, 
                                markerSize=40, thickness=2)
         #neue pixel markieren:   
        if self.new_rectangles:
            if len(self.new_rectangles):                   
                for (x, y, w, h) in self.new_rectangles:
                    center_x = x + int(w/2)
                    center_y = y + int(h/2)

                    cv.drawMarker(haystack_img, (center_x, center_y), 
                                            color=marker_color, markerType=marker_type, 
                                            markerSize=40, thickness=2)

        if debug_mode:
            cv.imshow('Matches', haystack_img)
            #cv.waitKey()
            #cv.imwrite('result_click_point.jpg', haystack_img)


        self.last_rectangles = rectangles

        return points