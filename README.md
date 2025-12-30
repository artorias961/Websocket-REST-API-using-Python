
# Integrated REST and WebSocket Backend Using Python

## Abstract

This repository presents an academic reference implementation of a Python-based backend that integrates RESTful APIs with WebSocket-based real-time communication. The system demonstrates how stateless HTTP endpoints and persistent, bidirectional WebSocket connections can coexist within a unified architecture. The implementation is intended for instructional, research, and prototyping purposes, particularly in the context of distributed systems, Internet of Things (IoT), and real-time data applications.



## 1. Introduction
Modern backend systems frequently require support for both synchronous and asynchronous communication models. RESTful APIs are widely used for structured, stateless request–response interactions, while WebSockets enable low-latency, continuous data exchange.

This project provides a minimal yet complete backend that:
- Exposes REST endpoints for control and data access
- Maintains a WebSocket server for real-time updates
- Shares state between REST and WebSocket layers
- Broadcasts events across all connected clients



## 2. System Architecture
The backend consists of three interacting layers:

1. **REST API Layer**
   - Provides HTTP endpoints for system status, data ingestion, and control commands
   - Suitable for configuration, monitoring, and command-based interactions

2. **WebSocket Communication Layer**
   - Maintains persistent client connections
   - Broadcasts state changes and control events in real time

3. **Client / Device Simulations**
   - Demonstrate both REST-based and WebSocket-based interactions
   - Serve as stand-ins for IoT devices or distributed clients

All layers operate on a shared in-memory state managed by the server.



## 3. Repository Structure
```
Websocket-REST-API-using-Python/
│
├── main.py            # FastAPI server (REST + WebSocket)
├── device_one.py      # WebSocket-based device simulation
├── device_two.py      # REST-based device simulation
├── dashboard.html     # Browser-based WebSocket dashboard
├── requirements.txt  # Python dependencies
└── README.md
```



## 4. Installation and Execution

### 4.1 Prerequisites
- Python 3.8 or later
- pip package manager

### 4.2 Installation
```bash
git clone https://github.com/artorias961/Websocket-REST-API-using-Python.git
cd Websocket-REST-API-using-Python
pip install -r requirements.txt
```

### 4.3 Running the Server
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Once running, the server will be accessible at:
```
http://127.0.0.1:8000
```



## 5. REST API Interfaces

### 5.1 Interactive Documentation
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

These interfaces allow interactive exploration and testing of all REST endpoints.

### 5.2 Core Endpoints

#### GET `/api/status`
Returns live server health and connection information.

Example output:
```json
{
  "ok": true,
  "devices_known": 2,
  "websocket_clients_connected": 1,
  "timestamp_utc": "..."
}
```

#### GET `/api/data`
Returns the current shared system state for all known devices.

#### POST `/api/data`
Ingests device data via REST and broadcasts updates to WebSocket clients.

#### POST `/api/control`
Broadcasts control commands to all connected WebSocket clients.



## 6. WebSocket Interface

### Endpoint
```
ws://127.0.0.1:8000/ws
```

### Supported Message Types
- `telemetry` — sends device data to the server
- `ping` — health check
- `control` — broadcasts control commands
- `hello` — server-sent initialization message

WebSocket messages update shared state and are broadcast to all connected clients.



## 7. Client / Device Behavior

### device_one.py (WebSocket Client)
- Connects via WebSocket
- Sends periodic telemetry updates
- Receives real-time broadcasts

Observed effects:
- Updates appear in `/api/data`
- Events appear in the dashboard log
- WebSocket connection count increases

### device_two.py (REST Client)
- Sends structured data via REST
- Issues control commands

Observed effects:
- REST data appears in `/api/data`
- Control events broadcast to WebSocket clients



## 8. Web Dashboard
The `dashboard.html` file provides a browser-based interface for observing system behavior.

Features:
- Live WebSocket connection status
- Real-time event log
- Live device state table
- Manual message injection (telemetry, control, raw JSON)

The dashboard connects directly to the WebSocket endpoint.



## 9. Expected Runtime Behavior
When the server and clients are running simultaneously:
- `/api/status` reflects active WebSocket connections
- `/api/data` updates dynamically as devices send data
- The dashboard displays live broadcasts and state changes
- REST-originated events are propagated via WebSocket



## 10. Limitations
- In-memory state only (no persistence)
- No authentication or authorization
- Single-process, single-node deployment
- Intended for instructional use


## 11. Future Work
Potential extensions include:
- Persistent storage backend
- Authentication and authorization layers
- Frontend integration
- Horizontal scaling
- Message queue or pub-sub integration



## 12. Conclusion
This repository serves as an academic demonstration of integrating REST and WebSocket communication in Python. It provides a clear, observable example of real-time backend behavior suitable for coursework, research, and prototyping.

