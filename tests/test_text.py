from card_classes.Cards import Color
from game_classes.game_modes.Sauspiel import Sauspiel
from game_classes.game_modes.Wenz import Wenz
from system.text import (
    show_collector_of_cards,
    show_played_card,
    show_player_cards,
    prompt_ask_play_card_decision,
    prompt_ask_swap_card_decision,
    prompt_choose_color,
    prompt_choose_game,
    tell_game_mode_announcement,
    tell_game_value_calculation,
    tell_most_point_teams,
    tell_player_chose_game_mode,
    tell_player_doubles_game_value,
    tell_player_money,
    tell_player_shoots,
    tell_team_players,
    tell_team_points,
    tell_winners,
)
from system.Renderer import ConsoleRenderer


def test_tell_game_mode_announcement_with_chooser_and_detail():
    assert (
        tell_game_mode_announcement(
            game_mode_name="Sauspiel", chooser_name="Daniel", detail="Eichel Sau"
        )
        == "Daniel chooses Sauspiel (Eichel Sau)."
    )


def test_tell_game_mode_announcement_with_chooser_no_detail():
    assert (
        tell_game_mode_announcement(game_mode_name="Wenz", chooser_name="Daniel")
        == "Daniel chooses Wenz."
    )


def test_tell_game_mode_announcement_without_chooser():
    assert (
        tell_game_mode_announcement(game_mode_name="Ramsch", chooser_name=None)
        == "Ramsch is being played."
    )


def test_console_renderer_announces_game_mode_with_detail(capsys, player_1):
    renderer = ConsoleRenderer()

    renderer.render_game_mode_announcement(
        game_mode_name="Sauspiel", chooser=player_1, detail="Eichel Sau"
    )

    captured = capsys.readouterr()
    assert captured.out.strip() == "Testplayer 1 chooses Sauspiel (Eichel Sau)."


def test_console_renderer_announces_game_mode_without_chooser(capsys):
    renderer = ConsoleRenderer()

    renderer.render_game_mode_announcement(game_mode_name="Ramsch", chooser=None)

    captured = capsys.readouterr()
    assert captured.out.strip() == "Ramsch is being played."


def test_console_renderer_render_farewell(capsys):
    renderer = ConsoleRenderer()

    renderer.render_farewell("\nThank you for playing!")

    captured = capsys.readouterr()
    assert captured.out.strip() == "Thank you for playing!"


def test_tell_player_doubles_game_value():
    assert (
        tell_player_doubles_game_value(player_name="Daniel")
        == "Daniel doubles the game value!"
    )


def test_console_renderer_announces_double_game_value(capsys, player_1):
    renderer = ConsoleRenderer()

    renderer.render_double_game_value_decision(player=player_1, doubles=True)

    captured = capsys.readouterr()
    assert captured.out.strip() == "Testplayer 1 doubles the game value!"


def test_console_renderer_does_not_announce_when_not_doubling(capsys, player_1):
    renderer = ConsoleRenderer()

    renderer.render_double_game_value_decision(player=player_1, doubles=False)

    captured = capsys.readouterr()
    assert captured.out == ""


def test_tell_player_shoots():
    assert tell_player_shoots(player_name="Daniel") == "Daniel shoots!"


def test_tell_player_shoots_back():
    assert (
        tell_player_shoots(player_name="Daniel", is_shoot_back=True)
        == "Daniel shoots back!"
    )


def test_console_renderer_announces_shoot(capsys, player_1):
    renderer = ConsoleRenderer()

    renderer.render_shoot_decision(player=player_1, shoots=True)

    captured = capsys.readouterr()
    assert captured.out.strip() == "Testplayer 1 shoots!"


def test_console_renderer_announces_shoot_back(capsys, player_1):
    renderer = ConsoleRenderer()

    renderer.render_shoot_decision(player=player_1, shoots=True, is_shoot_back=True)

    captured = capsys.readouterr()
    assert captured.out.strip() == "Testplayer 1 shoots back!"


def test_console_renderer_does_not_announce_when_not_shooting(capsys, player_1):
    renderer = ConsoleRenderer()

    renderer.render_shoot_decision(player=player_1, shoots=False)

    captured = capsys.readouterr()
    assert captured.out == ""


# --- show_player_cards ---


def test_show_player_cards_lists_cards_one_indexed(eichel_sau, herz_ober):
    result = show_player_cards("Daniel", [eichel_sau, herz_ober])

    assert result == "\nDaniel: 1: (Eichel Sau) | 2: (Herz Ober)"


def test_show_player_cards_with_three_cards(eichel_sau, herz_ober, gruen_unter):
    result = show_player_cards("Daniel", [eichel_sau, herz_ober, gruen_unter])

    assert (
        result
        == "\nDaniel: 1: (Eichel Sau) | 2: (Herz Ober) | 3: (Grün Unter)"
    )


# --- show_played_card ---


def test_show_played_card(eichel_sau):
    result = show_played_card("Daniel", eichel_sau)

    assert result == "\nDaniel played the card: (Eichel Sau)"


# --- show_collector_of_cards ---


