import pytest
from game_classes.game_modes.Sauspiel import Sauspiel
from game_classes.game_modes.Wenz import Wenz
from game_classes.game_modes.Solo import Solo
from card_classes.Cards import Color, Type
from input_validators.GameDecisionValidator import GameDecisionValidator

CHOOSABLE_GAME_RANK_MAPPING = {
    Sauspiel: Sauspiel.rank,
    Wenz: Wenz.rank,
    Solo: Solo.rank,
}


@pytest.fixture
def validator() -> GameDecisionValidator:
    return GameDecisionValidator(
        choosable_game_rank_mapping=CHOOSABLE_GAME_RANK_MAPPING
    )


def test_is_player_owns_sau_true(validator, eichel_sau, eichel_ten, gruen_koenig):
    player_cards = [eichel_sau, eichel_ten, gruen_koenig]
    assert validator.is_player_owns_sau(
        player_cards=player_cards, sau_color=Color.EICHEL
    )


def test_is_player_owns_sau_false(validator, eichel_ten, gruen_koenig, schellen_seven):
    player_cards = [eichel_ten, gruen_koenig, schellen_seven]
    assert not validator.is_player_owns_sau(
        player_cards=player_cards, sau_color=Color.EICHEL
    )


def test_is_player_owns_sau_wrong_color(validator, eichel_sau, gruen_koenig):
    player_cards = [eichel_sau, gruen_koenig]
    assert not validator.is_player_owns_sau(
        player_cards=player_cards, sau_color=Color.GRUEN
    )


def test_count_color_cards(
    validator, eichel_ober, eichel_unter, eichel_ten, eichel_seven
):
    player_cards = [eichel_ober, eichel_unter, eichel_ten, eichel_seven]
    # Ober and Unter are trump types -> they don't raise the count
    count = validator.count_color_cards(
        player_cards=player_cards,
        color=Color.EICHEL,
        trump_types=[Type.OBER, Type.UNTER],
    )
    assert count == 2  # only eichel_ten and eichel_seven


def test_count_color_cards_other_color_not_counted(
    validator, eichel_ten, gruen_ten, schellen_ten
):
    player_cards = [eichel_ten, gruen_ten, schellen_ten]
    count = validator.count_color_cards(
        player_cards=player_cards,
        color=Color.EICHEL,
        trump_types=[Type.OBER, Type.UNTER],
    )
    assert count == 1


def test_count_color_cards_empty_hand(validator):
    assert (
        validator.count_color_cards(
            player_cards=[], color=Color.EICHEL, trump_types=[Type.OBER, Type.UNTER]
        )
        == 0
    )


def test_sauspiel_playable_has_callable_color(
    validator, eichel_ten, gruen_koenig, herz_ober
):
    # No Eichel Sau → eichel choosable
    player_cards = [eichel_ten, gruen_koenig, herz_ober]
    assert validator.is_sauspiel_playable(player_cards=player_cards)


def test_sauspiel_not_playable_only_trumps(
    validator,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
):
    # Only Obers and Unters → no choosable color
    player_cards = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        eichel_unter,
        gruen_unter,
        herz_unter,
        schellen_unter,
    ]
    assert not validator.is_sauspiel_playable(player_cards=player_cards)


def test_sauspiel_not_playable_owns_all_saus(
    validator,
    eichel_sau,
    gruen_sau,
    schellen_sau,
    eichel_ten,
    gruen_ten,
    schellen_ten,
):
    # Player has all Saus → no Sauspiel possible
    player_cards = [
        eichel_sau,
        gruen_sau,
        schellen_sau,
        eichel_ten,
        gruen_ten,
        schellen_ten,
    ]
    assert not validator.is_sauspiel_playable(player_cards=player_cards)


def test_sauspiel_not_playable_has_sau_for_every_available_color(
    validator,
    eichel_sau,
    gruen_sau,
    eichel_ten,
    gruen_koenig,
):
    # Player has Eichel Sau and Grün-Sau, but also cards of color eichel and gruen
    # → he has the Sau for every color he owns → Sauspiel not playable
    player_cards = [eichel_sau, gruen_sau, eichel_ten, gruen_koenig]
    assert not validator.is_sauspiel_playable(player_cards=player_cards)


def test_available_game_modes_no_prev_game_sauspiel_possible(
    validator, eichel_ten, gruen_koenig, herz_ober
):
    player_cards = [eichel_ten, gruen_koenig, herz_ober]
    available_gamemodes = validator.get_available_game_modes(
        playable_games=[game for game in CHOOSABLE_GAME_RANK_MAPPING.keys()],
        prev_game=None,
        player_cards=player_cards,
    )
    assert Sauspiel in available_gamemodes
    assert Wenz in available_gamemodes
    assert Solo in available_gamemodes


