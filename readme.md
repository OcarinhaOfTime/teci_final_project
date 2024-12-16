# Retrieval-Augmented Generation (RAG) for Buildings’ Technical Documents
My proposal is to use RAG to recover information from the hundreds of thousands of buildings’ technical documents generated during their construction process. Commercial buildings offer a large amount of data specifying their structure, equipment, operational details, control philosophy specifications and more. These documents often consist of a set of unstructured PDFs, stored within their private servers.

The sheer amount of documents makes it difficult to manually find critical information that might be useful to engineers, operational & maintenance staff or compliance audits. Moreover, the implementation of intelligent systems often relies on particular constraints regarding the buildings’ internal operation to be met, or for specific properties to be present, thus an automated tool for retrieving these details would severely improve the overall agility of such procedures, ergo lowering costs, as less time is required for gathering the correct documents and information.

Being technical documents, the vocabulary and semantics associated with the aforementioned data can be rather distinct, with a prevalence of terms and abbreviations that are exclusive to buildings and their respective equipment and contractors. Henceforth, the creation of embeddings might require special treatment to account for their distinctiveness compared to natural language. Furthermore, a hybrid search might be considered, given that the myriad of domain specific terms can potentially hinder an approach that relies solely on semantic searching.


## Data Analysis
The data used in this study is proprietary and contains sensitive information, some of which has been disclosed. The available files lack standardized conventions in terms of content, naming, hierarchy, or file type. From the dataset, 609 PDF files were extracted, and their textual information was subsequently processed using the PyPDF library. A pre-processing step was then performed, which involved splitting the text into manageable chunks, creating embeddings for these chunks, and storing them in a persistent database for future retrieval and analysis.

## Project Structure
The following figure illustrates how the project was organized:

-------- figure here --------

The user interacts with a bot made using BLIP, which handles the front end of the application.
CHROMADB was the database solution of choice, for providing a convenient way to embed the textual information.
The RAG itself was made using gemini for both the generation of embeddings as for the backbone of the prompts.

## RAG
The RAG was organized by the following steps:
* Query transformation: The input query is transformed in a sample answer by Gemini, and then the result is utilized to create an embedding.
* Syntatic Search: The top 10 chunks are selected to became the context of the question.
* Prompt Composition: A template is filled with the question, the formatting instructions, the context and the output format (as a json), which is then sent to gemini.
* Answer Validation: The first output is scrutinized to assess its validity by another API call to Gemini, aiming to mitigate the cases where the LLM hallucinates an answer without enough context
* Results Report: At last, the user receives its answer, and in case a suitable result was produced, the document and page where the answer was found are also provided.

## Results


## Conclusions
The results indicate that RAG is a promising approach for retrieving information from an unstructured collection of technical documents. Empirical tests demonstrated that the system provided several accurate responses, and the automatically generated questions exhibited a high level of accuracy.

The validation component of the system helped mitigate issues related to hallucination when insufficient context accompanied the question. However, such scenarios remain a significant challenge. This may be attributed to the simplicity of the model, as it was based on the free version of Gemini; employing a more advanced model could potentially address these issues.

For future work, in addition to exploring alternative language models, it would be beneficial to incorporate non-textual elements from the dataset, further enhancing the system's performance.
