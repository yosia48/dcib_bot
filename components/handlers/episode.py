import json
import re
import time
from collections.abc import Sequence
from typing import Any, Dict, List, Optional, cast
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from requests import Response
from telegram import (
	InlineKeyboardButton,
	InlineKeyboardMarkup,
	Message,
	Update
)
from telegram.ext import ContextTypes

from ..const import (
	_DCW_URL,
	DEFAULT_HEADERS,
	WIKI_URL,
	WIKI_ANIME_URL
)


async def eps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	# message = cast(Message, update.effective_message)
	# episode = cast(str, message.text).split(" ")[-1]
	# episode_info: Dict[str, Any] = {}
	# r: Response = requests.get(WIKI_ANIME_URL, headers=DEFAULT_HEADERS)
	# soup = BeautifulSoup(r.text, "html.parser")
	
	# seasons: List = soup.find_all("table", class_=["wikitable", "seasontable"])
	# for season in seasons:
	# 	table_rows: List = season.find_all("tr")[1::]
	# 	for table_row in table_rows:
	# 		table_datas: List = table_row.find_all("td")
	# 		jpn_eps = cast(str, table_datas[0].text)
	# 		if jpn_eps != episode:
	# 			continue
			
	# 		episode_info["jpn"] = jpn_eps
	# 		episode_info["int"] = cast(str, table_datas[1].text)
	# 		episode_info["title"] = cast(str, table_datas[2].text)
	# 		episode_info["broadcast"] = cast(str, table_datas[3].text)
	# 		episode_info["plot"] = cast(str, table_datas[5].text)
	# 		episode_info["manga_src"] = cast(str, table_datas[6].text)
			
	# 		print(table_datas[5])
	# 		print(table_datas[2].a["href"])
	# 		print(table_datas[6].a["href"])
	# 		break
	
	message = cast(Message, update.effective_message)
	eps_to_search: str = cast(str, message.text).split(" ")[-1]
	r: Response = requests.get(urljoin(WIKI_URL, f"Episode_{eps_to_search}"), headers=DEFAULT_HEADERS)
	soup = BeautifulSoup(r.text, "html.parser")
	
	infobox = cast(Tag, soup.find("table", class_="infobox"))
	table_rows: List = infobox.find_all("tr")
	episode = cast(str, table_rows[0].text).strip().replace("  ", "\n")
	title = cast(str, table_rows[3].td.text).strip().replace("  ", "\n    ")
	jp_title = cast(str, table_rows[4].td.text).strip().replace("  ", "\n    ")
	#airdate = cast(str, table_rows[5].td.text).strip().replace("  ", "\n    ")
	
	if "%" in cast(str, table_rows[7].td.text):
		season = cast(str, table_rows[9].td.text).strip()
		#manga_case = cast(str, table_rows[8].td.text).strip().replace("  ", ", ")
		manga_source = cast(str, table_rows[10].td.text).strip().replace("  ", "\n    ")
		manga_source_as = table_rows[10].td.find_all("a")
	else:
		season = cast(str, table_rows[8].td.text).strip()
		#manga_case = cast(str, table_rows[7].td.text).strip().replace("  ", ", ")
		manga_source = cast(str, table_rows[9].td.text).strip().replace("  ", "\n    ")
		manga_source_as = table_rows[9].td.find_all("a")
	
	text  = f"<code>{episode}</code>\n\n"
	text += f"<code>🇬🇧: </code><code>{title}</code>\n"
	text += f"<code>🇯🇵: </code><code>{jp_title}</code>\n"
	#text += f"<code>🎈: </code><code>{airdate}</code>\n"
	text += f"<code>❄️: </code><code>{season}</code>\n"
	#text += f"<code>📂: </code><code>{manga_case}</code>\n"
	text += f"<code>🗂: </code><code>{manga_source}</code>"
	
	keyboard: List[List[InlineKeyboardButton]] = []
	buttons: List[InlineKeyboardButton] = []
	for manga_source_a in manga_source_as:
		if len(buttons) >= 2:
			keyboard.append(buttons)
			buttons = []
		buttons.append(InlineKeyboardButton(
			"🗂 Manga Source",
			url=urljoin(_DCW_URL, manga_source_a["href"])
		))
	if buttons:
		keyboard.append(buttons)
		buttons = []
	keyboard.append([InlineKeyboardButton(
		"🔍 Full Information",
		url=urljoin(WIKI_URL, r.url)
	)])

	reply_to_message_id: Optional[int] = None
	if message.reply_to_message:
		reply_to_message_id = cast(Message, message.reply_to_message).message_id
	await message.reply_text(
		text,
		reply_to_message_id=reply_to_message_id,
		do_quote=True,
		reply_markup=InlineKeyboardMarkup(keyboard)
	)


async def eps_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	episode_data: Dict[int, Any] = {}
	r: Response = requests.get(WIKI_ANIME_URL, headers=DEFAULT_HEADERS)
	soup = BeautifulSoup(r.text, "html.parser")
	
	seasons: List = soup.find_all("table", class_=["wikitable", "seasontable"])[::-1]
	for season in seasons:
		table_rows: List = season.find_all("tr")[1::]
		for table_row in table_rows:
			table_datas: List = table_row.find_all("td")
			jpn_eps = cast(str, table_datas[0].text)
			int_eps = cast(str, table_datas[1].text)
			eps_title = cast(str, table_datas[2].text)
			eps_broadcast = cast(str, table_datas[3].text)
			eps_en_dub_bc = cast(str, table_datas[4].text)
			eps_plot = cast(str, table_datas[5].text)
			eps_manga_src = cast(str, table_datas[6].text)
			
			jpn_eps_0: str = re.split("-|WPS", jpn_eps)[0]
			try:
				jpn_eps_0_int = int(jpn_eps_0)
			except:
				continue
			
			if jpn_eps_0_int in episode_data:
				continue
			
			episode_data[jpn_eps_0_int] = {
				"jpn_eps": jpn_eps,
				"int_eps": int_eps,
				"eps_title": eps_title,
				"eps_broadcast": eps_broadcast,
				"eps_en_dub_bc": eps_en_dub_bc,
				"eps_plot": eps_plot,
				"eps_manga_src": eps_manga_src
			}
	
	print(len(episode_data))
	file = open("episode.json", "w")
	file.write(json.dumps(episode_data, indent=4))
