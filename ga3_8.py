import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_ticket_status(ticket_id: int):
    return {"ticket_id": ticket_id}


def schedule_meeting(date: str, time: str, meeting_room: str):
    return {"date": date, "time": time, "meeting_room": meeting_room}


def get_expense_balance(employee_id: int):
    return {"employee_id": employee_id}


def calculate_performance_bonus(employee_id: int, current_year: int):
    return {"employee_id": employee_id, "current_year": current_year}


def report_office_issue(issue_code: int, department: str):
    return {"issue_code": issue_code, "department": department}


@app.get("/execute")
async def execute_query(q: str):
    try:
        query = q.lower()
        pattern_debug_info = {}

        # Ticket status pattern
        if re.search(r"ticket.*?\d+", query):
            ticket_id = int(re.search(r"ticket.*?(\d+)", query).group(1))
            return {"name": "get_ticket_status", "arguments": json.dumps({"ticket_id": ticket_id})}
        pattern_debug_info["ticket_status"] = re.search(
            r"ticket.*?\d+", query) is not None

        # Meeting scheduling pattern
        if re.search(r"schedule.?\d{4}-\d{2}-\d{2}.?\d{2}:\d{2}.*?room", query, re.IGNORECASE):
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", query)
            time_match = re.search(r"(\d{2}:\d{2})", query)
            room_match = re.search(
                r"room\s*([A-Za-z0-9]+)", query, re.IGNORECASE)
            if date_match and time_match and room_match:
                return {"name": "schedule_meeting", "arguments": json.dumps({
                    "date": date_match.group(1),
                    "time": time_match.group(1),
                    "meeting_room": f"Room {room_match.group(1).capitalize()}"
                })}
        pattern_debug_info["meeting_scheduling"] = re.search(
            r"schedule.?\d{4}-\d{2}-\d{2}.?\d{2}:\d{2}.*?room", query, re.IGNORECASE) is not None

        # Expense balance pattern
        if re.search(r"expense", query):
            emp_match = re.search(r"employee\s*(\d+)", query, re.IGNORECASE)
            if emp_match:
                return {"name": "get_expense_balance", "arguments": json.dumps({
                    "employee_id": int(emp_match.group(1))
                })}
        pattern_debug_info["expense_balance"] = re.search(
            r"expense", query) is not None

        # Performance bonus pattern
        if re.search(r"bonus", query, re.IGNORECASE):
            emp_match = re.search(
                r"emp(?:loyee)?\s*(\d+)", query, re.IGNORECASE)
            year_match = re.search(r"\b(2024|2025)\b", query)
            if emp_match and year_match:
                return {"name": "calculate_performance_bonus", "arguments": json.dumps({
                    "employee_id": int(emp_match.group(1)),
                    "current_year": int(year_match.group(1))
                })}
        pattern_debug_info["performance_bonus"] = re.search(
            r"bonus", query, re.IGNORECASE) is not None

        # Office issue pattern
        if re.search(r"(office issue|report issue)", query, re.IGNORECASE):
            code_match = re.search(
                r"(issue|number|code)\s*(\d+)", query, re.IGNORECASE)
            dept_match = re.search(
                r"(in|for the)\s+(\w+)(\s+department)?", query, re.IGNORECASE)
            if code_match and dept_match:
                return {"name": "report_office_issue", "arguments": json.dumps({
                    "issue_code": int(code_match.group(2)),
                    "department": dept_match.group(2).capitalize()
                })}
        pattern_debug_info["office_issue"] = re.search(
            r"(office issue|report issue)", query, re.IGNORECASE) is not None

        raise HTTPException(
            status_code=400, detail=f"Could not parse query: {q}")

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse query: {q}. Error: {str(e)}. Pattern matches: {pattern_debug_info}"
        )

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8080)
