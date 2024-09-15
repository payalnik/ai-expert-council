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

## Creating and Using Expert Files

You can create a file to load experts into the simulation. The file should list each expert on a new line with their expertise and personality traits. Here's an example of how to create and use an expert file:

1. Create a file named `app-experts.txt` with the following content:

   ```
   Steve (Expertise: CPO for LinkedIn, Personality: Straightforward and results-oriented)
   Maria (Expertise: User advocate, Personality: Kind but has strong opinions on positive and negative outcomes)
   Sasha (Expertise: Generative AI and applications, Personality: Curious and open-minded)
   Ken (Expertise: Career Coach with a lot of knowledge on the audience, Personality: Open minded and willing to share experience)
   Sadder (Expertise: Created a career course but couldn't find enough participants to sustain it, Personality: Open and direct)
   ```

2. Use the `/add` command followed by the filename to load these experts into the simulation:

   ```bash
   python expert-council.py /add app-experts.txt
   ```

This will add the experts from the file into the simulation, allowing you to start discussions with them.

You can load experts from a file using the `/add` command followed by the filename. Below is an example of how the experts file should be formatted:

```
Steve (Expertise: CPO for LinkedIn, Personality: Straightforward and results-oriented)
Maria (Expertise: User advocate, Personality: Kind but has strong opinions on positive and negative outcomes)
Sasha (Expertise: Generative AI and applications, Personality: Curious and open-minded)
Ken (Expertise: Career Coach with a lot of knowledge on the audience, Personality: Open minded and willing to share experience)
Sadder (Expertise: Created a career course but couldn't find enough participants to sustain it, Personality: Open and direct)
```

## License

This project is licensed under the MIT License.
