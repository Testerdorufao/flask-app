from flask import Flask, jsonify, request
import threading
import time
import json
import os
import random
import telebot
from datetime import datetime
from config import TOKEN, CHAT_ID, APP_ID, SECRET

app = Flask(__name__)

bot = telebot.TeleBot(TOKEN)
executando = False
produtos_enviados = {}

ARQUIVO_ESTADO = "estado_programa.json"
ordem_categorias = ["roupas", "eletrodomestico", "sofás", "roupa de cama"]
ordem_escolhida = 1
pagina_atual = 1
max_paginas = 5
ciclo_atual = 0

def salvar_estado():
    estado = {
        "ordem_categorias": ordem_categorias,
        "produtos_enviados": produtos_enviados,
        "ordem_escolhida": ordem_escolhida,
        "ciclo_atual": ciclo_atual,
        "pagina_atual": pagina_atual
    }
    with open(ARQUIVO_ESTADO, 'w') as arquivo:
        json.dump(estado, arquivo)

def carregar_estado():
    global ordem_categorias, produtos_enviados, ordem_escolhida, ciclo_atual, pagina_atual
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r') as arquivo:
            estado = json.load(arquivo)
            ordem_categorias = estado.get("ordem_categorias", ordem_categorias)
            produtos_enviados = estado.get("produtos_enviados", {})
            ordem_escolhida = estado.get("ordem_escolhida", 1)
            ciclo_atual = estado.get("ciclo_atual", 0)
            pagina_atual = estado.get("pagina_atual", 1)

def enviar_produtos():
    global executando, ciclo_atual, ordem_escolhida, pagina_atual
    while executando:
        try:
            categoria_nome = ordem_categorias[ciclo_atual % len(ordem_categorias)]
            bot.send_message(CHAT_ID, f"📢 Exibindo produtos da categoria {categoria_nome}")
            time.sleep(10)  # Simulando envio de produtos
            ciclo_atual += 1
            if ciclo_atual % len(ordem_categorias) == 0:
                ordem_escolhida = 2 if ordem_escolhida == 1 else 1
                pagina_atual = 1 if pagina_atual >= max_paginas else pagina_atual + 1
            bot.send_message(CHAT_ID, "⏳ Aguardando 5 minutos para enviar mais produtos...")
            time.sleep(300)
        except Exception as e:
            print(f"Erro inesperado: {e}")
            time.sleep(300)

@app.route('/start', methods=['GET'])
def start_bot():
    global executando
    if not executando:
        executando = True
        threading.Thread(target=enviar_produtos, daemon=True).start()
        return jsonify({"message": "Bot iniciado!"})
    return jsonify({"message": "Bot já está rodando!"})

@app.route('/stop', methods=['GET'])
def stop_bot():
    global executando
    executando = False
    salvar_estado()
    return jsonify({"message": "Bot parado e estado salvo!"})

@app.route('/status', methods=['GET'])
def status_bot():
    return jsonify({"executando": executando, "ciclo_atual": ciclo_atual, "pagina_atual": pagina_atual})

if __name__ == '__main__':
    carregar_estado()
    app.run(host='0.0.0.0', port=5000, debug=True)