# Kubeguardian: Autonomous Kubernetes Reliability Assistant

Kubeguardian is an autonomous Site Reliability Engineering (SRE) agent designed to monitor, analyze, and remediate issues inside Kubernetes clusters in real time. It integrates Google’s ADK (Agent Development Kit), MCP (Model Context Protocol), and kubectl-ai to reason over cluster events, enforce policies, and automate recovery actions.

This project was built for the GKE Hackathon.

## 🚀 Features

* 📡 Event Streaming: Publisher pod streams Kubernetes events (Pods, Deployments, Services, etc.) into RabbitMQ.
* 🔄 Automated Remediation: Subscriber pod consumes events and forwards them to the Remediator Agent for corrective actions.
* 💬 Interactive Chat Agent: Frontend UI lets users chat with a Chat Agent that can execute cluster commands and remediation requests.
* 🧠 MCP Integration: Uses a custom MCP server to expose Kubernetes and custom tools.
* 🗑️ User Management: PostgreSQL stores user sessions and data.
* ⚡ Built with GKE, ADK, MCP, RabbitMQ, PostgreSQL.

## 🍷 Service Architecture

| Service          | Language | Description                                                                  |
| ---------------- | -------- | ---------------------------------------------------------------------------- |
| Frontend         | React    | Web UI for users to chat with the Chat Agent and view alerts.                |
| Chat Agent       | Python   | Exposes HTTP API for handling user requests and cluster actions.             |
| Remediator Agent | Python   | Background agent that consumes events and remediates issues.                 |
| Publisher        | Python   | Watches Kubernetes events and publishes them into RabbitMQ.                  |
| Subscriber       | Python   | Consumes events from RabbitMQ and forwards to the Remediator Agent.          |
| MCP Server       | Python   | Exposes custom tools via the Model Context Protocol (MCP).                   |
| kubectl-ai       | Python   | MCP server exposing kubectl functions for cluster operations.                |
| PostgreSQL       | SQL      | Stores user accounts and session data.                                       |
| RabbitMQ         | Broker   | Message queue for event-driven communication between Publisher & Subscriber. |

## ⚡ Quickstart (Kubernetes)

### Prerequisites

* Google Cloud Project
* A Kubernetes cluster (e.g. GKE Autopilot)
* `kubectl` configured to talk to your cluster

### Deployment

1. Ensure you have the following requirements:
   - [Google Cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project).
   - Shell environment with `gcloud`, `git`, and `kubectl`.

2. Clone the repository.

   ```sh
   git clone https://github.com/muhammadolammi/kubeguardian
   cd bank-of-anthos/
   ```

3. Set the Google Cloud project and region and ensure the Google Kubernetes Engine API is enabled.

   ```sh
   export PROJECT_ID=<PROJECT_ID>
   export REGION=us-central1
   gcloud services enable container.googleapis.com \
     --project=${PROJECT_ID}
   ```

   Substitute `<PROJECT_ID>` with the ID of your Google Cloud project.

4. Create a GKE cluster and get the credentials for it.

   ```sh
   gcloud container clusters create-auto bank-of-anthos \
     --project=${PROJECT_ID} --region=${REGION}
   ```
       Creating the cluster may take a few minutes.


5. Deploy the manifests

```sh
kubectl apply -f kubernetes-manifests/
kubectl apply -f ./apps/bank-of-anthos/extras/jwt/jwt-secret.yaml
kubectl apply -f ./apps/bank-of-anthos/kubernetes-manifests

```

6. Wait for pods to be ready

```sh
kubectl get pods

```

7. Access the frontends

```sh
kubectl get ingress frontend-ingress (kubeguardian)
kubectl get service frontend -n bank-of-anthos | awk '{print $4}' (bank-of-anthos)

```

Visit the external IP/URL in your browser.

## 📊 Technologies Used

* **Google Kubernetes Engine (GKE)** – for orchestration
* **Google ADK (Agent Development Kit)** – for building autonomous agents
* **MCP (Model Context Protocol)** – for tool exposure & agent reasoning
* **kubectl-ai** – MCP server exposing Kubernetes control functions
* **RabbitMQ** – event queue for publisher → subscriber → remediator
* **PostgreSQL** – database for sessions and persistence
* **React** – frontend UI for user interaction

## 🎥 Demo

A \~3-minute demo video showcases:

1. Deploying Kubeguardian on GKE
2. Triggering a simulated issue → automated remediation by the Remediator Agent
3. Chatting with the Chat Agent to take manual actions

👉 [Demo Video Link](https://youtu.be/gdVGPySZXkE)

## 📚 Learnings & Findings

* Learned how to integrate ADK + MCP into Kubernetes-native workflows.
* Debugged GKE networking, ingress, and RabbitMQ connectivity.
* Designed a hybrid autonomous + human-in-the-loop system for reliability.
* Gained experience deploying multi-agent systems on Kubernetes.

## 🔗 Resources

* [GKE Docs](https://cloud.google.com/kubernetes-engine/docs)
* [ADK Overview](https://cloud.google.com/agent-development-kit)
* [Model Context Protocol](https://modelcontextprotocol.io)
