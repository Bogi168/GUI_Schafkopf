from system.text import (
    tell_game_mode_announcement,
    tell_player_doubles_game_value,
    tell_player_shoots,
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
