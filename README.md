# Expert Council Simulation

This project simulates an expert council where multiple AI experts can be added to discuss various topics. The user can interact with the council by adding experts and initiating discussions.

## Features

- Add AI experts with specific expertise and personality traits.
- Simulate discussions with multiple experts.
- Save and load the state of the council.

## Setup

1. Clone the repository.
2. Ensure you have Python installed.
3. Install the required packages:
   ```bash
   pip install openai
   ```
4. Create a `config.json` file with your OpenAI API key:
   ```json
   {
       "api_key": "your-api-key-here"
   }
   ```

## Usage

Run the main script to start the simulation:

```bash
python expert-council.py
```

You can add experts and start discussions through the command line interface.

## License

This project is licensed under the MIT License.
