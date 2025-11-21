import os, io, json, boto3
from PIL import Image

s3 = boto3.client('s3')

ORIGINALS_BUCKET = os.environ['ORIGINALS_BUCKET']
THUMBNAILS_BUCKET = os.environ['THUMBNAILS_BUCKET']
MAX_W = int(os.environ.get('THUMB_MAX_WIDTH', '512'))
MAX_H = int(os.environ.get('THUMB_MAX_HEIGHT', '512'))

def _resize_image(img_bytes):
    with Image.open(io.BytesIO(img_bytes)) as im:
        im = im.convert('RGB')
        im.thumbnail((MAX_W, MAX_H))
        out = io.BytesIO()
        im.save(out, format='JPEG', quality=85, optimize=True)
        out.seek(0)
        return out.read()

def handler(event, context):
    # Accept input: {"bucket": "...", "key": "uploads/filename.jpg"}
    src_bucket = (event.get("bucket") or ORIGINALS_BUCKET).strip()
    key = event.get("key")
    if not key:
        raise ValueError("Missing required field: 'key'")

    obj = s3.get_object(Bucket=src_bucket, Key=key)
    img_bytes = obj['Body'].read()

    thumb_bytes = _resize_image(img_bytes)

    filename = key.split('/')[-1]
    dst_key = f"thumbs/{os.path.splitext(filename)[0]}.jpg"

    s3.put_object(
        Bucket=THUMBNAILS_BUCKET,
        Key=dst_key,
        Body=thumb_bytes,
        ContentType="image/jpeg"
    )

    return {
        "ok": True,
        "src_bucket": src_bucket,
        "src_key": key,
        "dst_bucket": THUMBNAILS_BUCKET,
        "dst_key": dst_key,
        "max_width": MAX_W,
        "max_height": MAX_H
    }
