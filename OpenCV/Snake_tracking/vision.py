import cv2 as cv
import numpy as np
import sys, os


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
        self.old_head_pos = [0, 0]
        self.food = None

        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]

        #Methods:  TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = method


  


    def find(self, haystack_img, threshold=0.5, debug_mode=None):
        
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
        #print("locations in find: ",locations)
        locations = list(zip(*locations[::-1]))
        #print(locations)

        # remove overlapping rectangles
        rectangles = []
        rectangles_stripped = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            
            rectangles.append(rect)
            rectangles.append(rect)
        
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        #print(rectangles)

        if len(rectangles):
            rectangles_stripped = np.delete(rectangles, np.s_[2:5], axis=1)
            #print('stripped', rectangles_stripped)

        if np.any(rectangles_stripped != self.last_rectangles):

            #new_rectangles = np.where rectangles

            try:
               
                self.new_rectangles.clear()
                
                #kopf finden


                for rect in rectangles_stripped:
                
                    identisches_eck = np.isclose(self.last_rectangles, rect, atol = 2).all(axis = 1)                       
                    #print('identisch: ', identisches_eck)
                    if np.any(identisches_eck) == False:      
                        #print('neues Rechteck', rect)
                        self.new_rectangles.append(rect)
                

                #food finden

                for rect in rectangles_stripped:
                    near = np.isclose(rectangles_stripped, rect, atol = 25).all(axis = 1)
                    near = near.tolist()
                    #print('near', near)
                    if near.count(True) < 2:
                        self.food = rect
                        #print('Food', self.food)
                        break

                #food aus neuen rectangles entfernen  

                if len(self.new_rectangles) > 1:     
                    #print(self.new_rectangles)   
                    row = np.where((self.new_rectangles == self.food).all(axis = 1))
                    #print('row', row)
                    np.delete(self.new_rectangles, row,  axis = 0)   

                #richtung finden

                new_head_pos = np.array(self.new_rectangles)
                #print('newhead', new_head_pos)
                #print('oldhead', self.old_head_pos)
                direction = new_head_pos - self.old_head_pos
                #print('richtung', direction)
                self.old_head_pos = new_head_pos 

                direction_list = direction.tolist()
                direction_list = direction_list
                
                if direction_list[0][0] > 0:
                    richtung = 'x'
                elif direction_list[0][0] < 0:
                    richtung = '-x'
                elif direction_list[0][1] > 0:
                    richtung = 'y'
                elif direction_list[0][1] < 0:
                    richtung = '-y'
                #print(richtung)



            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)


        #else:
            #print("nichts neues")


        points = []
        if len(rectangles):
            w = 20
            h = 20
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
         #Kopf markieren:   
        if self.new_rectangles:
            if len(self.new_rectangles):                   
                for (x, y) in self.new_rectangles:
                    center_x = x + int(w/2)
                    center_y = y + int(h/2)

                    cv.drawMarker(haystack_img, (center_x, center_y), 
                                            color=marker_color, markerType= cv.MARKER_CROSS, 
                                            markerSize=40, thickness=2)
        #food markieren:
        if np.any(self.food) == True:
            food_marker_color = (0, 0,255)
            x = self.food[0]
            y = self.food[1]


            center_x = x + int(w/2)
            center_y = y + int(h/2)
            cv.drawMarker(haystack_img, (center_x, center_y), 
                                            color=food_marker_color, markerType = cv.MARKER_CROSS, 
                                            markerSize=40, thickness=2)



        if debug_mode:
            cv.imshow('Matches', haystack_img)
            #cv.waitKey()
            #cv.imwrite('result_click_point.jpg', haystack_img)


        self.last_rectangles = rectangles_stripped

        return points