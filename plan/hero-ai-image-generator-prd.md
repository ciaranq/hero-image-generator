# Product Requirements Document (PRD)
# Hero Image Generator - Flux & Gemini Integration

**Version:** 1.0  
**Date:** December 30, 2024  
**Project:** IntelliAgent Hero Image Generator  
**Repository:** https://github.com/ciaranq/hero-image-generator

---

## 1. Problem Statement

### What problem are we solving?
IntelliAgent needs high-quality, branded hero images for website content, landing pages, and marketing materials. Currently, the hero-image-generator repository has basic image generation capabilities but lacks:
- Access to state-of-the-art image generation models (Flux, Gemini)
- Flexible model selection and fallback mechanisms
- Quality validation to ensure generated images meet standards
- Proper cost tracking and management
- Multiple size output options for responsive design

### Who experiences this problem?
- IntelliAgent content creators needing hero images for blog posts and landing pages
- Marketing team requiring branded visuals for campaigns
- Development team needing placeholder/production images for website builds

### Current pain points and limitations
- Limited model options restrict image quality and style variety
- No automated quality validation leads to manual review overhead
- Single image size output requires manual resizing for responsive designs
- No cost tracking makes budgeting difficult
- Manual model selection without fallback causes failures to block workflow

---

## 2. Goals & Objectives

### Primary Goal
Build a flexible, production-ready Python-based hero image generator that integrates Flux (via Replicate) and Gemini 2.0 Flash (via Google Vertex AI) with intelligent model selection, quality validation, and comprehensive cost tracking.

### Secondary Goals
- Minimize generation failures through automatic model fallback
- Reduce manual quality review through AI-powered validation
- Support responsive design with configurable image sizes
- Maintain brand consistency through existing template integration
- Provide clear cost visibility for budget management

### Non-Goals (Phase 1)
- Prompt enhancement/optimization (Phase 2)
- Multiple image variations/A/B testing (Phase 2)
- EXIF metadata embedding (Phase 2)
- JSON manifest tracking (Phase 2)
- Automation hooks/webhooks (Phase 2)
- Web UI interface (CLI only for Phase 1)
- Real-time generation API (script-based only)

---

## 3. User Stories

### Story 1: Generate Hero Image with Default Settings
**As a** content creator  
**I want** to quickly generate a hero image using default settings  
**So that** I can get professional images without configuration overhead

**Acceptance Criteria:**
- Script runs with interactive prompts
- Uses default model from .env configuration
- Generates image in default size (medium)
- Saves to configured output directory
- Displays cost after generation
- Completes in under 60 seconds

### Story 2: Choose Specific Model and Size
**As a** marketing team member  
**I want** to select specific models (Flux Pro vs Gemini) and image sizes  
**So that** I can optimize for quality vs cost based on use case

**Acceptance Criteria:**
- Interactive prompt offers model selection
- Can override .env default model
- Can choose from small/medium/large sizes
- Model and size choices persist for session
- Cost estimate shown before generation

### Story 3: Automatic Quality Validation
**As a** content creator  
**I want** generated images automatically validated against my prompt  
**So that** I don't waste time on images that don't match requirements

**Acceptance Criteria:**
- Gemini Vision validates image matches prompt
- Clear pass/fail validation result
- Failed images trigger retry with fallback model
- Validation results logged with generation details
- Maximum 2 retry attempts before manual review

### Story 4: Model Fallback on Failure
**As a** developer  
**I want** automatic fallback to secondary model if primary fails  
**So that** generation workflow isn't blocked by API issues

**Acceptance Criteria:**
- Primary model failure triggers fallback automatically
- Clear logging of why fallback occurred
- User notified of model switch
- Cost tracking includes both attempts
- Fallback completes within 90 seconds total

### Story 5: Cost Tracking and Reporting
**As a** business owner  
**I want** to see generation costs after each run  
**So that** I can manage API spending and budget effectively

**Acceptance Criteria:**
- Cost displayed after each generation
- Breakdown by model (Flux vs Gemini)
- Includes quality validation costs
- Simple text log format
- Cumulative cost visible for session

### Story 6: Multi-Size Generation
**As a** web developer  
**I want** to generate hero images in multiple sizes  
**So that** I have responsive assets ready for deployment

