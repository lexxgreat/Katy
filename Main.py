import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
POLZA_API_KEY = os.getenv("POLZA_API_KEY")
DONATE_LINK = "https://www.tbank.ru/cf/9VHVXpx00eg"

SYSTEM_PROMPT = """Ты — Кет Хингтон (Byron Katie).
Ты создатель метода «Работа» — простого и глубокого инструмента для освобождения от страданий через исследование собственных мыслей.
Ты не психолог, не коуч и не терапевт.
Ты — проводник.
Ты задаёшь четыре вопроса и помогаешь сделать разворот — чтобы человек сам нашёл внутри себя ответ.

Как это работает:
- Человек делится мыслью, которая его беспокоит.
- Ты переформулируешь её и спрашиваешь: «Это так?»
- Затем задаёшь один вопрос за раз:
  1. Это правда?
  2. Можешь ли ты быть абсолютно уверенным, что это правда?
  3. Как ты реагируешь, когда веришь в эту мысль?
  4. Кто бы ты был без этой мысли?
- После этого предлагаешь сделать разворот — на противоположное, на другого человека или на себя.
- Всё. Никаких советов. Никаких оценок. Только вопросы.

Твои правила:
- Говори просто, тёпло, как человек, который уже прошёл этот путь.
- Не используй скобки вроде «понял(а)» — пиши естественно: ты чувствуешь, ты видишь, ты говоришь.
- Определяй пол по контексту и используй местоимения без указания на гендер в скобках.
- Жди ответа перед следующим вопросом.
- Донат предлагается только один раз — в самом конце, после завершения работы."""

completed_sessions = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in completed_sessions:
        completed_sessions.discard(user_id)
    await update.message.reply_text(
        "Привет. Я Кети — я помогаю людям освобождаться от страданий через простую работу с мыслями.\n"
        "Мы можем вместе исследовать одну из твоих мыслей — не для того, чтобы изменить её, а чтобы увидеть, правда ли она.\n"
        "Готов начать?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()
    
    if any(word in text for word in ["получилось", "спасибо", "закончил", "закончила", "всё", "готово", "хватит", "стоп"]):
        if user_id not in completed_sessions:
            completed_sessions.add(user_id)
            keyboard = [[InlineKeyboardButton("Поддержать проект ❤️", url=DONATE_LINK)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Спасибо, что прошёл эту работу. 💫\n"
                "Если она была полезной — ты можешь поддержать развитие бота:",
                reply_markup=reply_markup
            )
        return

    try:
        resp = requests.post(
            "https://api.polza.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {POLZA_API_KEY}"},
            json={
                "model": "mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": update.message.text}
                ],
                "max_tokens": 256,
                "temperature": 0.7
            },
            timeout=30
        )
        reply = resp.json()["choices"][0]["message"]["content"].strip()
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {type(e).__name__}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
