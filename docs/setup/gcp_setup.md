# Google Cloud Platform Setup Guide

This guide walks you through setting up Google Vertex AI for Gemini/Imagen image generation.

## 1. Create GCP Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "hero-image-generator")
4. Click "Create"
5. Wait for project creation (takes ~30 seconds)
6. Note your **Project ID** (not the project name - they may differ)

## 2. Enable Required APIs

1. In the GCP Console, go to "APIs & Services" → "Library"
2. Search for and enable:
   - **Vertex AI API**
   - **Cloud AI Platform API**

Click "Enable" for each.

## 3. Create Service Account

1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Enter details:
   - Name: `hero-image-generator`
   - ID: (auto-filled)
   - Description: "Service account for AI image generation"
4. Click "Create and Continue"
5. Grant role: **Vertex AI User**
6. Click "Continue" → "Done"

## 4. Create and Download Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON" format
5. Click "Create"
6. A JSON file downloads automatically

**Important:** Store this file securely. Anyone with this file can access your GCP resources.

## 5. Configure .env File

Move the downloaded JSON file to a secure location (e.g., `~/.gcp/hero-image-generator-key.json`)

Add to your `.env`:

```bash
GCP_PROJECT_ID=your-project-id-here
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/key.json
```

**Security tip:** Add `*.json` to your `.gitignore` to prevent accidentally committing keys.

## 6. Test Connection

Run this Python script to verify your setup:

```python
import os
from dotenv import load_dotenv
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

load_dotenv()

# Initialize Vertex AI
project_id = os.getenv('GCP_PROJECT_ID')
location = os.getenv('GCP_LOCATION', 'us-central1')

aiplatform.init(project=project_id, location=location)

print(f'✓ Connected to GCP project: {project_id}')

# Test image generation (costs ~$0.02)
model = ImageGenerationModel.from_pretrained('imagegeneration@006')
response = model.generate_images(
    prompt='simple test image',
    number_of_images=1
)

print(f'✓ Successfully generated test image')
print(f'  Model: Imagen')
print(f'  Cost: ~$0.02')
```

## 7. Pricing Information

| Service | Cost | Notes |
|---------|------|-------|
| Imagen (imagegeneration@006) | $0.020/image | Stable, production-ready |
| Gemini Vision (validation) | $0.001-0.002/call | For quality checks |

## 8. Set Up Billing

1. Go to "Billing" in GCP Console
2. Link a billing account (or create new one)
3. Add payment method
4. Enable billing for your project

**Free tier:** GCP offers $300 free credits for new accounts.

## 9. Set Budget Alerts (Recommended)

1. Go to "Billing" → "Budgets & alerts"
2. Click "Create budget"
3. Set budget amount (e.g., $50/month)
4. Set alert thresholds (50%, 90%, 100%)
5. Add your email for notifications

## 10. Troubleshooting

### Error: "Project not found"
- Double-check your `GCP_PROJECT_ID` in `.env`
- Use the Project ID, not the Project Name
- Verify project exists in console.cloud.google.com

### Error: "Permission denied"
- Ensure service account has "Vertex AI User" role
- Check that `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON file
- Verify APIs are enabled (step 2)

### Error: "Billing not enabled"
- Go to console.cloud.google.com/billing
- Link a billing account to your project

### Rate Limits
- Imagen: 60 requests/minute
- If you hit limits, implement delays or request quota increase

## Next Steps

- See [Replicate Setup](replicate_setup.md) for Flux configuration
- See [Testing Setup](testing_setup.md) for running tests
