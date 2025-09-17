FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY microservices/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared libraries first
COPY shared ./shared

# Copy service code
COPY microservices/api-gateway .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]