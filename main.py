from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import subprocess
import os
import tempfile
import pandas as pd
import json

app = FastAPI(title="LinkedIn Posts Scraper")

@app.get("/scrape")
async def scrape_posts(profile_url: str = Query(..., description="LinkedIn profile URL")):
    try:
        # Create temp CSV path
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            csv_path = tmp.name
        
        # Run original scraper (adjust filename if needed)
        cmd = ["python", "scrape_linkedin_posts.py", profile_url, csv_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            os.unlink(csv_path)
            return {"status": "success", "posts": df.to_dict('records')}
        else:
            return {"status": "error", "message": result.stderr}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {"message": "LinkedIn Posts Scraper API - POST /scrape"}
