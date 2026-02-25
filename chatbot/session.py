history=[]
from langgraph.checkpoint.memory import InMemorySaver

def fetch_history(thread_id,user_id,db):
    
    response=(
        db.table("messages")
        .select("role","content")
        .eq("thread_id",thread_id)
        .eq("user_id",user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    
    for msg in response.data:
        history.append(f'{msg["role"]}: {msg["content"]}')
    
    
    
def get_history():
    return "\n".join(history[-10:])  # return last 10 messages

def add_history(role,content):
    history.append(f'{role}: {content}')

    