**Acceptance Criteria:**
- Small, medium, large sizes configurable in .env
- Can generate single size or all sizes in one run
- Consistent naming convention for size variants
- All sizes validated for quality
- Cost shown per size generated

---

## 4. Technical Requirements

### Frontend
**N/A - CLI-only interface for Phase 1**

### Backend

#### 4.1 Architecture
```
hero-image-generator/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point with interactive CLI
│   ├── config.py               # Configuration management (.env loader)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract base class for models
│   │   ├── flux.py             # Flux integration via Replicate
│   │   └── gemini.py           # Gemini 2.0 Flash via Vertex AI
│   ├── validators/
│   │   ├── __init__.py
│   │   └── quality_check.py   # Gemini Vision validation
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_processing.py # Pillow-based processing
│   │   ├── cost_tracker.py     # Cost logging
│   │   └── logger.py           # Logging configuration
│   └── templates/
│       ├── __init__.py
│       └── prompts.py          # Integration with existing templates
├── public/
│   └── images/                 # Default output directory
├── tests/
│   └── test_*.py               # Unit tests
├── docs/
│   └── setup/
│       ├── gcp_setup.md        # GCP/Vertex AI setup guide
│       └── replicate_setup.md  # Replicate API setup guide
├── .env.example                # Example environment configuration
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

#### 4.2 Model Integration

**Flux (via Replicate API)**
- Models supported: `flux-pro`, `flux-dev`, `flux-schnell`
- API endpoint: Replicate Python SDK
- Authentication: API token in .env
- Parameters: prompt, width, height, num_outputs, guidance_scale
- Response: Image URL → download and save locally
- Cost: ~$0.055 per image (Flux Pro)

**Gemini 2.0 Flash (via Vertex AI)**
- Model: `gemini-2.0-flash-exp` with image generation
- API: Google Cloud AI Platform Python SDK
- Authentication: Service account JSON key
- Parameters: prompt, aspect_ratio, number_of_images
- Response: Base64 encoded image → decode and save
- Cost: ~$0.020 per image

**Gemini Vision (Quality Validation)**
- Model: `gemini-2.0-flash-exp` with vision capabilities
- Purpose: Validate generated image matches prompt
- Input: Generated image + original prompt
- Output: Boolean pass/fail + confidence score
- Cost: ~$0.001 per validation

#### 4.3 Configuration Management (.env)

```bash
# Model Configuration
DEFAULT_MODEL=flux-pro                    # flux-pro, flux-dev, flux-schnell, gemini
FALLBACK_MODEL=gemini                     # Secondary model if primary fails

# Flux Models via Replicate
REPLICATE_API_TOKEN=your_token_here
FLUX_MODEL_VERSION=flux-pro               # pro, dev, schnell

# Gemini via Vertex AI
GCP_PROJECT_ID=your_project_id
GCP_LOCATION=us-central1
GEMINI_MODEL=gemini-2.0-flash-exp
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Quality Validation
ENABLE_QUALITY_CHECK=true
QUALITY_CHECK_MODEL=gemini-vision
MIN_QUALITY_SCORE=0.7

# Image Sizes (width x height)
SIZE_SMALL=800x450
SIZE_MEDIUM=1920x1080
SIZE_LARGE=2560x1440
DEFAULT_SIZE=medium

# Output Configuration
OUTPUT_DIRECTORY=public/images
SAVE_FAILED_GENERATIONS=true
FAILED_OUTPUT_DIRECTORY=public/images/failed

# Cost Tracking
LOG_COSTS=true
COST_LOG_FILE=generation_costs.log

# Retry Logic
MAX_RETRIES=2
RETRY_DELAY_SECONDS=5
```

#### 4.4 API Integration Details

**Replicate SDK Usage:**
```python
import replicate

output = replicate.run(
    "black-forest-labs/flux-pro",
    input={
        "prompt": prompt_text,
        "width": 1920,
        "height": 1080,
        "num_outputs": 1,
        "guidance_scale": 7.5
    }
)
```

**Vertex AI SDK Usage:**
```python
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

