from game import Game


def run():
    game = Game(4, debug=True, shuffle_cards_won=True)
    winner = game.play_game(shuffle_deck=True)
