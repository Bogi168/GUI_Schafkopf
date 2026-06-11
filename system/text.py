from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from card_classes.Cards import Card, Color
    from player_classes.Player import Player
    from player_classes.Team import Team
    from game_classes.Game import Game


# regular text
def show_player_cards(player_name: str, player_cards: list[Card]) -> str:
    player_card_names = [card.card_name for card in player_cards]
    prepared_list = [
        f"{i}: {player_card_name}"
        for i, player_card_name in enumerate(player_card_names, start=1)
    ]
    return f"\n{player_name}: {" | ".join(prepared_list)}"


def show_played_card(player_name: str, decision: Card) -> str:
    return f"\n{player_name} played the card: {decision.card_name}"


def show_collector_of_cards(player_name: str, collected_cards: list[Card]) -> str:
    collected_cards_names = [
        collected_card.card_name for collected_card in collected_cards
    ]
    return f"\n{player_name} collected {", ".join(collected_cards_names[-4:])}\n"


def tell_most_point_teams(most_point_teams: list[Team]) -> str:
    most_point_team_names = [team.team_name for team in most_point_teams]
    if len(most_point_teams) == 1:
        return f"The team with the most points is: {most_point_teams[0].team_name}"
    else:
        return f"The teams with the most points are: {", ".join(most_point_team_names)}"


def tell_team_players(team_name: str, players: list[Player]) -> str:
    player_names = [player.player_name for player in players]
    if len(players) == 1:
        return f"The only player in {team_name} is: {player_names[0]}"
    else:
        return f"The players in {team_name} are: {", ".join(player_names)}"


def tell_team_points(team_name: str, points: int) -> str:
    return f"{team_name} has {points} points"


def tell_winners(winners: list[Player]) -> str:
    winner_names = [winner.player_name for winner in winners]
    if len(winners) == 1:
        return f"\nThe only game winner is: {winner_names[0]}"
    else:
        return f"\nThe game winners are: {", ".join(winner_names)}"


def tell_game_value_calculation(breakdown: str, game_value: int) -> str:
    return breakdown + f"\n\nThe game value is: {game_value}\n"


def tell_player_money(player_name: str, money: int) -> str:
    return f"{player_name:<6} has {money:^5} cents"


def tell_chosen_game_mode(
    game_name: str, chooser_name: str | None, detail: str | None = None
) -> str:
    if chooser_name is None:
        message = f"{game_name} is being played"
    else:
        message = f"{chooser_name} is playing a {game_name}"
    if detail is not None:
        message += f" ({detail})"
    return f"\n{message}."


def tell_player_wants_to_play(player_name: str, wants_to_play: bool) -> str:
    if wants_to_play:
        return f"{player_name} wants to play."
    else:
        return f"{player_name} does not want to play."


def tell_player_doubles_game_value(player_name: str) -> str:
    return f"{player_name} doubles the game value!"


def tell_player_chose_game_mode(player_name: str, game_mode: type[Game] | None) -> str:
    if game_mode is None:
        return f"{player_name} passes."
    else:
        return f"{player_name} chooses {game_mode.name}."


def tell_game_mode_announcement(
    game_mode_name: str, chooser_name: str | None, detail: str | None = None
) -> str:
    if chooser_name is None:
        message = f"{game_mode_name} is being played"
    else:
        message = f"{chooser_name} chooses {game_mode_name}"
    if detail is not None:
        message += f" ({detail})"
    return f"{message}."


no_game_phrase = "\nNo game was selected."

words_of_thanks = "\nThank you for playing!"

# text for inputs
error_message: str = "Your input is not valid!"

prompt_player_name: str = "\nEnter your name: "
prompt_play_again_message: str = "\nDo you want to play again? (Y/N): "


def prompt_ask_to_double_game_value(player_name: str) -> str:
    return f"{player_name}: Do you want to double the game value? (Y/N): "


def prompt_ask_to_choose_game(player_name: str) -> str:
    return f"{player_name}: Do you want to choose a game (Y/N): "


def prompt_choose_game(
    player_name: str,
    quitting_possible: bool,
    possible_game_mode_decisions: dict[str, type[Game]],
) -> str:
    prepared_game_mode_decisions: list[str] = [
        f"{key}: {game_mode.name}"
        for key, game_mode in possible_game_mode_decisions.items()
    ]
    if quitting_possible:
        return f"\n{player_name}: Which game do you want to choose? ({", ".join(prepared_game_mode_decisions)}) (Q to quit): "
    else:
        return f"\n{player_name}: Which game do you want to choose? ({", ".join(prepared_game_mode_decisions)}): "


def prompt_choose_color(player_name: str, valid_colors: dict[str, Color]) -> str:
    prepared_color_decisions: list[str] = [
        f"{key}: {color.display_name}" for key, color in valid_colors.items()
    ]
    return f"\n{player_name}: Which color? ({", ".join(prepared_color_decisions)}): "


def prompt_ask_for_hochzeit(player_name: str) -> str:
    return f"{player_name}: Do you want to be the partner of the Hochzeit? (Y/N): "


def prompt_ask_for_ramsch(player_name: str) -> str:
    return f"{player_name}: Do you want to play a Ramsch? (Y/N): "


def prompt_ask_player_shoots(player_name: str) -> str:
    return f"{player_name}: Do you want to shoot? (Y/N): "


def prompt_ask_player_shoots_back(player_name: str) -> str:
    return f"{player_name}: Do you want to shoot back? (Y/N): "


def prompt_ask_swap_card_decision(player_name: str, legal_mask: list[bool]) -> str:
    first_legal_index: int = legal_mask.index(True)
    last_legal_index: int = len(legal_mask) - 1 - legal_mask[::-1].index(True)
    if first_legal_index == last_legal_index:
        return f"{player_name}: Which card do you want to swap? ({first_legal_index + 1}): "
    else:
        return f"{player_name}: Which card do you want to swap? ({first_legal_index + 1}-{last_legal_index + 1}): "


def prompt_ask_play_card_decision(player_name: str, player_cards: list[Card]) -> str:
    if len(player_cards) == 1:
        return f"{player_name}: Which card do you want to play? (1): "
    else:
        return (
            f"{player_name}: Which card do you want to play? (1-{len(player_cards)}): "
        )