model = ImageGenerationModel.from_pretrained("imagegeneration@006")
response = model.generate_images(
    prompt=prompt_text,
    number_of_images=1,
    aspect_ratio="16:9"
)
```

#### 4.5 Error Handling & Retry Logic

**Error Categories:**
1. **API Failures** (500, 503, timeout)
   - Action: Retry with exponential backoff (5s, 10s)
   - Max retries: 2
   - If still fails: Switch to fallback model

2. **Authentication Errors** (401, 403)
   - Action: Log error, exit gracefully
   - Message: Check API keys/credentials

3. **Rate Limiting** (429)
   - Action: Wait (retry-after header) + retry
   - Max wait: 60 seconds

4. **Validation Failures**
   - Action: Retry generation with same model once
   - If fails again: Switch to fallback model
   - Max total attempts: 2

5. **Image Processing Errors**
   - Action: Log error, save raw response
   - Flag for manual review

**Logging Strategy:**
- INFO: Generation start, success, costs
- WARNING: Validation failures, retries
- ERROR: API failures, authentication issues
- DEBUG: Full request/response details (if enabled)

#### 4.6 Quality Validation Process

```
1. Generate image with primary model
2. Download/save image temporarily
3. Send to Gemini Vision with prompt:
   "Does this image accurately represent the following prompt? [prompt]
    Rate match quality from 0-1. Respond with score and brief explanation."
4. Parse response for score
5. If score >= MIN_QUALITY_SCORE:
   - Move to final output directory
   - Log success
6. If score < MIN_QUALITY_SCORE:
   - Trigger retry logic
   - Save to failed directory if SAVE_FAILED_GENERATIONS=true
7. Track validation cost
```

#### 4.7 Cost Tracking Implementation

**Cost Calculation:**
```python
COSTS = {
    'flux-pro': 0.055,
    'flux-dev': 0.020,  # Approximate for commercial use
    'flux-schnell': 0.010,
    'gemini': 0.020,
    'gemini-vision': 0.001
}

def calculate_cost(model, num_generations, validations):
    generation_cost = COSTS[model] * num_generations
    validation_cost = COSTS['gemini-vision'] * validations
    return generation_cost + validation_cost
```

**Log Format:**
```
[2024-12-30 10:30:45] Generated: hero_image_001.png | Model: flux-pro | Size: 1920x1080 | Cost: $0.056 | Status: Success
[2024-12-30 10:31:10] Generated: hero_image_002.png | Model: gemini (fallback) | Size: 1920x1080 | Cost: $0.021 | Status: Success after retry
```

### Infrastructure

#### 4.8 Dependencies (requirements.txt)

```
# Core dependencies
python-dotenv>=1.0.0
pillow>=10.0.0  # Already in repo

# API clients
replicate>=0.25.0
google-cloud-aiplatform>=1.38.0

