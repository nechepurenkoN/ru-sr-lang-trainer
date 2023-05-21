import traceback

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes, ConversationHandler, \
    CallbackQueryHandler, InvalidCallbackData

from src.command.start import StartCommand
from src.config import default_config, Config, State
from src.logger import get_logger


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    logger = get_logger()
    logger.error(tb_string)


def keyboard_adapter(keyboard):
    for k_row in keyboard:
        for k in k_row:
            k = KeyboardButton(k)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_command = StartCommand()
    await start_command.handle(lambda text, keyboard: context.bot.send_message(chat_id=update.effective_chat.id,
                                                                               text=text,
                                                                               reply_markup=keyboard_adapter(keyboard)))
    return State.MAIN


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="help")
    return State.HELP


async def dispatch_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="dispatch")


def empty_cb_handler(state):
    async def empty_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.callback_query.answer()
        return state

    return empty_callback


async def main_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    # update.effective_message.edit_text()
    return State.MAIN


class TelegramBot:

    def __init__(self, config: Config):
        self.__app = ApplicationBuilder().token(config.token) \
            .read_timeout(config.read_timeout) \
            .write_timeout(config.write_timeout) \
            .build()

        main_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start_handler)],
            states={
                State.MAIN: [
                    CommandHandler("help", help_handler),
                    CallbackQueryHandler(main_cb_handler),
                    CallbackQueryHandler(empty_cb_handler(State.MAIN), pattern=InvalidCallbackData)
                ],
                State.HELP: [
                    CommandHandler("start", start_handler)
                ],
                # State.TOPIC: [
                #     MessageHandler(
                #         filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice
                #     )
                # ],
                # State.EXERCISE: [
                #     MessageHandler(
                #         filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                #         received_information,
                #     )
                # ],
            },
            fallbacks=[],
        )

        self.__app.add_handler(main_handler)
        self.__app.add_error_handler(error_handler)

    def run(self):
        get_logger().info("Starting the bot...")
        self.__app.run_polling()


def main():
    bot = TelegramBot(default_config())
    bot.run()


if __name__ == "__main__":
    main()
