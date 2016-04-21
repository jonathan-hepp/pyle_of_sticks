from flask import abort, Flask, jsonify, render_template, request, session
from flask.ext.session import Session
from sticks_game import ComputerPlayer, EndOfGame, Game, HumanPlayer, PileOfSticks

app = Flask(__name__)
app.secret_key = "CHANGEIT"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# The pool of values shared by all computer players.
# If the app would be accessed by a lot of people at the same time
# some safe checking could be done here, just in case, but since 
# that's not the case and we only read and append, it's not really an issue. 
shared_pool = [[1,2,3] for x in range(21)]

def new_game_builder(human_player = None, computer_player = None):
    if computer_player is None:
        computer_player = ComputerPlayer()
        computer_player.pool = shared_pool
    if human_player is None:
        human_player = HumanPlayer()
    return Game(PileOfSticks(), computer_player, [human_player])


@app.route('/')
def index():
    if "game" not in session:
        session["game"] = new_game_builder()
    return render_template("index.html", initial_sticks=session["game"].pile.count())

# This method gets the number played by the user and then generates the number
# that the computer will play, returning the value to the view.
# If the game ends, we update the current game with a new one and return appropriate
# data to the view.
@app.route("/play", methods=["POST"])
def play():
    comp_number = 0
    try:
        if "game" in session:
            game = session["game"]
            number = int(request.form["number"])
            game.play(number)
            comp_number = game.computer_player.get_sticks_number(game.pile.count())
            game.play(comp_number)
            return jsonify({"number": comp_number})
        abort(401)
    except EndOfGame as error:
        session["game"].computer_player.end_game(error.loser is session["game"].human_players[0])
        session["game"] = new_game_builder(session["game"].human_players[0], session["game"].computer_player)
        return jsonify({"endOfGame": True, "loser": error.loser.name, "number": comp_number})


@app.errorhandler(401)
def session_expired(error):
    return "The session has expired.", 401

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
