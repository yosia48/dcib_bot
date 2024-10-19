import configparser

from telegram import LinkPreviewOptions, Update
from telegram.constants import ParseMode
from telegram.ext import (
	Application,
	ApplicationBuilder,
	CommandHandler,
	Defaults,
	filters
)

from components import (
	handlers as ha
)


def main() -> None:
	config = configparser.ConfigParser()
	config.read("bot.ini")

	defaults = Defaults(parse_mode=ParseMode.HTML,
	                    link_preview_options=LinkPreviewOptions(is_disabled=True),
	                    do_quote=False)
	app: Application = (
		ApplicationBuilder()
		.token(config["KEYS"]["bot_api"])
		.defaults(defaults)
		.build()
	)

	app.add_handler(CommandHandler("eps", ha.eps, filters=filters.UpdateType.MESSAGE))

	app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
	main()
