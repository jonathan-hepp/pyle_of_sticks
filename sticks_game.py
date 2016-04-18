from collections import deque
from random import choice

class PileOfSticks:
    """ This is the model that keeps track of the sticks  """

    def __init__(self, number_of_sticks = 20):
        self._total = number_of_sticks

    def count(self):
        return self._total

    def take(self, number):
        if number < 1 or number > 3:
            raise ValueError("Number of sticks to take must not be greater than 3")
        self._total -= number
        return self._total


class Player:
    """ Base class that establishes the common behavior of the players """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def get_sticks_number(self):
        raise NotImplementedError()

    def end_game(self, i_won = False):
        raise NotImplementedError()


class HumanPlayer(Player):
    """ 
    This subclass implements all the components needed for the human player.    
    """

    def __init__(self, name = "You"):
        super().__init__(name)

    def get_sticks_number(self, sticks_left):
        number = int(input("Player " + str(self.name) + ": "))
        return number

    def end_game(self, i_won = False):
        pass

class ComputerPlayer(Player):
    """ 
    The ComputerPlayer class has a little more to it. 
    
    """

    def __init__(self, name = "Computer", number_of_sticks = 20):
        super().__init__(name)
        self._max_number = number_of_sticks + 1
        # The pool is where the Computer selects its play.
        # There is one list o values for each stick.
        self.pool = [[1,2,3] for x in range(self._max_number)]
        # The register keeps track of the plays in the current match.
        self._register = {k:None for k in range(self._max_number)}
    
    # Note: the way the number gets selected is not optimal
    # Specially considering that the pool might grow unilaterally
    # So if the most common number on the pool is not a valid one,
    # This method might iterate quite a while.
    # In order to avoid reaching the recursivity limit, a 'while'
    # loop is used instead.
    # The whole point of this approach is to avoid interfering with
    # the number selection process.
    def get_sticks_number(self, sticks_left):
        number_to_play = choice(self.pool[sticks_left-1])
        while number_to_play > sticks_left:
            number_to_play = choice(self.pool[sticks_left-1])
        self._register[sticks_left] = number_to_play
        return number_to_play
    
    # If the Computer won, the plays saved to the register are included
    # in the pool, increasing the chances that the same play gets selected
    # in the future.
    # The register gets cleaned for the next match either way.
    def end_game(self, i_won = False):
        if i_won:
            for index in self._register:
                if self._register[index] is not None:
                    self.pool[index].append(self._register[index])
        self._register = {k:None for k in range(self._max_number)}


class EndOfGame(Exception):
    """ This exception is used as a signaling tool """

    def __init__(self, loser, winners, message = "The game is over."):
        super().__init__(message)
        self.loser = loser
        self.winners = winners
        self.message = message


class Game:
    """ 
    Although the game is meant to be played by 2 players using 20 sticks,
    this class is flexible enough to allow an arbitrary number of those.
    """

    def __init__(self, pile_of_sticks, computer_player, human_players):
        self.pile = pile_of_sticks
        self.computer_player = computer_player
        self.human_players = human_players
        self.current_player = None
        all_players = human_players[:]
        all_players.insert(0, computer_player)
        self._players_deque = deque(all_players)

    def next_round(self):
        self._players_deque.rotate()
        self.current_player = self._players_deque[0]

    def play(self, number, rotate = True):
        if rotate:
            self.next_round()
        self.pile.take(number)
        if(self.pile.count() <= 0):
            raise EndOfGame(self.current_player, [p for p in self._players_deque if p is not self.current_player])


if __name__ == '__main__':
    print("Welcome to the Game of Sticks!")
    pile = PileOfSticks()
    player1 = HumanPlayer(input("Type your name: "))
    computer = ComputerPlayer("HAL 9000")
    game = Game(pile, computer, [player1])
    while True:
        try:
            print("The pile has " + str(pile.count()) + " sticks")
            game.next_round()
            number = game.current_player.get_sticks_number(pile.count())
            print(str(game.current_player) + " took " + str(number) + " stick" + ("" if number == 1 else "s") + " from the pile")
            game.play(number, False)
        except EndOfGame as endGame:
            endGame.loser.end_game(False)
            print("Player " + str(endGame.loser) + " lost")
            for player in endGame.winners:
                player.end_game(True)
            if input("End of Game. Want to play again? [Y/n]").lower() == "n":
                break
            pile = PileOfSticks()
            game = Game(pile, computer, [player1])





