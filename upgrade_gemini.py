import subprocess
import datetime

log_path = "/Users/reeazmahmud/Desktop/BengaliAI/Gemini-CLI/GEMINI_LOG_2026_01_18.txt"

def log(message):
    with open(log_path, "a") as f:
        f.write(f"{message}\n")

try:
    result = subprocess.run(["brew", "upgrade", "gemini-cli"], capture_output=True, text=True)
    if result.returncode == 0:
        log("Status: Completed successfully")
        print("Successfully upgraded gemini-cli")
        print(result.stdout)
    else:
        # Check if it's already up to date
        if "already installed" in result.stderr or "already up-to-date" in result.stdout:
            log("Status: Already up to date")
            print("gemini-cli is already up to date.")
        else:
            log(f"Status: Failed with error: {result.stderr}")
            print(f"Failed to upgrade gemini-cli: {result.stderr}")
            print(result.stdout)
except Exception as e:
    log(f"Status: Exception occurred: {str(e)}")
    print(f"An error occurred: {str(e)}")
