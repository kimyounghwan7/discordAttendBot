import discord
from discord.ext import commands
from datetime import datetime, timedelta
from sqlalchemy import and_
from dotenv import load_dotenv
import os
from loguru import logger
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_init.models import Attendance, AttendanceSummary
from db_init.db import get_db

load_dotenv()
intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def 명령어(ctx):
	commands = ["❗ 사용 가능한 명령어", "출석", "출석확인", "출석순위"]
	await ctx.send("\n\n".join(commands))
 
@bot.command()
async def 출석(ctx):
	with get_db() as db:
		try:
			user_id = str(ctx.author.id)
			now = datetime.now()
			today = now.replace(hour=0, minute=0, second=0, microsecond=0)
			tomorrow = today + timedelta(days=1)
			# 오늘 날짜 범위 안에 해당 유저의 출석 여부 체크
			exists = db.query(Attendance).filter(
				and_(
					Attendance.user_id == user_id,
					Attendance.attend_datetime >= today,
					Attendance.attend_datetime < tomorrow
				)
			).first()

			if exists:
				await ctx.send(f"{ctx.author.mention} 이미 오늘 출석했어요!")
			else:
				db.add(Attendance(user_id=user_id, attend_datetime=now))
				
				summary = db.query(AttendanceSummary).filter_by(user_id=user_id).first()
				if not summary:
					summary = AttendanceSummary(user_id=user_id, total_days=1)
					db.add(summary)
				else:
					summary.total_days += 1

				db.commit()
				await ctx.send(f"{ctx.author.mention} 출석 완료!")
		except Exception as e:
			await ctx.send("⚠️ 출석 처리 중 오류가 발생했어요.")
			logger.error(f"[출석 오류] {e}")

@bot.command()
async def 출석확인(ctx):
	with get_db() as db:
		try:
			today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
			tomorrow = today + timedelta(days=1)
			records = (
				db.query(Attendance)
				.filter(and_(
					Attendance.attend_datetime >= today,
					Attendance.attend_datetime < tomorrow
				))
				.all()
			)

			if records:
				mentions = [f"<@{r.user_id}>" for r in records]
				await ctx.send(f"오늘 출석한 사람들:\n" + "\n".join(mentions))
			else:
				await ctx.send("오늘은 아직 아무도 출석하지 않았어요!")
		except Exception as e:
			logger.error(e)


@bot.command()
async def 출석순위(ctx):
	with get_db() as db:
		try:
			records = db.query(AttendanceSummary).order_by(AttendanceSummary.total_days.desc()).limit(10).all()
			if records:
				result = "\n".join(
					[f"{i+1}. <@{r.user_id}> - {r.total_days}일" for i, r in enumerate(records)]
				)
				await ctx.send(f"출석 순위 Top 10\n{result}")
			else:
				await ctx.send("아직 출석 기록이 없습니다.")
		except Exception as e:
			logger.error(e)

if __name__ == "__main__":
	bot.run(os.getenv("DISCORD_TOKEN"))
