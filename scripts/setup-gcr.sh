#!/bin/bash

# GCR Artifact Registry Setup Script
# This script sets up Google Cloud Artifact Registry for ZOBIS

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"zobis-prod"}
REGION=${GCP_REGION:-"asia-northeast3"}
REPOSITORY_NAME=${REPOSITORY_NAME:-"zobis"}
SERVICE_ACCOUNT_NAME=${SERVICE_ACCOUNT_NAME:-"zobis-github-actions"}

echo "🚀 Setting up GCR Artifact Registry for ZOBIS"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Repository: $REPOSITORY_NAME"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run 'gcloud auth login'"
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable iam.googleapis.com

# Create Artifact Registry repository
echo "📦 Creating Artifact Registry repository..."
if gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION &> /dev/null; then
    echo "✅ Repository $REPOSITORY_NAME already exists"
else
    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="ZOBIS Docker images repository"
    echo "✅ Repository $REPOSITORY_NAME created"
fi

# Create service account for GitHub Actions
echo "👤 Creating service account for GitHub Actions..."
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com &> /dev/null; then
    echo "✅ Service account $SERVICE_ACCOUNT_NAME already exists"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="ZOBIS GitHub Actions Service Account" \
        --description="Service account for ZOBIS GitHub Actions CI/CD"
    echo "✅ Service account $SERVICE_ACCOUNT_NAME created"
fi

# Grant necessary permissions
echo "🔐 Granting permissions to service account..."

# Artifact Registry permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Cloud Run permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Secret Manager permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# IAM permissions for Workload Identity
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountTokenCreator"

echo "✅ Permissions granted"

# Create Workload Identity Pool for GitHub Actions
echo "🔗 Setting up Workload Identity Federation..."
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-actions-provider"

# Check if pool exists
if gcloud iam workload-identity-pools describe $POOL_NAME --location="global" &> /dev/null; then
    echo "✅ Workload Identity Pool $POOL_NAME already exists"
else
    gcloud iam workload-identity-pools create $POOL_NAME \
        --location="global" \
        --display-name="GitHub Actions Pool"
    echo "✅ Workload Identity Pool $POOL_NAME created"
fi

# Check if provider exists
if gcloud iam workload-identity-pools providers describe $PROVIDER_NAME \
    --workload-identity-pool=$POOL_NAME \
    --location="global" &> /dev/null; then
    echo "✅ Workload Identity Provider $PROVIDER_NAME already exists"
else
    gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
        --workload-identity-pool=$POOL_NAME \
        --location="global" \
        --display-name="GitHub Actions Provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
        --issuer-uri="https://token.actions.githubusercontent.com"
    echo "✅ Workload Identity Provider $PROVIDER_NAME created"
fi

# Allow GitHub Actions to impersonate the service account
echo "🔐 Configuring Workload Identity binding..."
gcloud iam service-accounts add-iam-policy-binding \
    $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$(gcloud config get-value project)/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/zobis-ai/zobis1"

echo "✅ Workload Identity binding configured"

# Create secrets in Secret Manager
echo "🔑 Creating secrets in Secret Manager..."

# Function to create secret if it doesn't exist
create_secret_if_not_exists() {
    local secret_name=$1
    local secret_value=$2
    
    if gcloud secrets describe $secret_name &> /dev/null; then
        echo "✅ Secret $secret_name already exists"
    else
        echo "$secret_value" | gcloud secrets create $secret_name --data-file=-
        echo "✅ Secret $secret_name created"
    fi
}

# Create staging secrets
create_secret_if_not_exists "notion-token-staging" "your-notion-token-here"
create_secret_if_not_exists "hmac-secret-staging" "your-hmac-secret-here"
create_secret_if_not_exists "slack-webhook-staging" "your-slack-webhook-here"

# Create production secrets
create_secret_if_not_exists "notion-token-production" "your-notion-token-here"
create_secret_if_not_exists "hmac-secret-production" "your-hmac-secret-here"
create_secret_if_not_exists "slack-webhook-production" "your-slack-webhook-here"

echo "✅ Secrets created in Secret Manager"

# Generate service account key
echo "🔑 Generating service account key..."
KEY_FILE="zobis-github-actions-key.json"
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

echo "✅ Service account key generated: $KEY_FILE"

# Display summary
echo ""
echo "🎉 GCR Setup Complete!"
echo ""
echo "📋 Summary:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Repository: $REPOSITORY_NAME"
echo "  Service Account: $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo "  Workload Identity Pool: $POOL_NAME"
echo "  Workload Identity Provider: $PROVIDER_NAME"
echo ""
echo "🔑 Next Steps:"
echo "  1. Add the following secrets to your GitHub repository:"
echo "     - GCP_PROJECT_ID: $PROJECT_ID"
echo "     - GCP_SA_KEY: (content of $KEY_FILE)"
echo "  2. Update your GitHub Actions workflows to use Workload Identity"
echo "  3. Test the deployment pipeline"
echo ""
echo "⚠️  Security Note:"
echo "  - Keep the service account key file secure"
echo "  - Consider using Workload Identity instead of service account keys"
echo "  - Rotate secrets regularly"
