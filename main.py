import os
import subprocess
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
import uvicorn # Required for running the app with uvicorn

app = FastAPI()

@app.post('/compile')
async def compile_latex(request: Request):
    try:
        data = await request.json()
        if not data or 'source' not in data:
            raise HTTPException(status_code=400, detail='No source code provided')

        latex_source = data['source']
        
        unique_id = str(uuid.uuid4())
        tex_filename = f"{unique_id}.tex"
        pdf_filename = f"{unique_id}.pdf"
        log_filename = f"{unique_id}.log"
        aux_filename = f"{unique_id}.aux"

        # Save LaTeX source to a .tex file
        with open(tex_filename, 'w') as f:
            f.write(latex_source)

        # Compile LaTeX using Docker
        docker_command = [
            'docker', 'run', '--rm',
            '-v', f'{os.getcwd()}:/workdir', # Mount current directory
            'cristiangreco/pdflatex',
            'pdflatex', tex_filename
        ]
        
        process = subprocess.run(docker_command, capture_output=True, text=True)

        if process.returncode == 0 and os.path.exists(pdf_filename):
            return FileResponse(pdf_filename, media_type='application/pdf', filename=pdf_filename)
        else:
            error_message = process.stderr if process.stderr else 'Unknown compilation error'
            if os.path.exists(log_filename):
                with open(log_filename, 'r') as log_file:
                    error_message += "\n\n--- Log File ---\n" + log_file.read()
            raise HTTPException(status_code=500, detail=f"Compilation failed: {error_message}")

    except HTTPException:
        raise # Re-raise HTTPException to ensure FastAPI handles it
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary files
        for filename in [tex_filename, pdf_filename, log_filename, aux_filename]:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
