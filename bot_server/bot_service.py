import os
from loguru import logger
import sys
import asyncio
from datetime import datetime, timedelta, time
from sqlalchemy import and_

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_init.models import Attendance, AttendanceSummary

def handle_attendance(ctx, db):
	try:
		user_id = str(ctx.author.id)
		now = datetime.now()
		today = now.replace(hour=0, minute=0, second=0, microsecond=0)
		tomorrow = today + timedelta(days=1)

		# 출석 가능 시간대: 20:50 ~ 23:00
		start_time = time(20, 50)
		end_time = time(22, 0)

		if not (start_time <= now.time() < end_time): 
			return "⏰ 출석 가능한 시간은 **20:50부터 22:00까지**예요!"

		# 오늘 날짜 범위 안에 해당 유저의 출석 여부 체크
		exists = db.query(Attendance).filter(
			and_(
				Attendance.user_id == user_id,
				Attendance.attend_datetime >= today,
				Attendance.attend_datetime < tomorrow
			)
		).first()

		if exists:
			return f"{ctx.author.mention} 이미 오늘 출석했어요!"

		db.add(Attendance(user_id=user_id, attend_datetime=now))
		summary = db.query(AttendanceSummary).filter_by(user_id=user_id).first()
		if not summary:
			summary = AttendanceSummary(user_id=user_id, total_days=1)
			db.add(summary)
		else:
			summary.total_days += 1
		db.commit()
		return f"{ctx.author.mention} 출석 완료!"
	except Exception as e:
		logger.error(e)

def handle_attendance_check(db):
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
			return [f"<@{r.user_id}>" for r in records]
		return None
	except Exception as e:
		logger.error(e)

def handle_attendance_rank(db):
	try:
		logger.info("")
		records = db.query(AttendanceSummary).order_by(AttendanceSummary.total_days.desc()).limit(10).all()
		if records:
			result = "\n".join(
				[f"{i+1}. <@{r.user_id}> - {r.total_days}일" for i, r in enumerate(records)]
			)
			return f"출석 순위 Top 10\n{result}"
		return "아직 출석 기록이 없습니다."
	except Exception as e:
		logger.error(e)

async def create_daily_thread(bot, channel_id):
	try:
		now = datetime.now()
		channel = bot.get_channel(channel_id)
		if channel:
			thread_name = now.strftime('%m/%d') + " To-Do List"
			thread = await channel.create_thread(
				name=thread_name,
				auto_archive_duration=1440  # 24시간
			)
			thread_link = thread.jump_url  # 생성된 쓰레드의 링크
			await channel.send(f"Good Day!  {thread_link}")
			await thread.send(f"기분 좋은 {now.strftime('%m')} 월 {now.strftime('%d')}입니다. \n오늘 학습 목표를 입력해주세요 :)")
			return
		logger.error("쓰레드 생성 가능한 채널이 없습니다.")
	except Exception as e:
		logger.error(e)