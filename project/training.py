"""Fake models."""

import pickle
import sys

from project.models import FakeClassifier

if __name__ == '__main__':
    with open(sys.argv[1], 'wb') as f:
        pickle.dump(FakeClassifier(), f)
    print(f'Dumped fake classifier to {sys.argv[1]!r}')
