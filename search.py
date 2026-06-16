# meta developer: @strongestonez

import aiohttp
from .. import loader, utils

@loader.tds
class HergokuSearchMod(loader.Module):
    """Продвинутый поиск модулей (Обход блокировки GitHub API)"""
    strings = {"name": "HergokuSearch"}

    async def findmodcmd(self, message):
        """<запрос> - Найти готовый к установке модуль"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>❌ Что ищем? Пример: <code>.findmod tiktok</code></b>")
            return

        await message.edit(f"🔍 <b>Ищу модули по запросу:</b> <code>{args}</code>...")
        
        # Используем поиск по репозиториям (не требует токена и не выдает 401)
        query = f"{args} hikka language:python"
        url = f"https://api.github.com/search/repositories?q={query}&per_page=6"
        headers = {"User-Agent": "Hergoku-Search-Bot"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        await message.edit(f"❌ <b>Ошибка API GitHub: {response.status}</b>")
                        return
                    
                    data = await response.json()
                    repos = data.get("items", [])
                    
                    if not repos:
                        await message.edit("<b>😭 По твоему запросу ничего не найдено.</b>")
                        return

                    found_modules = []
                    await message.edit(f"⏳ <b>Анализирую найденные базы на наличие файлов...</b>")
                    
                    # Парсим каждый репозиторий изнутри
                    for repo in repos:
                        full_name = repo["full_name"]
                        branch = repo.get("default_branch", "main")
                        
                        # Попытка 1: Ищем файл repo.json (стандарт для юзерботов)
                        repo_json_url = f"https://raw.githubusercontent.com/{full_name}/{branch}/repo.json"
                        async with session.get(repo_json_url) as r_resp:
                            if r_resp.status == 200:
                                try:
                                    repo_data = await r_resp.json(content_type=None)
                                    if "modules" in repo_data:
                                        for mod_name, mod_info in repo_data["modules"].items():
                                            if args.lower() in mod_name.lower() or args.lower() in str(mod_info.get("description", "")).lower():
                                                dl_url = mod_info.get("url", f"https://raw.githubusercontent.com/{full_name}/{branch}/{mod_name}.py")
                                                desc = mod_info.get("description", "Без описания")
                                                found_modules.append((mod_name, full_name.split('/')[0], desc, dl_url))
                                except:
                                    pass
                            else:
                                # Попытка 2: Если repo.json нет, простукиваем прямой .py файл
                                guess_word = args.split()[0]
                                for guess in [guess_word.lower(), guess_word.capitalize()]:
                                    guess_url = f"https://raw.githubusercontent.com/{full_name}/{branch}/{guess}.py"
                                    async with session.head(guess_url) as head_resp:
                                        if head_resp.status == 200:
                                            found_modules.append((guess, full_name.split('/')[0], "Прямой файл (без описания)", guess_url))
                                            break
                                            
                    if not found_modules:
                        await message.edit("<b>❌ Репозитории найдены, но вытащить оттуда прямые ссылки на сам модуль не удалось.</b>")
                        return
                        
                    # Выводим красивый результат
                    text = f"<b>🎯 Найдено модулей по запросу «{args}»:</b>\n\n"
                    for idx, (m_name, m_author, m_desc, m_url) in enumerate(found_modules[:8], 1):
                        text += f"<b>{idx}. {m_name}</b> <i>(от {m_author})</i>\n"
                        text += f"📝 <i>{m_desc}</i>\n"
                        text += f"📥 <code>.dlmod {m_url}</code>\n\n"
                    
                    text += "💡 <i>Нажми на нужную команду .dlmod, чтобы скопировать её!</i>"
                    await message.edit(text, parse_mode="html", disable_web_page_preview=True)

            except Exception as e:
                await message.edit(f"❌ <b>Системная ошибка:</b> {str(e)}")
