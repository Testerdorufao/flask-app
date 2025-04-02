import tkinter as tk

from tkinter import messagebox

import subprocess

import os



# Obtém o diretório absoluto do script e define o caminho absoluto do config.py

script_dir = os.path.dirname(os.path.abspath(__file__))

config_file = os.path.join(script_dir, "config.py")

bot_process = None  # Variável para armazenar o processo do bot



def carregar_config():

    if os.path.exists(config_file):

        try:

            with open(config_file, "r") as f:

                linhas = f.readlines()

            dados = {}

            for linha in linhas:

                if " = " in linha:

                    chave, valor = linha.strip().split(" = ")

                    dados[chave] = valor.strip('\"')



            entry_token.insert(0, dados.get("TOKEN", ""))

            entry_chat_id.insert(0, dados.get("CHAT_ID", ""))

            entry_app_id.insert(0, dados.get("APP_ID", ""))

            entry_secret.insert(0, dados.get("SECRET", ""))

        except Exception as e:

            messagebox.showerror("Erro", f"Erro ao carregar configurações: {e}")



def salvar_config():

    token = entry_token.get().strip()

    chat_id = entry_chat_id.get().strip()

    app_id = entry_app_id.get().strip()

    secret = entry_secret.get().strip()



    if not token or not chat_id or not app_id or not secret:

        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")

        return



    try:

        with open(config_file, "w") as f:

            f.write(f'TOKEN = "{token}"\n')

            f.write(f'CHAT_ID = "{chat_id}"\n')

            f.write(f'APP_ID = "{app_id}"\n')

            f.write(f'SECRET = "{secret}"\n')



        messagebox.showinfo("Sucesso", "Configurações salvas!")

    except Exception as e:

        messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")



def iniciar_bot():

    global bot_process

    if bot_process is None:

        try:

            bot_process = subprocess.Popen(['python', os.path.join(script_dir, 'bot.py')],

                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,

                                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)

            messagebox.showinfo("Bot", "Bot iniciado em segundo plano!")

        except Exception as e:

            messagebox.showerror("Erro", f"Erro ao iniciar o bot: {e}")



def desligar_bot():

    global bot_process

    if bot_process:

        bot_process.terminate()

        bot_process = None

        messagebox.showinfo("Bot", "Bot desligado!")



def resetar_config():

    if os.path.exists(config_file):

        os.remove(config_file)

    entry_token.delete(0, tk.END)

    entry_chat_id.delete(0, tk.END)

    entry_app_id.delete(0, tk.END)

    entry_secret.delete(0, tk.END)

    messagebox.showinfo("Reset", "Configurações apagadas!")



# Configuração da interface gráfica

root = tk.Tk()

root.title("Configuração do Bot")



tk.Label(root, text="Token do Telegram").pack(pady=5)

entry_token = tk.Entry(root, width=50)

entry_token.pack(pady=5)



tk.Label(root, text="Chat ID do Telegram").pack(pady=5)

entry_chat_id = tk.Entry(root, width=50)

entry_chat_id.pack(pady=5)



tk.Label(root, text="App ID da Shopee").pack(pady=5)

entry_app_id = tk.Entry(root, width=50)

entry_app_id.pack(pady=5)



tk.Label(root, text="Secret da Shopee").pack(pady=5)

entry_secret = tk.Entry(root, width=50)

entry_secret.pack(pady=5)



tk.Button(root, text="Salvar Configuração", command=salvar_config).pack(pady=5)

tk.Button(root, text="Iniciar Bot", command=iniciar_bot).pack(pady=5)

tk.Button(root, text="Desligar Bot", command=desligar_bot).pack(pady=5)

tk.Button(root, text="Resetar Configurações", command=resetar_config).pack(pady=5)



# Carrega as configurações ao iniciar a interface

carregar_config()



# Fecha o bot ao sair da interface

def fechar_interface():

    desligar_bot()

    root.destroy()



root.protocol("WM_DELETE_WINDOW", fechar_interface)

root.mainloop()
