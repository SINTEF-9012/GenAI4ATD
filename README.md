# GenAI4ATD

Python scripts to extract data from technical debt (TD) assessments tools, build prompts and run chats with a Large
Language Model (LLM) through the [Ollama](https://ollama.com/) API.

## Limitations

Currently, the prototype only supports [Arcan](https://www.arcan.tech/) as a TD assessment tool.
It also only supports Java projects.

It should be in the future expanded to support [Designite](https://www.designite-tools.com/) and C# projects.

## Pre-requisites 

- Ollama
- Arcan CLI
- Python 3.12

```bash
pip install -r requirements.txt
```

## Usage examples

### Chat with a LLM about a one-version analysis

Run a one-version analysis on the Java project of your choice.

Using the output of the analysis, run the merger to merge the results in one file. 

Here the Arcan output is located
at ```./arcanOutput/myproject``` and we want the merged file at ```./genai4atdOutput/merger-output```. The repository
containing the project is located at ```./projects/myproject```.

```bash 
python merger_run.py ./arcanOutput/myproject ./genai4atdOutput/merger-output JAVA -r ./projects/myproject -e
```

We want to generate an examples file, which is a file that contains one smell of each kind retrieved from the data,
so we will use the ```--examples``` (```-e```) option.

It is possible for the merger to additionally retrieve the full lines of codes where each dependency is used in a class,
using the ```--loc``` (```-l```) option. As for now, it has not given us great results with the LLM, we do not recommend 
it.

Now we have the merged file at ```./genai4atdOutput/merger-output/myproject-merged.csv``` and the example file at
```./genai4atdOutput/merger-output/myproject-merged-examples.csv.```

Next we need to build the prompt file.

```bash 
python build_prompt_run.py ./genai4atdOutput/merger-output/myproject-merged-examples.csv ./genai4atdOutput/prompts-output JAVA -dep -def --json
```

We want the dependencies of each component in the prompt as well as definitions for smells and metrics (from the Arcan
documentation) included in the context, so we use the ```--dependencies``` (```-dep```) and ```--definitions``` 
(```-def```) options.

We also want the smell data in JSON format. We can write it in natural language, but it gave us longer prompts and no
better results than JSON.

Now we have the prompt file at ```./genai4atdOutput/prompts-output/json/defs/prompt_with_dependencies.json```

Finally, we can run the chat with the LLM. The API is at ```http://localhost:11434/api/chat``` and we want to use
the Llama 3 model.

```bash
python chat_run.py ./genai4atdOutput/prompts-output/json/defs/prompt_with_dependencies.json ./genai4atdOutput/chats-output http://localhost:11434/api/chat llama3 --json -def
```

```--json``` and ```-def``` options to specify that the prompt is in JSON format and contains definitions.

### Chat with a LLM about an evolution analysis

Run an evolution analysis on the Java project of your choice.

Using the output of the analysis, run the smell tracker. It will track smells across version to see if they increase,
decrease or disappears. When there is a variation or a disappearance, it can also retrieve the diff and/or commit history
of the relevant components.

Here the Arcan output is located at ```./arcanOutput/myproject-evo``` and we want the merged file at 
```./genai4atdOutput/smell-track-output```. The repository containing the project is located at ```./projects/myproject```.

```bash
python smell_tracker_run.py ./arcanOutput/myproject ./genai4atdOutput/smell-track-output ./projects/myproject JAVA -diffs -commits -e
```

We want the diffs and commit histories of the relevants components when there is a variation, and also an examples file
containing only smells that varied or disappeared, so we use the ```--ATDIVarDiffs``` (```-diffs```), 
```--ATDIVarCommitHistory``` (```-commits```) and ```--examples``` (```-e```) options.

Now we have the smell track file at ```./genai4atdOutput/smell-track-output/smell_track_myproject_evo.json``` and the 
example file at ```./genai4atdOutput/smell-track-output/smell_track_myproject_evo_example.json```

Next we can run the chat with the LLM. The API is at ```http://localhost:11434/api/chat``` and we want to use
the Llama 3 model.

```bash
python chat_run.py ./genai4atdOutput/smell-track-output/myproject_evo_smell_track_example.json ./genai4atdOutput/chats-output http://localhost:11434/api/chat llama3 -evo
```

We use the ```--evolution``` (```-evo```) option to specify that this is an evolution analysis.