def test_show_collector_of_cards_with_up_to_four_cards(eichel_sau, herz_ober):
    result = show_collector_of_cards("Daniel", [eichel_sau, herz_ober])

    assert result == "\nDaniel collected (Eichel Sau), (Herz Ober)\n"


def test_show_collector_of_cards_with_more_than_four_cards(
    eichel_sau, herz_ober, gruen_unter, schellen_koenig, eichel_ten
):
    collected_cards = [eichel_sau, herz_ober, gruen_unter, schellen_koenig, eichel_ten]

    result = show_collector_of_cards("Daniel", collected_cards)

    assert (
        result
        == "\nDaniel collected (Herz Ober), (Grün Unter), (Schellen König), (Eichel 10)\n"
    )


# --- tell_most_point_teams ---


def test_tell_most_point_teams_singular(team_alone_player_1):
    result = tell_most_point_teams([team_alone_player_1])

    assert result == "The team with the most points is: TeamAlonePlayer1"


def test_tell_most_point_teams_plural(team_alone_player_1, team_two_players_2):
    result = tell_most_point_teams([team_alone_player_1, team_two_players_2])

    assert (
        result
        == "The teams with the most points are: TeamAlonePlayer1, TeamTwoPlayers2"
    )


# --- tell_team_players ---


def test_tell_team_players_singular(player_1):
    result = tell_team_players("TeamAlonePlayer1", [player_1])

    assert result == "The only player in TeamAlonePlayer1 is: Testplayer 1"


def test_tell_team_players_plural(player_1, player_2):
    result = tell_team_players("TeamTwoPlayers1", [player_1, player_2])

    assert (
        result
        == "The players in TeamTwoPlayers1 are: Testplayer 1, Testplayer 2"
    )


# --- tell_winners ---


def test_tell_winners_singular(player_1):
    result = tell_winners([player_1])

    assert result == "\nThe only game winner is: Testplayer 1"


def test_tell_winners_plural(player_1, player_2):
    result = tell_winners([player_1, player_2])

    assert result == "\nThe game winners are: Testplayer 1, Testplayer 2"


# --- tell_team_points ---


def test_tell_team_points():
    result = tell_team_points("TeamAlonePlayer1", 60)

    assert result == "TeamAlonePlayer1 has 60 points"


# --- tell_game_value_calculation ---


def test_tell_game_value_calculation():
    breakdown = "Base: 20\nRunners: 10"

    result = tell_game_value_calculation(breakdown, 30)

    assert result == "Base: 20\nRunners: 10\n\nThe game value is: 30\n"


# --- tell_player_money ---


def test_tell_player_money_short_name_and_single_digit_money():
    result = tell_player_money("Bo", 5)

    assert result == "Bo     has   5   cents"


def test_tell_player_money_short_name_and_multi_digit_money():
    result = tell_player_money("Bo", 1234)

    assert result == "Bo     has 1234  cents"


# --- tell_player_chose_game_mode ---


def test_tell_player_chose_game_mode_passes():
    result = tell_player_chose_game_mode("Daniel", None)

    assert result == "Daniel passes."


def test_tell_player_chose_game_mode_chooses():
    result = tell_player_chose_game_mode("Daniel", Sauspiel)

    assert result == "Daniel chooses Sauspiel."


# --- prompt_choose_game ---


def test_prompt_choose_game_with_quitting_possible():
    decisions = {"1": Sauspiel, "2": Wenz}

    result = prompt_choose_game("Daniel", True, decisions)

    assert (
        result
        == "\nDaniel: Which game do you want to choose? (1: Sauspiel, 2: Wenz) (Q to quit): "
    )


def test_prompt_choose_game_without_quitting_possible():
    decisions = {"1": Sauspiel, "2": Wenz}

    result = prompt_choose_game("Daniel", False, decisions)

    assert (
        result
        == "\nDaniel: Which game do you want to choose? (1: Sauspiel, 2: Wenz): "
    )


# --- prompt_choose_color ---


def test_prompt_choose_color():
    valid_colors = {"1": Color.EICHEL, "2": Color.GRUEN}

    result = prompt_choose_color("Daniel", valid_colors)

    assert result == "\nDaniel: Which color? (1: Eichel, 2: Grün): "


# --- prompt_ask_swap_card_decision ---


def test_prompt_ask_swap_card_decision_single_card():
    legal_mask = [False, True, False]

    result = prompt_ask_swap_card_decision("Daniel", legal_mask)

    assert result == "Daniel: Which card do you want to swap? (2): "


def test_prompt_ask_swap_card_decision_range():
    legal_mask = [True, False, True, True]

    result = prompt_ask_swap_card_decision("Daniel", legal_mask)

    assert result == "Daniel: Which card do you want to swap? (1-4): "


# --- prompt_ask_play_card_decision ---


def test_prompt_ask_play_card_decision_single_card(eichel_sau):
    result = prompt_ask_play_card_decision("Daniel", [eichel_sau])

    assert result == "Daniel: Which card do you want to play? (1): "


def test_prompt_ask_play_card_decision_multiple_cards(eichel_sau, herz_ober, gruen_unter):
    result = prompt_ask_play_card_decision("Daniel", [eichel_sau, herz_ober, gruen_unter])

    assert result == "Daniel: Which card do you want to play? (1-3): "
