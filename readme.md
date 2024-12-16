# Retrieval-Augmented Generation (RAG) for Buildings’ Technical Documents
My proposal is to use RAG to recover information from the hundreds of thousands of buildings’ technical documents generated during their construction process. Commercial buildings offer a large amount of data specifying their structure, equipment, operational details, control philosophy specifications and more. These documents often consist of a set of unstructured PDFs, stored within their private servers.

The sheer amount of documents makes it difficult to manually find critical information that might be useful to engineers, operational & maintenance staff or compliance audits. Moreover, the implementation of intelligent systems often relies on particular constraints regarding the buildings’ internal operation to be met, or for specific properties to be present, thus an automated tool for retrieving these details would severely improve the overall agility of such procedures, ergo lowering costs, as less time is required for gathering the correct documents and information.

Being technical documents, the vocabulary and semantics associated with the aforementioned data can be rather distinct, with a prevalence of terms and abbreviations that are exclusive to buildings and their respective equipment and contractors. Henceforth, the creation of embeddings might require special treatment to account for their distinctiveness compared to natural language. Furthermore, a hybrid search might be considered, given that the myriad of domain specific terms can potentially hinder an approach that relies solely on semantic searching.


## Steps of the pipeline
* Gather data
* Parse the PDFS
* Create embeddings
* Syntax search

## Data Analysis
The data belongs to a private client, and some of its core contents are disclosed.
From all the files avvailable, their content, naming, hierarchy or file type lack any helpful convention.
We extracted 609 pdf files from the dataset, and their textual information was later extracted using the pypdf library.


## Project Structure
The following figure illustrates how the project was organized:

-------- figure here --------

The user interacts with a bot made using BLIP, which handles the front end of the application.
CHROMADB was the database solution of choice, for providing a convenient way to embed the textual information.
The RAG itself was made using gemini for both the generation of embeddings as for the backbone of the prompts.

## RAG

## Results

## Conclusions
