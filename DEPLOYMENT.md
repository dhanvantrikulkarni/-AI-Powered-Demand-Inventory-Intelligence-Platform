# Deployment Guide - Project FORESIGHT

## Local Docker Deployment

### Prerequisites
- Docker installed on your system
- Docker Compose installed
- At least 4GB RAM available for Docker

### Quick Start

1. **Build and start all services:**
```bash
docker compose up --build
```

2. **Access the applications:**
- **Streamlit Dashboard**: http://localhost:8501
- **FastAPI Service**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Individual Service Control

**Start only the Streamlit Dashboard:**
```bash
docker compose up streamlit-dashboard
```

**Start only the FastAPI Service:**
```bash
docker compose up fastapi-service
```

**Stop all services:**
```bash
docker compose down
```

**Stop and remove volumes:**
```bash
docker compose down -v
```

## Cloud Deployment Options

### Option 1: Render (Recommended for Easy Deployment)

**Deploy Streamlit Dashboard:**
1. Create a Render account at https://render.com
2. Create a new Web Service
3. Connect your GitHub repository
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=$PORT`
   - **Runtime**: Python 3.11

**Deploy FastAPI Service:**
1. Create another Web Service
2. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn service.api:app --host 0.0.0.0 --port=$PORT`
   - **Runtime**: Python 3.11

### Option 2: Railway

1. Create a Railway account at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Railway will auto-detect Python and deploy
4. Access your application via the provided Railway URL

### Option 3: Heroku

**Create Procfile:**
```
web: streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=$PORT
```

**Deploy:**
```bash
heroku create your-app-name
git push heroku main
```

### Option 4: AWS/Azure/GCP

For production deployments on major cloud providers, consider:

**AWS:**
- Use ECS (Elastic Container Service) with Docker Compose
- Or use AWS App Runner for container deployment
- Configure load balancer and domain

**Azure:**
- Use Azure Container Instances
- Or Azure Kubernetes Service (AKS)
- Configure Azure Front Door for CDN

**Google Cloud:**
- Use Cloud Run for container deployment
- Or Google Kubernetes Engine (GKE)
- Configure Cloud Load Balancing

## Environment Variables

Create a `.env` file for configuration:

```env
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Model Configuration
DEFAULT_MODEL=random_forest
STOCKOUT_THRESHOLD=0.8
OVERSTOCK_THRESHOLD=1.5
```

## Data Management

**For cloud deployments, you'll need to:**
1. Use cloud storage (S3, Azure Blob, GCS) instead of local `data/` directory
2. Update the data pipeline to read from cloud storage
3. Configure environment variables for cloud credentials

## Monitoring and Logging

**Add monitoring for production:**
- Streamlit: Built-in metrics at `/_stcore/health`
- FastAPI: Use `/health` endpoint
- Consider adding Sentry for error tracking
- Use cloud provider monitoring tools

## Security Considerations

**For production deployment:**
1. Add authentication to the API
2. Use HTTPS/SSL certificates
3. Implement rate limiting
4. Add API keys for sensitive operations
5. Configure CORS properly
6. Use environment variables for secrets
7. Regular security updates

## Scaling

**Horizontal scaling:**
- Use load balancer with multiple container instances
- Configure database connection pooling
- Use Redis for caching if needed

**Vertical scaling:**
- Increase container memory/CPU limits
- Optimize model inference time
- Use batch processing for forecasts

## Troubleshooting

**Container won't start:**
```bash
docker compose logs
```

**Port conflicts:**
- Change ports in docker-compose.yml
- Or stop conflicting services

**Memory issues:**
- Increase Docker memory limit
- Optimize data processing
- Use streaming for large datasets

## Cost Estimates

**Cloud deployment costs (monthly estimates):**
- Render: Free tier available, paid plans from $7/month
- Railway: $5/month for basic plan
- Heroku: $5-7/month for basic dyno
- AWS: $20-50/month for small ECS deployment
- Azure: Similar to AWS
- GCP: Similar to AWS

## Support

For deployment issues:
1. Check container logs: `docker-compose logs`
2. Verify data files are present
3. Check environment variables
4. Review cloud provider documentation
