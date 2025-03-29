import os
import sys
import uuid
import sqlite3
from typing import List, Dict, Any, Callable, Optional, Generator, Tuple
from io import BytesIO
from pathlib import Path

from azure.storage.blob import BlobProperties
from azwrap import Container, BlobType

from langchain_text_splitters import TokenTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.llms import BaseLLM
from langchain_core.runnables import RunnableSerializable
from langchain_openai import ChatOpenAI

class BlobGraphBuilder:

    chunk_size: int
    chunk_overlap: int
    text_splitter: TokenTextSplitter

    prompt_template: str = """
    -Goal-
    Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

    -Steps-
    1. Identify all entities. For each identified entity, extract the following information:
    - entity_name: Name of the entity, capitalized
    - entity_type: One of the following types: [large language model, differential privacy, federated learning, healthcare, adversarial training, security measures, open-source tool, dataset, learning rate, AdaGrad, RMSprop, adapter architecture, LoRA, API, model support, evaluation metrics, deployment, Python library, hardware accelerators, hyperparameters, data preprocessing, data imbalance, GPU-based deployment, distributed inference]
    - entity_description: Comprehensive description of the entity's attributes and activities
    Format each entity as ("entity"{{tuple_delimiter}}<entity_name>{{tuple_delimiter}}<entity_type>{{tuple_delimiter}}<entity_description>)

    2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
    For each pair of related entities, extract the following information:
    - source_entity: name of the source entity, as identified in step 1
    - target_entity: name of the target entity, as identified in step 1
    - relationship_description: explanation as to why you think the source entity and the target entity are related to each other
    - relationship_strength: an integer score between 1 to 10, indicating strength of the relationship between the source entity and target entity
    Format each relationship as ("relationship"{{tuple_delimiter}}<source_entity>{{tuple_delimiter}}<target_entity>{{tuple_delimiter}}<relationship_description>{{tuple_delimiter}}<relationship_strength>)

    3. Return output in The primary language of the provided text is "English." as a single list of all the entities and relationships identified in steps 1 and 2. Use **{{record_delimiter}}** as the list delimiter.

    4. If you have to translate into The primary language of the provided text is "English.", just translate the descriptions, nothing else!

    5. When finished, output {{completion_delimiter}}.

    -Examples-
    ######################

    Example 1:

    entity_types: [large language model, differential privacy, federated learning, healthcare, adversarial training, security measures, open-source tool, dataset, learning rate, AdaGrad, RMSprop, adapter architecture, LoRA, API, model support, evaluation metrics, deployment, Python library, hardware accelerators, hyperparameters, data preprocessing, data imbalance, GPU-based deployment, distributed inference]
    text:
    LLMs to create synthetic samples that mimic clients’ private data distribution using
    differential privacy. This approach significantly boosts SLMs’ performance by approximately 5% while
    maintaining data privacy with a minimal privacy budget, outperforming traditional methods relying
    solely on local private data.
    In healthcare, federated fine-tuning can allow hospitals to collaboratively train models on patient data
    without transferring sensitive information. This approach ensures data privacy while enabling the de-
    velopment of robust, generalisable AI systems.
    8https://ai.meta.com/responsible-ai/
    9https://huggingface.co/docs/hub/en/model-cards
    10https://www.tensorflow.org/responsible_ai/privacy/guide
    101 Frameworks for Enhancing Security
    Adversarial training and robust security measures[111] are essential for protecting fine-tuned models
    against attacks. The adversarial training approach involves training models with adversarial examples
    to improve their resilience against malicious inputs. Microsoft Azure’s
    ------------------------
    output:
    ("entity"{{tuple_delimiter}}DIFFERENTIAL PRIVACY{{tuple_delimiter}}differential privacy{{tuple_delimiter}}Differential privacy is a technique used to create synthetic samples that mimic clients' private data distribution while maintaining data privacy with a minimal privacy budget{{record_delimiter}}
    ("entity"{{tuple_delimiter}}HEALTHCARE{{tuple_delimiter}}healthcare{{tuple_delimiter}}In healthcare, federated fine-tuning allows hospitals to collaboratively train models on patient data without transferring sensitive information, ensuring data privacy{{record_delimiter}}
    ("entity"{{tuple_delimiter}}FEDERATED LEARNING{{tuple_delimiter}}federated learning{{tuple_delimiter}}Federated learning is a method that enables collaborative model training on decentralized data sources, such as hospitals, without sharing sensitive information{{record_delimiter}}
    ("entity"{{tuple_delimiter}}ADVERSARIAL TRAINING{{tuple_delimiter}}adversarial training{{tuple_delimiter}}Adversarial training involves training models with adversarial examples to improve their resilience against malicious inputs{{record_delimiter}}
    ("entity"{{tuple_delimiter}}SECURITY MEASURES{{tuple_delimiter}}security measures{{tuple_delimiter}}Robust security measures are essential for protecting fine-tuned models against attacks{{record_delimiter}}
    ("relationship"{{tuple_delimiter}}DIFFERENTIAL PRIVACY{{tuple_delimiter}}FEDERATED LEARNING{{tuple_delimiter}}Differential privacy is used in federated learning to maintain data privacy while training models collaboratively{{tuple_delimiter}}8{{record_delimiter}}
    ("relationship"{{tuple_delimiter}}HEALTHCARE{{tuple_delimiter}}FEDERATED LEARNING{{tuple_delimiter}}Federated learning is applied in healthcare to train models on patient data without transferring sensitive information{{tuple_delimiter}}9{{record_delimiter}}
    ("relationship"{{tuple_delimiter}}ADVERSARIAL TRAINING{{tuple_delimiter}}SECURITY MEASURES{{tuple_delimiter}}Adversarial training is a security measure used to protect models against attacks by improving their resilience{{tuple_delimiter}}8{{completion_delimiter}}
    #############################


    Example 2:

    entity_types: [large language model, differential privacy, federated learning, healthcare, adversarial training, security measures, open-source tool, dataset, learning rate, AdaGrad, RMSprop, adapter architecture, LoRA, API, model support, evaluation metrics, deployment, Python library, hardware accelerators, hyperparameters, data preprocessing, data imbalance, GPU-based deployment, distributed inference]
    text:
    ARD [82] is an innovative open-source tool developed to enhance the safety of interactions
    with large language models (LLMs). This tool addresses three critical moderation tasks: detecting
    2https://huggingface.co/docs/transformers/en/model_doc/auto#transformers.AutoModelForCausalLM
    63 harmful intent in user prompts, identifying safety risks in model responses, and determining when a
    model appropriately refuses unsafe requests. Central to its development is WILDGUARD MIX3, a
    meticulously curated dataset comprising 92,000 labelled examples that include both benign prompts and
    adversarial attempts to bypass safety measures. The dataset is divided into WILDGUARD TRAIN, used
    for training the model, and WILDGUARD TEST, consisting of high-quality human-annotated examples
    for evaluation.
    The WILDGUARD model itself is fine-tuned on the Mistral-7B language model using the WILDGUARD
    TRAIN dataset, enabling it to perform all
    ------------------------
    output:
    ```plaintext
    ("entity"{{tuple_delimiter}}ARD{{tuple_delimiter}}open-source tool{{tuple_delimiter}}ARD is an innovative open-source tool developed to enhance the safety of interactions with large language models by addressing moderation tasks such as detecting harmful intent, identifying safety risks, and determining appropriate refusals of unsafe requests)
    {{record_delimiter}}
    ("entity"{{tuple_delimiter}}LARGE LANGUAGE MODELS{{tuple_delimiter}}large language model{{tuple_delimiter}}Large language models (LLMs) are advanced AI models designed to understand and generate human-like text, which ARD aims to interact with safely)
    {{record_delimiter}}
    ("entity"{{tuple_delimiter}}WILDGUARD MIX3{{tuple_delimiter}}dataset{{tuple_delimiter}}WILDGUARD MIX3 is a meticulously curated dataset comprising 92,000 labeled examples, including benign prompts and adversarial attempts, used for training and evaluating safety measures in language models)
    {{record_delimiter}}
    ("entity"{{tuple_delimiter}}WILDGUARD TRAIN{{tuple_delimiter}}dataset{{tuple_delimiter}}WILDGUARD TRAIN is a subset of the WILDGUARD MIX3 dataset used specifically for training the model on safety measures)
    {{record_delimiter}}
    ("entity"{{tuple_delimiter}}WILDGUARD TEST{{tuple_delimiter}}dataset{{tuple_delimiter}}WILDGUARD TEST is a subset of the WILDGUARD MIX3 dataset consisting of high-quality human-annotated examples used for evaluating the model's performance)
    {{record_delimiter}}
    ("entity"{{tuple_delimiter}}MISTRAL-7B{{tuple_delimiter}}large language model{{tuple_delimiter}}Mistral-7B is a language model that the WILDGUARD model is fine-tuned on using the WILDGUARD TRAIN dataset to enhance its safety performance)
    {{record_delimiter}}
    ("entity"{{tuple_delimiter}}ADVERSARIAL ATTEMPTS{{tuple_delimiter}}adversarial training{{tuple_delimiter}}Adversarial attempts are part of the WILDGUARD MIX3 dataset, used to test and improve the model's ability to handle unsafe or harmful inputs)
    {{record_delimiter}}
    ("entity"{{tuple_delimiter}}SAFETY MEASURES{{tuple_delimiter}}security measures{{tuple_delimiter}}Safety measures are protocols and techniques implemented to ensure that large language models interact safely with users, which ARD and the WILDGUARD dataset aim to enhance)
    {{record_delimiter}}
    ("relationship"{{tuple_delimiter}}ARD{{tuple_delimiter}}LARGE LANGUAGE MODELS{{tuple_delimiter}}ARD is designed to enhance the safety of interactions with large language models by addressing critical moderation tasks{{tuple_delimiter}}8)
    {{record_delimiter}}
    ("relationship"{{tuple_delimiter}}ARD{{tuple_delimiter}}WILDGUARD MIX3{{tuple_delimiter}}ARD uses the WILDGUARD MIX3 dataset to train and evaluate its moderation capabilities{{tuple_delimiter}}7)
    {{record_delimiter}}
    ("relationship"{{tuple_delimiter}}WILDGUARD MIX3{{tuple_delimiter}}WILDGUARD TRAIN{{tuple_delimiter}}WILDGUARD TRAIN is a subset of the WILDGUARD MIX3 dataset used for training{{tuple_delimiter}}9)
    {{record_delimiter}}
    ("relationship"{{tuple_delimiter}}WILDGUARD MIX3{{tuple_delimiter}}WILDGUARD TEST{{tuple_delimiter}}WILDGUARD TEST is a subset of the WILDGUARD MIX3 dataset used for evaluation{{tuple_delimiter}}9)
    {{record_delimiter}}
    ("relationship"{{tuple_delimiter}}WILDGUARD TRAIN{{tuple_delimiter}}MISTRAL-7B{{tuple_delimiter}}The WILDGUARD TRAIN dataset is used to fine-tune the Mistral-7B language model{{tuple_delimiter}}8)
    {{record_delimiter}}
    ("relationship"{{tuple_delimiter}}ADVERSARIAL ATTEMPTS{{tuple_delimiter}}SAFETY MEASURES{{tuple_delimiter}}Adversarial attempts are used to test and improve safety measures in language models{{tuple_delimiter}}7)
    {{completion_delimiter}}
    ```
    #############################



    -Real Data-
    ######################
    entity_types: [large language model, differential privacy, federated learning, healthcare, adversarial training, security measures, open-source tool, dataset, learning rate, AdaGrad, RMSprop, adapter architecture, LoRA, API, model support, evaluation metrics, deployment, Python library, hardware accelerators, hyperparameters, data preprocessing, data imbalance, GPU-based deployment, distributed inference]
    text: {input_text}
    ######################
    output:
    """
    prompt: ChatPromptTemplate

    llm: BaseLLM
    chain = RunnableSerializable[dict, str]
    
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 100, llm: Optional[BaseLLM] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        self.prompt = ChatPromptTemplate.from_template(self.prompt_template)
        self.llm = llm 
        if llm is not None:
            self.chain = self.prompt | llm | StrOutputParser()

    def set_llm(self, llm: BaseLLM):
        self.llm = llm
        self.chain = self.prompt | llm | StrOutputParser()

    def get_entities(self, text: str) -> str:
        texts = self.text_splitter.split_text(text)
        results = self.chain.invoke({"input_text": text})
        return results
        
    def process_blob_text(self, text: str, properties: BlobProperties, root_folder: str, 
                         chunk_function: Optional[Callable[[str], List[str]]] = None, 
                         db_path: str = 'blob_chunks.db') -> List[str]:
        """
        Process blob text content, chunk it, save chunks to filesystem, and record in SQLite.
        
        Args:
            text: The text content of the blob
            properties: The BlobProperties object containing metadata
            root_folder: The root folder where blob chunks will be stored
            chunk_function: Custom text chunking function (defaults to internal text_splitter if None)
            db_path: Path to the SQLite database file
            
        Returns:
            List of generated chunk file paths
        """
        
        # Step 3: Chunk the text
        logger.log(INFO, f"Chunking text for blob: {properties.name}")
        if chunk_function is None:
            chunks = self.text_splitter.split_text(text)
            logger.log(DEBUG, f"Using internal text splitter with chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap}")
        else:
            logger.log(DEBUG, "Using provided chunking function")
            chunks = chunk_function(text)
        
        logger.log(INFO, f"Created {len(chunks)} chunks from text")
        



