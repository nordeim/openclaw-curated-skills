"""
FIS 3.1 Lite - Ticket Manager
任务票据生命周期管理
"""

import json
import re
from pathlib import Path
from datetime import datetime
from enum import Enum
from fis_config import get_shared_hub_path

SHARED_HUB = get_shared_hub_path()
TICKETS_DIR = SHARED_HUB / "tickets"

class TicketStatus(Enum):
    PENDING = "pending"      # 待处理
    ACTIVE = "active"        # 进行中
    BLOCKED = "blocked"      # 阻塞/等待
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class TicketManager:
    """任务票据管理器"""
    
    def __init__(self):
        self.active_dir = TICKETS_DIR / "active"
        self.completed_dir = TICKETS_DIR / "completed"
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_ticket_id(self, prefix: str = "TASK") -> str:
        """生成票据 ID: TASK-YYYY-MM-DD-XXX"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Count existing tickets today
        existing = list(self.active_dir.glob(f"*{today}*"))
        existing += list(self.completed_dir.glob(f"*{today}*"))
        seq = len(existing) + 1
        
        return f"{prefix}-{today}-{seq:03d}"
    
    def create_ticket(self, title: str, description: str, 
                     assignee: str = None, priority: int = 3,
                     metadata: dict = None) -> dict:
        """
        创建新票据
        
        Args:
            title: 票据标题
            description: 详细描述
            assignee: 负责人
            priority: 优先级 (1=最高, 5=最低)
            metadata: 额外元数据
        
        Returns:
            ticket: 票据数据
        """
        ticket_id = self._generate_ticket_id()
        now = datetime.now().isoformat()
        
        ticket = {
            "ticket_id": ticket_id,
            "title": title,
            "description": description,
            "status": TicketStatus.PENDING.value,
            "priority": priority,
            "assignee": assignee,
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
            "metadata": metadata or {},
            "progress": {
                "current_step": 0,
                "total_steps": 0,
                "notes": []
            }
        }
        
        # Save to file
        filename = f"{ticket_id}.json"
        filepath = self.active_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        print(f"✅ Created ticket: {ticket_id}")
        return ticket
    
    def get_ticket(self, ticket_id: str) -> dict:
        """获取票据信息"""
        # Try active first
        filepath = self.active_dir / f"{ticket_id}.json"
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        
        # Try completed
        filepath = self.completed_dir / f"{ticket_id}.json"
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        
        return None
    
    def update_ticket(self, ticket_id: str, **kwargs) -> dict:
        """更新票据"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {ticket_id}")
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if key in ticket:
                ticket[key] = value
        
        ticket["updated_at"] = datetime.now().isoformat()
        
        # Save back
        status = ticket.get("status", "pending")
        if status in [TicketStatus.COMPLETED.value, TicketStatus.CANCELLED.value]:
            filepath = self.completed_dir / f"{ticket_id}.json"
        else:
            filepath = self.active_dir / f"{ticket_id}.json"
        
        with open(filepath, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        print(f"✅ Updated ticket: {ticket_id}")
        return ticket
    
    def start_ticket(self, ticket_id: str) -> dict:
        """开始处理票据"""
        return self.update_ticket(
            ticket_id, 
            status=TicketStatus.ACTIVE.value
        )
    
    def complete_ticket(self, ticket_id: str, result: str = None) -> dict:
        """完成票据"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None
        
        ticket["status"] = TicketStatus.COMPLETED.value
        ticket["completed_at"] = datetime.now().isoformat()
        
        if result:
            ticket["result"] = result
        
        # Move to completed
        active_path = self.active_dir / f"{ticket_id}.json"
        completed_path = self.completed_dir / f"{ticket_id}.json"
        
        with open(completed_path, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        if active_path.exists():
            active_path.unlink()
        
        print(f"✅ Completed ticket: {ticket_id}")
        return ticket
    
    def list_active(self, assignee: str = None) -> list:
        """列出所有活跃票据"""
        tickets = []
        
        for ticket_file in self.active_dir.glob("*.json"):
            try:
                with open(ticket_file) as f:
                    ticket = json.load(f)
                    if assignee is None or ticket.get("assignee") == assignee:
                        tickets.append(ticket)
            except Exception as e:
                print(f"Error loading {ticket_file}: {e}")
        
        # Sort by priority (asc) and created_at (desc)
        tickets.sort(key=lambda t: (t.get("priority", 5), t.get("created_at", "")), reverse=False)
        
        return tickets
    
    def list_completed(self, limit: int = 10) -> list:
        """列出已完成的票据"""
        tickets = []
        
        for ticket_file in self.completed_dir.glob("*.json"):
            try:
                with open(ticket_file) as f:
                    tickets.append(json.load(f))
            except Exception as e:
                print(f"Error loading {ticket_file}: {e}")
        
        # Sort by completed_at (desc)
        tickets.sort(key=lambda t: t.get("completed_at", ""), reverse=True)
        
        return tickets[:limit]
    
    def add_progress_note(self, ticket_id: str, note: str) -> dict:
        """添加进度备注"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None
        
        progress = ticket.get("progress", {})
        notes = progress.get("notes", [])
        notes.append({
            "timestamp": datetime.now().isoformat(),
            "note": note
        })
        progress["notes"] = notes
        
        return self.update_ticket(ticket_id, progress=progress)
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        active = len(list(self.active_dir.glob("*.json")))
        completed = len(list(self.completed_dir.glob("*.json")))
        
        # Calculate completion rate for last 7 days
        recent_completed = 0
        now = datetime.now()
        
        for ticket_file in self.completed_dir.glob("*.json"):
            try:
                with open(ticket_file) as f:
                    ticket = json.load(f)
                    completed_at = ticket.get("completed_at")
                    if completed_at:
                        completed_time = datetime.fromisoformat(completed_at)
                        days_diff = (now - completed_time).days
                        if days_diff <= 7:
                            recent_completed += 1
            except:
                pass
        
        return {
            "active": active,
            "completed": completed,
            "total": active + completed,
            "recent_completed_7d": recent_completed
        }

if __name__ == "__main__":
    # Test
    manager = TicketManager()
    
    # Create test ticket
    ticket = manager.create_ticket(
        title="测试票据",
        description="这是一个测试票据",
        assignee="cybermao",
        priority=2
    )
    
    print(f"\nStats: {manager.get_stats()}")
    print(f"\nActive tickets: {len(manager.list_active())}")
