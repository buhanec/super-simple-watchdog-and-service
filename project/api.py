from flask import Flask, jsonify, request
from http import HTTPStatus
from urllib.parse import unquote_plus

app = Flask(__name__)

DATABASE = {}


def make_error(reason: str, code: int):
    """
    Make an error response

    :param reason: Error text
    :param code: Error code
    :return: Error "response"
    """
    return {'reason': reason, 'code': code}, code


@app.route('/<path:log_path>', methods=['PUT'])
def create_record(log_path: str):
    """
    Create a record of an analysed log

    :param log_path: Log path
    :return: Response
    """
    if 'class_name' not in request.values:
        return make_error('Missing "class_name" parameter', HTTPStatus.BAD_REQUEST)
    if log_path in DATABASE:
        return make_error('Record already exists', HTTPStatus.CONFLICT)
    DATABASE[log_path] = unquote_plus(request.values['class_name'])
    return jsonify({'log_path': log_path, 'class_name': DATABASE[log_path]})


@app.route('/<path:log_path>', methods=['DELETE'])
def delete_record(log_path: str):
    """
    Delete a record of an analysed log

    :param log_path: Log path
    :return: Response
    """
    if log_path not in DATABASE:
        return make_error('Record does not exist', HTTPStatus.NOT_FOUND)
    return jsonify({'log_path': log_path, 'class_name': DATABASE.pop(log_path)})


@app.route('/<path:log_path>', methods=['GET'])
def get_record(log_path: str):
    """
    Get a single record of an analysed log.

    :param log_path: Log path
    :return: Response
    """
    if log_path not in DATABASE:
        return make_error('Record does not exist', HTTPStatus.NOT_FOUND)
    return jsonify({'log_path': log_path, 'class_name': DATABASE[log_path]})


@app.route('/', methods=['GET'])
def get_all():
    """
    Get all the analysed logs.

    :return: Response
    """
    return jsonify(DATABASE)


if __name__ == '__main__':
    app.run(debug=True)
