from transformers import AutoTokenizer, AutoModel
from database import Preprocessor
import torch
import torch.nn.functional as F
import numpy as np
import json
import time
from collections import Counter
from sentence_transformers import CrossEncoder


class EmbeddingsModel:

    def __init__(self):
        # Load model from HuggingFace Hub
        self.tokenizer = AutoTokenizer.from_pretrained(
            'sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained(
            'sentence-transformers/all-MiniLM-L6-v2')

    def _tokenize_sentences(self, sentences: 'list[str]'):
        encoded_input = self.tokenizer(sentences, padding=True,
                                       truncation=True, return_tensors='pt')
        return encoded_input

    def _mean_pooling(self, model_output, attention_mask):
        # First element of model_output contains all token embeddings
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(
            -1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def _calculate_embeddings(self, tokenized_sentences: 'list[np.array]'):

        start_time = time.time()
        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**tokenized_sentences)

        end_time = time.time() - start_time
        print(f"Inference took {end_time} seconds")

        # Perform pooling
        sentence_embeddings = self._mean_pooling(
            model_output, tokenized_sentences['attention_mask'])

        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        sentence_embeddings = list(sentence_embeddings)

        return sentence_embeddings

    def __call__(self, sentences: 'list[str]'):
        tokenized_text = self._tokenize_sentences(sentences)
        embeddings = self._calculate_embeddings(tokenized_text)
        return embeddings


