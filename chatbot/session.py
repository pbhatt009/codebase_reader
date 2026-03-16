import time
import threading

history_store = {}
session_last_active = {}

SESSION_TIMEOUT = 600   # 10 minutes
CLEANUP_INTERVAL = 300  # 5 minutes


def fetch_history(thread_id, user_id, db):
    if user_id in history_store and thread_id  in history_store[user_id]:
      return 
    """Fetch last messages from DB and store them in memory."""

    response = (
        db.table("messages")
        .select("role", "content")
        .eq("thread_id", thread_id)
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )

    if user_id not in history_store:
        history_store[user_id] = {}

    if thread_id not in history_store[user_id]:
        history_store[user_id][thread_id] = []

    for msg in reversed(response.data):
        history_store[user_id][thread_id].append(
            f'{msg["role"]}: {msg["content"]}'
        )

    update_activity(user_id, thread_id)


def get_history(user_id, thread_id):
    """Return last 10 messages of a user thread."""

    if user_id not in history_store:
        return ""

    if thread_id not in history_store[user_id]:
        return ""

    update_activity(user_id, thread_id)

    history = history_store[user_id][thread_id]
    return "\n".join(history[-10:])


def add_history(user_id, thread_id, role, content):
    """Add a new message to history."""

    if user_id not in history_store:
        history_store[user_id] = {}

    if thread_id not in history_store[user_id]:
        history_store[user_id][thread_id] = []

    history_store[user_id][thread_id].append(f"{role}: {content}")

    update_activity(user_id, thread_id)


def clear_history(user_id, thread_id):
    """Clear history of a specific thread."""

    if user_id in history_store and thread_id in history_store[user_id]:
        history_store[user_id][thread_id] = []

    if user_id in session_last_active and thread_id in session_last_active[user_id]:
        del session_last_active[user_id][thread_id]


def update_activity(user_id, thread_id):
    """Update last activity time."""

    if user_id not in session_last_active:
        session_last_active[user_id] = {}

    session_last_active[user_id][thread_id] = time.time()


def cleanup_sessions():
    """Remove sessions inactive for more than SESSION_TIMEOUT."""

    while True:
        time.sleep(CLEANUP_INTERVAL)
        current_time = time.time()

        for user_id in list(session_last_active.keys()):
            for thread_id in list(session_last_active[user_id].keys()):

                last_active = session_last_active[user_id][thread_id]

                if current_time - last_active > SESSION_TIMEOUT:
                    print(f"Session expired for user {user_id}, thread {thread_id}")

                    if user_id in history_store and thread_id in history_store[user_id]:
                        del history_store[user_id][thread_id]

                    del session_last_active[user_id][thread_id]

            if not session_last_active[user_id]:
                del session_last_active[user_id]


# start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_sessions, daemon=True)
cleanup_thread.start()