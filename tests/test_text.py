from system.text import tell_game_mode_announcement
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
