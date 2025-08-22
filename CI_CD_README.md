# 🚀 CI/CD Pipeline with GitHub Container Registry

This project now includes automated CI/CD pipelines that build Docker images and publish them to GitHub Container Registry (GHCR).

## 🎯 What This Gives You

### **Before (Local Builds):**
- Copy source code to target host
- Build Docker images on target host
- Slow deployments, potential build failures
- Inconsistent environments

### **After (Registry Deployments):**
- Pre-built, tested images
- Fast `docker pull` deployments
- Consistent environments everywhere
- Version control and rollbacks
- Professional CI/CD pipeline

## 📋 Setup Requirements

### **1. Repository Settings**
- **Public repository** (recommended for free GHCR)
- **GitHub Actions enabled**
- **Packages permissions** for Actions

### **2. Secrets (Optional)**
If using private images, add these secrets:
```bash
# In GitHub repository settings > Secrets and variables > Actions
GHCR_TOKEN=your_github_personal_access_token
```

## 🔄 How the CI/CD Works

### **Automatic Triggers:**
- **Push to main/develop** → Build and publish images
- **Pull requests** → Build images for testing
- **Releases** → Build and tag release images

### **Image Naming:**
```
ghcr.io/your-username/sleeper-bot-mcp-server:latest
ghcr.io/your-username/sleeper-bot-llm-agent:latest
ghcr.io/your-username/sleeper-bot-discord-bot:latest
```

### **Available Tags:**
- `latest` - Latest main branch
- `develop` - Latest develop branch
- `main-abc123` - Specific commit on main
- `develop-def456` - Specific commit on develop

## 🚀 Deployment Options

### **Option 1: Registry Deployment (Recommended)**
```bash
# Deploy using pre-built images
ansible-playbook -i ansible/inventory.yml ansible/deploy-registry.yml \
  -e "github_repository=your-username/sleeper-bot" \
  -e "image_tag=latest"
```

### **Option 2: Local Build Deployment**
```bash
# Deploy by building locally (original method)
ansible-playbook -i ansible/inventory.yml ansible/deploy.yml
```

## 📁 New Files Created

### **GitHub Actions Workflows:**
- `.github/workflows/build-mcp-server.yml`
- `.github/workflows/build-llm-agent.yml`
- `.github/workflows/build-discord-bot.yml`

### **Registry Docker Compose:**
- `docker-compose.registry.yml` - Pulls from GHCR

### **Registry Ansible Playbook:**
- `ansible/deploy-registry.yml` - Deploys from registry

## 🔧 Configuration

### **Environment Variables:**
```bash
# Required for registry deployment
GITHUB_REPOSITORY=your-username/sleeper-bot
IMAGE_TAG=latest

# Your existing variables
API_KEY=your-secure-api-key
DISCORD_TOKEN=your-discord-token
DEFAULT_LEAGUE_ID=your-league-id
LLM_PROVIDER=ollama
LLM_URL=http://host.docker.internal:11434/api/generate
LLM_MODEL=llama3.2:latest
```

### **Ansible Variables:**
```yaml
# In ansible/group_vars/sleeper_bot_hosts.yml
github_repository: "your-username/sleeper-bot"
image_tag: "latest"
```

## 🚀 Quick Start

### **1. First Time Setup:**
```bash
# Push your code to trigger first build
git add .
git commit -m "Add CI/CD pipeline"
git push origin main

# Wait for GitHub Actions to complete
# Check Actions tab in your repository
```

### **2. Deploy to Production:**
```bash
# Deploy using registry images
ansible-playbook -i ansible/inventory.yml ansible/deploy-registry.yml
```

### **3. Update and Redeploy:**
```bash
# Make code changes
git add .
git commit -m "Fix bot response handling"
git push origin main

# Wait for new images to build
# Deploy with new images
ansible-playbook -i ansible/inventory.yml ansible/deploy-registry.yml
```

## 📊 Monitoring and Management

### **Check Build Status:**
- GitHub repository → Actions tab
- Monitor build progress and logs

### **View Published Images:**
- GitHub repository → Packages tab
- See all published container images

### **Service Management:**
```bash
# On target host
cd /opt/sleeper-bot

# Check status
docker compose ps

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Update to latest images
docker compose pull
docker compose up -d
```

## 🔄 Rollback Strategy

### **Rollback to Previous Version:**
```bash
# Deploy specific tag
ansible-playbook -i ansible/inventory.yml ansible/deploy-registry.yml \
  -e "image_tag=main-abc123"

# Or rollback on host
cd /opt/sleeper-bot
docker compose pull ghcr.io/your-username/sleeper-bot-mcp-server:main-abc123
docker compose up -d
```

## 💰 Cost Analysis

### **GitHub Container Registry:**
- **Public repos**: 100% FREE
- **Private repos**: 500MB free, then $0.50/GB

### **GitHub Actions:**
- **Public repos**: 2,000 minutes/month FREE
- **Private repos**: 2,000 minutes/month FREE
- **Additional**: $0.008/minute

### **Estimated Monthly Cost:**
- **Small project**: $0-5/month
- **Medium project**: $5-20/month
- **Large project**: $20+/month

## 🚨 Troubleshooting

### **Build Failures:**
```bash
# Check GitHub Actions logs
# Verify Dockerfile syntax
# Check for dependency issues
```

### **Deployment Issues:**
```bash
# Verify image names in registry
# Check network connectivity
# Validate environment variables
```

### **Common Issues:**
1. **Permission denied**: Check repository permissions
2. **Image not found**: Verify image names and tags
3. **Build timeout**: Check Dockerfile optimization
4. **Registry auth**: Verify GHCR access

## 🎉 Benefits Summary

✅ **Faster deployments** - No more building on target hosts  
✅ **Consistent environments** - Same images everywhere  
✅ **Version control** - Tagged releases and rollbacks  
✅ **Professional CI/CD** - Automated testing and building  
✅ **Cost effective** - Free for public repos  
✅ **Scalable** - Easy to deploy to multiple hosts  
✅ **Reliable** - Pre-tested, pre-built images  

## 🔮 Next Steps

1. **Push code** to trigger first builds
2. **Test deployment** with registry images
3. **Set up monitoring** for build status
4. **Configure alerts** for build failures
5. **Add testing** to CI/CD pipeline
6. **Implement staging** environment

This CI/CD setup transforms your deployment from a manual, error-prone process to a professional, automated pipeline that's fast, reliable, and scalable!
