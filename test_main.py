import pytest
import httpx

# Define the base URL for the API service
API_BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_compile_simple_latex():
    """
    Tests the /compile endpoint with a simple LaTeX document.
    """
    latex_source = r"\documentclass{article}\begin{document}Hello, world!\end{document}}"
    payload = {"source": latex_source}

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/compile", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0

# Placeholder for more tests if needed
# @pytest.mark.asyncio
# async def test_compile_invalid_latex():
#     """
#     Tests the /compile endpoint with invalid LaTeX source.
#     """
#     latex_source = r"\documentclass{article}\begin{document}\invalidcommand\end{document}}"
#     payload = {"source": latex_source}

#     async with httpx.AsyncClient() as client:
#         response = await client.post(f"{API_BASE_URL}/compile", json=payload)

#     assert response.status_code == 500 
#     # Further assertions can be made on the error message if the API returns structured errors
#     # For example:
#     # error_details = response.json()
#     # assert "Compilation failed" in error_details.get("detail", "")
#     # assert "details" in error_details # Check if the 'details' key (containing logs) is present.
#
# @pytest.mark.asyncio
# async def test_compile_no_source():
#     """
#     Tests the /compile endpoint with no source code provided.
#     """
#     payload = {} # Empty payload or missing 'source' key

#     async with httpx.AsyncClient() as client:
#         response = await client.post(f"{API_BASE_URL}/compile", json=payload)
    
#     assert response.status_code == 400
#     # error_details = response.json()
#     # assert "No source code provided" in error_details.get("detail", "")
