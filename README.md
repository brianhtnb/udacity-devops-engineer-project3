# Coworking Space Service

A microservice-based application that enables users to request one-time tokens and administrators to authorize access to a coworking space. This repository contains the analytics service deployment configuration.

## Architecture

- **Backend**: Python Flask application
- **Database**: PostgreSQL
- **Container Registry**: Amazon ECR
- **Container Orchestration**: Amazon EKS (Kubernetes)
- **CI/CD**: AWS CodeBuild
- **Monitoring**: AWS CloudWatch Container Insights

## Deployment Process

1. **Container Build & Push**:
   - Docker image is built using `analytics/Dockerfile`
   - AWS CodeBuild automatically builds and pushes to ECR when code is updated

2. **Database Setup**:
   - PostgreSQL is deployed using Kubernetes configurations in `deployment/`
   - Persistent storage is configured using PV and PVC
   - Database schema and seed data are automatically initialized

3. **Application Deployment**:
   - Application is deployed to EKS using Kubernetes manifests
   - Environment variables are managed through ConfigMaps and Secrets
   - Health checks ensure application availability

## Resource Specifications

- **EKS Node Type**: t3.small (optimal balance of compute and memory)
- **Resource Limits**:
  - CPU: 200m
  - Memory: 256Mi

## Cost Optimization

- Single node EKS cluster with autoscaling (1-2 nodes)
- Spot instances can be used for non-production environments
- Resource limits prevent container overallocation

## Monitoring

Application health and performance are monitored through:
- Kubernetes liveness and readiness probes
- CloudWatch Container Insights
- EKS control plane logging

## Deployment Instructions

Detailed deployment steps are maintained in the project documentation. For new deployments:
1. Update application code
2. Push to repository
3. CodeBuild automatically builds and pushes new image
4. Apply Kubernetes configurations: `kubectl apply -f deployment/`