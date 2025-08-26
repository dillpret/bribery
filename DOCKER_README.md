# Bribery Game Docker Image

This Docker image contains the multiplayer bribery game built with Flask-SocketIO.

## Usage

Pull the image:
```powershell
docker pull ghcr.io/dillpret/bribery:latest
```

Run the container:
```powershell
docker run -p 80:5000 --name bribery-game ghcr.io/dillpret/bribery:latest
```

The game will be available at http://localhost/ (or your server's IP address).

## Version
This image is automatically built from the repository's main branch using GitHub Actions.

## Source
[GitHub Repository](https://github.com/dillpret/bribery)
