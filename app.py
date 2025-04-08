from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from neo4j import GraphDatabase
import google.generativeai as genai
import socket
import json
import re

# ==== Configure Gemini API ====
genai.configure(api_key="<<Gemini-key>>")  
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')  

# ==== Neo4j Configuration ====
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USERNAME = "<<neo4j-username>>"
NEO4J_PASSWORD = "<<neo4j-password>>"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# ==== Flask App Setup ====
app = Flask(__name__)
CORS(app)

# ==== Neo4j: Fetch roadmap ====
def fetch_from_neo4j(topic):
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Topic {name: $topic})-[:HAS_SUBTOPIC]->(s:Subtopic)
            OPTIONAL MATCH (s)-[:HAS_CONCEPT]->(c:Concept)
            RETURN t.name AS topic, s.name AS subtopic, collect(c.name) AS concepts
        """, topic=topic)

        data = {}
        for record in result:
            subtopic = record["subtopic"]
            concepts = [c for c in record["concepts"] if c is not None]
            data[subtopic] = concepts

        return data if data else None

# ==== Neo4j: Save roadmap ====
def save_to_neo4j(topic, roadmap):
    with driver.session() as session:
        session.run("MERGE (t:Topic {name: $topic})", topic=topic)
        for subtopic, concepts in roadmap.items():
            session.run("""
                MATCH (t:Topic {name: $topic})
                MERGE (s:Subtopic {name: $subtopic})
                MERGE (t)-[:HAS_SUBTOPIC]->(s)
            """, topic=topic, subtopic=subtopic)

            for concept in concepts:
                session.run("""
                    MATCH (s:Subtopic {name: $subtopic})
                    MERGE (c:Concept {name: $concept})
                    MERGE (s)-[:HAS_CONCEPT]->(c)
                """, subtopic=subtopic, concept=concept)

# ==== Ask Gemini for Roadmap ====
def ask_gemini_for_roadmap(topic):
    prompt = f"""Create a structured learning roadmap for the topic: {topic}.
List main subtopics and under each, list key concepts or skills to be learned. Return only a dictionary in JSON format. Example:
{{
  "Subtopic 1": ["Concept A", "Concept B"],
  "Subtopic 2": ["Concept X", "Concept Y"]
}}"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip().strip("```json").strip("```").strip()
        roadmap = json.loads(response_text)
        return roadmap
    except Exception as e:
        return {"error": f"LLM failed: {e}"}

# ==== Route: Generate Personalized Roadmap ====
@app.route("/personalized-roadmap", methods=["POST"])
def generate_personalized_roadmap():
    data = request.get_json()
    topic = data.get("topic")
    ratings = data.get("ratings")

    if not topic or not ratings:
        return jsonify({"error": "Missing topic or ratings"}), 400

    low_rated_subtopics = [sub for sub, score in ratings.items() if score <= 5]

    if not low_rated_subtopics:
        return jsonify({
            "message": "You rated yourself high in all areas. No roadmap needed!",
            "low_rated_subtopics": []
        })

    prompt = f"""The user is learning '{topic}' and rated themselves low (1–5) in the following subtopics:
{', '.join(low_rated_subtopics)}.

Generate a learning roadmap ONLY for these subtopics. Under each, include key concepts or skills to learn.
Respond ONLY with a valid JSON dictionary like this:
{{
  "Subtopic 1": ["Concept A", "Concept B"],
  "Subtopic 2": ["Concept X", "Concept Y"]
}}"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if not match:
            raise ValueError("No JSON object found in the response")

        roadmap = json.loads(match.group())

        save_to_neo4j(topic, roadmap)

        return jsonify({
            "source": "LLM (personalized)",
            "topic": topic,
            "low_rated_subtopics": low_rated_subtopics,
            "personalized_roadmap": roadmap
        })

    except Exception as e:
        return jsonify({"error": f"Failed to generate personalized roadmap: {e}"}), 500

# ==== Route: Get Subtopics ====
@app.route("/subtopics", methods=["GET"])
def get_subtopics():
    topic = request.args.get("topic")
    if not topic:
        return jsonify({"error": "Missing topic"}), 400
    try:
        roadmap = fetch_from_neo4j(topic)
        if not roadmap:
            roadmap = ask_gemini_for_roadmap(topic)
        subtopics = list(roadmap.keys())
        return jsonify({"topic": topic, "subtopics": subtopics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==== Route: Homepage ====
@app.route("/")
def index():
    return render_template("index.html")

# ==== Run Server ====
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
