import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
import models

scheduler = BackgroundScheduler()

def update_all_pre_budgets():
    db: Session = SessionLocal()
    today = datetime.datetime.now().date()
    budgets = db.query(models.Budget).all()
    
    for budget in budgets:
        db_last_date_month = int(str(budget.last_updated_date).split('-')[1])
        if budget.last_updated_date is None or db_last_date_month != today.month:
            budget.pre_budget = budget.budget_amount
            budget.last_updated_date = today
    
    db.commit()
    db.close()

def start_scheduler():
    scheduler.add_job(update_all_pre_budgets, 'cron', day=2, hour=0, minute=0)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()
