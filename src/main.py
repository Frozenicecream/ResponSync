import subprocess
import os
import sys
import threading
import time

# Get the directory of the main.py script (c:/Code/ResponSync/src)
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths to the scripts
CREATE_DB_SCRIPT = os.path.join(SRC_DIR, "database", "create_db.py")
MODEL_SCRIPT = os.path.join(SRC_DIR, "model", "alloting_resources.py")

# Define the data directory where CSV files are located
# DATA_DIR will be c:/Code/ResponSync/data/
DATA_DIR = os.path.abspath(os.path.join(SRC_DIR, "..", "data"))


def execute_script(script_path, cwd=None):
    """Executes a Python script using subprocess."""
    command = [sys.executable, script_path]
    effective_cwd = cwd if cwd else os.getcwd()
    print(f"Executing: \"{' '.join(command)}\" in directory \"{effective_cwd}\"")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'  # Specify encoding for robustness
        )
        if result.stdout:
            print(f"Output of {os.path.basename(script_path)}:\n{result.stdout}")
        if result.stderr: # Should be empty if check=True and no error, but good to log
            print(f"Errors (stderr) from {os.path.basename(script_path)}:\n{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path} (return code {e.returncode}):")
        if e.stdout:
            print(f"Stdout:\n{e.stdout}")
        if e.stderr:
            print(f"Stderr:\n{e.stderr}")
        raise  # Re-raise the exception to stop execution if a script fails
    except FileNotFoundError:
        print(f"Error: The Python interpreter '{sys.executable}' or script '{script_path}' was not found.")
        raise

def run_generator():
    """Runs the generate_incidents.py script in a separate process."""
    generator_script = os.path.join(SRC_DIR, "backend", "generate_incidents.py")
    try:
        execute_script(generator_script)
    except Exception as e:
        print(f"Error running incident generator: {e}")

def run_model():
    """Runs the resource assignment model in a separate thread."""
    while True:
        try:
            print("\nRunning resource assignment model...")
            print(f"Model script '{MODEL_SCRIPT}' will be run with CWD set to '{DATA_DIR}'.")
            execute_script(MODEL_SCRIPT, cwd=DATA_DIR)
            print(f"Resource assignment model script finished successfully.")
            time.sleep(15)  # Wait for 15 seconds before next run
        except Exception as e:
            print(f"Failed to run resource assignment model: {e}")
            time.sleep(5)  # Wait a bit before retrying on error

def main():
    print("Starting main execution...")
    print(f"Source directory (SRC_DIR): {SRC_DIR}")
    print(f"Data directory (DATA_DIR) for model CSVs: {DATA_DIR}")

    # 1. Execute create_db.py
    print("\nStep 1: Initializing database...")
    try:
        execute_script(CREATE_DB_SCRIPT)
        print("Database initialization script finished successfully.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return

    # 2. Start the Flask API first (required by assigning_resource.py)
    print("\nStep 2: Starting Flask API server...")
    try:
        if SRC_DIR not in sys.path:
            sys.path.insert(0, SRC_DIR)

        from backend.api import app as flask_app

        print("Flask API imported. Starting server on http://127.0.0.1:5000/ (or http://0.0.0.0:5000/)")
        print("The server will run indefinitely. Press CTRL+C to stop.")
        
        # Start the incident generator in a separate thread
        generator_thread = threading.Thread(target=run_generator, daemon=True)
        generator_thread.start()
        
        # Start the model in a separate thread
        model_thread = threading.Thread(target=run_model, daemon=True)
        model_thread.start()
        
        # Start the Flask app
        flask_app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"Error importing Flask app: {e}")
        print(f"Please ensure 'c:\\Code\\ResponSync\\src\\backend\\__init__.py' exists (can be empty),")
        print(f"and that all dependencies for api.py (like Flask) are installed.")
        print(f"Current sys.path: {sys.path}")
    except Exception as e:
        print(f"Error running Flask API: {e}")

if __name__ == "__main__":
    main()