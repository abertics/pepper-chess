----------------------
1) File List:
----------------------
PyPepperChess:
  i.   cv2.so
  ii.  pystockfish_edited.py 
  iii. ChessDetector.py
  iv.  serveur.py

----------------------
2) What else you need:
----------------------
- opencv
- stockfish executable at root level (google stockfish and install)
- python 2.7 (math, numpy, json, socket) & node (for js stuff)
- all the hardware stuff

----------------------
3) What each file is/does:
----------------------
cv2.so: opencv library; image capture and treatment (think filters)
pystockfish_edited.py: chess engine and match classes; to get chess engine's response to move
ChessDetector.py: where the fun stuff happens; find pieces&locations, detect move, get next move
serveur.py: the python server (what else would it be); configure ChessDetector settings, serve stuff up

----------------------
4) How to run it:
----------------------
-run serveur.py first, then app.js second (close them in reverse order)
    - config: -if you want a match vs engine, set c.is_match =True (default is False)
              -if you just wanna see pieces move or play against other sentient being, set c.is_match=False
              -c.three_d should be False unless you know what you're doing (have stephanes 3D client)
-open localhost:3000
(for the first couple of times right after you plug in camera, its quality isn't the best, so you might have to run serveur.py one or two times before it's good)

----------------------
5) Common errors & their solutions:
----------------------
Error:
Warning, camera failed to properly initialize!

Fix:
Unplug and replug camera.

~~~~~~~~

Error:
(lots of traceback stuff)...in find_pieces
original = cv2.add(cv2.add(cv2.add(o/2,oa/2)/2, cv2.add(ob/2,oc/2)/2)/2, cv2.add(cv2.add(od/2,oe/2)/2, cv2.add(of/2,og/2)/2)/2)
TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'

When and where it occurs:
serveur.py lauched fine, but app.js messed things up and disconnected and seurver.py shows this error

Why it occurs:
the camera isn't connected

How to fix:
plug the camera in, make sure its in the right port, maybe unplug and replug (sometimes its really not your fault, the camera is just finicky), if it's still not working check photobooth, you should see the chessboard

~~~~~~~~

Error:
SyntaxError: Unexpected token u
at Object.parse (native)    etc etc (long error statement)

When and where it occurs:
directly after lauch of app.js, in app.js

Why it occurs:
something weird with chessboard js client, don't worry

How to fix:
refresh localhost:3000, should be fine

~~~~~~~~

Error: occurs at checkmate or somewhere there about

Why:
To make it so that it warns about illegal moves and doesnt crash when white does something wrong, or it sees something wrong, I had to install a check. The problem is that the program has a very similar response to an illegal move as it does to no viable moves left. Will try to fix.

~~~~~~~~

Error:
Camera dropped frame!

Fix:
Don't worry about it. It's something with the camera driver and opencv makes it really hard to supress these print statements. (it doesn't happen in my code; it occurs in the opencv stuf) If you're motivated, go for it and try to get rid of them. The program works just as well with them there.




