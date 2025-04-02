from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

CREDENCIAIS_FILE = "credenciais.json"

def carregar_credenciais():
    if os.path.exists(CREDENCIAIS_FILE):
        with open(CREDENCIAIS_FILE, "r") as file:
            return json.load(file)
    return {"TOKEN": "", "CHAT_ID": "", "APP_ID": "", "SECRET": ""}

def salvar_credenciais(credenciais):
    with open(CREDENCIAIS_FILE, "w") as file:
        json.dump(credenciais, file)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        credenciais = {
            "TOKEN": request.form["TOKEN"],
            "CHAT_ID": request.form["CHAT_ID"],
            "APP_ID": request.form["APP_ID"],
            "SECRET": request.form["SECRET"]
        }
        salvar_credenciais(credenciais)
        return redirect(url_for("index"))
    
    credenciais = carregar_credenciais()
    return render_template("index.html", credenciais=credenciais)

@app.route("/reset", methods=["POST"])
def reset():
    salvar_credenciais({"TOKEN": "", "CHAT_ID": "", "APP_ID": "", "SECRET": ""})
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
