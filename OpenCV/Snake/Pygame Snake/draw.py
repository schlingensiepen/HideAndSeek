import cv2 as cv
import numpy as np
import sys, os







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