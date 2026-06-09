from system.Renderer import ConsoleRenderer
from schafkopf_classes.Schafkopf import Schafkopf

if __name__ == "__main__":
    game = Schafkopf(
        renderer=ConsoleRenderer(), base_price=10, call_price=20, alone_price=30
    )
    game.main()
