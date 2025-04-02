import os

import json

import time

import hashlib

import requests

import telebot

import threading

import random

from datetime import datetime, timedelta



# Importar configurações do arquivo config.py

from config import TOKEN, CHAT_ID, APP_ID, SECRET



# Configurações do bot Telegram

bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()



# Configuração do histórico de produtos e estado

tempo_limite_dias = 3  # Produtos serão reenviados após 3 dias

ARQUIVO_PRODUTOS = "produtos_enviados.json"

ARQUIVO_ESTADO = "estado_programa.json"



# Dicionário de categorias principais com suas subcategorias

categorias_hierarquicas = {

    "roupas": [100104, 100352, 100358, 100367, 100244, 100242, 100240, 101016, 101761, 101762, 101766, 101773, 101777, 101778],

    "eletrodomestico": [100177, 100178, 100462, 100175, 100463, 100185, 100191, 100193, 100194, 100195, 100196, 100197, 100198, 100199, 100200, 100201, 100202, 100203, 100204, 100205, 100206, 100207, 100468, 100469, 100470, 100471, 100472, 100473, 100474, 100209, 100210, 100211, 100212, 100213, 100214, 100216, 100217, 100218, 100219, 100220, 100045, 100046],

    "eletronicos": [100270, 100475, 100277, 100279, 100282, 100288, 100490, 100291, 100573, 100574, 100578],

    "roupa de cama": [101145, 101146, 101148, 101150, 101152],

    "organizadores": [101254, 101255, 101257, 101258, 101259, 101260, 101261, 101262],

    "louça": [101238, 101239, 101240, 101241, 101242, 101243, 101244, 101245, 101246, 101247, 101248],

    "cozinha": [101216, 101217, 101218, 101219, 101220, 101223, 101224, 101225, 101226, 101227, 101228, 101229, 101230, 101231, 101232, 101233, 101234, 101235, 101237],

    "cuidados da casa": [101200, 101201, 101202, 101203, 101204, 101205, 101206, 101207],

    "guarda roupa": [101170],

    "sofás": [101172],

    "armários": [101173],

    "outros moveis": [101166, 101168, 101169, 101171, 101174, 101175],

    "banheiro": [101132, 101133, 101790, 101791, 101792, 101793, 101137, 101138, 101139, 101140, 101141, 101142, 101143],

    "decoração": [101153, 101154, 101155, 101156, 101157, 101158, 101159, 101160, 101161, 101162, 101163, 101164, 101165]

}



# Lista com todas as categorias disponíveis para seleção

todas_categorias = list(categorias_hierarquicas.keys()) + sum(categorias_hierarquicas.values(), [])



# Ordem das categorias

ordem_categorias = [

    "roupas", "eletrodomestico", "sofás", "roupa de cama",

    "organizadores", "louça", "cozinha", "cuidados da casa", "guarda roupa",

    "armários", "outros moveis", "banheiro", "decoração"

]



# Variáveis de controle

executando = False

ordem_escolhida = 1  # Inicia com sortType 1

MAX_PRODUTOS = 10  # Limite de produtos a serem enviados por ciclo

ciclo_atual = 0   # Variável para controlar o ciclo atual

pagina_atual = 1  # Página atual para a consulta à API

max_paginas = 5   # Número máximo de páginas a serem percorridas



# Histórico de produtos enviados

produtos_enviados = {}



# Lista de frases de oferta

oferta_frases = [

    "🚨 Não perca essa oportunidade única!",

    "💥 Desconto especial para você!",

    "⚡ Promoção relâmpago! Aproveite antes que acabe!",

    "🎉 Essa oferta está imperdível!",

    "💸 Economize agora com essa super oferta!",

    "🏷️ Preço incrível, só por tempo limitado!",

    "🚀 Não deixe essa chance passar!",

    "🏷️ Oferta exclusiva! Não perca!"

]



def escolher_categoria():

    global ordem_categorias

    try:

        categoria_escolhida = ordem_categorias.pop(0)

        ordem_categorias.append(categoria_escolhida)

        if categoria_escolhida in categorias_hierarquicas:

            subcategorias = categorias_hierarquicas[categoria_escolhida]

            # Remove a primeira subcategoria e adiciona ao final da lista

            subcategoria = subcategorias.pop(0)

            subcategorias.append(subcategoria)

            return categoria_escolhida, subcategoria

        return None, categoria_escolhida

    except Exception as e:

        print(f"Erro ao escolher categoria: {e}")

        return None, None



def gerar_assinatura(payload):

    try:

        timestamp = str(int(time.time()))

        string_para_assinar = f'{APP_ID}{timestamp}{payload}{SECRET}'

        return timestamp, hashlib.sha256(string_para_assinar.encode('utf-8')).hexdigest()

    except Exception as e:

        print(f"Erro ao gerar assinatura: {e}")

        return None, None



def buscar_produtos(categoria_id, sort_type=1, page=1):

    try:

        payload = {

            "query": f"""

            {{

                productOfferV2(

                    sortType: {sort_type},

                    page: {page},

                    limit: 10,

                    productCatId: {categoria_id}

                ) {{

                    nodes {{

                        itemId

                        productName

                        offerLink

                        priceMin

                        priceDiscountRate

                        imageUrl

                    }}

                }}

            }}

            """

        }

        timestamp, signature = gerar_assinatura(json.dumps(payload))

        headers = {

            "Authorization": f"SHA256 Credential={APP_ID}, Timestamp={timestamp}, Signature={signature}",

            "Content-Type": "application/json"

        }

        response = requests.post("https://open-api.affiliate.shopee.com.br/graphql", headers=headers, json=payload)

        response.raise_for_status()

        return response.json() if response.status_code == 200 else None

    except requests.exceptions.RequestException as e:

        print(f"Erro ao buscar produtos: {e}")

        return None



