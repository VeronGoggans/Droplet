from droplet import Droplet
from argparse import Namespace
from .parsers import type_parser



def size(db: Droplet, args: Namespace) -> None:
    unit = args.unit
    size = db.get_size()

    kb = size / 1024
    mb = size / (1024 ** 2)
    gb = size / (1024 ** 3)

    if unit == 'bytes':
        print(f'SIZE Bytes: {size}')
    if unit == 'kb':
        print(f'SIZE KiB: {kb:.2f}')
    if unit == 'mb':
        print(f'SIZE MiB: {mb:.2f}')
    if unit == 'gb':
        print(f'SIZE GiB: {gb:.2f}')



def count(db: Droplet) -> None:
    print(f'Number of keys: {db.count()}')


def view(db: Droplet) -> None:
    print(db.view())


def values(db: Droplet) -> None:
    print(db.values())


def keys(db: Droplet) -> None:
    print(db.keys())


def increment(db: Droplet, args: Namespace) -> None:
    new_value: int = db.increment(
        args.key,
        args.amount,
        args.namespace
    )
    print(f'INCREMENT {args.key}: {new_value}')


def decrement(db: Droplet, args: Namespace) -> None:
    new_value: int = db.decrement(
        args.key,
        args.amount,
        args.namespace
    )
    print(f'DECREMENT {args.key}: {new_value}')


def delete_item(db: Droplet, args: Namespace) -> None:
    deleted_value = db.delete(
        args.key, 
        args.namespace
    )
    print(f'DELETE {args.key}: {deleted_value}')


def set_item(db: Droplet, args: Namespace) -> None:
    key = args.key
    namespace = args.namespace

    value = db.set(
        key=key,
        value=type_parser(args.value, args.type, args.iterable_type),
        ttl=args.ttl,
        namespace=namespace
    )

    if namespace:
        print(f'SET {namespace}:{key}: {value}')
    else:
        print(f'SET {key}: {value}')


def get_item(db: Droplet, args: Namespace) -> None:
    key = args.key
    value = db.get(
        key=key,
        namespace=args.namespace,
    )

    if args.inspect:
        print(f'GET {key}: {value} {type(value)}')
    else:
        print(f'GET {key}: {value}')


def ttl(db: Droplet, args: Namespace) -> None:
    unit = args.unit

    time = db.ttl(
        key=args.key,
        namespace=args.namespace
    )

    minutes = time / 60
    hours = time / (60 * 60)

    if unit == 'min':
        print(f'TTL minutes remaining: {minutes}')
    elif unit == 'hrs':
        print(f'TTL hours remaining: {hours}')
    else:
        print(f'TTL seconds remaining: {time}')


def exists(db: Droplet, args: Namespace) -> None:
    item_exists = db.exists(
        key=args.key, 
        namespace=args.namespace
    )
    print(f'EXISTS {str(item_exists).lower()}')
