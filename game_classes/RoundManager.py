from __future__ import annotations
from typing import TYPE_CHECKING

from player_classes.Team import Team

if TYPE_CHECKING:
    from player_classes.Player import Player
    from card_classes.Cards import Card
    from card_classes.CardPowerCalculator import CardPowerCalculator
    from input_validators.CardDecisionValidator import CardDecisionValidator
    from game_classes.GameRenderer import GameRenderer


class RoundManager:
    def __init__(
        self,
        players: list[Player],
        player_teams: dict[Player, Team],
        trumps: list[Card],
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        active_team: Team | None,
        game_renderer: GameRenderer,
    ) -> None:
        self.players: list[Player] = players
        self.player_teams: dict[Player, Team] = player_teams
        self.trumps: list[Card] = trumps
        self.active_team: Team | None = active_team
        self.card_power_calculator: CardPowerCalculator = card_power_calculator
        self.card_decision_validator: CardDecisionValidator = card_decision_validator
        self.game_renderer: GameRenderer = game_renderer
        self.played_cards: list[Card] = []
        self.amt_game_val_doubles: int = 0

    @property
    def lead_card(self) -> Card | None:
        """
        :return: The first played card of the round
        :rtype: Card | None
        """

        if self.played_cards:
            return self.played_cards[0]
        else:
            return None

    def handle_shooting(self, players_team: Team, player: Player) -> bool:
        if self.active_team is None or players_team == self.active_team:
            return True
        if player.ask_shoot():
            self.amt_game_val_doubles += 1
            for prev_active_player in self.active_team.players:
                if prev_active_player.ask_shoot(ask_shoot_back=True):
                    self.amt_game_val_doubles += 1
                    break
            else:
                self.active_team = players_team
            shooting_possible: bool = False
            return shooting_possible
        else:
            shooting_possible: bool = True
            return shooting_possible

    def play_card(self, player: Player) -> None:
        card_decision: Card = player.get_card_play_decision(
            move_validator=lambda d, p=player: self.card_decision_validator.is_move_legal(
                player_cards=p.player_cards,
                decision=d,
                trumps=self.trumps,
                lead_card=self.lead_card,
            ),
        )
        self.played_cards.append(card_decision)
        self.game_renderer.render_played_cards(played_cards=self.played_cards)

    def get_round_winner(self) -> Player:
        strongest_card: Card = self.card_power_calculator.get_strongest_played_card(
            played_cards=self.played_cards, trumps=self.trumps
        )
        round_winner_index: int = self.played_cards.index(strongest_card)
        round_winner: Player = self.players[round_winner_index]
        return round_winner

    def reward_round_winner(self, round_winner: Player) -> None:
        for card in self.played_cards:
            round_winner.collected_cards.append(card)
        self.game_renderer.render_collector_of_cards(collector=round_winner)

    def sort_players(self, starter: Player) -> None:
        """
        Sorts the list of Players.
        The given starter moves to Index 0, but the order remains the same.
        :param starter: The player who should start the next game or round
        :type starter: Player
        :return: None
        """

        starter_index = self.players.index(starter)
        self.players = self.players[starter_index:] + self.players[:starter_index]

    def prepare_next_round(self, round_winner: Player) -> None:
        self.sort_players(starter=round_winner)
        self.played_cards.clear()

    def play_round(self, is_first_round: bool) -> None:
        """
        Simulates one round. Every player gets to play a card.
        The player who plays the strongest card is the round winner
        and starts the next round.
        :param is_first_round: A boolean indicating whether it is the first round of the game
        :type is_first_round: bool
        :return: None
        """

        shooting_possible: bool = is_first_round

        for player in self.players:
            if shooting_possible:
                shooting_possible = self.handle_shooting(
                    players_team=self.player_teams[player], player=player
                )
            self.play_card(player=player)


class RamschRoundManager(RoundManager):

    def __init__(
        self,
        players: list[Player],
        player_teams: dict[Player, Team],
        trumps: list[Card],
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        game_renderer: GameRenderer,
    ) -> None:
        super().__init__(
            players=players,
            player_teams=player_teams,
            trumps=trumps,
            card_power_calculator=card_power_calculator,
            card_decision_validator=card_decision_validator,
            active_team=None,
            game_renderer=game_renderer,
        )
        self.active_players: list[Player] = []

    def handle_shooting(self, players_team: Team, player: Player) -> bool:
        if player.ask_shoot():
            self.amt_game_val_doubles += 1
            self.active_players.append(player)
        shooting_possible: bool = True
        return shooting_possible
