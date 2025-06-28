import asyncio

import speedtest
from WinxMusic import app
from WinxMusic.misc import SUDOERS
from strings import command


@app.on_message(command("SPEEDTEST_COMMAND") & SUDOERS)
async def speedtest_function(client, message):
    m = await message.reply_text("🚀 **Iniciando SpeedTest**...")

    def run_speedtest():
        try:
            test = speedtest.Speedtest()
            test.get_best_server()
            test.download()
            test.upload()
            test.results.share()
            return test.results.dict()
        except Exception as e:
            return {"error": str(e)}

    async def update_status():
        stages = [
            "⏳ Performing**download** ... ⬇️",
            "⏳ Initialising **upload** ... ⬆️",
            "↻ Sharing the Speedtest Results... 📊"
        ]

        for stage in stages:
            if not speedtest_task.done():
                try:
                    await m.edit(stage)
                    await asyncio.sleep(3)
                except Exception:
                    pass

    loop = asyncio.get_running_loop()
    speedtest_task = loop.run_in_executor(None, run_speedtest)

    update_task = asyncio.create_task(update_status())

    result = await speedtest_task

    if not update_task.done():
        update_task.cancel()

    if "error" in result:
        await m.edit(f"⚠️ **Error Occurred While Performing Speedtest:**\n\n`{result['error']}`")
        return

    latency = str(result['server']['latency']).replace('.', ',')
    ping = str(result['ping']).replace('.', ',')

    output = f"""**SpeedTest Final Results** 📊

<u>**Clients:**</u>
🌐 **ISP:** {result['client']['isp']}
🏳️ **Country:** {result['client']['country']}

<u>**Server Info:**</u>
🌍 **Name:** {result['server']['name']}
🇦🇺 **Country:** {result['server']['country']}, {result['server']['cc']}
💼 **Provider/Sponsor:** {result['server']['sponsor']}
⚡ **Latency:** {latency} ms  
🏓 **Ping:** {ping} ms"""

    try:
        await app.send_photo(
            chat_id=message.chat.id,
            photo=result["share"],
            caption=output
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"⚠️ **Error Occurred While Sharing Speedtest Results:**\n\n`{str(e)}`")
