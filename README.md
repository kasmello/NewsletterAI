# CrewAI

This project loads `CLAUDE_API_KEY` from a single `.env` file using `python-dotenv`.

## Usage

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy the example env file:

   ```bash
   cp .env.example .env
   ```

3. Add your API key to `.env`:

   ```dotenv
   CLAUDE_API_KEY=your-claude-api-key
   SERPER_API_KEY=your-serper-api-key
   ```

4. Run the app:

   ```bash
   python main.py
   ```
