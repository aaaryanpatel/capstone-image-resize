# Capstone – Image Resize Pipeline (S3 → Lambda → Step Functions → API)

## What it does
Uploads go to **S3 (originals)**, a Lambda resizes to 512px max side using Pillow, and writes to **S3 (thumbnails)**.
A Step Functions state machine runs the Lambda and branches Success/Fail.

## Buckets (us-east-2)
- Originals: `capstone-images-originals-aryanpatel`
- Thumbnails: `capstone-images-thumbnails-aryanpatel`

## Lambda
- Name: `capstone-image-resize`
- Runtime: Python 3.9 (x86_64)
- Env: `ORIGINALS_BUCKET`, `THUMBNAILS_BUCKET`, `THUMB_MAX_WIDTH=512`, `THUMB_MAX_HEIGHT=512`
- Dependencies: `Pillow` (via `requirements.txt`)
- Handler: `lambda_function.lambda_handler`

## Step Functions
- Name: `capstone-image-resize-sm`
- Definition: see `state_machine.json`
- Flow: `ResizeImage (Lambda Task)` → `WasOk? (Choice)` → `Success | Fail`

## API Gateway
- REST API with resource `/start` (POST)
- **AWS Service** integration to **Step Functions** `StartExecution`
- Execution role for API Gateway is allowed:  
  `states:StartExecution` on the state machine ARN
- Mapping template (application/json) passes the incoming body to SFN as input

---

## How to test (manual)
1. Upload `test.jpg` to `capstone-images-originals-aryanpatel`.
2. Invoke Lambda with:
   ```json
   {"bucket":"capstone-images-originals-aryanpatel","key":"test.jpg"}
