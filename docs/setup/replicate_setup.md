# Replicate API Setup Guide

This guide walks you through setting up Replicate API access for Flux image generation.

## 1. Create Replicate Account

1. Go to [replicate.com](https://replicate.com)
2. Click "Sign Up" in the top right
3. Sign up with GitHub, Google, or email
4. Verify your email if required

## 2. Get API Token

1. Log in to Replicate
2. Click your profile icon (top right)
3. Select "API tokens" from the dropdown
4. Click "Create token"
5. Give it a name (e.g., "hero-image-generator")
6. Copy the token (starts with `r8_...`)

**Important:** Save this token securely. You won't be able to see it again.

## 3. Add Token to .env

Open your `.env` file and add:

```bash
REPLICATE_API_TOKEN=r8_YourTokenHere
```

## 4. Test Connection

Run this Python script to verify your setup:

```python
import os
from dotenv import load_dotenv
import replicate

load_dotenv()

# Verify token is loaded
token = os.getenv('REPLICATE_API_TOKEN')
print(f'Token loaded: {token[:10]}...' if token else 'Token not found!')

# Test API call (very cheap - $0.01)
output = replicate.run(
    "black-forest-labs/flux-schnell",
    input={"prompt": "test image", "width": 512, "height": 512}
)

print(f'Success! Generated image URL: {output[0]}')
```

## 5. Pricing Information

| Model | Cost per Image | Quality | Speed |
|-------|---------------|---------|-------|
| Flux Pro | $0.055 | Highest | ~6s |
| Flux Dev | $0.020 | Good | ~4s |
| Flux Schnell | $0.010 | Fast drafts | ~2s |

## 6. Troubleshooting

### Error: "Invalid API token"
- Check that you copied the full token (starts with `r8_`)
- Ensure there are no spaces in the `.env` file
- Try regenerating the token

### Error: "Insufficient credits"
- Go to replicate.com/account/billing
- Add payment method
- Purchase credits ($10 minimum)

### Rate Limits
- Standard tier: 50 concurrent requests, 600/minute
- If you hit limits, wait 60 seconds or upgrade tier

## Next Steps

- See [GCP Setup](gcp_setup.md) for Gemini/Imagen configuration
- See [Testing Setup](testing_setup.md) for running tests
