import sys
import subprocess
import uvicorn

def main():
    print("==================================================")
    print("   LinkedIn Jobs Explorer Web Application")
    print("==================================================")
    print("Starting server at http://127.0.0.1:8000 ...")
    print("Press Ctrl+C to stop the server.\n")

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