# Utilities
requests>=2.31.0
tenacity>=8.2.3  # For retry logic
```

#### 4.9 Authentication Setup

**Replicate:**
1. Sign up at replicate.com
2. Generate API token from account settings
3. Add to .env: `REPLICATE_API_TOKEN=r8_...`

**Google Cloud Platform:**
1. Create new GCP project
2. Enable Vertex AI API
3. Create service account with Vertex AI User role
4. Download JSON key file
5. Add to .env: `GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json`

Detailed setup guides in `docs/setup/`

#### 4.10 Security Requirements

- Never commit .env or service account keys
- Add to .gitignore: `.env`, `*.json` (service accounts)
- Use environment variables for all credentials
- Validate file paths to prevent directory traversal
- Sanitize user inputs before API calls
- Rate limit user interactions if exposed via API (Phase 2)

---

## 5. Success Metrics

### Key Performance Indicators (KPIs)

**Performance Metrics:**
- Average generation time: < 45 seconds per image
- Success rate: > 95% (including fallback)
- Quality validation pass rate: > 80% on first attempt

**Cost Metrics:**
- Average cost per image: $0.03 - $0.06
- Cost reduction through fallback: 20% when Gemini used vs Flux Pro

**Reliability Metrics:**
- API uptime dependency: > 99%
- Fallback activation rate: < 10%
- Zero unhandled exceptions in production

**User Experience Metrics:**
- Time to first image: < 2 minutes (including setup)
- User satisfaction: Subjective feedback via team
- Retry rate: < 5% manual retries needed

### User Acceptance Criteria

**Must Have:**
- ✅ Generate images using Flux or Gemini
- ✅ Automatic quality validation
- ✅ Model fallback on failure
- ✅ Cost tracking per generation
- ✅ Multiple size support (S/M/L)
- ✅ Interactive CLI interface
- ✅ Integration with existing templates
- ✅ Comprehensive setup documentation

**Should Have:**
- Quality validation confidence scoring
- Session-based cost aggregation
- Detailed error messages with suggestions
- Progress indicators for long operations

**Nice to Have:**
- Color validation against brand palette
- Prompt suggestions based on history
- Batch mode for multiple prompts

---

## 6. Timeline & Phases

### Phase 1: Core Implementation (Current PRD)
**Estimated Effort:** 2-3 days

**Day 1: Foundation & Integration**
- Set up project structure
- Implement config management (.env loader)
- Integrate Replicate SDK for Flux
- Integrate Vertex AI SDK for Gemini
- Basic image generation working

**Day 2: Quality & Reliability**
- Implement Gemini Vision quality validation
- Build retry logic and fallback mechanism
- Add cost tracking and logging
- Error handling and edge cases

**Day 3: User Experience & Documentation**
- Interactive CLI implementation
- Multi-size generation support
- Comprehensive README with setup guides
- Testing and bug fixes

**Dependencies:**
- Replicate API access (immediate)
- GCP project setup (1 hour setup time)
- Existing template integration (dependent on repo structure)

**Potential Risks:**
- GCP setup complexity may extend timeline
- API rate limits during testing
- Quality validation accuracy tuning may require iteration

### Phase 2: Enhanced Features (Future Development)
**Estimated Effort:** 3-5 days

**Features:**
1. **Prompt Enhancement**
   - Use Gemini to improve/expand user prompts
   - Maintain prompt history for reuse
   - Prompt template library

2. **Image Variations & A/B Testing**
   - Generate multiple variations of same prompt
   - Side-by-side comparison interface
   - Voting/selection mechanism

3. **Metadata & Attribution**
   - Embed generation details in image EXIF
   - JSON manifest of all generations
   - Searchable generation history

4. **Automation & Integration**
   - Webhook notifications on completion
   - API endpoint for programmatic access
   - Integration with CMS/website builder
   - Scheduled batch generation

5. **Advanced Quality Control**
   - Brand color palette validation
   - Composition analysis (rule of thirds, etc.)
   - Accessibility checks (contrast ratios)
   - Multi-validator consensus (Gemini + Claude)

**Dependencies:**
- Phase 1 completion and stabilization
- User feedback from Phase 1
- Additional API budgets for advanced features

---

## 7. Open Questions

### Technical Unknowns

**Q1: Gemini 2.0 Flash Image Generation Availability**
- **Question:** Is Gemini 2.0 Flash image generation fully available in Vertex AI, or still in preview?
- **Impact:** May affect stability and API limits
- **Action:** Verify during implementation, document any preview limitations
- **Decision needed by:** Start of development

**Q2: Quality Validation Accuracy**
- **Question:** What minimum quality score threshold works best for IntelliAgent brand standards?
- **Impact:** Affects retry rate and cost
- **Action:** Test with sample generations, tune threshold
- **Decision needed by:** Day 2 of development

**Q3: Existing Template Structure**
- **Question:** What format are current color schemes/templates in the existing repo?
- **Impact:** Integration complexity
- **Action:** Review existing repo structure before implementation
- **Decision needed by:** Day 1 of development

### Decisions Needed

**D1: Fallback Priority**
- **Question:** Should Flux always be primary, or smart selection based on prompt complexity?
- **Options:** 
  - A) Flux always primary (simpler)
  - B) Smart selection based on prompt analysis (more complex)
- **Recommendation:** Option A for Phase 1, Option B for Phase 2
- **Decision owner:** Kieran (IntelliAgent)

**D2: Cost Budget Limits**
- **Question:** Should there be hard spending limits per session/day/month?
- **Options:**
  - A) No limits, trust user judgment
  - B) Soft warning at threshold
  - C) Hard stop at limit
- **Recommendation:** Option B with configurable threshold in .env
- **Decision owner:** Kieran (IntelliAgent)

**D3: Failed Image Handling**
- **Question:** How long should failed generations be retained?
- **Options:**
  - A) Keep forever (manual cleanup)
  - B) Auto-delete after 7 days
  - C) Don't save failed attempts
- **Recommendation:** Option A for Phase 1 (debugging valuable)
- **Decision owner:** Kieran (IntelliAgent)

### Items Requiring Further Research

**R1: Flux Model Comparison**
- **Research needed:** Real-world quality comparison of Flux Pro vs Dev vs Schnell for hero images
- **Method:** Generate test batch with same prompts across all three
- **Timeline:** During Day 1 implementation
- **Owner:** Development team

**R2: Gemini Vision Prompt Engineering**
- **Research needed:** Optimal prompt structure for quality validation
- **Method:** Test various prompt formats, measure accuracy
- **Timeline:** Day 2 implementation
- **Owner:** Development team

**R3: Brand Template Integration**
- **Research needed:** Current repo structure and template format
- **Method:** Code review of existing hero-image-generator repo
- **Timeline:** Before Day 1 kickoff
- **Owner:** Kieran (IntelliAgent)

**R4: API Rate Limits**
- **Research needed:** Replicate and Vertex AI rate limits for image generation
- **Method:** Review API documentation, test during development
- **Timeline:** Day 1
- **Owner:** Development team

---

## 8. Appendices

### A. API Cost Breakdown

| Service | Operation | Cost per Call | Monthly Estimate (100 images) |
|---------|-----------|---------------|-------------------------------|
| Flux Pro | Image generation | $0.055 | $5.50 |
| Flux Dev | Image generation | $0.020 | $2.00 |
| Flux Schnell | Image generation | $0.010 | $1.00 |
| Gemini 2.0 | Image generation | $0.020 | $2.00 |
| Gemini Vision | Quality validation | $0.001 | $0.10 |
| **Total (Flux Pro + validation)** | | **$0.056** | **$5.60** |

**Assumptions:**
- 100 images/month baseline
- 5% retry rate (5 additional generations)
- 100% validation rate
- Fallback used 10% of time (10 Gemini generations)

**Cost Optimization Scenarios:**
- Using Flux Dev instead of Pro: Save ~60% ($2.10/month vs $5.60)
- Disabling validation: Save $0.10/month
- Using Gemini as primary: Save ~65% ($2.10/month vs $5.60)

### B. Example Prompts

**Prompt Template Structure:**
```
Base Template: "Professional hero image for {topic}, {style}, featuring {elements}"

