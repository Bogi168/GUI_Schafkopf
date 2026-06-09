import pytest
from card_classes.Cards import Card, Color, Type
from unittest.mock import MagicMock
from player_classes.Player import Player
from player_classes.Team import Team


@pytest.fixture
def eichel_ober():
    return Card(Color.EICHEL, Type.OBER)


@pytest.fixture
def gruen_ober():
    return Card(Color.GRUEN, Type.OBER)


@pytest.fixture
def herz_ober():
    return Card(Color.HERZ, Type.OBER)


@pytest.fixture
def schellen_ober():
    return Card(Color.SCHELLEN, Type.OBER)


@pytest.fixture
def eichel_unter():
    return Card(Color.EICHEL, Type.UNTER)


@pytest.fixture
def gruen_unter():
    return Card(Color.GRUEN, Type.UNTER)


@pytest.fixture
def herz_unter():
    return Card(Color.HERZ, Type.UNTER)


@pytest.fixture
def schellen_unter():
    return Card(Color.SCHELLEN, Type.UNTER)


@pytest.fixture
def eichel_sau():
    return Card(Color.EICHEL, Type.SAU)


@pytest.fixture
def eichel_ten():
    return Card(Color.EICHEL, Type.TEN)


@pytest.fixture
def eichel_koenig():
    return Card(Color.EICHEL, Type.KOENIG)


@pytest.fixture
def eichel_nine():
    return Card(Color.EICHEL, Type.NINE)


@pytest.fixture
def eichel_eight():
    return Card(Color.EICHEL, Type.EIGHT)


@pytest.fixture
def eichel_seven():
    return Card(Color.EICHEL, Type.SEVEN)


@pytest.fixture
def gruen_sau():
    return Card(Color.GRUEN, Type.SAU)


@pytest.fixture
def gruen_ten():
    return Card(Color.GRUEN, Type.TEN)


@pytest.fixture
def gruen_koenig():
    return Card(Color.GRUEN, Type.KOENIG)


@pytest.fixture
def gruen_nine():
    return Card(Color.GRUEN, Type.NINE)


@pytest.fixture
def gruen_eight():
    return Card(Color.GRUEN, Type.EIGHT)


@pytest.fixture
def gruen_seven():
    return Card(Color.GRUEN, Type.SEVEN)


@pytest.fixture
def herz_sau():
    return Card(Color.HERZ, Type.SAU)


@pytest.fixture
def herz_ten():
    return Card(Color.HERZ, Type.TEN)


@pytest.fixture
def herz_koenig():
    return Card(Color.HERZ, Type.KOENIG)


@pytest.fixture
def herz_nine():
    return Card(Color.HERZ, Type.NINE)


@pytest.fixture
def herz_eight():
    return Card(Color.HERZ, Type.EIGHT)


@pytest.fixture
def herz_seven():
    return Card(Color.HERZ, Type.SEVEN)


@pytest.fixture
def schellen_sau():
    return Card(Color.SCHELLEN, Type.SAU)


@pytest.fixture
def schellen_ten():
    return Card(Color.SCHELLEN, Type.TEN)


@pytest.fixture
def schellen_koenig():
    return Card(Color.SCHELLEN, Type.KOENIG)


@pytest.fixture
def schellen_nine():
    return Card(Color.SCHELLEN, Type.NINE)


@pytest.fixture
def schellen_eight():
    return Card(Color.SCHELLEN, Type.EIGHT)


@pytest.fixture
def schellen_seven():
    return Card(Color.SCHELLEN, Type.SEVEN)


@pytest.fixture
def all_cards(
    eichel_ober,
    eichel_unter,
    eichel_sau,
    eichel_ten,
    eichel_koenig,
    eichel_nine,
    eichel_eight,
    eichel_seven,
    gruen_ober,
    gruen_unter,
    gruen_sau,
    gruen_ten,
    gruen_koenig,
    gruen_nine,
    gruen_eight,
    gruen_seven,
    herz_ober,
    herz_unter,
    herz_sau,
    herz_ten,
    herz_koenig,
    herz_nine,
    herz_eight,
    herz_seven,
    schellen_ober,
    schellen_unter,
    schellen_sau,
    schellen_ten,
    schellen_koenig,
    schellen_nine,
    schellen_eight,
    schellen_seven,
):
    return [
        eichel_ober,
        eichel_unter,
        eichel_sau,
        eichel_ten,
        eichel_koenig,
        eichel_nine,
        eichel_eight,
        eichel_seven,
        gruen_ober,
        gruen_unter,
        gruen_sau,
        gruen_ten,
        gruen_koenig,
        gruen_nine,
        gruen_eight,
        gruen_seven,
        herz_ober,
        herz_unter,
        herz_sau,
        herz_ten,
        herz_koenig,
        herz_nine,
        herz_eight,
        herz_seven,
        schellen_ober,
        schellen_unter,
        schellen_sau,
        schellen_ten,
        schellen_koenig,
        schellen_nine,
        schellen_eight,
        schellen_seven,
    ]


