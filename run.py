import sys
from db.models import main as models_main

from bot.start_bot import start_bot


def main(argv):
    if len(argv) == 1:
        start_bot()
    else:
        pam = argv[-1]
        match pam:
            case 'db':
                models_main()


if __name__ == '__main__':
    main(sys.argv)
