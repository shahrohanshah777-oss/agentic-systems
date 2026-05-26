# The Problem

A coaching institute wants to build a support assistant for student questions. The institute has:

500 FAQ articles about fees, refunds, login issues, placements, and certificates.
A SQL database with student profiles, payments, and order/status records.
A future plan to use a vector database for meaning-based retrieval.
Create a clear design plan for how the institute should use SQL, embeddings, and a vector database together.

# The solution

## Which data should stay in SQL
- **Student Profiles**: This includes student IDs, names, contact information, and enrollment details. This data is structured and can be easily queried for specific information.
- **Payments**: Records of payment transactions, including payment totals, dates, and methods. This allows for quick retrieval of financial information and status.
- **Order/Status Records**: Information about course enrollments, completion status, and certificate issuance. This helps in tracking student progress and providing updates on their course status.

## Which data should go into the vector database
- **FAQ Articles**: The 500 FAQ articles should be chunked into smaller sections (e.g., paragraphs or sentences) and embedded into vectors. This allows for meaning-based retrieval when students ask questions that may not match the exact wording of the FAQs but are semantically similar.

## Metadata to store with each vector
- **Article ID**: A unique identifier for each FAQ article to link back to the original content.
- **Chunk Position**: The position of the chunk within the article (e.g., paragraph number) to provide context for the retrieved information.
- **Topic Tags**: Keywords or tags related to the content of the chunk (e.g "fees", "refunds", "login issues") to help with filtering and relevance.
- **Last Updated**: A timestamp indicating when the FAQ article was last updated to ensure that the information is current and relevant.

## Query-time flow
1. **User Question**: A student asks a question related to fees, refunds, login issues, placements, or certificates.
2. **Query Embedding**: The user's question is converted into a vector embedding using a language model.
3. **Vector Search**: The embedded query is compared against the stored vectors in the vector database to find the most relevant chunks of information.
4. **Top-k Chunks**: The system retrieves the top-k most relevant chunks based on similarity scores.
5. **Final Application Use**: The retrieved chunks are then used to generate a response to the user's question, either by directly providing the information or by using it to inform a more complex response generation process.

## Why brute force is not enough at scale- 
- **Performance Issues**: As the number of stored vectors increases, comparing every query with every vector becomes computationally expensive and slow, leading to long response times.
- **Indexing and ANN**: To address this, indexing techniques (like KD-trees or HNSW) and Approximate Nearest Neighbor (ANN) algorithms can be used to quickly narrow down the search space, allowing for faster retrieval of relevant vectors without needing to compare against every single vector.
       
## One exact-match example and one similarity-search example
- **Exact-Match Example**: A student asks, "What is the total fee for the Data Science course?" This can be directly answered by querying the SQL database for the payment totals associated with the Data Science course.
- **Similarity-Search Example**: A student asks, "How can I get a refund if I am not satisfied with the course?" This question may not match any FAQ article word-for-word, but a vector similarity search can retrieve relevant chunks from the FAQ articles that discuss refund policies and procedures, providing a helpful response to the student's query.