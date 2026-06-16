# meta developer: @strongestonez

import aiohttp
from .. import loader, utils

@loader.tds
class HergokuSearchMod(loader.Module):
    """Твой личный поисковик модулей по всему GitHub"""
    strings = {"name": "HergokuSearch"}

    async def findmodcmd(self, message):
        """<запрос> - Найти модули на GitHub"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>❌ Что ищем? Пример: <code>.findmod анекдоты</code></b>")
            return

        await message.edit(f"🔍 <b>Ищу модули по запросу:</b> <code>{args}</code>...")
        
        # Ищем репозитории, где есть ключевые слова и теги модулей
        query = f"{args} hikka module language:python"
        url = f"https://api.github.com/search/repositories?q={query}&per_page=8"
        headers = {"User-Agent": "HergokuSearchBot"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        await message.edit(f"❌ <b>Ошибка API GitHub: {response.status}</b>")
                        return
                    
                    data = await response.json()
                    items = data.get("items", [])
                    
                    if not items:
                        await message.edit("<b>😭 Ничего не найдено. Попробуй синоним.</b>")
                        return
                    
                    text = f"<b>🎯 Найдено для '{args}':</b>\n\n"
                    for idx, item in enumerate(items, 1):
                        name = item["full_name"]
                        desc = item["description"] or "Нет описания"
                        repo_url = item["html_url"]
                        
                        text += f"<b>{idx}. <a href='{repo_url}'>{name}</a></b>\n"
                        text += f"📝 <i>{desc}</i>\n\n"
                    
                    text += "💡 <i>Кликни по названию, чтобы открыть репо и забрать нужный модуль!</i>"
                    await message.edit(text, parse_mode="html", disable_web_page_preview=True)
                    
            except Exception as e:
                await message.edit(f"❌ <b>Ошибка:</b> {str(e)}")
