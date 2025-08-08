# Azure IoT Edge Data Pipeline (Replicable Guide)

Minimal, reproducible setup for an Edge → IoT Hub → Event Hub data flow using:
- IoT Edge module (simulated sensor in Docker)
- Ubuntu Core VM running Azure IoT Edge (snap)
- Event Hub consumer (Python)

## 1. Repository Structure

```
.
├─ iot-device/          # Edge module (simulated temperature device)
│  ├─ Dockerfile
│  └─ main.py
├─ event-consumer/      # Local/Event Hub consumer
│  └─ main.py
└─ requirements.txt
```

## 2. Prerequisites

- Azure subscription (free)
- Docker installed locally
- Python 3.8+
- An SSH key (for Ubuntu Core login association)
- Basic familiarity with Azure Portal blades:
  - Container Registry (ACR)
  - IoT Hub (IoT Edge devices)
  - Event Hubs

## 3. Create Azure Resources (Portal)

In Azure Portal (no CLI):

1. Create Container Registry (ACR)
2. Create IoT Hub

## 4. Build & Push Edge Module Image

```bash
# From repo root
docker build -t temperature-sensor:latest ./iot-device
```

Tag for your Azure Container Registry (ACR):

```bash
# Replace registry + optional version tag
docker tag temperature-sensor:latest YOUR_REGISTRY.azurecr.io/temperature-sensor:latest
```

Login & push (Portal-created ACR — use admin user/pass from ACR Access Keys):

```bash
docker login YOUR_REGISTRY.azurecr.io
docker push YOUR_REGISTRY.azurecr.io/temperature-sensor:latest
```

## 5. Create IoT Edge Device (Portal)

In IoT Hub → IoT Edge → “Add IoT Edge device”
- Authentication: Symmetric key
- Save Primary Connection String (used in `config.toml` AND module env var)

## 6. Set Up Ubuntu Core VM (for IoT Edge Runtime)

Inside your hypervisor:
1. Download Ubuntu Desktop ISO (only to boot a live session)
2. Boot VM with ISO, choose “Try Ubuntu” (don’t install)
3. In Firefox go to:
   ```
   https://cdimage.ubuntu.com/ubuntu-core/24/stable/current/
   ```
   Download `ubuntu-core-24-amd64.img.xz`
4. Open terminal:
   ```bash
   sudo -i
   fdisk -l          # Identify main disk (e.g., /dev/sda)
   cd /home/ubuntu/Downloads/
   xzcat ubuntu-core-24-amd64.img.xz | dd of=/dev/sda bs=32M status=progress; sync
   ```
5. Reboot VM → boots into Ubuntu Core
6. Attach (or create) Ubuntu One account & add your SSH key there
7. On Ubuntu Core, log in using your Ubuntu One account.
8. From your host you can now:
   ```bash
   ssh ubuntu@VM_IP
   ```

## 7. Install & Provision Azure IoT Edge (Symmetric Key)

On Ubuntu Core (via SSH):

```bash
sudo snap install docker
sudo snap install azure-iot-identity
sudo snap install azure-iot-edge
```

Connect required interfaces (exact sequence):

```bash
# Identity Service
sudo snap connect azure-iot-identity:log-observe
sudo snap connect azure-iot-identity:mount-observe
sudo snap connect azure-iot-identity:system-observe
sudo snap connect azure-iot-identity:hostname-control
sudo snap connect azure-iot-identity:tpm || true  # Only if TPM present

# IoT Edge
sudo snap connect azure-iot-edge:home
sudo snap connect azure-iot-edge:log-observe
sudo snap connect azure-iot-edge:mount-observe
sudo snap connect azure-iot-edge:system-observe
sudo snap connect azure-iot-edge:hostname-control
sudo snap connect azure-iot-edge:run-iotedge
sudo snap connect azure-iot-edge:docker docker:docker-daemon
```

Create provisioning file:

```bash
nano ~/config.toml
```

Content (replace placeholder with device primary connection string from IoT Hub):

```toml
[provisioning]
source = "manual"
connection_string = "REPLACE_WITH_DEVICE_CONNECTION_STRING"
```

Apply:

```bash
sudo snap set azure-iot-edge raw-config="$(cat ~/config.toml)"
```

Health check:

```bash
sudo iotedge check
```

## 8. Configure Module Deployment (Portal)

In IoT Hub → IoT Edge → Select Device → “Set modules”:
1. Add container registry credentials (ACR login server, username, password)
2. Add new module:
   - Image URI: `YOUR_REGISTRY.azurecr.io/temperature-sensor:latest`
   - Environment variables:
     - `IOT_HUB_CONNECTION_STRING` = (device primary connection string)  
3. Review + Create deployment

## 9. Verify on the Device

SSH into device:

```bash
sudo iotedge list
```

You should see the module in “running” state after pull.

Logs (replace with module name if different):

```bash
sudo iotedge logs temperature-sensor -f
```

## 10. Event Hub Consumer (Local)

Create `.env` inside `event-consumer/`:

```
EVENTHUB_CONNECTION_STRING="Endpoint=sb://..."
EVENTHUB_NAME="iothub-..."
```

Install & run:

```bash
cd event-consumer
pip install -r requirements.txt
python main.py
```