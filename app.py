from flask import Flask, request, jsonify
from string import ascii_uppercase
from random import choice


# Mock Data Store
LICENSE_KEY_STORE = {
    "PRIVATE_LICENSE_KEY": {
        "renewal": True,
        "discord": "DISCORD_ID",
        "expire": "2022-01-01 00:00 UTC",
        "plan": "Lifetime"
    }
}

PLANS = ["Lifetime", "$60/6 months"]

# API Key
API_KEY = "jJz23yFoMdm87XPCXXjv9E4H22vvYJ"


app = Flask(__name__)


@app.route('/verify', methods=['POST'])
def verify_endpoint():
    """
    Verify a given license, whether it's valid or not
    Input in JSON format :
    {
        "license": <LICENSE_STR>,
        "discord": <DISCORD_ID_STR>
    }
    :return: 200 OK
    {
        "require_renewal": <RENEWAL_BOOL>,
        "expire_datetime": <EXPIRE_yyyy-mm-dd hh:mm UTC>
    }
    :return 401 Unauthorized
    :return 404 Not Found
    """
    if request.headers.get("Authorization") != API_KEY:
        return jsonify({"error": "Invalid API Key"}), 401

    data = request.json
    license = data["license"]
    discord = data["discord"]

    # Check if the license exists or not, return 404 if not found
    if license not in LICENSE_KEY_STORE:
        return jsonify({
            "error": "Key not found"
        }), 404

    # License exists
    # Check if the specified discord is the same, return 404 if not
    if LICENSE_KEY_STORE[license]["discord"] != discord:
        return jsonify({
            "error": "Discord not found"
        }), 404

    # License exists & valid discord
    # Return json with 200 status code
    license_data = LICENSE_KEY_STORE[license]
    return jsonify({
        "require_renewal": license_data["renewal"],
        "expire_datetime": license_data["expire"],
        "plan": license_data["plan"]
    }), 200


@app.route("/transfer", methods=["POST"])
def transfer_endpoint():
    """
    Transfer ownership of a given license by
    deactivating the old one and create a new one
    with the same expiry

    Input in JSON format :
    {
        "from_license": <FROM_LICENSE_STR>,
        "from_discord": <FROM_DISCORD_ID_STR>,
        "to_discord": <TO_DISCORD_ID_STR>
    }

    :return: 200 OK
    {
        "license": <NEW_LICENSE_STR>,
        "discord": <TO_DISCORD_ID_STR>
    }

    :return 404 Not Found
    """
    if request.headers.get("Authorization") != API_KEY:
        return jsonify({"error": "Invalid API Key"}), 401

    data = request.json
    license = data["from_license"]
    discord = data["from_discord"]
    to_discord = data["to_discord"]

    # Check if the license exists or not, return 404 if not found
    if license not in LICENSE_KEY_STORE:
        return jsonify({
            "error": "Key not found"
        }), 404

    # License exists
    # Check if the specified discord is the same, return 404 if not
    if LICENSE_KEY_STORE[license]["discord"] != discord:
        return jsonify({
            "error": "Discord not found"
        }), 404

    # Generate new license made up from random chars
    new_license = [choice(ascii_uppercase) for _ in range(10)]
    new_license = ''.join(new_license)

    # Copy the old license to new license
    LICENSE_KEY_STORE[new_license] = LICENSE_KEY_STORE[license]

    # Change to new discord
    LICENSE_KEY_STORE[new_license]["discord"] = to_discord

    # Delete the old license
    del LICENSE_KEY_STORE[license]

    return jsonify({
        "discord": LICENSE_KEY_STORE[new_license]["discord"],
        "license": new_license,
        "plan": LICENSE_KEY_STORE[new_license]["plan"]
    }), 200


@app.route("/plan", methods=["GET"])
def plan_endpoint():
    """
    Return list of available license plan

    Input: None

    :return: 200 OK
    {
        "plans" : ["plan1", "plan2", ...]
    }
    """
    return jsonify({"plans": PLANS})


if __name__ == "__main__":
    app.run()
