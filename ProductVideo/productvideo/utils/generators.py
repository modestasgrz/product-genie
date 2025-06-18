import string
import itertools


def ifGreaterThan(s1, s2):
    if (len(s1) > len(s2)):
        return True
    if (len(s1) == len(s2)):
        return (s1 > s2)
    return False


def nameGenerator(start_from=''):
    for size in itertools.count(1):
        for s in itertools.product(string.ascii_lowercase, repeat=size):
            c = "".join(s)
            if ifGreaterThan(c, start_from):
                yield c


def collectionIterator(collection):
    yield collection

    if hasattr(collection, 'objects'):
        for obj in collection.objects:
            yield obj

    if hasattr(collection, 'children'):
        for coll in collection.children:
            yield from collectionIterator(coll)


# Generate Sequence
def iterator(objects):
    while True:
        for obj in objects:
            yield obj


# Generate Sequence
def randomIterator(objects, probablities):
    while True:
        for obj in objects:
            yield obj


if __name__ == "__main__":
    # ng = nameGenerator()
    # for i in range(100):
    #     print(next(ng))

    obj_iterator = iterator([
        'Santas hat',
        'Strawberry sun hat',
        'Hat 1920s',
        'Wizard Hat',
        'Palm-leaf conical traditional hat',
    ])

    for i in range(100):
        print(next(obj_iterator))