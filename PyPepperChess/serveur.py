import socket
import json
from ChessDetector import ChessDetect

HOST, PORT = "localhost", 9004


#dicts below used to give pepper appropriate x & y coordinates to grab from/ place to
y_coor = {'a': 0, 'c': 2, 'b': 1, 'e': 4, 'd': 3, 'g': 6, 'f': 5, 'h': 7}
x_coor = {1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1, 8: 0}

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', PORT))
c = ChessDetect()
c.open_camera()

# ****** if c.is_match, you are playing white against computer (black), match rules apply
# ****** if not c.is_match, the program just displays the pieces of the board regardless of move validity

#c.is_match = True
# c.three_d = True

while True:
    socket.listen(5)
    client, address = socket.accept()
    print "{} connected".format( address )
    while True:
        response = client.recv(1024)
        if not response:
            break

        arr = c.detection()

        if c.is_match:
            if arr["move"]:
                mm = arr["move"]
                nm = c.next_move(arr["move"])
                if c.match.winner:
                    print "Winner is", c.match.winner
                    c.is_match = False
                    break
                pepper_move = {"xi": x_coor[int(nm[1])], "yi": y_coor[nm[0]], "xf": x_coor[int(nm[3])], "yf": y_coor[nm[2]]}
                arr["move"] = pepper_move

                if nm[0:2] in c.old_piece_dict:
                    if c.old_piece_dict[nm[0:2]][0] == "w":
                        #chess engine is trying to move other player's piece
                        #reset back one move and try again
                        print "Your move was illegal! Try again plz."
                        c.pepper_move = False
                        c.match.moves = c.match.moves[:len(c.match.moves)-2]
                        c.illegal = mm
                        print c.illegal
                else:
                    #again, illegal move, resetting back 2 plays
                    print "Your move was illegal! Try again plz."
                    c.pepper_move = False
                    c.match.moves = c.match.moves[:len(c.match.moves)-2]
                    c.illegal = mm
                    print c.illegal
                print c.match.moves

        client.send(json.dumps(arr))



print "Close"
client.close()
stock.close()
c.close_camera()