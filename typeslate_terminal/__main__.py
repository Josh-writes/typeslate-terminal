"""Entry point for `python -m typeslate_terminal` and the `typeslate` command."""

from typeslate_terminal.app import TypeSlateApp


def main():
    app = TypeSlateApp()
    app.run()


if __name__ == "__main__":
    main()