Style Options:
- Modern and clean
- Bold and dynamic  
- Minimal and elegant
- Vibrant and energetic

Elements:
- Abstract technology patterns
- Geometric shapes
- Gradient backgrounds
- Data visualization themes
```

**Sample Prompts:**
1. "Professional hero image for AI consultancy, modern and clean, featuring abstract neural network patterns in blue and purple gradients, 16:9 aspect ratio"

2. "Professional hero image for SEO services, bold and dynamic, featuring rising graph charts and search icons, vibrant teal and orange color scheme, 16:9 aspect ratio"

3. "Professional hero image for e-commerce optimization, minimal and elegant, featuring shopping cart icons and conversion funnel, navy blue and gold accents, 16:9 aspect ratio"

### C. Reference Links

**API Documentation:**
- Replicate API: https://replicate.com/docs
- Flux Models: https://replicate.com/black-forest-labs
- Vertex AI: https://cloud.google.com/vertex-ai/docs
- Gemini API: https://ai.google.dev/docs

**Setup Guides:**
- GCP Project Setup: https://cloud.google.com/resource-manager/docs/creating-managing-projects
- Service Accounts: https://cloud.google.com/iam/docs/service-accounts
- Vertex AI Quickstart: https://cloud.google.com/vertex-ai/docs/start/quickstart

**Related Projects:**
- IntelliAgent: https://intelliagent.com.au
- Hero Image Generator Repo: https://github.com/ciaranq/hero-image-generator

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-12-30 | Claude + Kieran | Initial PRD based on requirements gathering |

---

**PRD Status:** ✅ Ready for Implementation  
**Next Step:** Review PRD → Approve → Begin Development (Phase 1, Day 1)
