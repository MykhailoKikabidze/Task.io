import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from grpc_app.analytics_service import serve

if __name__ == "__main__":
    server = serve()
    print("Starting AnalyticsService on port 50054...")
    server.start()
    server.wait_for_termination()
