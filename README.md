# README

## Open AI Agent with Routing Agent for Business Databases

This repository contains a demonstration of an Open AI Agent with a Routing Agent designed to manage business-related databases. The project is written in Python and uses the Pydantic library for data validation and settings management using Python type annotations.

### Project Structure

The project is structured as follows:

```plaintext
project-root/
│
├── database/
│   ├── db.py          # Database connection and setup
│   ├── models.py      # Database models/schemas
|   └── utils.py       # Database utilities
│
├── tools/
│   ├── base.py        # Base class for tools
│   ├── add_data.py    # Tool for adding data to the database
│   ├── query_data.py  # Tool for querying data from the database
|   └── utils.py       # Tool utilities
│
├── agents/
│   ├── base.py            # Main AI agent logic
│   ├── routing_agent.py   # Specialized agent for routing tasks
|   └── utils.py           # agent utilities
│
└── utils.py           # Utility functions and classes
```

### Setup

To use this code, you need to add a `.env` file to the root directory of the project. This file should contain your OpenAI API key, like so:

```env
OPENAI_API_KEY=your-api-key-here
```

Replace `your-api-key-here` with your actual OpenAI API key.

### Usage

To run the code, open the `run.ipynb` notebook in a Jupyter environment and execute the cells in order.


Please ensure these are installed before running the code.

### Contributing

Contributions are welcome. Please open an issue to discuss your ideas before making a pull request.

### License

This project is licensed under the terms of the MIT license.