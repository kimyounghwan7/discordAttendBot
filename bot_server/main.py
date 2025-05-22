import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
import os
from loguru import logger
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_init.db import get_db
from bot_server.bot_service import handle_attendance, handle_attendance_check, handle_attendance_rank, create_daily_thread

load_dotenv()
intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
TODO_CHANNEL_ID = 1359320235181867057
ATTEND_CHANNEL_ID = 1359499532806914128

@bot.command()
async def 명령어(ctx):
	commands = ["❗ 사용 가능한 명령어", "출석", "출석확인", "출석순위"]
	await ctx.send("\n\n".join(commands))
 
@bot.command()
async def 출석(ctx):
	with get_db() as db:
		try:
			await ctx.send(handle_attendance(ctx, db))
		except Exception as e:
			await ctx.send("⚠️ 출석 처리 중 오류가 발생했어요.")
			logger.error(f"[출석 오류] {e}")

@bot.command()
async def 출석확인(ctx):
	with get_db() as db:
		try:
			mentions = handle_attendance_check(db)
			if mentions:
				await ctx.send("오늘 출석한 사람들:\n" + "\n".join(mentions))
				return
			await ctx.send("오늘은 아직 아무도 출석하지 않았어요!")
		except Exception as e:
			logger.error(e)

@bot.command()
async def 출석순위(ctx):
	with get_db() as db:
		try:
			await ctx.send(handle_attendance_rank(db))
		except Exception as e:
			logger.error(e)

@bot.event
async def on_ready():
	create_thread.start()

@tasks.loop(hours=24)  # 매일 24시간마다 작업 실행
async def create_thread():
	try:
		now = datetime.now()
		target_time = time(19, 50, 0)

		# 매일 오전 9시에 스레드 생성
		if now.time() >= target_time:
			next_target = datetime.combine(now.date() + timedelta(days=1), target_time)
		else:
			next_target = datetime.combine(now.date(), target_time)

		time_until_next = (next_target - now).total_seconds()
		await asyncio.sleep(time_until_next)  # 다음 실행 시간까지 대기
  
		if next_target.weekday() == 6 or next_target.weekday() == 5:
			logger.info("일요일이라서 스킵")
			return
		with get_db() as db:
			await create_daily_thread(bot, TODO_CHANNEL_ID, ATTEND_CHANNEL_ID, db)
	except Exception as e:
		logger.error(e)

if __name__ == "__main__":
	bot.run(os.getenv("DISCORD_TOKEN"))
