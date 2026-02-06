from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.security import APIKeyHeader
import subprocess
import os
import tempfile
import pandas as pd

app = FastAPI()

# API Key from Render Environment Variable
API_KEY = os.getenv("MY_API_KEY", "mitrax24-secret-2026")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@app.get("/scrape")
async def scrape_posts(profile_url: str = Query(...), api_key: str = Depends(verify_api_key)):
    # Your existing scraper code (unchanged)
    try:
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            csv_path = tmp.name
        
        cmd = ["python", "scrape.py", profile_url, csv_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0 and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            os.unlink(csv_path)
            return {"status": "success", "posts": df.to_dict('records'), "count": len(df)}
        else:
            return {"status": "error", "message": result.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {"message": "Protected API - Use X-API-Key header"}
