from clients.grpc.pm_grpc import PmGrpcClient
from websockets.manager import manager as ws_manager


async def notify_project_participants(
    project_id: str,
    event_type: str,
    payload: dict
):
    client = PmGrpcClient()
    users_resp = client.get_project_users(project_id)
    user_ids = [u.user_id for u in users_resp.users]
    event = {"type": event_type, "project_id": project_id, **payload}
    for uid in user_ids:
        await ws_manager.send_personal_json(uid, event)


async def notify_project_user_changes(
    project_id: str,
    old_users: list[str],
    new_users: list[str],
):
    old_set = set(old_users)
    new_set = set(new_users)

    added = new_set - old_set
    removed = old_set - new_set

    for uid in added:
        await ws_manager.send_personal_json(uid, {
            "type": "project_user_added",
            "project_id": project_id,
            "user_id": uid
        })

    for uid in removed:
        await ws_manager.send_personal_json(uid, {
            "type": "project_user_removed",
            "project_id": project_id,
            "user_id": uid
        })


async def notify_sprint_event(event_type: str, sprint) -> None:
    await notify_project_participants(
        project_id=sprint.project_id,
        event_type=event_type,
        payload={
            "sprint": {
                "id": sprint.id,
                "name": sprint.name,
                "description": getattr(sprint, "description", None),
                "start_date": sprint.start_date,
                "end_date": sprint.end_date,
                "is_started": sprint.is_started,
            }
        },
    )


async def notify_epic_event(event_type: str, epic) -> None:
    await notify_project_participants(
        project_id=epic.project_id,
        event_type=event_type,
        payload={
            "epic": {
                "id": epic.id,
                "name": epic.name,
                "description": getattr(epic, "description", None),
                "priority": epic.priority,
                "start_date": epic.start_date,
                "end_date": epic.end_date,
            }
        },
    )


async def notify_task_event(event_type: str, task) -> None:
    project_id = getattr(task, "project_id", None)
    if not project_id:
        return

    client = PmGrpcClient()
    users_resp = client.get_project_users(project_id)
    user_ids = [u.user_id for u in users_resp.users]

    payload = {
        "type": event_type,
        "project_id": project_id,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "type": task.type,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "epic_id": task.epic_id,
            "sprint_id": task.sprint_id,
            "start_date": task.start_date,
            "end_date": task.end_date,
        },
    }
    for uid in user_ids:
        await ws_manager.send_personal_json(uid, payload)
