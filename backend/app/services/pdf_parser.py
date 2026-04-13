import logging
from io import BytesIO
from typing import Optional

import pdfplumber

logger = logging.getLogger(__name__)


async def extract(resume_bytes: bytes) -> str:
    try:
        with pdfplumber.open(BytesIO(resume_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)

            if not pages_text:
                raise ValueError("No text extracted from PDF")

            full_text = "\n\n".join(pages_text)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise


async def extract_from_base64(base64_str: str) -> str:
    import base64 as b64

    try:
        resume_bytes = b64.b64decode(base64_str)
        return await extract(resume_bytes)
    except Exception as e:
        logger.error(f"Base64 decode or PDF extraction failed: {e}")
        raise
