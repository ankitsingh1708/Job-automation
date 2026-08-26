import sys
import subprocess
import uvicorn

def main():
    print("==================================================")
    print("   LinkedIn Jobs Explorer Web Application")
    print("==================================================")
    print("Starting server at:")
    print("  • Local:   http://127.0.0.1:8000")
    print("  • Network: http://192.168.31.38:8000 (Use on mobile)")
    print("Press Ctrl+C to stop the server.\n")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
