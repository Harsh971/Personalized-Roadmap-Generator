# LLMOps Personalized Roadmap Generator

The **LLMOps Personalized Roadmap Generator** is a learning platform that leverages large language models (LLMs) and graph databases to create customized learning roadmaps for users. The project uses Google’s Gemini API to generate structured learning plans based on a user’s topic of interest. These roadmaps break down the topic into subtopics and key concepts. The resulting data is stored in a Neo4j graph database, allowing users not only to retrieve personalized learning paths via a RESTful Flask API but also to visualize how topics, subtopics, and concepts are interconnected using Neo4j’s powerful graph visualization tools.

## Project Overview

### **Process Flow**

1. **User Input & UI Interaction:**
   - Users visit the web interface served by the Flask application (at `http://127.0.0.1:5001/`).
   - They input a topic they wish to learn about (for example, "Docker").

2. **Generating Learning Roadmaps:**
   - The Flask app interacts with Google’s Gemini API by sending a prompt that asks for a structured learning roadmap. The Gemini LLM responds with a JSON-formatted dictionary of subtopics and associated key concepts.
   - In addition, if the user provides self-assessment ratings for each subtopic (e.g., rating their knowledge on "Containers" or "Networking"), a personalized roadmap is generated that focuses on weaker areas.

3. **Storing Data in Neo4j:**
   - Once the roadmap is generated by the LLM, the Flask app stores the structured data into a Neo4j graph database.
   - In Neo4j, each **Topic** is represented as a node. It is linked via relationships (edges) to **Subtopic** nodes, which in turn connect to individual **Concept** nodes. This graph structure allows for efficient querying and visualizations that help illustrate how different learning components are related.
   - Users (or administrators) can explore this graph using the Neo4j Browser (at `http://localhost:7474`), viewing how various learning objectives are connected.

4. **User Benefits:**
   - **Personalized Learning Roadmaps:** Users receive a learning plan that highlights weaker areas and suggests key topics and skills to focus on.
   - **Interactive Graph Visualization:** Using Neo4j, the underlying learning structure is visualized as a graph, making it easier to understand the relationships between topics and the progression of learning.
   - **Seamless Integration of LLMs:** The combination of a state-of-the-art generative model (Google Gemini) and graph databases provides a cutting-edge solution for adaptive learning.
   - **Containerized Environment:** The entire application stack is containerized using Docker, ensuring a consistent and reproducible setup across environments.

### **How Neo4j is Used**

- **Graph Data Modeling:** Neo4j is used to model the learning roadmap as a graph. This includes:
  - **Topic Nodes:** Represent the high-level subject (e.g., "Docker").
  - **Subtopic Nodes:** Detail the major categories or modules within the topic.
  - **Concept Nodes:** Outline the individual skills or concepts related to each subtopic.
- **Relationships:** The graph database stores relationships between topics, subtopics, and concepts, enabling queries that can retrieve structured learning roadmaps and support advanced analytics.
- **Visualization:** Users can use the Neo4j Browser to visually inspect the roadmap. This interactive graph view helps to identify learning paths and the interconnections between various learning components.

---

## Prerequisites

Before running the application, ensure you have the following installed on your system:
- **Docker** – for containerizing the app and database  
- **Python 3.10** – for the local virtual environment (if you plan on making local modifications)  
- **Git** – for cloning this repository

> **Important:** Before building the Docker image, you need to perform some manual configuration:
> 1. **Generate a Google Gemini API Key:**  
>    - Visit the [Google Gemini API Console](https://cloud.google.com/generative-ai) (or the appropriate URL) and generate your API key.
>    - **Update the file where the Gemini key is configured** (currently, in `app.py`) by replacing the placeholder with your key.
>
> 2. **Choose a Neo4j User ID and Password:**  
>    - Decide on a username and password for Neo4j (e.g., `neo4j` and `harsh123`).
>    - **Update all the files that contain Neo4j credentials:**  
>      - `app.py`  
>      - `neo4j_test.py`  
>      - `seed_roadmaps.py`  
>    Replace the existing username and password with your chosen values.
>
> Once these changes are made, continue with the Docker build steps below.

## Setup Instructions

Follow these steps to get the application up and running:

### 1. System Update and Certificates

Update your system and reinstall CA certificates to ensure secure connections:

```bash
sudo apt-get update
sudo apt-get install --reinstall ca-certificates
```

### 2. Install Python and Create a Virtual Environment
Pull the official Python image (if needed):

```bash
docker pull python
```

Add the necessary PPA for Python 3.10 and create a virtual environment:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
python3.10 -m venv genai-env
```
Activate the virtual environment and update pip:
```bash
source genai-env/bin/activate
pip install --upgrade pip
```

Install the necessary Python package for Gemini integration:
```bash
pip install google-generativeai
```

### 3. [Pre-Build Configuration] Update API and Neo4j Credentials
Before proceeding further, perform the following manual configuration:
- Google Gemini API Key:

In the file app.py, find the following line:
```bash
genai.configure(api_key="YOUR_API_KEY_HERE")
```
Replace ```"YOUR_API_KEY_HERE"``` with your actual Google Gemini API key.

- Neo4j Credentials:

In the following files, locate and update the Neo4j credentials to match your chosen userid and password:
```app.py```, ```neo4j_test.py```,``` seed_roadmaps.py```
For example, change these lines:
```bash
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "harsh123"
```
to use the username and password of your choice.

Once you have updated these four files, you are ready to build the Docker image.

### 4. Build the Flask Application Docker Image
Make sure your ```Dockerfile``` is in the repository root. Then build the Docker image:
```bash
docker build -t flask_neo4j_app .
```

### 5. Run the Neo4j Container
Start a Neo4j container with the credentials you configured (e.g., username: ```neo4j``` and password: ```harsh123```):
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/harsh123 \
  neo4j
```

### 6. Run the Flask Application Container
Run the Flask application container and link it to the Neo4j container so that the hostname ```neo4j``` is available inside the Flask container:
```bash
docker run -d \
  --name flask_app \
  --link neo4j \
  -p 5001:5001 \
  flask_neo4j_app
```

---------
## Application Usage
- Web View (Flask API):

Open your browser and navigate to:
```bash
http://127.0.0.1:5001/
```
This is the landing page served by the Flask application, which allows users to input topics and generate personalized learning roadmaps.


- Neo4j Graph View:

To view the graph data stored in Neo4j, open your browser and navigate to:
```bash
http://localhost:7474
```
Log in with the credentials you set (e.g., ```neo4j``` / ```harsh123```). You can then run Cypher queries like:
```bash
MATCH (n) RETURN n LIMIT 50;
```
to view the stored nodes and relationships.


---------
## Cleanup
To stop and remove containers:
```bash
docker stop flask_app neo4j
docker rm flask_app neo4j
```
To remove the built Docker image:
```bash
docker rmi flask_neo4j_app
```






