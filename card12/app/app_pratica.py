# BOT DE WHATSAPP COM LANGFLOW E WAHA (MÉTODO DE POLLING)
#
# DESCRIÇÃO:
# Este script implementa um chatbot para WhatsApp que utiliza o Langflow para
# gerar respostas inteligentes. Ele opera através de "polling", um método
# onde o script ativamente e periodicamente consulta a API do WAHA para
# verificar se novas mensagens foram recebidas.
# ==============================================================================

# --- MÓDULOS NECESSÁRIOS ---
# Importação das bibliotecas que dão poder ao nosso script.
import requests  # Essencial para fazer a comunicação com as APIs (WAHA e Langflow)
import time      # Usado para criar pausas no nosso loop, controlando a frequência das verificações
import sys       # Fornece acesso a funções do sistema, como a de encerrar o programa
from typing import Set, List, Dict, Any # Melhora a legibilidade do código com anotações de tipo

# --- PARÂMETROS DE CONFIGURAÇÃO ---
# Centralizar as configurações aqui facilita futuras manutenções.

# Configurações da API do Langflow
LANGFLOW_API_URL = "http://127.0.0.1:7860/api/v1/run"
FLOW_ID = "bdacc69f-6ff8-4962-b2cf-de2ff7aff8d1"  # IMPORTANTE: Insira o ID do seu fluxo do Langflow aqui.

# Configurações da API do WAHA (WhatsApp)
WAHA_API_URL = "http://localhost:3000/api"
WAHA_SESSION_NAME = "default"

# Configuração de Execução do Bot
# Lista inicial de conversas para o bot monitorar. Novas conversas serão adicionadas automaticamente.
INITIAL_CHATS_TO_MONITOR = [
    "5562994975838@c.us",  # Seu número de WhatsApp(onde o bot está rodando)
    "5562995137239@c.us"   # Número usado para enviar as mensagens de teste
]
POLLING_INTERVAL = 5  # Segundos de espera entre cada ciclo de verificação.
MAX_RETRIES = 3       # Número de tentativas em caso de falha de conexão com a API do WAHA.


# --- DEFINIÇÃO DAS FUNÇÕES PRINCIPAIS ---

def get_langflow_response(user_message: str, session_id: str) -> str:
    """
    Envia a pergunta do usuário para o fluxo do Langflow e obtém a resposta da IA.

    Args:
        user_message (str): O texto da mensagem recebida do WhatsApp.
        session_id (str): O ID do chat do usuário (ex: '55119..._@c.us'). Usado pelo
                          Langflow para manter o histórico e o contexto de cada conversa.

    Returns:
        str: A resposta gerada pela IA ou uma mensagem de erro padrão.
    """
    print(f"[LANGFLOW] Enviando prompt: '{user_message}' para a sessão: {session_id}")
    
    # O payload é o "corpo" da nossa requisição para o Langflow.
    # 'input_value' é a entrada principal e 'session_id' é crucial para a memória do bot.
    payload = {
        "input_value": user_message,
        "session_id": session_id
    }
    
    request_url = f"{LANGFLOW_API_URL}/{FLOW_ID}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(request_url, json=payload, headers=headers, timeout=45)
        response.raise_for_status() # Garante que a requisição foi bem-sucedida (status 2xx)
        
        data = response.json()
        
        # A resposta do Langflow vem em uma estrutura aninhada (nested).
        # Esta navegação segura com .get() evita erros caso algum campo não exista.
        results = data.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {})
        ai_response = results.get("message", "Desculpe, não pude gerar uma resposta.")

        # Tratamento extra caso 'message' seja um dicionário (ex: {"text": "..."})
        if isinstance(ai_response, dict):
            ai_response = ai_response.get('text', "Erro ao formatar a resposta da IA.")
            
        print(f"[LANGFLOW] Resposta recebida: {str(ai_response)[:100]}...")
        return str(ai_response)

    except Exception as e:
        print(f"[ERRO] Falha ao consultar o Langflow: {e}")
        return "Desculpe, meu cérebro de IA está temporariamente offline."

