from neo4j import GraphDatabase

# Neo4j Connection
URI = "bolt://neo4j:7687"
USERNAME = "<<neo4j-username>>"
PASSWORD = "<<neo4j-password>>"

class SeedRoadmaps:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def seed_data(self):
        with self.driver.session() as session:
            session.write_transaction(self._seed_topics)

    @staticmethod
    def _seed_topics(tx):
        topics = [
            {"topic": "Docker", "subtopics": ["Intro", "Images", "Containers"]},
            {"topic": "DSA", "subtopics": ["Arrays", "Linked Lists", "Trees"]}
        ]
        for t in topics:
            query = """
            MERGE (t:Topic {name: $topic})
            WITH t
            UNWIND $subtopics AS subtopic
            MERGE (s:Subtopic {name: subtopic})
            MERGE (t)-[:HAS_SUBTOPIC]->(s)
            """
            tx.run(query, topic=t["topic"], subtopics=t["subtopics"])

if __name__ == "__main__":
    seeder = SeedRoadmaps(URI, USERNAME, PASSWORD)
    seeder.seed_data()
    print("Database seeded successfully!")
    seeder.close()
