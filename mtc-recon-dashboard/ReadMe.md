# Create the ECR repository - DONT RUN THIS
<!-- aws ecr create-repository --repository-name reconciliation-api-backend --region ap-south-1 -->

# Authenticate Docker with ECR
aws ecr get-login-password --region ap-south-1 | \
docker login --username AWS \
--password-stdin 463356420488.dkr.ecr.ap-south-1.amazonaws.com

# Build the Docker image
docker build -t reconciliation-api .

# Create a dynamic tag
NEW_TAG=v-$(date +%s)

# Tag the image properly
docker tag reconciliation-api:latest \
463356420488.dkr.ecr.ap-south-1.amazonaws.com/reconciliation-api-backend:$NEW_TAG

# Push the image to ECR
docker push 463356420488.dkr.ecr.ap-south-1.amazonaws.com/reconciliation-api-backend:$NEW_TAG
