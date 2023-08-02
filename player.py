class Player:

    def __init__(self, player_nbr: int, deck: list = []):
        self.player_nbr = player_nbr
        self.deck = deck
        self.cards_won_deck = []

    def play_card(self) -> int:
        card = self.deck.pop(0)

        return card

    # Maybe rewrite code -> it's a mess
    def play_battle_cards(self) -> list | bool:
        battle_cards = []

        if len(self.deck) < 2:
            if len(self.deck + self.cards_won_deck) < 2:
                if len(self.deck + self.cards_won_deck) == 0:
                    return False
                else:
                    battle_cards.append(self.deck.pop(0))
                    return battle_cards
            else:
                self.deck += self.cards_won_deck.copy()
                self.cards_won_deck = []

        for i in range(2):
            battle_cards.append(self.deck.pop(0))

        return battle_cards

    def won_round(self, cards_won: list):
        self.cards_won_deck += cards_won

    def check_deck(self):
        # If current deck is empty, switch it with the won cards
        if len(self.deck) == 0:
            self.deck = self.cards_won_deck.copy()
            self.cards_won_deck = []

        # If the deck is still empty, the player has lost
        if len(self.deck) == 0:
            return False
        return True

    # Debugging
    def get_deck(self):
        print(
            f'Player {self.player_nbr} stats: Power Score: {sum(self.deck + self.cards_won_deck) * (list(self.deck + self.cards_won_deck).count(14) + 1)}; Score: {sum(self.deck + self.cards_won_deck)}; Total Cards: {len(self.deck) + len(self.cards_won_deck)} cards; Deck: {len(self.deck)} cards; Cards Won Deck: {len(self.cards_won_deck)} cards')
        print(f"Player {self.player_nbr} deck: {self.deck} ({len(self.deck)} cards)")
        print(f"Player {self.player_nbr} cards won deck: {self.cards_won_deck} ({len(self.cards_won_deck)} cards)")
