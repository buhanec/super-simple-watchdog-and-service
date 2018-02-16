import glob
import logging
import pickle
import sys
import time
from typing import Set
from urllib.parse import quote_plus

import requests

API_HOST = '127.0.0.1'
API_PORT = 5000
API_URL = f'http://{API_HOST}:{API_PORT}'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)6s - %(message)s'))
logger.addHandler(handler)


def load_classifier(path: str):
    """
    Load classifier from path.

    :param path: Path to pickled classifier
    :return: Classifier
    """
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        logger.fatal(f'Could not load classifier {path!r}: {e}', exc_info=True)
        raise


def query_done() -> Set[str]:
    """
    Query API to determine which logs were processed.

    :return: Set of processed logs
    """
    response = requests.get(f'{API_URL}/')
    if response.ok:
        done_logs = set(response.json())
        logger.debug(f'Successfully loaded {len(done_logs)} records')
        return done_logs
    else:
        logger.error(f'Error loading records')
        return set()


def send_result(log_path: str, class_name: str) -> bool:
    """
    Try and submit a classification result.

    :param log_path: Log path
    :param class_name: Classified error
    :return: true if successful, false otherwise
    """
    response = requests.put(f'{API_URL}/{quote_plus(log_path)}', data={'class_name': class_name})
    if response.ok:
        logger.info(f'Successfully reported {log_path!r} as {class_name!r}')
        return True
    else:
        logger.error(f'Error reporting {log_path!r}')
        return False


def main(classifier_path: str, watch_pattern: str) -> int:
    """
    Main loop doing all the magic.

    :param classifier_path: Path to classifier
    :param watch_pattern: Path pattern to monitor
    :return: Exit code
    """
    try:
        clf = load_classifier(classifier_path)
    except:
        return 1
    while True:
        files = set(glob.glob(watch_pattern))
        done_files = query_done()
        for file in files - done_files:
            with open(file) as f:
                content = f.read()
                predicted = clf.predict([content])
                send_result(file, predicted)
        time.sleep(1)


if __name__ == '__main__':
    _, classifier_path, watch_pattern = sys.argv
    sys.exit(main(classifier_path, watch_pattern))