class BestSolutionsFinder:
    """Uses the embedding model to vectorize all the solution titles and the user query
    then uses cosine similarity to find the most relevant solutions and refines that ranking by applying a cross encoder
    """

    def __init__(self, all_solutions: 'list[str]', all_classes: 'list[str]') -> None:
        """
        Args:
            all_solutions (list[str]): The list of all solution titles and the user query as the last element
        """
        self.all_solutions = all_solutions
        self.model = EmbeddingsModel()
        self.all_classes = all_classes

    def relevant_solutions(self):
        # Turn the solutions and user query into embeddings
        self.all_embeddings = self.model(self.all_solutions)
        start_time = time.time()
        # Calculate cosine similarity between each solution embedding and the query
        self.cosine_similarity_scores = self._calculate_similarity_scores()
        # Find the indexes of the best solutions (we select solutions that are within 0.2 of the best)
        self.best_solution_indexes = self._find_best_solutions(0.2)
        # Here are the titles that correspond to the best solutions
        self.best_solution_titles = [self.all_solutions[i]
                                     for i in self.best_solution_indexes]
        # We calculate another metric to find which solution is the best
        self.cross_encoded_scores = self._apply_cross_encoder()
        # We store the 2 scores for each solution in a dictionnary and sort on the cross encoding score (higher is better)
        self.sorted_dict_of_solutions = self.store_and_sort_solutions()
        # Extract the best solution indexes after sorting on cross encoder score
        self.best_solutions_by_cross_encoder = list(
            self.sorted_dict_of_solutions.keys())
        # In all those solutions, find if a certain class (for instance Utilité + Froid) represent more than 30% and return it
        # Always returns the 3 best solutions
        self.relevant_data = self._adapt_solutions_based_on_results()
        # Show some visual output
        if type(self.relevant_data[0]) is int:
            print(
                f"Here are a few relevant solutions for your query : {[self.all_solutions[x] for x in self.relevant_data]}")
        else:
            print(
                f"Here are the categories that contains all the info you need : {[x[0] for x in self.relevant_data[0]]}")
            print(
                f"Here is are a few relevant solutions for your query : {[self.all_solutions[x] for x in self.relevant_data[1]]}")

        print(
            f"The rest of the processing took {time.time() - start_time} seconds")

    def _cosine_similarity(self, embedding1, embedding2):
        """A distance metric to find how close 2 embeddings are"""
        return np.dot(embedding1, embedding2)/(np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    def _calculate_similarity_scores(self):
        """Calculates the distance between the query embedding and each solution embedding"""
        all_similarity_scores = []
        for embedding in self.all_embeddings[:-1]:
            all_similarity_scores.append(
                self._cosine_similarity(embedding, self.all_embeddings[-1]))
        return all_similarity_scores

    def _apply_cross_encoder(self):
        model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
        user_query = self.all_solutions[-1]
        scores = model.predict(
            [(user_query, solution) for solution in self.all_solutions]
        )
        return scores

    def _find_best_solutions(self, max_distance_from_best: float):
        best_score = max(self.cosine_similarity_scores)
        best_solutions_indexes = []
        for solution_index in range(len(self.cosine_similarity_scores)):
            if np.abs(self.cosine_similarity_scores[solution_index] - best_score) < max_distance_from_best:
                best_solutions_indexes.append(solution_index)
        return best_solutions_indexes

    def store_and_sort_solutions(self):
        sorted_dict_by_cross_encoded = {
            index_all_sentences: {
                "cosine_similarity": self.cosine_similarity_scores[index_all_sentences],
                "cross_encoded": self.cross_encoded_scores[index_best_solutions]
            }
            for index_best_solutions, index_all_sentences in enumerate(self.best_solution_indexes)
        }
        # Sort the dictionary items by 'cross_encoded' in descending order and directly update the dictionary
        sorted_dict_by_cross_encoded = dict(sorted(
            sorted_dict_by_cross_encoded.items(),
            key=lambda item: item[1]['cross_encoded'],
            reverse=True
        ))
        return sorted_dict_by_cross_encoded

    def _adapt_solutions_based_on_results(self):
        """Calculate the most frequent class in the best solutions and if frequency is high,
        consider that the query was tailored for a category so give back the name of that category
        Also always returns the 3 best solutions
        """

        classes_in_best_solutions = [classes[x]
                                     for x in self.best_solutions_by_cross_encoder]
        # Initialize a dictionary of Counters for each level of component, recalculating directly
        direct_component_counts = {1: Counter(), 2: Counter(), 3: Counter()}

        # Process the list and update the counts directly
        for c in classes_in_best_solutions:
            parts = c.split(' + ')
            for i in range(1, len(parts) + 1):
                general_class = ' + '.join(parts[:i])
                direct_component_counts[len(parts[:i])][general_class] += 1

        frequencies_dict = {}
        for counter_index in range(1, 4):
            # Calculate the total count of all items
            total_count = sum(direct_component_counts[counter_index].values())

            # Calculate the frequency of each item and store in a dictionary
            frequencies = {item: count / total_count for item,
                           count in direct_component_counts[counter_index].items()}
            frequencies_dict[counter_index] = frequencies

        if len(self.best_solutions_by_cross_encoder) > 3:
            # We try to find the most specific class that represents more than 50% of the best solutions
            best_classes_and_frequencies = []
            for x in range(1, 4)[::-1]:
                for item, frequency in frequencies_dict[x].items():
                    if frequency > 0.3:
                        best_classes_and_frequencies.append((item, frequency))
                if best_classes_and_frequencies:  # If a more specific class is very frequent, don't test the more general ones
                    break
            return best_classes_and_frequencies, self.best_solutions_by_cross_encoder[:3]
        else:
            return self.best_solutions_by_cross_encoder


def retrieve_all_solutions_and_classes(dictionnary):
    """For each solution in the data.json file, add its class before its name
    For instance, the solution 'photovoltaic solar panel' belongs to the class 'new energy photovoltaic solar sensor', so its full name will be :
    new energy photovoltaic solar sensor photovoltaic solar panel 

    We do this because the category the solution belongs to usually contains useful data for finding out if it relevant.
    Args:
        dictionnary : The dict from data.json
    """
    solutions = []
    solutions_ids = {}
    classes = []
    for i in range(len(dictionnary["label"])):
        solutions.append(dictionnary["label_text"][i] +
                         " " + dictionnary["text"][i])
        solutions_ids[i] = dictionnary["solution_ids"]
        classes.append(dictionnary["base_label_text"][i])
    return solutions, classes


with open("./data/data.json", "r") as f:
    input_dict = json.load(f)

preprocessor = Preprocessor()
sentences, classes = retrieve_all_solutions_and_classes(input_dict)
user_query = "I would like to size a solar panel"
print(preprocessor(user_query))
sentences.append(
    preprocessor(user_query))  # We put the query at the end of the sentences


finder = BestSolutionsFinder(sentences, classes)
finder.relevant_solutions()
