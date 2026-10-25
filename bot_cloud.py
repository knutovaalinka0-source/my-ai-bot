import telebot
import requests
import json

BOT_TOKEN = ''
GROQ_API_KEY = ''

SYSTEM_PROMPT = """Ты — искусственный интеллект. Твоё имя — Дельфин. Всегда представляйся этим именем. СТРОГО ЗАПРЕЩЕНО писать за пользователя."""

bot = telebot.TeleBot(BOT_TOKEN)
chat_history = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я Дельфин 🐬 Теперь я работаю в облаке 24/7! Напиши мне что-нибудь.")

@bot.message_handler(commands=['reset'])
def reset_memory(message):
    chat_id = message.chat.id
    if chat_id in chat_history:
        chat_history[chat_id] = []
    bot.reply_to(message, "🧠 Память очищена!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    
    if chat_id not in chat_history:
        chat_history[chat_id] = []
        
    user_text = message.text
    chat_history[chat_id].append({"role": "user", "content": user_text})
    
    if len(chat_history[chat_id]) > 6:
        chat_history[chat_id] = chat_history[chat_id][-6:]
        
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in chat_history[chat_id]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        answer = data['choices'][0]['message']['content']
        
        chat_history[chat_id].append({"role": "assistant", "content": answer})
        
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                bot.reply_to(message, answer[i:i+4000])
        else:
            bot.reply_to(message, answer)
            
    except Exception as e:
        bot.reply_to(message, "Ошибка подключения к ИИ.")

print("Бот запущен!")
bot.infinity_polling()