def test_available_game_modes_no_prev_game_sauspiel_not_possible(
    validator,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
):
    player_cards = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        eichel_unter,
        gruen_unter,
        herz_unter,
        schellen_unter,
    ]
    available_gamemodes = validator.get_available_game_modes(
        playable_games=list(CHOOSABLE_GAME_RANK_MAPPING.keys()),
        prev_game=None,
        player_cards=player_cards,
    )
    assert Sauspiel not in available_gamemodes
    assert Wenz in available_gamemodes
    assert Solo in available_gamemodes


def test_available_game_modes_prev_sauspiel_only_higher_ranks(validator, eichel_ten):
    # Previously chosen game mode is Sauspiel → only Wenz and Solo available
    available_gamemodes = validator.get_available_game_modes(
        playable_games=list(CHOOSABLE_GAME_RANK_MAPPING.keys()),
        prev_game=Sauspiel,
        player_cards=[eichel_ten],
    )
    assert Sauspiel not in available_gamemodes
    assert Wenz in available_gamemodes
    assert Solo in available_gamemodes


def test_available_game_modes_prev_wenz_only_solo(validator, eichel_ten):
    available_gamemodes = validator.get_available_game_modes(
        playable_games=list(CHOOSABLE_GAME_RANK_MAPPING.keys()),
        prev_game=Wenz,
        player_cards=[eichel_ten],
    )
    assert Sauspiel not in available_gamemodes
    assert Wenz not in available_gamemodes
    assert Solo in available_gamemodes


def test_available_game_modes_prev_solo_nothing_left(validator, eichel_ten):
    available_gamemodes = validator.get_available_game_modes(
        playable_games=list(CHOOSABLE_GAME_RANK_MAPPING.keys()),
        prev_game=Solo,
        player_cards=[eichel_ten],
    )
    assert available_gamemodes == []


def test_valid_game_mode_decisions_keys_are_consecutive_strings(
    validator, eichel_ten, gruen_koenig
):
    decisions = validator.get_valid_game_mode_decisions(
        prev_game_mode=None,
        player_cards=[eichel_ten, gruen_koenig],
    )
    assert [key for key in decisions.keys()] == [
        str(i) for i in range(1, len(decisions) + 1)
    ]


def test_valid_game_mode_decisions_prev_sauspiel(validator, eichel_ten):
    decisions = validator.get_valid_game_mode_decisions(
        prev_game_mode=Sauspiel,
        player_cards=[eichel_ten],
    )
    assert Sauspiel not in decisions.values()
    assert Wenz in decisions.values()
    assert Solo in decisions.values()


def test_valid_call_sau_colors_excludes_owned_sau(
    validator, eichel_sau, eichel_ten, gruen_ten
):
    # Player owns Eichel Sau → Eichel is not choosable
    player_cards = [eichel_sau, eichel_ten, gruen_ten]
    colors = validator.get_valid_call_sau_colors(player_cards=player_cards)
    assert Color.EICHEL not in colors
    assert Color.GRUEN in colors


def test_valid_call_sau_colors_excludes_color_without_cards(
    validator, eichel_ten, gruen_koenig, schellen_ober
):
    # Player has no cards of color Schellen (except schellen_ober, which is trump) → Schellen not choosable
    player_cards = [eichel_ten, gruen_koenig, schellen_ober]
    colors = validator.get_valid_call_sau_colors(player_cards=player_cards)
    assert Color.SCHELLEN not in colors


def test_valid_call_sau_colors_only_non_trump_cards_count(
    validator, eichel_ober, eichel_ten
):
    # eichel_ober is of trump type → doesn't count as color card
    # eichel_ten is not a sau → Eichel is choosable
    player_cards = [eichel_ober, eichel_ten]
    colors = validator.get_valid_call_sau_colors(player_cards=player_cards)
    assert Color.EICHEL in colors


def test_valid_call_sau_color_inputs_keys_are_consecutive_strings(
    validator, eichel_ten, gruen_ten
):
    inputs = validator.get_valid_call_sau_color_inputs(
        player_cards=[eichel_ten, gruen_ten]
    )
    assert list(inputs.keys()) == [str(i) for i in range(1, len(inputs) + 1)]
    assert all(isinstance(v, Color) for v in inputs.values())


def test_valid_solo_color_inputs_contains_all_colors(validator):
    inputs = validator.get_valid_solo_color_inputs()
    assert sorted(
        [color for color in inputs.values()], key=lambda x: x.value
    ) == sorted(
        [
            Color.EICHEL,
            Color.GRUEN,
            Color.HERZ,
            Color.SCHELLEN,
        ],
        key=lambda x: x.value,
    )


def test_valid_solo_color_inputs_keys_are_consecutive_strings(validator):
    inputs = validator.get_valid_solo_color_inputs()
    assert list(inputs.keys()) == [str(i) for i in range(1, len(inputs) + 1)]
