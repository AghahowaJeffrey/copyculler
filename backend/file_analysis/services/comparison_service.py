import textract
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import numpy as np

class FileComparator:
    def __init__(self):
        # Load Sentence Transformer for semantic similarity
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load summarization model
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def extract_text(self, file_path):
        """Extract text from a file using textract."""
        return textract.process(file_path).decode('utf-8')

    def find_common_sections(self, texts, similarity_threshold=0.8):
        """
        Find semantically similar content across multiple texts.
        """
        # Split texts into sentences
        sentences_list = [text.split('. ') for text in texts]
        
        # Flatten sentences and compute embeddings
        all_sentences = [sentence for sentences in sentences_list for sentence in sentences]
        embeddings = self.similarity_model.encode(all_sentences)
        
        # Find common sentences based on semantic similarity
        common_sentences = set()
        for i, sentence1 in enumerate(all_sentences):
            for j, sentence2 in enumerate(all_sentences):
                if i != j and util.cos_sim(embeddings[i], embeddings[j]) > similarity_threshold:
                    common_sentences.add(sentence1)
        
        return '. '.join(common_sentences)

    def find_unique_sections(self, texts, similarity_threshold=0.8):
        """
        Find unique content per file based on semantic similarity.
        """
        unique_sections = []
        for i, text in enumerate(texts):
            other_texts = [t for j, t in enumerate(texts) if j != i]
            other_sentences = [sentence for t in other_texts for sentence in t.split('. ')]
            
            # Compute embeddings
            text_sentences = text.split('. ')
            text_embeddings = self.similarity_model.encode(text_sentences)
            other_embeddings = self.similarity_model.encode(other_sentences)
            
            # Find sentences in this text that are not similar to any in other texts
            unique_sentences = []
            for sentence, embedding in zip(text_sentences, text_embeddings):
                is_unique = True
                for other_embedding in other_embeddings:
                    if util.cos_sim(embedding, other_embedding) > similarity_threshold:
                        is_unique = False
                        break
                if is_unique:
                    unique_sentences.append(sentence)
            
            unique_sections.append('. '.join(unique_sentences))
        
        return unique_sections

    def summarize_text(self, text, max_length=130, min_length=30):
        """
        Generate a concise summary of the given text.
        """
        if len(text.split()) > 100:  # Only summarize long texts
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary[0]['summary_text']
        return text