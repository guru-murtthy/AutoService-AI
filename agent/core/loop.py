import uuid
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.all_models import AgentTask, AgentEvent, AuditLog
from agent.tools.registry import AgentToolRegistry
from agent.policies.safety import SafetyPolicyEngine, SafetyPolicyViolation

logger = logging.getLogger("agent_core")

class AutonomousAgent:
    """
    Autonomous Agent Core execution loop:
    OBSERVE -> THINK -> PLAN -> ACT -> VERIFY -> RECORD -> LEARN
    """
    def __init__(self, db: Session):
        self.db = db
        self.tool_registry = AgentToolRegistry(db)
        self.safety_engine = SafetyPolicyEngine(db)

    def execute_task(self, task_type: str, input_data: dict, priority: int = 5) -> dict:
        task_id = str(uuid.uuid4())
        task = AgentTask(
            id=task_id,
            task_type=task_type,
            status="IN_PROGRESS",
            priority=priority,
            input_data=input_data,
            created_at=datetime.utcnow()
        )
        self.db.add(task)
        self.db.commit()

        start_time = datetime.utcnow()

        try:
            # 1. OBSERVE & THINK
            plan = self._plan_task(task_type, input_data)
            
            # 2. PLAN & SAFETY CHECK
            for step in plan:
                tool_name = step["tool"]
                params = step["params"]
                cost = step.get("estimated_cost", 0.0)

                # Enforce Safety Policy before action
                self.safety_engine.validate_action(tool_name, params, cost)

            # 3. ACT
            output_results = []
            for step in plan:
                res = self.tool_registry.execute_tool(step["tool"], step["params"])
                output_results.append({"step": step["name"], "result": res})

            # 4. VERIFY & RECORD
            task.status = "COMPLETED"
            task.output_data = {"steps": output_results}
            task.completed_at = datetime.utcnow()
            self.db.commit()

            # Record Agent Event
            evt = AgentEvent(
                agent_name="AutonomousAgentCore",
                event_type=f"TASK_COMPLETED:{task_type}",
                payload={"task_id": task_id, "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000},
                severity="INFO"
            )
            self.db.add(evt)
            self.db.commit()

            return {"task_id": task_id, "status": "COMPLETED", "output": output_results}

        except SafetyPolicyViolation as spe:
            task.status = "FAILED"
            task.error = f"Safety Policy Violation: {str(spe)}"
            self.db.commit()
            logger.warning(f"Task {task_id} failed safety policy: {spe}")
            return {"task_id": task_id, "status": "FAILED", "error": str(spe)}

        except Exception as e:
            task.status = "FAILED"
            task.error = str(e)
            self.db.commit()
            logger.error(f"Task {task_id} failed with error: {e}")
            return {"task_id": task_id, "status": "FAILED", "error": str(e)}

    def _plan_task(self, task_type: str, input_data: dict) -> list:
        if task_type == "PROCESS_UNQUALIFIED_LEADS":
            return [
                {"name": "Search New Leads", "tool": "search_leads", "params": {"business_id": input_data.get("business_id"), "status": "NEW"}},
            ]
        elif task_type == "GENERATE_QUOTATION_FOR_LEAD":
            return [
                {"name": "Calculate Quote", "tool": "calculate_quote", "params": input_data},
                {"name": "Create Quote Record", "tool": "create_quote", "params": input_data}
            ]
        elif task_type == "EXECUTE_DUE_FOLLOWUPS":
            return [
                {"name": "Schedule Lead Followups", "tool": "schedule_followup", "params": input_data}
            ]
        else:
            return [
                {"name": "Fetch System Metrics", "tool": "get_system_health", "params": {}}
            ]
