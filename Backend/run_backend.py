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

import sounddevice as sd

def main() -> None:
    try:
        print("Available audio devices at backend launch:")
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            print(f"  [{i}] {d['name']} (inputs: {d['max_input_channels']}, outputs: {d['max_output_channels']})")
    except Exception as e:
        print(f"Failed to list audio devices: {e}")

    uvicorn.run(
        fastapi_app,
        host="127.0.0.1",
        port=8000,
        log_config=log_cfg,
        workers=1,
    )

if __name__ == "__main__":
    main()