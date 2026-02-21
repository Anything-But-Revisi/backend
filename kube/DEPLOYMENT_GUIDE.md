# SafeSpace Backend - Kubernetes Deployment Guide

## Prerequisites

- `kubectl` CLI installed dan configured ke target Kubernetes cluster
- Docker installed (untuk build dan push image)
- Access to Docker registry (e.g., Docker Hub, ECR, GCR)
- Kubernetes cluster minimal v1.19+
- TLS certificate untuk domain `anything-but-revisi.hackathon.sev-2.com`

## Infrastructure Details

- **Kubernetes Namespace**: `anything-but-revisi`
- **PostgreSQL Host**: `103.185.52.138:1185`
- **Database**: `anything_but_revisi`
- **Domain**: `https://anything-but-revisi.hackathon.sev-2.com`
- **Resource Limits**: 256Mi RAM, 0.5 CPU per pod
- **Service Port**: 80 (external) → 8000 (container)

## Step 1: Build and Push Docker Image

```bash
# Build Docker image
docker build -t <your-registry>/safespace-backend:latest .

# Login to registry (if not already logged in)
docker login

# Push image to registry
docker push <your-registry>/safespace-backend:latest

# Verify image is accessible
docker pull <your-registry>/safespace-backend:latest
```

Replace `<your-registry>` dengan Docker Hub username atau private registry URL.

## Step 2: Create Kubernetes Namespace

```bash
# Create namespace
kubectl create namespace anything-but-revisi

# Verify namespace
kubectl get namespaces | grep anything-but-revisi
```

## Step 3: Create TLS Secret (if not already created)

Assume TLS certificate file tersedia (cert.crt dan key.key):

```bash
# Create TLS secret
kubectl create secret tls safespace-tls \
  --cert=path/to/cert.crt \
  --key=path/to/key.key \
  --namespace=anything-but-revisi

# Verify secret
kubectl get secrets -n anything-but-revisi
```

Atau jika menggunakan cert-manager, ciptakan Certificate resource.

## Step 4: Apply Kubernetes Manifests

```bash
# Apply ConfigMap
kubectl apply -f kube/configmap.yaml

# Apply Secret
# PENTING: Update GOOGLE_API_KEY value sesuai actual key
# Edit kube/secret.yaml dan ganti base64 encoded value
kubectl apply -f kube/secret.yaml

# Apply Deployment
# PENTING: Update image path di kube/deployment.yaml
# Ganti 'your-dockerhub-user/safespace-backend:latest' dengan actual registry path
kubectl apply -f kube/deployment.yaml

# Apply Service
kubectl apply -f kube/service.yaml

# Apply Ingress
kubectl apply -f kube/ingress.yaml

# Verify semua resources
kubectl get all -n anything-but-revisi
```

## Step 5: Verify Deployment

```bash
# Check pod status
kubectl get pods -n anything-but-revisi

# Check pod details (jika status bukan Running)
kubectl describe pod <pod-name> -n anything-but-revisi

# Check deployment status
kubectl rollout status deployment/safespace-backend -n anything-but-revisi

# View pod logs
kubectl logs deployment/safespace-backend -n anything-but-revisi

# Follow logs in real-time
kubectl logs -f deployment/safespace-backend -n anything-but-revisi
```

## Step 6: Verify Health Checks

```bash
# Port forward to pod untuk test local
kubectl port-forward svc/safespace-backend 8000:80 -n anything-but-revisi

# Test health endpoint dalam terminal lain
curl http://localhost:8000/health/db

# Jika response adalah JSON dengan "status": "healthy", deployment successful!
```

## Step 7: Verify External Access

```bash
# Tunggu Ingress IP/hostname ter-allocate
kubectl get ingress -n anything-but-revisi

# Test HTTPS access (ganti dengan actual domain)
curl https://anything-but-revisi.hackathon.sev-2.com/health/db

# Test API endpoints
curl -X POST https://anything-but-revisi.hackathon.sev-2.com/api/v1/sessions

# Verify database connectivity (lihat logs untuk error)
kubectl logs deployment/safespace-backend -n anything-but-revisi | grep -i database
```

## Troubleshooting

### Pods tidak bisa start (ImagePullBackOff)
- Verify Docker image push ke registry: `docker push <registry>/safespace-backend:latest`
- Check image path di deployment.yaml
- Verify pull secret jika menggunakan private registry

### Pod jalan tapi health check fail
- Check logs: `kubectl logs <pod-name> -n anything-but-revisi`
- Verify environment variables: `kubectl exec -it <pod-name> -n anything-but-revisi -- env | grep DB`
- Verify database connectivity dari cluster: `kubectl exec -it <pod-name> -n anything-but-revisi -- curl http://localhost:8000/health/db`

### Ingress tidak bisa diakses
- Verify Ingress created: `kubectl get ingress -n anything-but-revisi`
- Check Ingress controller running: `kubectl get pods -n ingress-nginx`
- Verify DNS records point ke Ingress IP
- Check TLS certificate: `kubectl get secrets -n anything-but-revisi`

### Database connection error
- Verify DB_HOST accessible dari cluster
- Check port 1185 terbuka: `kubectl exec -it <pod-name> -n anything-but-revisi -- nc -zv 103.185.52.138 1185`
- Verify credentials di Secret

## Scaling

```bash
# Scale ke 3 replicas
kubectl scale deployment/safespace-backend --replicas=3 -n anything-but-revisi

# Check status
kubectl get pods -n anything-but-revisi
```

## Updating Image

```bash
# Update image tag
kubectl set image deployment/safespace-backend \
  safespace-backend=<your-registry>/safespace-backend:v1.0 \
  -n anything-but-revisi

# Check rollout status
kubectl rollout status deployment/safespace-backend -n anything-but-revisi

# Rollback jika ada issue
kubectl rollout undo deployment/safespace-backend -n anything-but-revisi
```

## Useful Commands

```bash
# Get all resources in namespace
kubectl get all -n anything-but-revisi

# Describe specific resource
kubectl describe deployment/safespace-backend -n anything-but-revisi

# Delete entire namespace (WARNING: menghapus semua resources!)
kubectl delete namespace anything-but-revisi

# SSH into pod
kubectl exec -it <pod-name> -n anything-but-revisi -- /bin/bash

# Stream logs dari semua pods
kubectl logs -f deployment/safespace-backend --all-containers=true -n anything-but-revisi
```

## Next Steps

1. Monitor aplikasi menggunakan Kubernetes dashboard atau kubectl
2. Setup monitoring/alerting (Prometheus, Grafana, dll)
3. Setup CI/CD untuk auto-deploy pada push ke repository
4. Document any custom configurations atau troubleshooting
