from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import subprocess
import os
import tempfile
import pandas as pd

app = FastAPI()

@app.get("/scrape")
async def scrape_posts(profile_url: str = Query(...)):
    try:
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            csv_path = tmp.name
        
        # FIXED: Use scrape.py (your file name)
        cmd = ["python", "scrape.py", profile_url, csv_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0 and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            os.unlink(csv_path)
            return {"status": "success", "posts": df.to_dict('records'), "count": len(df)}
        else:
            return {"status": "error", "message": result.stderr or "CSV not generated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def root():
    return {"message": "LinkedIn Scraper Ready - GET /scrape?profile_url=PROFILE_URL"}
