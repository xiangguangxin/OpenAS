import json
import sys


def main():
    """Deliberately broken CLI example: input is a JSON list of numbers."""
    numbers = json.load(sys.stdin)
    print(json.dumps({'count': len(numbers), 'total': 0}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