from sqlite3 import Connection, Cursor
class SqliteIndex:
    conn = Connection 
    cursor = Cursor

    @staticmethod
    def create_chunk_index(cursor: Cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunk_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blob_name TEXT,
                blob_type TEXT,
                content_type TEXT,
                creation_time TEXT,
                last_modified TEXT,
                size INTEGER,
                chunk_order INTEGER,
                chunk_uuid TEXT,
                chunk_path TEXT
            )
            ''')
        
    @staticmethod
    def create_blob_index(cursor: Cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blob_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blob_name TEXT,
                blob_type TEXT,
                content_type TEXT,
                creation_time TEXT,
                last_modified TEXT,
                size INTEGER,
                blob_uuid TEXT,
                blob_path TEXT
            )
            ''')     

    def store_blob(self, properties: BlobProperties, id:uuid.uuid4, blob_path: str):
        blob_uuid = str(id)
        self.cursor.execute('''
            INSERT INTO blob_index (
                blob_name, blob_type, content_type, creation_time, 
                last_modified, size, blob_uuid, blob_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                properties.name,
                properties.blob_type,
                properties.content_settings.content_type if properties.content_settings else None,
                str(properties.creation_time) if properties.creation_time else None,
                str(properties.last_modified) if properties.last_modified else None,
                properties.size,
                blob_uuid,
                str(blob_path)
            ))        

    def store_chunk(self, properties: BlobProperties, id:uuid.uuid4, chunk_index: int, chunk_path: str):
        chunk_uuid = str(id)
        chunk_filename = f"{chunk_uuid}.txt"
        #chunk_path = target_folder / chunk_filename
        
        self.cursor.execute('''
            INSERT INTO chunk_index (
                blob_name, blob_type, content_type, creation_time, 
                last_modified, size, chunk_order, chunk_uuid, chunk_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                properties.name,
                properties.blob_type,
                properties.content_settings.content_type if properties.content_settings else None,
                str(properties.creation_time) if properties.creation_time else None,
                str(properties.last_modified) if properties.last_modified else None,
                properties.size,
                chunk_index,
                chunk_uuid,
                str(chunk_path)
            ))        



    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        SqliteIndex.create_blob_index(self.cursor)
        SqliteIndex.create_chunk_index(self.cursor)

    def commit(self):
        self.conn.commit()
    
    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def get_chunks(self, blob_name: str) -> List[Tuple[str, str]]:
        query = "SELECT chunk_uuid, chunk_path FROM blob_chunks WHERE blob_name = ?"
        self.cursor.execute(query, (blob_name,))
        return self.cursor.fetchall()

