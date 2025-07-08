from sqlalchemy import Column, String, DateTime, BigInteger, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Attendance(Base):
	__tablename__ = 'attendance'

	id = Column(BigInteger, primary_key=True)
	user_id = Column(String)
	attend_datetime = Column(DateTime)

class AttendanceSummary(Base):
	__tablename__ = 'attendance_summary'

	id = Column(BigInteger, primary_key=True)
	user_id = Column(String)
	total_days = Column(Integer, default=0)
	disabled = Column(Boolean, default=False)