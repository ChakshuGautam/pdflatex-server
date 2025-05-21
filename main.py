import os
import subprocess
import uuid
import logging # Added
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse # JSONResponse Added
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

@app.post('/compile')
async def compile_latex(request: Request):
    unique_id = str(uuid.uuid4())
    # Define base filename and paths (consistent with example, using unique_id as base)
    base_filename = unique_id 
    tex_filepath = f"{base_filename}.tex" # File will be created in current working directory
    pdf_filepath = f"{base_filename}.pdf"
    log_filepath = f"{base_filename}.log" # For pdflatex log
    aux_filepath = f"{base_filename}.aux" # For pdflatex aux files

    try:
        data = await request.json()
        if not data or 'source' not in data:
            logging.warning(f"Request {unique_id}: No source code provided.")
            raise HTTPException(status_code=400, detail='No source code provided')

        latex_source = data['source']
        
        # Save LaTeX source to a .tex file
        with open(tex_filepath, 'w') as f:
            f.write(latex_source)
        logging.info(f"Request {unique_id}: LaTeX source saved to {tex_filepath}")

        # Compile LaTeX using Docker
        # The command mounts the current working directory (where tex_filepath is) to /workdir
        # pdflatex reads from /workdir/tex_filename and outputs to /workdir/pdf_filename
        docker_command = [
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}:/workdir', # Mount current directory as /workdir
            'cristiangreco/pdflatex',
            'pdflatex', 
            '-interaction=nonstopmode', # Ensure it doesn't hang on errors
            '-output-directory=/workdir', # Output PDF to /workdir
            f'/workdir/{base_filename}.tex'    # Input tex file from /workdir
        ]
        
        logging.info(f"Request {unique_id}: Executing Docker command: {' '.join(docker_command)}")
        
        # Using check=False to handle errors manually for better logging
        process = subprocess.run(docker_command, capture_output=True, text=True, check=False)

        if process.stdout:
            logging.info(f"Request {unique_id}: pdflatex stdout:\n{process.stdout}")
        if process.stderr: # pdflatex often uses stderr for info/warnings too
            logging.info(f"Request {unique_id}: pdflatex stderr:\n{process.stderr}")

        if process.returncode == 0 and os.path.exists(pdf_filepath):
            logging.info(f"Request {unique_id}: Compilation successful. PDF generated at {pdf_filepath}")
            return FileResponse(pdf_filepath, media_type='application/pdf', filename=pdf_filepath)
        else:
            # Compilation failed or PDF not found
            logging.error(f"Request {unique_id}: Compilation failed. Return code: {process.returncode}")
            error_detail = process.stderr or process.stdout or "Unknown compilation error"
            # Attempt to read the log file for more detailed errors if it exists
            if os.path.exists(log_filepath):
                with open(log_filepath, 'r') as log_file_content:
                    error_detail += "\n\n--- LaTeX Log File ---\n" + log_file_content.read()
            
            # Use JSONResponse for structured error
            return JSONResponse(
                status_code=500, # Internal server error for compilation failure
                content={'error': 'Compilation failed', 'details': error_detail}
            )

    except subprocess.CalledProcessError as e: # Should not be reached if check=False
        logging.error(f"Request {unique_id}: pdflatex compilation failed with CalledProcessError.", exc_info=True)
        logging.error(f"Command: {' '.join(e.cmd)}")
        logging.error(f"Return code: {e.returncode}")
        logging.error(f"stdout: {e.stdout}")
        logging.error(f"stderr: {e.stderr}")
        return JSONResponse(
            status_code=500,
            content={"error": "LaTeX compilation failed (CalledProcessError)", "details": e.stderr or e.stdout},
        )
    except HTTPException: # Re-raise HTTPException to ensure FastAPI handles it (like 400)
        raise
    except Exception as e:
        logging.error(f"Request {unique_id}: An unexpected error occurred: {str(e)}", exc_info=True)
        return JSONResponse( # Use JSONResponse
            status_code=500,
            content={"error": "An internal server error occurred.", "details": str(e)},
        )
    finally:
        logging.info(f"Request {unique_id}: Cleaning up temporary files.")
        # Clean up temporary files
        for filename in [tex_filepath, pdf_filepath, log_filepath, aux_filepath]:
            if os.path.exists(filename):
                os.remove(filename)
                logging.info(f"Request {unique_id}: Removed {filename}")

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