class BlobProcessor:
    container: Container
    properties: BlobProperties

    def __init__(self, container: Container, properties: BlobProperties):
        self.container = container
        self.properties = properties
    
    def get_name(self) -> str:
        return self.properties.name 
    
    def get_blob_type(self) -> str:
        return self.properties.content_settings.content_type 

    def get_target_folder(self, root:str = ".", create_folder:bool=True) -> Path:
        # Extract folder path from blob name
        blob_path = Path(self.properties.name)
        folder_path = blob_path.parent
        target_folder = Path(root) / folder_path
        
        if not target_folder.exists() and create_folder:
            target_folder.mkdir(parents=True, exist_ok=True)
        return target_folder
    

    def get_BlobType(self) -> Optional[BlobType]:
        return BlobType.from_mime_type(self.properties.content_settings.content_type)

    def get_text_content(self, encoding: str = 'utf-8') -> str:
        """
        Get the content of a text file blob as a string
        
        Args:
            blob_name: Name of the blob to retrieve
            encoding: Text encoding to use (default: utf-8)
            
        Returns:
            str: The text content of the blob
            
        Raises:
            ValueError: If the blob cannot be found or accessed
        """
        try:
            # Get the blob content as bytes
            content_bytes = container.get_blob_content(self.properties.name)
            
            # Decode the content to string
            text_content = content_bytes.decode(encoding)
            
            return text_content
        except UnicodeDecodeError as e:
            raise ValueError(f"Error decoding text content for blob {self.properties.name}: The '{encoding = }' is not correct for this file. {str(e)}")
        except Exception as e:
            raise ValueError(f"Error retrieving text content for blob {self.properties.name}: {str(e)}")
    
    def get_docx_content(self) -> str:
        """
        Get the content of a Word DOCX file as text
        
        Args:
            blob_name: Name of the blob to retrieve
            
        Returns:
            str: The text content extracted from the DOCX file
            
        Raises:
            ValueError: If the blob cannot be found, accessed, or is not a valid DOCX file
            ImportError: If the required docx package is not installed
        """
        try:
            # Import docx library for processing Word documents
            try:
                import docx
            except ImportError:
                raise ImportError("The python-docx package is required to read DOCX files. Install it with 'pip install python-docx'")
            
            # Get the blob content as bytes
            content_bytes = container.get_blob_content(self.properties.name)
            
            # Create a file-like object from the bytes
            from io import BytesIO
            docx_file = BytesIO(content_bytes)
            
            # Load the document
            document = docx.Document(docx_file)
            
            # Extract text from all paragraphs
            paragraphs = [para.text for para in document.paragraphs]
            
            # Join paragraphs with newlines
            text_content = '\n'.join(paragraphs)
            
            return text_content
        except ImportError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX blob {self.properties.name}: {str(e)}")


