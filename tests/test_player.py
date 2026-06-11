from unittest.mock import MagicMock

from card_classes.Cards import Color, Type
from player_classes.Player import Bot
from system.Renderer import ColorChoiceKind, YesNoKind


def test_points_sums_collected_card_points(eichel_ober, herz_sau, player_1):
    player_1.collected_cards = [eichel_ober, herz_sau]

    assert player_1.points == 14


def test_points_is_zero_with_no_collected_cards(player_1):
    player_1.collected_cards = []

    assert player_1.points == 0


def test_player_is_not_a_bot(player_1):
    assert player_1.is_bot is False


def test_bot_is_a_bot():
    bot = Bot(bot_name="B", renderer=MagicMock(), game_decision_validator=MagicMock())

    assert bot.is_bot is True


def test_repr_returns_player_name(player_1):
    assert repr(player_1) == "Testplayer 1"


def test_ask_double_game_value_true(player_1, eichel_ober, herz_sau):
    player_1.player_cards = [eichel_ober, herz_sau]
    player_1.renderer.ask_yes_no.return_value = True

    result = player_1.ask_double_game_value()

    assert result is True
    player_1.renderer.render_hand.assert_called_once_with(
        player=player_1, cards=player_1.player_cards
    )
    player_1.renderer.ask_yes_no.assert_called_once_with(
        player=player_1, kind=YesNoKind.DOUBLE_GAME_VALUE
    )


def test_ask_double_game_value_false(player_1, eichel_ober, herz_sau):
    player_1.player_cards = [eichel_ober, herz_sau]
    player_1.renderer.ask_yes_no.return_value = False

    result = player_1.ask_double_game_value()

    assert result is False
    player_1.renderer.ask_yes_no.assert_called_once_with(
        player=player_1, kind=YesNoKind.DOUBLE_GAME_VALUE
    )


def test_ask_want_choose_game_returns_renderer_result(player_1):
    player_1.renderer.ask_yes_no.return_value = True

    result = player_1.ask_want_choose_game(players_who_want_to_play_count=2)

    assert result is True
    player_1.renderer.ask_yes_no.assert_called_once_with(
        player=player_1, kind=YesNoKind.CHOOSE_GAME
    )


def test_ask_want_choose_game_returns_false(player_1):
    player_1.renderer.ask_yes_no.return_value = False

    result = player_1.ask_want_choose_game(players_who_want_to_play_count=0)

    assert result is False


def test_ask_for_hochzeit_disallows_yes_for_all_trump_hand(
    player_1, eichel_ober, eichel_unter, herz_unter, schellen_ober
):
    player_1.player_cards = [eichel_ober, eichel_unter, herz_unter, schellen_ober]
    player_1.renderer.ask_yes_no.return_value = False

    result = player_1.ask_for_hochzeit()

    assert result is False
    player_1.renderer.render_hand.assert_called_once_with(
        player=player_1, cards=player_1.player_cards
    )
    call_kwargs = player_1.renderer.ask_yes_no.call_args.kwargs
    assert call_kwargs["kind"] == YesNoKind.HOCHZEIT
    assert call_kwargs["allow_yes"] is False


def test_ask_for_hochzeit_disallows_yes_for_all_herz_hand(
    player_1, herz_sau, herz_ten, herz_koenig
):
    player_1.player_cards = [herz_sau, herz_ten, herz_koenig]
    player_1.renderer.ask_yes_no.return_value = False

    player_1.ask_for_hochzeit()

    call_kwargs = player_1.renderer.ask_yes_no.call_args.kwargs
    assert call_kwargs["allow_yes"] is False


def test_ask_for_hochzeit_allows_yes_with_loose_card(
    player_1, eichel_ober, gruen_sau
):
    player_1.player_cards = [eichel_ober, gruen_sau]
    player_1.renderer.ask_yes_no.return_value = True

    result = player_1.ask_for_hochzeit()

    assert result is True
    call_kwargs = player_1.renderer.ask_yes_no.call_args.kwargs
    assert call_kwargs["allow_yes"] is True


def test_get_sau_color(player_1, eichel_ober):
    player_1.player_cards = [eichel_ober]
    valid_inputs = {"1": Color.EICHEL}
    player_1.game_decision_validator.get_valid_call_sau_color_inputs.return_value = (
        valid_inputs
    )
    player_1.renderer.ask_color.return_value = Color.EICHEL

    result = player_1.get_sau_color()

    assert result == Color.EICHEL
    player_1.game_decision_validator.get_valid_call_sau_color_inputs.assert_called_once_with(
        player_cards=player_1.player_cards
    )
    call_kwargs = player_1.renderer.ask_color.call_args.kwargs
    assert call_kwargs["options"] == valid_inputs
    assert call_kwargs["kind"] == ColorChoiceKind.SAU
    assert call_kwargs["player"] == player_1


def test_get_trump_color(player_1):
    valid_inputs = {"1": Color.HERZ}
    player_1.game_decision_validator.get_valid_solo_color_inputs.return_value = (
        valid_inputs
    )
    player_1.renderer.ask_color.return_value = Color.HERZ

    result = player_1.get_trump_color()

    assert result == Color.HERZ
    player_1.game_decision_validator.get_valid_solo_color_inputs.assert_called_once_with()
    call_kwargs = player_1.renderer.ask_color.call_args.kwargs
    assert call_kwargs["options"] == valid_inputs
    assert call_kwargs["kind"] == ColorChoiceKind.TRUMP
    assert call_kwargs["player"] == player_1


