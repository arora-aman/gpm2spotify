from flask import Blueprint, current_app, jsonify, request

auth_api = Blueprint("auth", __name__, url_prefix="")


@auth_api.route("/on_auth", methods=["GET"])
def on_authenticated():
    print(request.args)

    return jsonify(message="OK"), 200