def send_whatsapp_message(chat_id: str, text_message: str):
    """
    Utiliza a API do WAHA para enviar uma mensagem de texto para um chat específico.

    Args:
        chat_id (str): O ID do chat de destino (para quem a mensagem será enviada).
        text_message (str): O conteúdo da mensagem a ser enviada.
    """
    print(f"[WAHA] Enviando resposta para: {chat_id}")
    
    endpoint = f"{WAHA_API_URL}/sendText"
    payload = {
        "session": WAHA_SESSION_NAME,
        "chatId": chat_id,
        "text": str(text_message)
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        print(f"[WAHA] Mensagem para {chat_id} enviada com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem via WAHA para {chat_id}: {e}")

def fetch_new_messages(chat_id: str, processed_ids: Set[str], monitored_chats: Set[str]) -> List[Dict]:
    """
    Busca as mensagens mais recentes de um chat e filtra as que são novas e válidas.
    """
    # Usamos limit=1 para pegar apenas a mensagem mais recente, tornando o bot mais responsivo.
    endpoint = f"{WAHA_API_URL}/messages?chatId={chat_id}&limit=1"
    
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        messages = response.json()
    except requests.exceptions.RequestException as e:
        # Lança a exceção para que o loop de 'retries' possa tratá-la.
        raise e

    valid_new_messages = []
    for msg in messages:
        message_id = msg.get("id")
        is_from_me = msg.get("fromMe", False)
        body = msg.get("body")
        sender = msg.get("from")
        
        # Filtro de validação:
        # 1. A mensagem ainda não foi processada.
        # 2. Não foi enviada pelo próprio bot (essencial para evitar loops).
        # 3. Contém texto.
        if message_id not in processed_ids and not is_from_me and body:
            print(f"-> Mensagem nova e válida de '{sender}': {body}")
            valid_new_messages.append(msg)
            processed_ids.add(message_id) # Adiciona ao controle para não processar de novo
            
            # Lógica de aprendizado de novos chats.
            if sender and sender not in monitored_chats:
                monitored_chats.add(sender)
                print(f"-> Chat '{sender}' agora está sendo monitorado.")
    
    return valid_new_messages

# --- FUNÇÃO PRINCIPAL DE EXECUÇÃO ---

def run_bot():
    """
    O coração do bot. Contém o loop infinito que orquestra todo o processo.
    """
    print("==============================================")
    print("== Bot de WhatsApp com Langflow - Iniciado ==")
    print("==============================================")
    
    processed_message_ids: Set[str] = set()
    chats_to_monitor: Set[str] = set(INITIAL_CHATS_TO_MONITOR)

    while True:
        try:
            print(f"\n--- Ciclo de verificação iniciado às {time.strftime('%H:%M:%S')} ---")
            
            # Itera sobre uma cópia da lista, para permitir a modificação da original
            # se um novo chat for descoberto pela função fetch_new_messages.
            for chat_id in list(chats_to_monitor):
                retries = 0
                while retries < MAX_RETRIES:
                    try:
                        print(f"Verificando chat: {chat_id}")
                        new_messages = fetch_new_messages(chat_id, processed_message_ids, chats_to_monitor)
                        
                        for message in new_messages:
                            sender = message.get("from")
                            text = message.get("body")
                            
                            # Orquestração do fluxo:
                            # 1. Pega a resposta da IA
                            ai_response = get_langflow_response(text, sender)
                            # 2. Envia a resposta de volta para o remetente original
                            send_whatsapp_message(sender, ai_response)
                        
                        break # Se a verificação foi bem-sucedida, sai do loop de tentativas

                    except requests.exceptions.RequestException as conn_error:
                        retries += 1
                        print(f"AVISO: Falha de conexão ao verificar {chat_id}. Tentativa {retries}/{MAX_RETRIES}.")
                        if retries >= MAX_RETRIES:
                            print(f"ERRO: Desistindo de verificar o chat {chat_id} neste ciclo.")
                        else:
                            time.sleep(3) # Espera um pouco antes de tentar de novo

            print(f"--- Ciclo finalizado. Aguardando {POLLING_INTERVAL} segundos. ---")
            time.sleep(POLLING_INTERVAL)

        except KeyboardInterrupt:
            print("\n\nSinal de interrupção (Ctrl+C) recebido. Encerrando o bot.")
            sys.exit(0)
        except Exception as e:
            print(f"ERRO CRÍTICO no loop principal: {e}. O bot vai esperar 20 segundos e tentar continuar.")
            time.sleep(20)

# --- PONTO DE ENTRADA DO SCRIPT ---
# Este bloco 'if' garante que a função run_bot() só será chamada
# quando o arquivo for executado diretamente (ex: python seu_arquivo.py).
if __name__ == "__main__":
    run_bot()