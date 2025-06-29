"""
 Author: Ahmad Alhourani
 GitHub: https://github.com/AhmadAlhourani19
 Date Created: 23.06.2025
 Unauthorized copying or reproduction is strictly prohibited.
"""

"""
Standalone launcher for FastAPI backend – safe for PyInstaller/Tauri.
"""

import sys
from pathlib import Path
import copy
import uvicorn

here = Path(__file__).resolve()
project_root = here.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from Backend.restAPIBackend import app as fastapi_app

from uvicorn.config import LOGGING_CONFIG as BASE_LOG

log_cfg = copy.deepcopy(BASE_LOG)
log_cfg["formatters"]["default"]["use_colors"] = False
log_cfg["handlers"]["default"]["stream"] = "ext://sys.stdout"

log_cfg["formatters"].pop("access", None)
log_cfg["handlers"].pop("access", None)
log_cfg["loggers"]["uvicorn.access"] = {"handlers": [], "level": "INFO"}

def main() -> None:
    print("Launching backend...")

    uvicorn.run(
        fastapi_app,
        host="127.0.0.1",
        port=8000,
        log_config=log_cfg,
        workers=1,
    )

if __name__ == "__main__":
    main()