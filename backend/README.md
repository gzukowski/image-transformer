## Setup
1. Set .env
2. Apply migrations
    ```
    uv run alembic upgrade head
    ```
3. Generating migrations
   ```
   uv run alembic revision --autogenerate -m "Init"
   ```
4. placeholder