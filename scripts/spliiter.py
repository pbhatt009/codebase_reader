from langchain_text_splitters import RecursiveCharacterTextSplitter

python_separators = [
    "\nclass ",
    "\ndef ",
    "\n\n",
    "\n",
    " "
]

js_ts_separators = [
    "\nclass ",
    "\nfunction ",
    "\nconst ",
    "\nlet ",
    "\nvar ",
    "\n\n",
    "\n",
    " "
]

java_separators = [
    "\nclass ",
    "\ninterface ",
    "\nenum ",
    "\npublic ",
    "\nprotected ",
    "\nprivate ",
    "\n\n",
    "\n",
    " "
]

cpp_separators = [
    "\nclass ",
    "\nstruct ",
    "\nnamespace ",
    "\nvoid ",
    "\nint ",
    "\nfloat ",
    "\ndouble ",
    "\n\n",
    "\n",
    " "
]

go_separators = [
    "\nfunc ",
    "\ntype ",
    "\nstruct ",
    "\ninterface ",
    "\n\n",
    "\n",
    " "
]

rust_separators = [
    "\nimpl ",
    "\nfn ",
    "\nstruct ",
    "\nenum ",
    "\ntrait ",
    "\n\n",
    "\n",
    " "
]
json_separators = [
    "\n",
    " ",
    ",",
    ":",
    "{",
    "}",
    "[",
    "]"
]


default_separators = [
    "\n\n",
    "\n",
    " "
]


def get_separators(ext):
    mapping = {
        "py": python_separators,
        "js": js_ts_separators,
        "ts": js_ts_separators,
        "java": java_separators,
        "cpp": cpp_separators,
        "c": cpp_separators,
        "go": go_separators,
        "rs": rust_separators,
        "json": json_separators,
        "other": default_separators
       
    }
    if(ext in mapping):
        return mapping[ext]
    else:
        return mapping["other"]
    

def splitter(docs):
    chunks_list = []
    for doc in docs:
        """Get the file extension from the document metadata."""
        ext=doc.metadata['source'].split(".")[-1]
        separators=get_separators(ext)
        text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=1000,
            chunk_overlap=100,
        )
        chunks = text_splitter.split_documents([doc])
        chunks_list.extend(chunks)
    return chunks_list