@pytest.fixture
def sauspiel_trumps(
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
    herz_sau,
    herz_ten,
    herz_koenig,
    herz_nine,
    herz_eight,
    herz_seven,
):
    return [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        eichel_unter,
        gruen_unter,
        herz_unter,
        schellen_unter,
        herz_sau,
        herz_ten,
        herz_koenig,
        herz_nine,
        herz_eight,
        herz_seven,
    ]


@pytest.fixture
def wenz_trumps(eichel_unter, gruen_unter, herz_unter, schellen_unter):
    return [eichel_unter, gruen_unter, herz_unter, schellen_unter]


class DummyPlayer(Player):
    def __init__(self, player_name: str):
        super().__init__(
            player_name=player_name,
            renderer=MagicMock(),
            game_decision_validator=MagicMock(),
        )

    def __eq__(self, other):
        return self.player_name == other.player_name

    def __hash__(self):
        return hash(self.player_name)


class DummyTeam(Team):
    def __init__(self, team_name: str):
        self.team_name: str = team_name
        self.players: list[DummyPlayer] = []
        self._points: int = 0

    @property
    def points(self) -> int:
        return self._points

    @points.setter
    def points(self, points: int) -> None:
        self._points = points


@pytest.fixture
def player_1() -> DummyPlayer:
    return DummyPlayer(player_name="Testplayer 1")


@pytest.fixture
def player_2() -> DummyPlayer:
    return DummyPlayer(player_name="Testplayer 2")


@pytest.fixture
def player_3() -> DummyPlayer:
    return DummyPlayer(player_name="Testplayer 3")


@pytest.fixture
def player_4() -> DummyPlayer:
    return DummyPlayer(player_name="Testplayer 4")


@pytest.fixture
def players(player_1, player_2, player_3, player_4) -> list[DummyPlayer]:
    return [player_1, player_2, player_3, player_4]


@pytest.fixture
def team_alone_player_1(player_1) -> DummyTeam:
    team_alone_player = DummyTeam(team_name="TeamAlonePlayer1")
    team_alone_player.players = [player_1]
    return team_alone_player


@pytest.fixture
def team_alone_player_2(player_2) -> DummyTeam:
    team_alone_player = DummyTeam(team_name="TeamAlonePlayer2")
    team_alone_player.players = [player_2]
    return team_alone_player


@pytest.fixture
def team_alone_player_3(player_3) -> DummyTeam:
    team_alone_player = DummyTeam(team_name="TeamAlonePlayer3")
    team_alone_player.players = [player_3]
    return team_alone_player


@pytest.fixture
def team_alone_player_4(player_4) -> DummyTeam:
    team_alone_player = DummyTeam(team_name="TeamAlonePlayer4")
    team_alone_player.players = [player_4]
    return team_alone_player


@pytest.fixture
def team_two_players_1(player_1, player_2) -> DummyTeam:
    team_two_players_1 = DummyTeam(team_name="TeamTwoPlayers1")
    team_two_players_1.players = [player_1, player_2]
    return team_two_players_1


@pytest.fixture
def team_two_players_2(player_3, player_4) -> DummyTeam:
    team_two_players_2 = DummyTeam(team_name="TeamTwoPlayers2")
    team_two_players_2.players = [player_3, player_4]
    return team_two_players_2


@pytest.fixture
def team_three_players_2_3_4(player_2, player_3, player_4) -> DummyTeam:
    team_alone_player = DummyTeam(team_name="TeamThreePlayers")
    team_alone_player.players = [player_2, player_3, player_4]
    return team_alone_player
