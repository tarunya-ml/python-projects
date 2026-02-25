from flask import Flask, render_template, request, session, redirect, url_for
import random
import json
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

FILE_PATH = "file_data/file_data.json"


def generate_random_number():
    return random.randint(1, 100)


def update_high_score(score):
    if not os.path.exists("projects"):
        os.makedirs("projects")

    try:
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {
            "highest score": score,
            "total games played": 0,
            "last score": None
        }

    data["total games played"] += 1
    data["last score"] = score

    if score < data["highest score"]:
        data["highest score"] = score

    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

    return data


@app.route("/", methods=["GET", "POST"])
def index():

    if "number" not in session:
        session["number"] = generate_random_number()
        session["attempts"] = 0

    message = ""
    game_over = False
    stats = None

    if request.method == "POST":
        guess = request.form.get("guess")

        if guess:
            try:
                guess = int(guess)
            except ValueError:
                message = "Please enter a valid number!"
                return render_template("index.html", message=message)

            if guess < 1 or guess > 100:
                message = "Number must be between 1 and 100!"
            else:
                session["attempts"] += 1

                if guess == session["number"]:
                    game_over = True
                    stats = update_high_score(session["attempts"])
                    message = f"🎉 Correct! You guessed in {session['attempts']} attempts."
                    session.pop("number")
                    session.pop("attempts")

                elif guess < session["number"]:
                    message = "Higher number please!"
                else:
                    message = "Lower number please!"

    return render_template("index.html", message=message, game_over=game_over, stats=stats)


@app.route("/restart")
def restart():
    session.pop("number", None)
    session.pop("attempts", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)