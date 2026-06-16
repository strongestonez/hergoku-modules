# meta developer: @strongestonez

import aiohttp
from .. import loader, utils

@loader.tds
class HergokuSearchMod(loader.Module):
    """Продвинутый поиск модулей для Heroku/Hikka"""
    strings = {"name": "HergokuSearch"}

    async def findmodcmd(self, message):
        """<запрос> - Найти готовый к установке модуль по коду на GitHub"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>❌ Что ищем? Пример: <code>.findmod tiktok</code> или <code>.findmod music</code></b>")
            return

        await message.edit(f"🔍 <b>Глубокое сканирование кода GitHub по запросу:</b> <code>{args}</code>...")
        
        # Ищем конкретные .py файлы, которые содержат ключевое слово и базу loader.Module
        query = f"{args} loader.Module in:file language:python extension:py"
        url = f"https://api.github.com/search/code?q={query}&per_page=7"
        headers = {"User-Agent": "Hergoku-Search-Engine"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 403:
                        await message.edit("❌ <b>GitHub временно ограничил поиск (анти-спам лимит). Попробуй через минуту!</b>")
                        return
                    if response.status != 200:
                        await message.edit(f"❌ <b>Ошибка API: {response.status}</b>")
                        return
                    
                    data = await response.json()
                    items = data.get("items", [])
                    
                    if not items:
                        await message.edit("<b>😭 Готовых модулей не найдено. Попробуй написать запрос на английском (например, inline).</b>")
                        return
                    
                    text = f"<b>🎯 Найдено для «{args}»:</b>\n\n"
                    for idx, item in enumerate(items, 1):
                        file_name = item["name"]
                        repo_name = item["repository"]["full_name"]
                        html_url = item["html_url"]
                        
                        # Магия: превращаем обычную ссылку в прямую (raw) для установки
                        raw_url = html_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
                        
                        text += f"<b>{idx}. {file_name.replace('.py', '')}</b> <i>(автор: {repo_name.split('/')[0]})</i>\n"
                        text += f"📥 <code>.dlmod {raw_url}</code>\n\n"
                    
                    text += "💡 <i>Нажми на нужную команду .dlmod, чтобы скопировать её, и отправь в чат!</i>"
                    await message.edit(text, parse_mode="html", disable_web_page_preview=True)
                    
            except Exception as e:
                await message.edit(f"❌ <b>Системная ошибка:</b> {str(e)}")
