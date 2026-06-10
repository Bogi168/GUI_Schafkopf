import argparse

from system.Renderer import ConsoleRenderer
from schafkopf_classes.Schafkopf import Schafkopf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play Schafkopf")
    parser.add_argument(
        "--console",
        action="store_true",
        help="Run in the terminal instead of the pygame GUI.",
    )
    args = parser.parse_args()

    if args.console:
        renderer = ConsoleRenderer()
        game = Schafkopf(renderer=renderer, base_price=10, call_price=20, alone_price=30)
        game.main()
    else:
        from system.gui import GUIRenderer

        renderer = GUIRenderer()
        game = Schafkopf(renderer=renderer, base_price=10, call_price=20, alone_price=30)
        renderer.run(game.main)
