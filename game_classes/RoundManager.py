from __future__ import annotations
from typing import TYPE_CHECKING

from player_classes.Team import Team
from player_classes.card_play_strategy import CardPlayContext
from player_classes.team_knowledge import infer_team_knowledge

if TYPE_CHECKING:
    from player_classes.Player import Player
    from card_classes.Cards import Card
    from card_classes.CardPowerCalculator import CardPowerCalculator
    from input_validators.CardDecisionValidator import CardDecisionValidator
    from system.Renderer import Renderer


class RoundManager:
    is_ramsch: bool = False

    def __init__(
        self,
        players: list[Player],
        player_teams: dict[Player, Team],
        trumps: list[Card],
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        active_team: Team | None,
        renderer: Renderer,
        is_tout: bool = False,
    ) -> None:
        self.players: list[Player] = players
        self.player_teams: dict[Player, Team] = player_teams
        self.trumps: list[Card] = trumps
        self.active_team: Team | None = active_team
        self.card_power_calculator: CardPowerCalculator = card_power_calculator
        self.card_decision_validator: CardDecisionValidator = card_decision_validator
        self.renderer: Renderer = renderer
        self.is_tout: bool = is_tout
        self.game_chooser: Player | None = None
        self.call_sau: Card | None = None
        self.known_trumpless: list[Player] = []
        self.played_cards: list[Card] = []
        self.trick_history: list[list[tuple[Player, Card]]] = []
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

    @property
    def current_trick(self) -> list[tuple[Player, Card]]:
        """
        :return: The (player, card) pairs played so far in the current round
        :rtype: list[tuple[Player, Card]]
        """

        return list(zip(self.players, self.played_cards))

    def handle_shooting(self, players_team: Team, player: Player) -> bool:
        if self.active_team is None or players_team == self.active_team:
            return True
        shoots = player.ask_shoot(
            trumps=self.trumps, is_tout=self.is_tout, is_ramsch=self.is_ramsch
        )
        self.renderer.render_shoot_decision(player=player, shoots=shoots)
        if shoots:
            self.amt_game_val_doubles += 1
            for prev_active_player in self.active_team.players:
                shoots_back = prev_active_player.ask_shoot(
                    ask_shoot_back=True,
                    trumps=self.trumps,
                    is_tout=self.is_tout,
                    is_ramsch=self.is_ramsch,
                )
                self.renderer.render_shoot_decision(
                    player=prev_active_player, shoots=shoots_back, is_shoot_back=True
                )
                if shoots_back:
                    self.amt_game_val_doubles += 1
                    break
            else:
                self.active_team = players_team
            shooting_possible: bool = False
            return shooting_possible
        else:
            shooting_possible: bool = True
            return shooting_possible

    def _build_context(self, player: Player) -> CardPlayContext:
        played_cards_history: list[Card] = [
            card for trick in self.trick_history for _, card in trick
        ]
        team_knowledge = infer_team_knowledge(
            player=player,
            players=self.players,
            player_teams=self.player_teams,
            game_chooser=self.game_chooser,
            call_sau=self.call_sau,
            trick_history=self.trick_history,
        )
        team_sizes = {len(team.players) for team in self.player_teams.values()}
        return CardPlayContext(
            current_trick=self.current_trick,
            trumps=self.trumps,
            card_power_calculator=self.card_power_calculator,
            played_cards_history=played_cards_history,
            team_knowledge=team_knowledge,
            is_ramsch=self.is_ramsch,
            is_tout=self.is_tout,
            is_active_team=self.player_teams[player] is self.active_team,
            is_solo_mode=team_sizes == {1, 3},
            call_sau=self.call_sau,
            tricks_remaining=len(player.player_cards),
            trick_history=list(self.trick_history),
            known_trumpless=list(self.known_trumpless),
        )

    def play_card(self, player: Player) -> None:
        context: CardPlayContext | None = (
            self._build_context(player) if player.is_bot else None
        )
        was_lead: bool = self.lead_card is None
        card_decision: Card = player.get_card_play_decision(
            move_validator=lambda d, p=player: self.card_decision_validator.is_move_legal(
                player_cards=p.player_cards,
                decision=d,
                trumps=self.trumps,
                lead_card=self.lead_card,
            ),
            context=context,
        )
        self.played_cards.append(card_decision)
        self.card_decision_validator.notify_card_played(
            card=card_decision, was_lead=was_lead, player_cards=player.player_cards
        )
        self.renderer.render_played_card(player=player, card=card_decision)

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
        self.renderer.render_trick_winner(winner=round_winner)

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
        self.trick_history.append(self.current_trick)
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
    is_ramsch: bool = True

    def __init__(
        self,
        players: list[Player],
        player_teams: dict[Player, Team],
        trumps: list[Card],
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        renderer: Renderer,
    ) -> None:
        super().__init__(
            players=players,
            player_teams=player_teams,
            trumps=trumps,
            card_power_calculator=card_power_calculator,
            card_decision_validator=card_decision_validator,
            active_team=None,
            renderer=renderer,
        )
        self.active_players: list[Player] = []

    def handle_shooting(self, players_team: Team, player: Player) -> bool:
        shoots = player.ask_shoot(is_ramsch=True)
        self.renderer.render_shoot_decision(player=player, shoots=shoots)
        if shoots:
            self.amt_game_val_doubles += 1
            self.active_players.append(player)
        shooting_possible: bool = True
        return shooting_possible
