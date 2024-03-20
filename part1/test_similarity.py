from transformers import AutoTokenizer, AutoModel
from DataBattle2024.part1.database import Preprocessor
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

    def __init__(self, user_input_embedding: str) -> None:
        self.user_input_embedding = user_input_embedding

    def _cosine_similarity(self, embedding1, embedding2):
        return np.dot(embedding1, embedding2)/(np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    def calculate_similarity_scores(self, all_embeddings: 'list[np.array]'):
        all_similarity_scores = []
        for embedding in all_embeddings[:-1]:
            all_similarity_scores.append(
                self._cosine_similarity(embedding, self.user_input_embedding))
        return all_similarity_scores

    def apply_cross_encoder(self, query, solutions):
        model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
        scores = model.predict(
            [(query, solution) for solution in solutions]
        )
        return scores

    def find_best_solutions(self, max_distance_from_best: float, similarity_scores: 'list[float]'):
        best_score = max(similarity_scores)
        best_solutions_indexes = []
        for solution_index in range(len(similarity_scores)):
            # We keep solutions that are not too far away from the best
            if np.abs(similarity_scores[solution_index] - best_score) < max_distance_from_best:
                best_solutions_indexes.append(solution_index)
        return best_solutions_indexes

    def adapt_solutions_based_on_results(self, best_solutions_indexes, classes):
        """Calculate the most frequent class in the best solutions and if frequency is high,
        consider that the query was tailored for a category so give back the name of that category
        Also always returns the 3 best solutions
        """

        classes_in_best_solutions = [classes[x]
                                     for x in best_solutions_indexes]
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

        if len(best_solutions_indexes) > 3:
            # We try to find the most specific class that represents more than 50% of the best solutions
            best_classes_and_frequencies = []
            for x in range(1, 4)[::-1]:
                for item, frequency in frequencies_dict[x].items():
                    if frequency > 0.3:
                        best_classes_and_frequencies.append((item, frequency))
                if best_classes_and_frequencies:  # If a more specific class is very frequent, don't test the more general ones
                    break
            return best_classes_and_frequencies, best_solutions_indexes[:3]
        else:
            return best_solutions_indexes


def retrieve_all_solutions_and_classes(dictionnary):
    solutions = []
    classes = []
    for i in range(len(dictionnary["label"])):
        solutions.append(dictionnary["label_text"][i] +
                         " " + dictionnary["text"][i])
        classes.append(dictionnary["base_label_text"][i])
    return solutions, classes


with open("./data/data.json", "r") as f:
    input_dict = json.load(f)

preprocessor = Preprocessor()
sentences, classes = retrieve_all_solutions_and_classes(input_dict)
sentence = "I would like to size a solar panel ?"
print(preprocessor(sentence))
sentences.append(
    preprocessor(sentence))  # We put the query at the end of the sentences

model = EmbeddingsModel()
sentence_embeddings = model(sentences)
finder = BestSolutionsFinder(sentence_embeddings[-1])
scores = finder.calculate_similarity_scores(sentence_embeddings)
solution_indexes = finder.find_best_solutions(0.2, scores)
solutions = [sentences[x] for x in solution_indexes]
cross_encoded_scores = finder.apply_cross_encoder(
    sentences[-1], solutions)

dataset = {}
for index_in_best_solutions, index_in_all_sentences in zip(range(len(solution_indexes)), solution_indexes):
    dataset[index_in_all_sentences] = {"cosine_similarity": scores[index_in_all_sentences],
                                       "cross_encoded": cross_encoded_scores[index_in_best_solutions]}

# Sort by 'cross_encoded'
sorted_by_cross_encoded = sorted(
    dataset.items(), key=lambda item: item[1]['cross_encoded'], reverse=True)

# Convert the sorted tuples back into a dictionary
sorted_dict_by_cross_encoded = dict(sorted_by_cross_encoded)
for key, value in sorted_dict_by_cross_encoded.items():
    print(f"{sentences[key]} : {value}")
best_solution_indexes = [key for key,
                         value in sorted_dict_by_cross_encoded.items()]


final_result = finder.adapt_solutions_based_on_results(
    best_solution_indexes, classes)
if type(final_result[0]) is int:
    print(
        f"Here are a few relevant solutions for your query : {[sentences[x] for x in final_result]}")
else:
    print(
        f"Here are the categories that contains all the info you need : {[x[0] for x in final_result[0]]}")
    print(
        f"Here is are a few relevant solutions for your query : {[sentences[x] for x in final_result[1]]}")
