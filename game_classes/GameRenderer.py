from __future__ import annotations
from typing import TYPE_CHECKING

from system.Renderer import Renderer
from system.text import (
    show_played_cards,
    show_collector_of_cards,
    tell_most_point_teams,
    tell_team_points,
    tell_team_players,
    tell_winners,
    tell_player_money,
    tell_game_value_calculation,
)

if TYPE_CHECKING:
    from card_classes.Cards import Card
    from player_classes.Player import Player
    from player_classes.Team import Team
    from money_handling.GameValueCalculator import GameValueCalculator


class GameRenderer:
    def __init__(self, renderer: Renderer):
        self.renderer = renderer

    def render_played_cards(self, played_cards: list[Card]):
        self.renderer.render(message=show_played_cards(played_cards=played_cards))

    def render_collector_of_cards(self, collector: Player):
        self.renderer.render(
            message=show_collector_of_cards(
                player_name=collector.player_name,
                collected_cards=collector.collected_cards,
            )
        )

    def render_most_point_teams(self, most_point_teams: list[Team]):
        self.renderer.render(
            message=tell_most_point_teams(most_point_teams=most_point_teams)
        )

    def render_team_points(self, team: Team):
        self.renderer.render(
            message=tell_team_points(team_name=team.team_name, points=team.points)
        )

    def render_team_players(self, team: Team):
        self.renderer.render(
            message=tell_team_players(team_name=team.team_name, players=team.players)
        )

    def render_winners(self, winners: list[Player]):
        self.renderer.render(message=tell_winners(winners=winners))

    def render_game_value_calculation(
        self,
        gv_calculator: GameValueCalculator,
        game_value: int,
    ):
        self.renderer.render(
            message=tell_game_value_calculation(
                gv_calculator=gv_calculator,
                game_value=game_value,
            )
        )

    def render_player_money(self, player: Player):
        self.renderer.render(
            message=tell_player_money(
                player_name=player.player_name, money=player.money
            )
        )
