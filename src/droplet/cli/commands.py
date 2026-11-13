from droplet import Droplet
from argparse import Namespace
from typing import Union
from .parsers import type_parser
from .assets import GREEN, RED, BOLD, RESET



def _output(text: str) -> None:
    print(f'→ {text}')


def _success(text: str) -> None:
    _output(f'{GREEN}{text}{RESET}')


def error(text: str) -> None:
    _output(f'{RED}{text}{RESET}')


def _bold(text: str) -> None:
    _output(f'{BOLD}{text}{RESET}')


def size(db: Droplet, args: Namespace) -> None:
    unit = args.unit
    size = db.get_size()

    kb = size / 1024
    mb = size / (1024 ** 2)
    gb = size / (1024 ** 3)

    if unit == 'bytes':
        print(f'{size} bytes')
    if unit == 'kb':
        print(f'{kb:.2f} kb')
    if unit == 'mb':
        print(f'{mb:.2f} mb')
    if unit == 'gb':
        print(f'{gb:.2f} gb')



def count(db: Droplet) -> None:
    _output(db.count())


def view(db: Droplet) -> None:
    pairs = db.view()
    if _is_db_empty(pairs): return

    # Find the maximum length of the keys for perfect alignment
    max_key_len = max(len(str(k)) for k in pairs.keys())

    print(f"{BOLD}{'DATABASE RECORDS':^45}{RESET}")
    print("_" * 45)
    
    for key, value in pairs.items():
        print(f" {BOLD}{str(key):<{max_key_len}}{RESET} : {value}")
        
    print("_" * 45)


def values(db: Droplet) -> None:
    db_values = db.values()
    if _is_db_empty(db_values): return
    
    _output(db_values)


def keys(db: Droplet) -> None:
    db_keys = db.keys()
    if _is_db_empty(db_keys): return

    _output(db_keys)


def increment(db: Droplet, args: Namespace) -> None:
    new_value: int = db.increment(
        args.key,
        args.amount,
        args.namespace
    )
    print(new_value)
    _output(new_value)


def decrement(db: Droplet, args: Namespace) -> None:
    new_value: int = db.decrement(
        args.key,
        args.amount,
        args.namespace
    )
    _output(new_value)


def delete_item(db: Droplet, args: Namespace) -> None:
    db.delete(
        args.key, 
        args.namespace
    )
    _success('Key deleted successfully.')
    

def set_item(db: Droplet, args: Namespace) -> None:
    db.set(
        key=args.key,
        value=type_parser(args.value, args.type, args.iterable_type),
        ttl=args.ttl,
        namespace=args.namespace
    )
    _success('Value stored successfully.')


def get_item(db: Droplet, args: Namespace) -> None:
    key = args.key
    value = db.get(
        key=key,
        namespace=args.namespace,
    )

    if args.inspect:
        _output(f'{value} {BOLD}{type(value)}{RESET}')
    else:
        _output(value)


def get_namespace(db: Droplet, args: Namespace) -> None:
    namespace: str = args.name
    values = db.get_namespace(namespace=namespace)

    if not values:
        _output(f'{namespace} is empty or does not exist')
        return

    max_key_len = max(len(str(k)) for k in values.keys())

    print(f"{BOLD}{namespace.upper() + ' NAMESPACE':^45}{RESET}")
    print("_" * 45)
    
    for key, value in values.items():
        print(f" {BOLD}{str(key):<{max_key_len}}{RESET} : {value}")
        
    print("_" * 45)
    

def ttl(db: Droplet, args: Namespace) -> None:
    unit = args.unit

    time = db.ttl(
        key=args.key,
        namespace=args.namespace
    )

    minutes = time / 60
    hours = time / (60 * 60)

    if unit == 'min':
        _output(f'Minutes remaining: {minutes}')
    elif unit == 'hrs':
        _output(f'Hours remaining: {hours}')
    else:
        _output(f'Seconds remaining: {time}')


def exists(db: Droplet, args: Namespace) -> None:
    item_exists = db.exists(
        key=args.key, 
        namespace=args.namespace
    )
    _output(str(item_exists).upper())


def clear_db(db: Droplet, args: Namespace) -> None:
    db.clear()
    _success(f'{db.path} has been cleared')


def compact_db(db: Droplet, args: Namespace) -> None:
    db.compact()
    _success(f'Compaction successful')


def _is_db_empty(iterable: Union[dict, list]) -> None:
    if not iterable:
        _bold('Database is empty.')
        return True
    return False