def test_choose_game_mode_quitting_possible_true(player_1):
    valid_decisions = {"1": object()}
    player_1.game_decision_validator.get_valid_game_mode_decisions.return_value = (
        valid_decisions
    )
    player_1.renderer.ask_game_mode.return_value = None

    result = player_1.choose_game_mode(prev_game_mode=None, quitting_possible=True)

    assert result is None
    player_1.game_decision_validator.get_valid_game_mode_decisions.assert_called_once_with(
        prev_game_mode=None, player_cards=player_1.player_cards
    )
    call_kwargs = player_1.renderer.ask_game_mode.call_args.kwargs
    assert call_kwargs["options"] == valid_decisions
    assert call_kwargs["quitting_possible"] is True
    assert call_kwargs["player"] == player_1


def test_choose_game_mode_quitting_possible_false(player_1):
    chosen_mode = object()
    valid_decisions = {"1": chosen_mode}
    player_1.game_decision_validator.get_valid_game_mode_decisions.return_value = (
        valid_decisions
    )
    player_1.renderer.ask_game_mode.return_value = chosen_mode

    result = player_1.choose_game_mode(prev_game_mode=None, quitting_possible=False)

    assert result is chosen_mode
    call_kwargs = player_1.renderer.ask_game_mode.call_args.kwargs
    assert call_kwargs["quitting_possible"] is False


def test_ask_for_ramsch(player_1):
    player_1.renderer.ask_yes_no.return_value = True

    result = player_1.ask_for_ramsch()

    assert result is True
    player_1.renderer.ask_yes_no.assert_called_once_with(
        player=player_1, kind=YesNoKind.RAMSCH
    )


def test_ask_for_ramsch_false(player_1):
    player_1.renderer.ask_yes_no.return_value = False

    result = player_1.ask_for_ramsch()

    assert result is False


def test_ask_shoot_default_uses_shoot_kind(player_1, eichel_ober):
    player_1.player_cards = [eichel_ober]
    player_1.renderer.ask_yes_no.return_value = True

    result = player_1.ask_shoot()

    assert result is True
    player_1.renderer.render_hand.assert_called_once_with(
        player=player_1, cards=player_1.player_cards
    )
    player_1.renderer.ask_yes_no.assert_called_once_with(
        player=player_1, kind=YesNoKind.SHOOT
    )


def test_ask_shoot_back_uses_shoot_back_kind(player_1, eichel_ober):
    player_1.player_cards = [eichel_ober]
    player_1.renderer.ask_yes_no.return_value = False

    result = player_1.ask_shoot(ask_shoot_back=True)

    assert result is False
    player_1.renderer.ask_yes_no.assert_called_once_with(
        player=player_1, kind=YesNoKind.SHOOT_BACK
    )


def test_get_card_swap_decision(player_1, eichel_ober, gruen_sau, herz_unter):
    player_1.player_cards = [eichel_ober, gruen_sau, herz_unter]
    rendered_hands = []
    player_1.renderer.render_hand.side_effect = (
        lambda player, cards: rendered_hands.append(list(cards))
    )
    player_1.renderer.ask_card.return_value = 1

    move_validator = lambda c: c.card_type != Type.OBER

    result = player_1.get_card_swap_decision(move_validator)

    assert result == gruen_sau
    assert player_1.player_cards == [eichel_ober, herz_unter]
    assert rendered_hands == [[eichel_ober, gruen_sau, herz_unter]]
    call_kwargs = player_1.renderer.ask_card.call_args.kwargs
    assert call_kwargs["legal_mask"] == [False, True, True]
    assert call_kwargs["is_swap"] is True
    assert call_kwargs["player"] == player_1


def test_get_card_play_decision(player_1, eichel_ober, gruen_sau, herz_unter):
    player_1.player_cards = [eichel_ober, gruen_sau, herz_unter]
    rendered_hands = []
    player_1.renderer.render_hand.side_effect = (
        lambda player, cards: rendered_hands.append(list(cards))
    )
    player_1.renderer.ask_card.return_value = 0

    move_validator = lambda c: c.card_type != Type.UNTER

    result = player_1.get_card_play_decision(move_validator)

    assert result == eichel_ober
    assert player_1.player_cards == [gruen_sau, herz_unter]
    assert rendered_hands == [[eichel_ober, gruen_sau, herz_unter]]
    call_kwargs = player_1.renderer.ask_card.call_args.kwargs
    assert call_kwargs["legal_mask"] == [True, True, False]
    assert "is_swap" not in call_kwargs
    assert call_kwargs["player"] == player_1


def test_get_card_play_decision_ignores_context(player_1, eichel_ober, gruen_sau):
    player_1.player_cards = [eichel_ober, gruen_sau]
    player_1.renderer.ask_card.return_value = 1

    move_validator = lambda c: True

    result = player_1.get_card_play_decision(move_validator, context="some context")

    assert result == gruen_sau
    assert player_1.player_cards == [eichel_ober]
