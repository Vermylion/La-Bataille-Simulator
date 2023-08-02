import random
import math
from cards import default_deck
from player import Player


class Game:

    # Change players to a list
    def __init__(self, players: int = 2, debug: bool = False, shuffle_cards_won: bool = False):
        self.player_count = players
        self.debug = debug
        self.shuffle_cards_won = shuffle_cards_won
        self.players = []
        self.round = 0

        # Initiate player objects and create self.players list
        for i in range(1, self.player_count + 1):
            self.players.append(f'player{i}')
            globals()[self.players[i - 1]] = Player(i)

        # Debugging
        if self.debug:
            print(f'\nA {self.player_count} player game is initiated.')

    def play_game(self, shuffle_deck: bool = False):
        if shuffle_deck:
            self.shuffle_deck()

        while True:
            player_has_won = self.play_round()
            if type(player_has_won) != bool:
                return self.players[0]

            if self.round > 4500:  # 10000
                # Debugging
                if self.debug:
                    print('\nExceeding round limit. Here are the decks: ')
                    for player in self.players:
                        globals()[player].get_deck()
                return False

    def shuffle_deck(self):
        new_deck = default_deck.copy()
        random.shuffle(new_deck)

        # Call set_deck -> distributes the deck given to the players
        self.set_deck(new_deck)

    def set_deck(self, deck: list):
        new_deck = deck.copy()

        # Debugging
        if self.debug:
            print(f'\nGame starting with:')

        # Loop through each player
        for player in self.players:
            globals()[f'{player}_deck'] = []

            # Give part of the deck to the player (transfer)
            for i in range(round(len(new_deck) / (self.player_count - self.players.index(player)))):
                globals()[f'{player}_deck'].append(new_deck.pop(0))

            # Set player object deck to previously determined player deck
            globals()[player].deck = globals()[f'{player}_deck']

            # Debugging
            if self.debug:
                globals()[player].get_deck()

    def play_round(self):
        self.round += 1
        cards_played = dict()

        # Check players' deck -> if deck and won_deck amount to 0, they get eliminated
        self.check_player_deck()

        # Check for winner
        if len(self.players) == 1:
            # Debugging
            if self.debug:
                print(f'\nPlayer {globals()[self.players[0]].player_nbr} is the winner!')

            return self.players[0]

        # Debugging
        if self.debug:
            print(f'\nRound {self.round}:')

        # Get cards played into dict cards_played -> player: card
        for player in self.players:
            cards_played[player] = globals()[player].play_card()

        # Debugging
        if self.debug:
            for player in self.players:
                print(f'Player {globals()[player].player_nbr} played a {cards_played[player]}', end=' ')
                print(
                    f'(Power Score: {sum(globals()[player].deck + globals()[player].cards_won_deck) * (list(globals()[player].deck + globals()[player].cards_won_deck).count(14) + 1)}; Score: {sum(globals()[player].deck + globals()[player].cards_won_deck)}; Total Cards: {len(globals()[player].deck) + len(globals()[player].cards_won_deck)} cards; Deck: {len(globals()[player].deck)} cards; Cards Won Deck: {len(globals()[player].cards_won_deck)} cards)')

        strongest_card, winning_player = self.evaluate_cards(cards_played)

        cards_played_values = list(cards_played.values())

        # Check for battle: if so, launch battle
        battle_bool, battling_cards = self.check_for_battle(cards_played, strongest_card)
        if battle_bool:
            strongest_card, winning_player, cards_played_values = self.battle(battling_cards, cards_played_values)

        # Shuffle won cards around to imitate the variables in picking up the cards in real life
        if self.shuffle_cards_won:
            random.shuffle(cards_played_values)

        # Give cards to winning player
        globals()[winning_player].won_round(cards_played_values)

        # Debugging
        if self.debug:
            print(f"Player {globals()[winning_player].player_nbr} won this round with a {strongest_card} and won {len(cards_played_values)} cards: {', '.join(str(card) for card in cards_played_values)}")

        return False

    def evaluate_cards(self, cards: dict):
        # Separate dict into 2 lists
        cards_values = list(cards.values())
        cards_keys = list(cards.keys())

        # Evaluate the strongest card and winning player
        strongest_card = max(cards_values)
        winning_player = cards_keys[cards_values.index(strongest_card)]

        return strongest_card, winning_player

    def check_for_battle(self, cards_played: dict, strongest_card: int) -> tuple:
        # clean deck to check for double
        new_cards_played_values = list(cards_played.values())
        new_cards_played_values.remove(strongest_card)
        # True would mean the card still exists after having removed it; therefore a double
        if strongest_card in new_cards_played_values:
            battling_cards = dict()
            # Create deck of battling cards
            for player in cards_played:
                if cards_played[player] == strongest_card:
                    battling_cards[player] = strongest_card

            # Debugging
            if self.debug:
                print(f"""{' and '.join([f"Player {globals()[player].player_nbr}" for player in list(battling_cards.keys())])} are battling with their {strongest_card}'s!""")

            return True, battling_cards
        else:
            return False, cards_played

    # Need to comment
    def battle(self, battling_cards: dict, cards_played_values: list):
        played_battle_cards = dict()
        battle_cards = dict()

        for i, player in enumerate(battling_cards, start=1):
            # Check if output is False -> player doesn't have enough cards left
            player_battle_cards = globals()[player].play_battle_cards()
            if not player_battle_cards:
                continue

            played_battle_cards[player] = player_battle_cards
            # If player only has 1 card, makes sure it doesn't go into play
            if len(player_battle_cards) > 1:
                battle_cards[player] = played_battle_cards[player][-1]

        # Debugging
        if self.debug:
            print(f"""Battle: {battle_cards}; Cards in play: {played_battle_cards}""")

        strongest_card, winning_player = self.evaluate_cards(battle_cards)

        played_battle_cards_values = [value for sublist in played_battle_cards.values() for value in sublist]
        cards_played_values += played_battle_cards_values

        # Check for battle: if so, launch battle
        battle_bool, battling_cards = self.check_for_battle(battle_cards, strongest_card)
        if battle_bool:
            strongest_card, winning_player, cards_played_values = self.battle(battling_cards, cards_played_values)

        return strongest_card, winning_player, cards_played_values

    def check_player_deck(self):
        # Make second list to not impact first list cycle in 'for' loop
        players_eliminated = []
        for player in self.players:
            can_play = globals()[player].check_deck()

            if not can_play:
                players_eliminated.append(player)

        for player in players_eliminated:
            self.players.remove(player)

            # Debugging
            if self.debug:
                print(f'\nPlayer {globals()[player].player_nbr} is eliminated!')

            # Debugging
            if self.debug:
                if len(self.players) == 2:
                    print(f'\nOnly 2 players left! Here are their decks: ')
                    for player in self.players:
                        globals()[player].get_deck()