def obter_descricao_sort_type(sort_type):

    if sort_type == 1:

        return "relevantes"

    elif sort_type == 2:

        return "mais vendidos"

    else:

        return "desconhecido"



def enviar_produtos():

    global executando, produtos_enviados, ciclo_atual, ordem_escolhida, pagina_atual

    while executando:

        try:

            categoria_nome, categoria_id = escolher_categoria()

            if categoria_nome is None:

                print("Falha ao escolher categoria.")

                continue

            descricao_sort_type = obter_descricao_sort_type(ordem_escolhida)

            bot.send_message(CHAT_ID, f"📢 Exibindo produtos {descricao_sort_type} da categoria {categoria_nome} (ID {categoria_id})")



            dados_produtos = buscar_produtos(categoria_id, ordem_escolhida, pagina_atual)

            if not dados_produtos or 'data' not in dados_produtos:

                print("Falha ao buscar produtos.")

                continue



            produtos = dados_produtos['data']['productOfferV2']['nodes']

            random.shuffle(produtos)

            contador_produtos_enviados = 0

            for produto in produtos:

                if contador_produtos_enviados >= MAX_PRODUTOS or not executando:

                    break

                produto_id = produto['itemId']

                if produto_id in produtos_enviados:

                    continue

                nome_produto = produto['productName']

                preco_min = float(produto['priceMin'])

                imagem_url = produto['imageUrl']

                offer_link = produto['offerLink']

                desconto = produto.get('priceDiscountRate', 0)

                preco_antigo = round(preco_min / (1 - desconto / 100), 2) if desconto > 0 else preco_min



                produtos_enviados[produto_id] = datetime.now().isoformat()

                mensagem = (

                    f"{random.choice(oferta_frases)}\n\n"

                    f"🔥 {nome_produto}\n\n"

                    f"~De: R$ {preco_antigo:.2f}~\n"

                    f"*Por: R$ {preco_min:.2f}*\n\n"

                    f"🔗 {offer_link}\n\n"

                    "🎟️ Resgate os cupons:\n"

                    "https://s.shopee.com.br/7V2YvU1y3Z\n"

                    "⚠️ Promoção sujeita a alteração a qualquer momento."

                )



                bot.send_photo(CHAT_ID, imagem_url, mensagem)

                contador_produtos_enviados += 1

                time.sleep(10)



            # Alterna o sortType a cada ciclo completo

            ciclo_atual += 1

            if ciclo_atual % len(ordem_categorias) == 0:

                ordem_escolhida = 2 if ordem_escolhida == 1 else 1

                pagina_atual += 1

                if pagina_atual > max_paginas:

                    pagina_atual = 1



            bot.send_message(CHAT_ID, "⏳ Aguardando 5 minutos para enviar mais produtos...")

            time.sleep(300)

        except Exception as e:

            print(f"Erro inesperado: {e}")

            time.sleep(300)



def salvar_estado():

    estado = {

        "ordem_categorias": ordem_categorias,

        "categorias_hierarquicas": categorias_hierarquicas,

        "produtos_enviados": produtos_enviados,

        "ordem_escolhida": ordem_escolhida,

        "ciclo_atual": ciclo_atual,

        "pagina_atual": pagina_atual

    }

    with open(ARQUIVO_ESTADO, 'w') as arquivo:

        json.dump(estado, arquivo)



def carregar_estado():

    global ordem_categorias, categorias_hierarquicas, produtos_enviados, ordem_escolhida, ciclo_atual, pagina_atual

    if os.path.exists(ARQUIVO_ESTADO):

        with open(ARQUIVO_ESTADO, 'r') as arquivo:

            estado = json.load(arquivo)

            ordem_categorias = estado.get("ordem_categorias", [

                "roupas", "eletrodomestico", "sofás", "roupa de cama",

                "organizadores", "louça", "cozinha", "cuidados da casa", "guarda roupa",

                "armários", "outros moveis", "banheiro", "decoração"

            ])

            categorias_hierarquicas = estado.get("categorias_hierarquicas", categorias_hierarquicas)

            produtos_enviados = estado.get("produtos_enviados", {})

            ordem_escolhida = estado.get("ordem_escolhida", 1)

            ciclo_atual = estado.get("ciclo_atual", 0)

            pagina_atual = estado.get("pagina_atual", 1)



# Carregar o estado ao iniciar o programa

carregar_estado()



def start(message):

    global executando

    if not executando:

        executando = True

        bot.send_message(CHAT_ID, "📢 Iniciando envio de ofertas...")

        threading.Thread(target=enviar_produtos, daemon=True).start()



def stop(message):

    global executando

    executando = False

    bot.send_message(CHAT_ID, "🛑 Envio de ofertas parado!")

    salvar_estado()  # Salvar o estado antes de parar



# Comandos do bot

@bot.message_handler(commands=['start', 'help'])

def send_welcome(message):

    bot.reply_to(message, "Olá! Eu sou o seu bot de ofertas. Use /iniciar para começar a receber ofertas ou /stop para parar.")



@bot.message_handler(commands=['iniciar'])

def iniciar_bot_command(message):

    start(message)

    bot.reply_to(message, "Bot iniciado! Aguarde enquanto busco ofertas para você.")



@bot.message_handler(commands=['stop'])

def parar_bot_command(message):

    stop(message)

    bot.reply_to(message, "Bot interrompido e estado salvo.")



if __name__ == "__main__":

    print("Bot está pronto para iniciar.")  # Log para depuração

    bot.polling(none_stop=True)
