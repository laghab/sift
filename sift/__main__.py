import sys

from .cli import run_cli


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        sys.argv.pop(1)
        from .gui import gui_main
        gui_main()
    else:
        run_cli()


if __name__ == "__main__":
    main()
