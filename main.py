import os
import subprocess
import uuid
import logging
import shutil # Added
from pathlib import Path # Added
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

TEMP_BASE_DIR = Path("/app/temp_files")

# Create TEMP_BASE_DIR at startup if it doesn't exist. This is more efficient.
TEMP_BASE_DIR.mkdir(parents=True, exist_ok=True)


@app.post('/compile')
async def compile_latex(request: Request):
    unique_id = str(uuid.uuid4())
    request_temp_dir = TEMP_BASE_DIR / unique_id
    
    # Fixed filenames within the unique temp dir
    tex_filename = "document.tex"
    pdf_filename = "document.pdf"
    log_filename = "document.log" # For pdflatex log
    # aux_filename = "document.aux" # Not explicitly used for cleanup list, but shutil.rmtree handles it

    tex_file_path = request_temp_dir / tex_filename
    pdf_file_path = request_temp_dir / pdf_filename
    log_file_path = request_temp_dir / log_filename # For reading the log on error

    try:
        # Ensure TEMP_BASE_DIR exists (redundant if created at startup, but harmless)
        TEMP_BASE_DIR.mkdir(parents=True, exist_ok=True)
        request_temp_dir.mkdir()
        logging.info(f"Request {unique_id}: Created temporary directory {request_temp_dir}")

        data = await request.json()
        if not data or 'source' not in data:
            logging.warning(f"Request {unique_id}: No source code provided.")
            raise HTTPException(status_code=400, detail='No source code provided')

        latex_source = data['source']
        
        logging.info(f"Request {unique_id}: LaTeX source will be saved to {tex_file_path}")
        with open(tex_file_path, 'w') as f:
            f.write(latex_source)

        docker_command = [
            'docker', 'run', '--rm',
            '-v', f"{request_temp_dir.resolve()}:/workdir", # Mount unique dir
            'cristiangreco/pdflatex',
            'pdflatex', 
            '-interaction=nonstopmode',
            '-output-directory=/workdir', # Output PDF in /workdir
            tex_filename                  # Input .tex file (relative to /workdir)
        ]
        
        logging.info(f"Request {unique_id}: Executing Docker command: {' '.join(docker_command)}")
        
        process = subprocess.run(docker_command, capture_output=True, text=True, check=False)

        if process.stdout:
            logging.info(f"Request {unique_id}: pdflatex stdout:\n{process.stdout}")
        if process.stderr:
            logging.info(f"Request {unique_id}: pdflatex stderr:\n{process.stderr}")

        if process.returncode == 0 and pdf_file_path.exists():
            logging.info(f"Request {unique_id}: Compilation successful. PDF generated at {pdf_file_path}")
            return FileResponse(pdf_file_path, media_type='application/pdf', filename=pdf_filename) # Return with fixed PDF name
        else:
            logging.error(f"Request {unique_id}: Compilation failed. Return code: {process.returncode}")
            error_detail = process.stderr or process.stdout or "Unknown compilation error"
            if log_file_path.exists():
                with open(log_file_path, 'r') as log_file_content:
                    error_detail += "\n\n--- LaTeX Log File ---\n" + log_file_content.read()
            
            return JSONResponse(
                status_code=500,
                content={'error': 'Compilation failed', 'details': error_detail}
            )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Request {unique_id}: An unexpected error occurred: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "An internal server error occurred.", "details": str(e)},
        )
    finally:
        if request_temp_dir.exists():
            logging.info(f"Request {unique_id}: Cleaning up temporary directory: {request_temp_dir}")
            shutil.rmtree(request_temp_dir)
            logging.info(f"Request {unique_id}: Removed {request_temp_dir}")

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
