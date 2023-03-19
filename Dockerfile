FROM python:3.9-slim

WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application contents
COPY service/ ./service/
RUN useradd --uid 1000 theia
RUN chown -R theia:theia /app
USER theia
# Run the service
EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "service:app"]