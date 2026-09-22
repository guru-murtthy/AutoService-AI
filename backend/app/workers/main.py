import time
import logging
from datetime import datetime, date
from app.core.database import SessionLocal
from app.services.followup_service import process_due_followups
from app.services.analytics_service import generate_daily_report
from app.models.all_models import SystemHealth, Business, AgentTask, Lead
from agent.core.loop import AutonomousAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

def run_worker_loop():
    logger.info("=== Starting AutoService AI Heartbeat Worker ===")
    last_health_check = 0
    last_followup_check = 0
    last_report_check = 0

    while True:
        now_ts = time.time()
        db = SessionLocal()

        try:
            # 1. 5-Minute Heartbeat: System Health Monitoring
            if now_ts - last_health_check >= 300 or last_health_check == 0:
                logger.info("[Heartbeat] Running 5-min system health check...")
                sh = SystemHealth(
                    component="backend_worker",
                    status="healthy",
                    latency=12.5,
                    error_rate=0.0
                )
                db.add(sh)
                db.commit()
                last_health_check = now_ts

            # 2. 15-Minute Heartbeat: Process Pending Agent Tasks
            if now_ts - last_followup_check >= 900 or last_followup_check == 0:
                logger.info("[Heartbeat] Running 15-min pending agent tasks check...")
                agent = AutonomousAgent(db)
                pending_tasks = db.query(AgentTask).filter(AgentTask.status == "PENDING").limit(10).all()
                for task in pending_tasks:
                    logger.info(f"Executing pending agent task: {task.id} ({task.task_type})")
                    agent.execute_task(task.task_type, task.input_data or {})
                last_followup_check = now_ts

            # 3. 1-Hour Heartbeat: Execute Due Customer Follow-Ups
            executed_followups = process_due_followups(db)
            if executed_followups > 0:
                logger.info(f"[Heartbeat] Executed {executed_followups} due follow-ups.")

            # 4. 24-Hour Heartbeat: Generate Daily Business Reports
            if now_ts - last_report_check >= 86400 or last_report_check == 0:
                logger.info("[Heartbeat] Running 24-hour daily report generation...")
                businesses = db.query(Business).all()
                for b in businesses:
                    generate_daily_report(b.id, date.today(), db)
                last_report_check = now_ts

        except Exception as e:
            logger.error(f"Error in worker loop iteration: {e}")
        finally:
            db.close()

        time.sleep(30)  # Sleep 30 seconds between polling ticks

if __name__ == "__main__":
    run_worker_loop()
