# discordAttendBot

## 사용 설명서
```
간단한 출첵용 디스코드 봇

1.DB supabase를 통해 postgresDB 배포 및 설정.

2.project root에 .env 만들고 DB 세션 연결 주소 입력.

3.Docker build

4.docker-compose -f docker-compose-bot.yml up -d (command: tail -F /dev/null)

5.alembic init alembic

6.alembic.ini 안에 sqlalchemy.url = [DB주소]

7.alembic/env.py 수정 [project_root]/env.py 내용을 복사 후 붙혀넣기.

8.alembic revision --autogenerate -m "create attendance tables" 마이그레이션 파일 생성

9.alembic upgrade head 마이그레이션 적용.

10.Discord.dev에서 봇을 생성하고 해당 봇의 token을 발행.

11.Railway or Render Backworker를 통해 배포.

12. bot token, db url id pw는 배포 서비스에서 설정으로 추가.

13. docker hub를 활용해서 build deploy 시간 단축.
```