<div align="center">
  <table>
    <tr>
      <td><h1>LLMOps Workshop</h1></td>
      <td align="right"><img src="https://upload.wikimedia.org/wikipedia/fr/thumb/8/86/Logo_CentraleSup%C3%A9lec.svg/700px-Logo_CentraleSup%C3%A9lec.svg.png?20190428215410" alt="CentraleSupélec Logo" width="200"/></td>
    </tr>
  </table>
</div>

Fatma's work

> The slides that were presented are in the moodle 🥸 

---


## Workshop Goals

- [ ] Understand the foundations of Large Language Models and their deployment challenges
- [ ] Master some practical techniques for building LLM applications
- [ ] Learn a touch about optimization, testing, evaluation, and DevOps 

### Prerequisites

In order to successfully complete this workshop, it will be nice to have :

- Python programming experience (at least OOP concepts)
- Working knowledge of Git and GitHub
- Familiarity with API architectures
- Basic knowledge of Docker

### Hands on

This workshop consists of two practical exercises (TPs) and one lab project that will help you apply the concepts learned during lectures. 

The sequence of assignments is designed to progressively advance you through different development environments and paradigms, from interactive jupyter notebooks to scripts to a full FastAPI implementation 😎


#### TP1: Chroma & Langchain Quickstart

This notebook exercise will help you understand the frameworks [chromadb](https://docs.trychroma.com/docs/overview/introduction) and [langchain](https://python.langchain.com/docs/introduction/), and their basic concepts like :

- Connect to a Chroma database running in Docker
- Create collections and add documents
- Query vector collections
- Work with LangChain components for LLM applications
- Implement parsing for structured LLM outputs
- Interact with ChromaDB and Langchain
- Upload, process, and query PDF documents in a vector database

> You just need to RTFM and play with the notebook 🤗 
 
#### TP2: Local PDF RAG System

In this exercise, you will build a PDF Retrieval Augmented Generation (RAG) system using local models [Ollama](https://ollama.com) that can answer questions about PDF documents without sending the PDFs to external servers. 

> This meets the requirements of organizations dealing with sensitive information like legal firms 🕵️

**Key components you'll implement:**
- Document loading and processing
- Text splitting and chunking
- Vector embedding generation
- Vector database creation and querying
- Retrieval QA chain setup
- Interactive question answering

You'll use a simple shell-based interface to query the system about uploaded PDFs, with an option for structured output responses. 

> See more in the dedicated README in the TP2 folder.

### LAB : Building a tiny LLM Server Gateway with FastAPI 🐳

In this lab project, you will build a unified API gateway that can handle the communication with various LLM providers.

The gateway will serve as a middleware layer that standardizes requests and responses across multiple LLM services including [OpenAI](https://platform.openai.com/docs/overview?lang=python), [Anthropic](https://docs.anthropic.com/en/docs/welcome), [Groq](https://console.groq.com/docs/overview), and locally hosted models via [Ollama](https://github.com/ollama/ollama/tree/main/docs).

**🛠️ Some key features of your mission 🛠️**
- FastAPI app connecting multiple providers with extension capabilities
- Robust error handling and logging
- Rate limiting and request validation
- Caching mechanisms for optimization
- Fallback strategies
- Testing driven strategy
- Docker local deployment 

--- 

## Submission Guidelines

All code for the workshop (tps and lab) should be coded **in your personal GitHub account in a PUBLIC repository**. Please make sure to follow the 4 steps below :

1. Create a separate repository for this workshop (or one for each activities but explain this when you are at the step 4)
2. Organize your code according to the provided guidelines as much as possible 
3. Write detailed documentation and README files for the hands on section 
4. **Share your repository link** at my cs email address

Your repository should be clean and well organized, with documentation of each part of your implementation 😇

### Issues

If you encounter any issues or have coding questions during the workshop, please follow this procedure :

1. **Open a git issue in your repository** with a clear description of your problem 
2. Include screenshots if applicable to help illustrate the issue
3. Tag me in the issue and/or send an email notification 
4. Use descriptive titles for your issues (like "Error connecting to Chroma database in TP2" rather than "Not working... Help plz🥲")

Please check the existing issues before creating yours (you are not the only one with your problem) 🥹 


### Evaluation 

Your work will be evaluated based on the following criteras :

- [ ] Functionality and completeness of implementations (see more in the dedicated README in the LAB folder)
- [ ] Problem-solving approaches
- [ ] Testing and error handling
- [ ] Documentation quality


--- 

## Env set Up  

Create a conda env and install the required dependencies with the commands below : 

```
conda create -n llmops python=3.12 -y 
conda activate llmops
```

then

```
pip install -r requirements.txt
```

and access the created env inside your jupyter server : 

```
python -m ipykernel install --user --name=llmops
```

Happy coding 🤗

