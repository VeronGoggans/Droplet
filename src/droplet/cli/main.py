import argparse

from droplet import Droplet
from .commands import *



def main():
    parser = argparse.ArgumentParser(
        prog='droplet',
        description='Droplet key-value database CLI'
    )

    parser.add_argument(
        '--file',
        default='database.droplet',
        help='Path to the database file'
    )

    commands = parser.add_subparsers(
        dest='command',
        required=True
    )

    # Utilities
    commands.add_parser('keys')
    commands.add_parser('values')
    commands.add_parser('count')
    commands.add_parser('view')
    
    size_parser = commands.add_parser('size')
    size_parser.add_argument(
        '-u',
        '--unit',
        default='bytes',
        choices=['bytes', 'kb', 'mb', 'gb'],
        help="Size unit of the database (default: bytes)"
    )

    # Counters
    increment_parser = commands.add_parser('incr')
    increment_parser.add_argument('key')
    increment_parser.add_argument('--amount', default=1, type=int)
    increment_parser.add_argument('--namespace', default='', type=str)

    decrement_parser = commands.add_parser('decr')
    decrement_parser.add_argument('--amount', default=1, type=int)
    decrement_parser.add_argument('--namespace', default='', type=str)

    # GET
    get_parser = commands.add_parser('get')
    get_parser.add_argument('key')
    get_parser.add_argument('--namespace', default='', type=str)
    get_parser.add_argument('--inspect', action="store_true")

    # SET
    set_parser = commands.add_parser('set')
    set_parser.add_argument('key')
    set_parser.add_argument('value')
    set_parser.add_argument('--ttl', default=0, type=int)
    set_parser.add_argument('--namespace', default='', type=str)
    set_parser.add_argument(
        '-t', 
        '--type', 
        default='str', 
        choices=['str', 'int', 'float', 'bool', 'json', 'list', 'tuple', 'uuid'],
        help="Data type of the value (default: str)"
    )
    set_parser.add_argument(
        '-it',
        '--iterable_type',
        default='str', 
        choices=['str', 'int', 'float', 'bool', 'uuid'],
        help="Data type of the iterable values (default: str)"
    )

    # Exists
    get_parser = commands.add_parser('exists')
    get_parser.add_argument('key')
    get_parser.add_argument('--namespace', default='', type=str)

    # DELETE
    delete_parser = commands.add_parser('del')
    delete_parser.add_argument('key')
    delete_parser.add_argument('--namespace', default='', type=str)

    # TTL
    ttl_parser = commands.add_parser('ttl')
    ttl_parser.add_argument('key')
    ttl_parser.add_argument('--namespace', default='', type=str)
    ttl_parser.add_argument(
        '-u',
        '--unit',
        default='sec',
        choices=['sec', 'min', 'hrs'],
        help="Time unit of ttl time remaining (default: sec)"
    )

    args = parser.parse_args()
 
    with Droplet(args.file, 'persistent') as db:
        try:
            match args.command:
                case 'get':
                    get_item(db, args)
                case 'set':
                    set_item(db, args)
                case 'del':
                    delete_item(db, args)
                case 'exists':
                    exists(db, args)
                case 'keys':
                    keys(db)
                case 'values':
                    values(db)
                case 'count':
                    count(db)
                case 'view':
                    view(db)
                case 'size':
                    size(db, args)
                case 'incr':
                    increment(db, args)
                case 'decr':
                    decrement(db, args)
                case 'ttl':
                    ttl(db, args)

        except KeyError as e:
            print(str(e))

if __name__ == '__main__':
    main()