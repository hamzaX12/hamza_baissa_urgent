# multi_agent_communication

# Multi-Agent Communication System

A Docker-based multi-agent communication system using ejabberd XMPP server.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

Follow these steps to set up and run the system:

### 1. Stop Old Containers

If you have previously run this project, stop and remove the old containers:
```bash
docker-compose down
```

### 2. Start the System

Build and start the containers:
```bash
docker-compose up --build
```

### 3. Register Agents

Open a new terminal window and register the agents with ejabberd:
```bash
docker-compose exec ejabberd ejabberdctl register agent1 localhost agent1pass
docker-compose exec ejabberd ejabberdctl register agent2 localhost agent2pass
```

## Project Structure

- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-container orchestration
- `agent.py` - Agent implementation
- `setup_server.py` - Server setup script
- `requirements.txt` - Python dependencies

## Usage

After completing the setup steps above, your agents will be registered and ready to communicate through the ejabberd XMPP server.

## Troubleshooting

If you encounter issues:

1. Ensure Docker and Docker Compose are properly installed
2. Check that no other services are using the required ports
3. Verify containers are running: `docker-compose ps`
4. Check logs: `docker-compose logs`

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
"# hamza_baissa_urgent" 
