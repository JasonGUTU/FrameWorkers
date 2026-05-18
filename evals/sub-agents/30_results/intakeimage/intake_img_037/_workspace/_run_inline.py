import sys
sys.path.insert(0, "/home/zhendong_li/FrameWorkers/plan-stack-backend")
from src.app import create_app
app = create_app()
app.run(host='0.0.0.0', port=5106, debug=False, use_reloader=False)
