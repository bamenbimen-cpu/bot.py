
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# =========================================
# BOT TOKEN: Terminal-এ পেস্ট করবে
# =========================================

def get_bot_token():
    print("\n=== TELEGRAM AUTO APPROVE BOT ===")
    token = input("Paste your Bot Token here: ").strip()
    token = token.strip('"').strip("'").strip()

    if not token:
        raise SystemExit("ERROR: Bot Token is empty.")

    return token


# =========================================
# FOUR BUTTONS
# =========================================

URL = "https://auctionr.org/4/3804923517ebeb72c4cac0d5cc0420a7"

def make_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Watch Now", url=URL)],
        [InlineKeyboardButton("🎬 New Video", url=URL)],
        [InlineKeyboardButton("🍿 Latest Movies", url=URL)],
        [InlineKeyboardButton("🔥 Trending Viral Video", url=URL)],
    ])


WELCOME_TEXT = (
    "👋 Welcome! Your join request has been approved.\n\n"
    "Watch your favorite videos and explore "
    "the latest updates below. 🎬"
)


# =========================================
# SEND PRIVATE WELCOME
# =========================================

async def send_welcome(bot, user_id):
    await bot.send_message(
        chat_id=user_id,
        text=WELCOME_TEXT,
        reply_markup=make_keyboard(),
    )


# =========================================
# WHEN USER STARTS THE BOT
# =========================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if user is None or update.effective_message is None:
        return

    try:
        await send_welcome(context.bot, user.id)
        logger.info("Welcome sent after /start: %s", user.id)

    except TelegramError:
        logger.exception("Could not send /start welcome to %s", user.id)


# =========================================
# AUTO APPROVE JOIN REQUEST
# =========================================

async def handle_join_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    request = update.chat_join_request

    if request is None:
        return

    user = request.from_user

    try:
        await context.bot.approve_chat_join_request(
            chat_id=request.chat.id,
            user_id=user.id,
        )
        logger.info("Join request approved: %s", user.id)

    except TelegramError:
        logger.exception("Join request approval failed for %s", user.id)
        return

    # Approval and private messaging are separate actions.
    try:
        await send_welcome(context.bot, user.id)
        logger.info("Private welcome sent: %s", user.id)

    except TelegramError:
        logger.warning(
            "Private message failed for user %s. "
            "Ask the user to open the bot and press Start.",
            user.id,
        )


# =========================================
# RUN BOT
# =========================================

def main():
    token = get_bot_token()

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(
        ChatJoinRequestHandler(handle_join_request)
    )

    print("\nBot is starting...")
    print("Auto Join Approval: ON")
    print("Private Welcome: ON")
    print("Inline Buttons: 4")
    print("Press Ctrl+C to stop.\n")

    app.run_polling(
        allowed_updates=["message", "chat_join_request"]
    )


if __name__ == "__main__":
    main()
