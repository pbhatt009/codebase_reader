def add_utils(data_b,model):
    global hf,db
    hf=model
    db=data_b
    
def get_utils():
    return (hf,db)