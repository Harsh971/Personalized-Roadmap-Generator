from neo4j import GraphDatabase

# Neo4j Connection
URI = "bolt://neo4j:7687"  # Update if your Neo4j URL is different
USERNAME = "<<neo4j-username>>"
PASSWORD = "<<neo4j-password>>"

class Neo4jTest:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_roadmap(self, topic, content):
        with self.driver.session() as session:
            session.write_transaction(self._create_roadmap, topic, content)

    def get_roadmap(self, topic):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_roadmap, topic)
            return result

    @staticmethod
    def _create_roadmap(tx, topic, content):
        query = """
        MERGE (r:Roadmap {topic: $topic})
        SET r.content = $content
        """
        tx.run(query, topic=topic, content=content)

    @staticmethod
    def _get_roadmap(tx, topic):
        query = "MATCH (r:Roadmap {topic: $topic}) RETURN r.content AS content"
        result = tx.run(query, topic=topic)
        return [record["content"] for record in result]

if __name__ == "__main__":
    neo4j_test = Neo4jTest(URI, USERNAME, PASSWORD)

    # Test creating a roadmap
    neo4j_test.create_roadmap("Docker", "Final roadmap content for Docker.")

    # Retrieve roadmap
    roadmap = neo4j_test.get_roadmap("Docker")
    print("Retrieved Roadmap:", roadmap)

    neo4j_test.close()
