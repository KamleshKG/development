
import json
from pathlib import Path
from typing import Dict, Any

REQUIRED_Q_FIELDS = {"question_id","level","question","options","correct_options","is_multi_select"}
REQUIRED_T_FIELDS = {"code","title","description","level","points","require_attachment"}

def load_questions_json(path: str) -> Dict[str, Any]:
    data = json.loads(Path(path).read_text())
    assert "plugin" in data and "questions" in data, "Invalid questions.json"
    for q in data["questions"]:
        missing = REQUIRED_Q_FIELDS - set(q.keys())
        if missing:
            raise ValueError(f"Question missing fields: {missing}")
    return data

def load_tasks_json(path: str) -> Dict[str, Any]:
    data = json.loads(Path(path).read_text())
    assert "plugin" in data and "tasks" in data, "Invalid tasks.json"
    for t in data["tasks"]:
        missing = REQUIRED_T_FIELDS - set(t.keys())
        if missing:
            raise ValueError(f"Task missing fields: {missing}")
    return data

def scan_plugins(plugins_dir: str = "plugins"):
    pd = Path(plugins_dir)
    for plug in pd.iterdir():
        if not plug.is_dir():
            continue
        qf = plug / "questions.json"
        tf = plug / "tasks.json"
        yield {"code": plug.name, "questions_path": str(qf) if qf.exists() else None, "tasks_path": str(tf) if tf.exists() else None}
