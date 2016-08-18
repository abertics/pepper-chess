
import math
import cv2
import numpy as np

from pystockfish_edited import Engine, HumanEngineMatch


class ChessDetect(object):
    """docstring for ChessDetect
    	- ChessDetect.detection() returns the location of all pieces on board and the move made (if any)
    		format: {"pieces": pieces, "move": move}    pieces = {loc: name}
    	- ChessDetect.next_move() returns the chess engine's response to the move
    	(All the other functions help those two to happen)
    """

    def __init__(self):
        self.old_piece_dict = {}
        self.fr, self.to = {}, {}
        self.e = Engine(depth=10)
        self.match = HumanEngineMatch(self.e)
        self.pepper_move, self.illegal, self.is_match, self.three_d = False, False, False, False

    def open_camera(self):
        self.cap = cv2.VideoCapture(1)

    def take_picture(self):
        return self.cap.read()[1]

    def close_camera(self):
        self.cap.release()

    def crop_to_chessboard(self, original_photo):
    	""" Camera might have to be configured... this cropping is done to a 
    		photo which was originally 1920x1080 pixels"""

        #renders photo into black and white for analysis
        gray = cv2.cvtColor(original_photo, cv2.COLOR_BGR2GRAY)
        #crops photo to just a square which contains the chessboard, removes border
        gray = gray[8:1072, 482:1546]

        num_rows, num_cols = gray.shape[:2]
        mat_rot = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), -0.7, 1 )
        #rotates photo for more accurate division of board into 64 quadrants
        return cv2.warpAffine(gray, mat_rot, (num_cols, num_rows))

    def get_points(self,approx):
        #takes the points of a contour out of the multi-layered numpy array
        return approx[0][0][0], approx[1][0][0], approx[2][0][0], approx[3][0][0], approx[0][0][1], approx[1][0][1], approx[2][0][1], approx[3][0][1]

    def get_two_maxx_points(self,approx):
        #finds the two points with the greatest x component
        xa, xb, xc, xd, ya, yb, yc, yd = self.get_points(approx)
        coor_dict = {xa:ya, xb:yb, xc:yc, xd:yd}

        xs = [xa,xb,xc,xd]
        maxx = max(xs)
        xs.remove(maxx)
        maxxx = max(xs)
        xs.remove(maxxx)

        if coor_dict[maxx] == coor_dict[maxxx]:
            maxxx = max(xs)

        return maxx,coor_dict[maxx],maxxx,coor_dict[maxxx]

    def dist_points(self,x1,y1,x2,y2):
        return ((x2-x1)**2+(y2-y1)**2)**(.5)

    def get_center_of_contour(self, approx):
        xa, xb, xc, xd, ya, yb, yc, yd = self.get_points(approx)
        return ((xa+xb+xc+xd)/4, (ya+yb+yc+yd)/4)

    def get_angle(self,xa, ya, xb, yb, xc, yc):
        #calculates the angle of rotation needed to straighten out the chess piece by finding the angle
        #between the vector between [the center of the piece and the center of the furthest leftward edge]
        #and the vertical unit vector
        xg = (xa+xb)/2
        yg = (ya+yb)/2

        delta_y = abs(yg-yc)*1.0
        dist = self.dist_points(xg,yg,xc,yc)

        if dist == 0: return 0

        if yg < yc:
            ang = abs(math.acos((delta_y)/dist)*(180/math.pi))
        else:
            ang = -abs(math.acos((delta_y)/dist)*(180/math.pi))
        return ang

    def is_chess_piece(self,cnt, peri,approx, loc):
        """
        determines whether contour could be a chess piece
        	- chess pieces are square and we know their size,
        	so the contour found should satisfy the following criteria
        """
        a = .70
        area = cv2.contourArea(cnt)
        #these cases are in case it finds a contour with 8 or 16 edges, which
        #doesn't neccessarily rule out it being a chess piece
        if len(approx) == 8 and (peri>400*a and peri<600*a):
            return 8
        if len(approx) == 16 and (peri>800*a and peri<1120*a):
            return 16
        if peri/len(approx)>50*a and peri/len(approx) < 50*a:
            return len(approx)

        #area should be between two values, and perimeter too.
        #this rules out the contours which are super skinny (like the side of the chessboard square)
        #or too small (like the actual qr code) or too big
        if area > 2500*a*a and area < 4900*a*a:
            n=1
        elif peri<200*a or peri>280*a:
            return False

        if len(approx)<4:
            return False

        xa, xb, xc, xd, ya, yb, yc, yd = self.get_points(approx)

        #this makes sure it's a square, by checking distance between all the points
        #the side of a square should never be less than 40*a
        if self.dist_points(xa,ya,xb,yb) < 40*a or self.dist_points(xc,yc,xb,yb) < 40*a:
            return False
        if self.dist_points(xc,yc,xd,yd) < 40*a or self.dist_points(xa,ya,xd,yd) < 40*a:
            return False
        return True

    def orient_piece(self,pixels):
        #finds the white corner and orients pixels accordingly
        #the pieces have three black and one white corner. the piece should be read
        #with the white corner in the upper left
        c = pixels[:]
        if c[0]:
            return c
        elif c[2]:
            return [c[2] , c[5] , c[8] ,c[1] , c[4] , c[7] ,c[0] , c[3] , c[6]]
        elif c[6]:
            return [c[6] , c[3] , c[0] ,c[7] , c[4] , c[1] ,c[8] , c[5] , c[2]]
        elif c[8]:
            return [c[8] , c[7] , c[6] ,c[5] , c[4] , c[3] ,c[2] , c[1] , c[0]]
        else:
            #every contour found should have a white corner
            return False

    def find_chess_piece_contour(self, current_square, loc):
    	#searches each square on the chess board for a chess piece

        edged_current_square = cv2.Canny(current_square, 30, 200)

        (cnts, _) = cv2.findContours(edged_current_square.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

        choices = []
        min_length = 3000
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            cs = self.is_chess_piece(c, peri, approx, loc)
            if cs:
                if cs == 8:
                    approx = [[[approx[0][0][0], approx[0][0][1]]],[[approx[2][0][0], approx[2][0][1]]],[[approx[4][0][0], approx[4][0][1]]],[[approx[6][0][0], approx[6][0][1]]]]
                if peri < min_length:
                    min_length = peri
                    choices = [approx]
        return choices

    def find_location(self,x,y):
        #converts x and y coordinates into chess square location
        rows = {0:"a",1:"b",2:"c",3:"d",4:"e",5:"f",6:"g",7:"h"}
        cols = {0:"1",1:"2",2:"3",3:"4",4:"5",5:"6",6:"7",7:"8"}
        return  rows[y]+cols[x]

    def find_pixels(self,final_mat,curr):
        #analyzes each of the nine squares within the piece and appropriates either a
        #1 if it is bright or a 0 if it is dark; converts photo to list of 1s and 0s
        tab = []
        a = .7
        ecart = 16*a
        normTab = []
        for l in range (0,3,1):
            for m in range (0,3,1):
                curr = final_mat[l*ecart:(l+1)*ecart,m*ecart:(m+1)*ecart]
                normTab.append(cv2.norm (curr))
        meanNorm = (min(normTab)+max(normTab))/2
        for currNorm in normTab :
            if currNorm > meanNorm :
                tab.append(1)
            else :
                tab.append(0)
        return tab, curr

    def decode_piece(self, p):
        #converts the pattern of black and white pixels into piece id
        #the pieces have encoded in them a binary number between 0 and 31,
        #inclusive, using the squares, save the corners, which are for orientation
        if not p:
            return "Error"
        d = {0: 'wR', 1: 'wN', 2: 'wB', 3: 'wQ', 4: 'wK', 5: 'wB', 6: 'wN', 7: 'wR', 8: 'wP', 9: 'wP', 10: 'wP', 11: 'wP', 12: 'wP', 13: 'wP', 14: 'wP', 15: 'wP', 16: 'bP', 17: 'bP', 18: 'bP', 19: 'bP', 20: 'bP', 21: 'bP', 22: 'bP', 23: 'bP', 24: 'bR', 25: 'bN', 26: 'bB', 27: 'bQ', 28: 'bK', 29: 'bB', 30: 'bN', 31: 'bR'}
        if self.three_d:
        	#for 3D visualization, each piece needs an individual id
            return int("".join(map(str,[p[1],p[3],p[4],p[5],p[7]])), base=2)
        #but for playing a game, or twoD visualization, the type of piece suffices
        return d[int("".join(map(str,[p[1],p[3],p[4],p[5],p[7]])), base=2)]

    def find_pieces(self):
        # find all pieces & locations on the chessboard

        piece_dict = {}

        o = self.take_picture()
        oa = self.take_picture()
        ob = self.take_picture()
        oc = self.take_picture()
        od = self.take_picture()
        oe = self.take_picture()
        of = self.take_picture()
        og = self.take_picture()
        #takes the average of 8 photos to remove stripes caused by weird camera/light frequencies
        original = cv2.add(cv2.add(cv2.add(o/2,oa/2)/2, cv2.add(ob/2,oc/2)/2)/2, cv2.add(cv2.add(od/2,oe/2)/2, cv2.add(of/2,og/2)/2)/2)

        chessboard_photo = self.crop_to_chessboard(original)

        chessboard_height, chessboard_width = 1064, 1064
        increment = chessboard_height/8
        gap = 10

        for i in range(0,chessboard_height,increment):
            for j in range(0,chessboard_width,increment):
                #checks each of the 64 squares on the chessboard
                current_square = chessboard_photo[i+gap:i+increment-gap, j+gap:j+increment-gap].copy()
                curr = current_square.copy()

                chess_piece_contour = self.find_chess_piece_contour(current_square, self.find_location(i/increment, j/increment))
                
                if chess_piece_contour:

                    xmax,ymax,xmaxx,ymaxx = self.get_two_maxx_points(chess_piece_contour[0])
                    xcenter, ycenter = self.get_center_of_contour(chess_piece_contour[0])

                    #we rotate picture so that the piece can be cropped well and read with the sides straight
                    #up and the top and bottom horizontal
                    angle = self.get_angle(xmax,ymax, xmaxx, ymaxx, xcenter, ycenter)

                    num_rows, num_cols = curr.shape[:2]
                    mat_rot = cv2.getRotationMatrix2D((xcenter, ycenter), angle, 1 )
                    rotated = cv2.warpAffine(curr, mat_rot, (num_cols, num_rows))

                    #crop rotated picture to chess piece to analyze pixels within
                    a=.7
                    final_mat = rotated[ycenter-24*a:ycenter+24*a , xcenter-24*a:xcenter+24*a]

                    pixels, images = self.find_pixels(final_mat,curr)
                    oriented_pixels = self.orient_piece(pixels)
                    name = self.decode_piece(oriented_pixels)

                    loc = self.find_location(i/increment, j/increment)
                    if name == "Error":
                        continue
                    piece_dict[loc] = name
                else:
                    loc = self.find_location(i/increment, j/increment)
                    pixels = False
        return piece_dict.copy()


    def detection(self):
   		#eliminates false readings and finds any move taken

        if not self.old_piece_dict:
            self.old_piece_dict = self.find_pieces()

        #both results must agree for a change to take place
        #this slows it down, but serves to avoid jumps in the pieces
        #and moves that didn't actually happen
        d1 = self.find_pieces()
        d2 = self.find_pieces()

        if self.is_match:
        	#if playing against pepper, chess engine
            if self.illegal:
            	#if the chess engine says that the move made was illegal
            	#allows user to reset piece (otherwise game would crash
            	# and would have to start from scratch)
                l = self.illegal["from"]
                if l in d1 and l in d2:
                    if d1[l] == d2[l] and d1[l] ==self.illegal["piece"]:
                        for ok in self.old_piece_dict.copy():
                            if ok not in d1 and ok not in d2:
                                del self.old_piece_dict[ok]
                        self.old_piece_dict[l] = d2[l]
                        print "Thank you. Piece has been reset."
                        self.illegal = False
                else:
                    print "Pls move", self.illegal["piece"], "back to", self.illegal["from"]
                return {"pieces": self.old_piece_dict, "move": False}

            if self.pepper_move:
                fr = self.pepper_move[0:2]
                to = self.pepper_move[2:4]
                piece = self.pepper_move[4:6]
                print "Pepper's turn:", piece, "from", fr, "to", to
                if (fr not in d1 and fr not in d2) and (to in d1 and to in d2):
                    if piece == d1[to] and piece == d2[to]:
                        del self.old_piece_dict[fr]
                        self.old_piece_dict[to] = piece
                        self.pepper_move = False
                        return {"pieces": self.old_piece_dict, "move": False}
                return {"pieces": self.old_piece_dict, "move": False}
            print "User's turn..."

        if d2 != self.old_piece_dict or d1 != self.old_piece_dict:
        	#if both d1 and d2 agree wit self.old_piece_dict, no change happened
            for ok in self.old_piece_dict.copy():
                if ok not in d1 and ok not in d2:
                	#removing piece
                    if not self.three_d:
                        if self.old_piece_dict[ok][0] == "w" and self.is_match:
                            self.fr = {"piece": self.old_piece_dict[ok], "loc": ok}
                            del self.old_piece_dict[ok]
                        elif not self.is_match:
                            del self.old_piece_dict[ok]
                    else:
                        del self.old_piece_dict[ok]
                elif ok in d1 and ok in d2:
                    if d1[ok] == d2[ok] and self.old_piece_dict[ok] != d1[ok]:
                    	#piece switched at location
                        if not self.three_d:
                            if d1[ok][0] == "w" and self.is_match:
                                self.to = {"piece": d1[ok], "loc": ok}
                                self.old_piece_dict[ok] = d1[ok]
                            elif not self.is_match:
                                self.old_piece_dict[ok] = d1[ok]
                        else:
                            self.old_piece_dict[ok] = d1[ok]
            for k1 in d1:
                if k1 not in self.old_piece_dict and k1 in d2:
                    if d1[k1] == d2[k1]:
                    	#removing piece
                        if not self.three_d:
                            if d1[k1][0] == "w" and self.is_match:
                                self.to = {"piece": d1[k1], "loc": k1}
                                self.old_piece_dict[k1] = d1[k1]
                            elif not self.is_match:
                                self.old_piece_dict[k1] = d1[k1]
                        else:
                            self.old_piece_dict[k1] = d1[k1]

        move = False
        if self.to and self.fr:
            if self.to["piece"] == self.fr["piece"]:
                move = {"piece": self.to["piece"], "to": self.to["loc"], "from": self.fr["loc"]}
                print "Move:", move
                self.fr = {}
                self.to = {}
        # print self.old_piece_dict
        return {"pieces": self.old_piece_dict, "move": move}


    def next_move(self, move):
    	#there is still some issues that occur around checkmate
        if move["piece"][0] == "w":
            comp = self.match.move(move["from"]+move["to"])
            try:
                self.pepper_move = comp+self.old_piece_dict[comp[0:2]]
            except:
                print "Error occured @ next_move", comp
            return comp