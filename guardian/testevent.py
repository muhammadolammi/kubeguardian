from datetime import datetime

test_event = {
    "type": "ADDED",
    "object": {
        "kind": "Pod",
        "api_version": "v1",
        "metadata": {
            "name": "coredns-test-pod",
            "namespace": "kube-system",
            "creation_timestamp": datetime.utcnow().isoformat() + "Z",
            "labels": {"k8s-app": "kube-dns"},
            "uid": "test-uid-1234"
        },
        "status": {
            "phase": "Running",
            "host_ip": "192.168.49.2",
            "pod_ip": "10.244.0.2",
            "container_statuses": [
                {
                    "name": "coredns",
                    "image": "registry.k8s.io/coredns/coredns:v1.12.0",
                    "ready": True,
                    "restart_count": 0
                }
            ]
        },
        "spec": {
            "node_name": "minikube",
            "containers": [
                {
                    "name": "coredns",
                    "image": "registry.k8s.io/coredns/coredns:v1.12.0",
                    "ports": [{"container_port": 53, "protocol": "UDP"}]
                }
            ]
        }
    }
}
