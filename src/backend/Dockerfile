FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary directories
COPY src/backend/ /app/backend/
COPY src/database/ /app/database/
COPY src/model/ /app/model/
COPY data/ /data/
COPY src/main.py /app/

EXPOSE 5000

# Create a shell script to run both Python files
RUN echo '#!/bin/bash\n\
    python main.py &\n\
    MAIN_PID=$!\n\
    \n\
    # Function to handle shutdown\n\
    function cleanup() {\n\
    echo "Shutting down main.py..."\n\
    kill $MAIN_PID\n\
    echo "Running KPI.py..."\n\
    python backend/KPI.py\n\
    exit 0\n\
    }\n\
    \n\
    # Set up trap for SIGTERM\n\
    trap cleanup SIGTERM\n\
    \n\
    # Wait for main.py to finish\n\
    wait $MAIN_PID\n\
    \n\
    # Run KPI.py after main.py finishes\n\
    python backend/KPI.py' > /app/run.sh && chmod +x /app/run.sh

# Run the shell script
CMD ["/app/run.sh"]