wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.body = '{"source": "\\documentclass{article}\\begin{document}Hello from API!\\end{document}"}'