from logger import logger, INFO, ERROR



# Example usage
if __name__ == "__main__":

    from config import (
        AZURE_TENANT_ID,
        AZURE_CLIENT_ID,
        AZURE_CLIENT_SECRET,
        AZURE_SUBSCRIPTION_ID,
        AZURE_RESOURCE_GROUP,
        AZURE_STORAGE_ACCOUNT_NAME,
        AZURE_STORAGE_CONTAINER_NAME
    )

    def get_container() -> Container:
        from azwrap import Identity, Subscription, ResourceGroup, StorageAccount

        identity: Identity = Identity(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
        subscription: Subscription = identity.get_subscription(AZURE_SUBSCRIPTION_ID)
        resource_group: ResourceGroup = subscription.get_resource_group(AZURE_RESOURCE_GROUP)
        storage_account: StorageAccount = resource_group.get_storage_account(AZURE_STORAGE_ACCOUNT_NAME)
        container: Container = storage_account.get_container(AZURE_STORAGE_CONTAINER_NAME)
        return container


    # Get the container
    container = get_container()
    
    blobs = container.find_blobs_by_filename(".DS_Store")
    for blob in blobs:
        container.delete_blob(blob.name)

    sqllite = SqliteIndex("blob_index.db")

    blobs = container.get_blobs()

    # Compose the root folder path
    working_docs_folder = Path(os.getcwd()) / "working_docs"
    if not working_docs_folder.exists():
        working_docs_folder.mkdir(parents=True, exist_ok=True)


    for item in blobs:
    
        blob = BlobProcessor(container, item)
        btype = blob.get_blob_type()
        if btype == BlobType.TEXT_PLAIN.value:
            pass
        elif btype == BlobType.MS_WORD.value:
            text = blob.get_docx_content()
            id = uuid.uuid4()
            target_folder = blob.get_target_folder(root=working_docs_folder)
            blob_filename = target_folder / f"{id}.txt"           

            with open(blob_filename, "w", encoding="utf-8") as f:
                f.write(text)

            sqllite.store_blob(blob.properties, id, target_folder)
        else:
            pass 


    sqllite.commit()
    sqllite.close()

    exit() 








    
    # Initialize the BlobGraphBuilder with custom settings
    graph_builder = BlobGraphBuilder(chunk_size=1000, chunk_overlap=100)
    
    # Create a root folder for processing blobs
    root_folder = "./processed_blobs"
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)
    
    # Process each blob
    for b in container.get_blobs():
        blob_processor = BlobProcessor(container, b)
        blob_properties = blob_processor.properties
        
        # Process text blobs
        blob_type = blob_processor.get_BlobType()
        if blob_type == BlobType.TEXT_PLAIN:
            try:
                # Get the text content
                text_content = blob_processor.get_text_content()
                
                # Process the text with our new method
                chunk_paths = graph_builder.process_blob_text(
                    text=text_content,
                    properties=blob_properties,
                    root_folder=root_folder,
                    db_path="blob_index.db"
                )
                
                logger.log(INFO, f"Processed text blob: {blob_properties.name}, created {len(chunk_paths)} chunks")
                
            except Exception as e:
                logger.log(ERROR, f"Error processing text blob {blob_properties.name}: {str(e)}")
                
        # Process Word documents
        elif blob_type == BlobType.MS_WORD:
            try:
                # Get the text content from the Word document
                text_content = blob_processor.get_docx_content()
                
                # Process the text with our new method
                chunk_paths = graph_builder.process_blob_text(
                    text=text_content,
                    properties=blob_properties,
                    root_folder=root_folder,
                    db_path="blob_index.db"
                )
                
                logger.log(INFO, f"Processed Word blob: {blob_properties.name}, created {len(chunk_paths)} chunks")
                
            except Exception as e:
                logger.log(ERROR, f"Error processing Word blob {blob_properties.name}: {str(e)}")
                
        else:
            logger.log(INFO, f"Skipping unsupported blob type: {blob_properties.name}, type: {blob_type}")
