The code for this project is essentially comprised of three files: a server (server.py), client (client.py), and text file which holds the top 300 most common english words for the prompt generation.

In order to run your own version of the demo, simply download these three files (in the FOR_DEMO folder).

Start by running the server (you can choose your own options using —help for argument details, or more simply run it in debug mode with “python3 server.py -d”)

Next, create as many clients as you would like using multiple terminal windows and the following command: python3 client.py

It is suggested to include an optional -u (or —username) parameter when running the client.py script so that you can see who is who (if no user is specified, a random uuid64 ID will be generated.

When you are ready to begin the demo, simply type “ready” in all the client windows, the server will start a countdown and the game will begin. Note that your WPM (words per minute) is also tracked while playing the game. The calculation of which is as follows:
((characters typed / 5) / time_elapsed) / 60

Questions can be directed to mlt365@nyu.edu.
