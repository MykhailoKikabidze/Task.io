import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from grpc_app.task_service import serve

if __name__ == "__main__":
    server = serve()
    print("Starting TaskService on port 50053...")
    server.start()
    server.wait_for_termination()
