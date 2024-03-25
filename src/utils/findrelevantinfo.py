from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import numpy as np
import time
from collections import Counter
from sentence_transformers import CrossEncoder
from utils.database import SolutionDBList, SolutionForInference


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

    def __init__(self, all_solutions: 'list[SolutionForInference]', user_query: str) -> None:
        """
        Args:
            all_solutions (list[str]): The list of all solution titles and the user query as the last element
        """
        self.all_solutions = all_solutions
        self.user_query = user_query
        self.model = EmbeddingsModel()

    def relevant_solutions(self):
        # Turn the solutions and user query into embeddings
        # self._calc_solution_embeddings()
        user_query_embedding = self.model(self.user_query)[0]
        # Calculate cosine similarity between each solution embedding and the query

        self._calculate_similarity_scores(user_query_embedding)

        # Find the best solutions using cosine similarity (we select solutions that are within 0.2 of the best)

        self.best_solutions = self._find_best_solutions(0.2)

        # We calculate another metric to make another ranking within the best solutions

        self._apply_cross_encoder()

        # sort on the cross encoding score (higher is better)

        self.ordered_best_solutions: 'list[SolutionForInference]'
        self.ordered_best_solutions = sorted(
            self.best_solutions, key=lambda solution: solution.get_cross_encoded_score(), reverse=True)

        # In all those solutions, find if a certain class (for instance Utilité + Froid) represent more than 30% and return it
        # Always returns the 3 best solutions

        three_best_solutions, solution_that_represents_a_class = self._adapt_solutions_based_on_results()

        # Show some visual output
        # print(
        #     f"The rest of the processing took {time.time() - start_time} seconds\n")
        # print(
        #     f"Here are the categories that contains all the info you need : {best_classes}")
        # print(
        #     f"Here are a few relevant solutions for your query : {[str(solution) for solution in three_best_solutions]}")
        return [solution.id for solution in three_best_solutions], solution_that_represents_a_class

    # def _calc_solution_embeddings(self):
    #     solution_texts = [solution.text for solution in self.all_solutions]
    #     embeddings = self.model(solution_texts)
    #     for i in range(len(embeddings)):
    #         self.all_solutions[i].set_embedding(embeddings[i])

    def _cosine_similarity(self, vec1, vec2):
        """Calculate the cosine similarity between two vectors."""
        cosine_similarity = torch.nn.functional.cosine_similarity(
            vec1.unsqueeze(0), vec2.unsqueeze(0))
        return cosine_similarity.item()

    def _calculate_similarity_scores(self, user_query_embedding):
        """Calculates the distance between the query embedding and each solution embedding"""
        for solution in self.all_solutions:
            cosine_similarity = self._cosine_similarity(
                solution.get_embedding(), user_query_embedding)
            solution.set_cosine_similarity_score(
                cosine_similarity)

    def _apply_cross_encoder(self):
        model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)
        scores = model.predict(
            [(self.user_query, solution.text)
             for solution in self.best_solutions]
        )

        for i in range(len(scores)):
            self.best_solutions[i].set_cross_encoded_score(scores[i])

    def _find_best_solutions(self, max_distance_from_best: float) -> 'list[SolutionForInference]':
        best_solution = max(
            self.all_solutions, key=lambda solution: solution.get_cosine_similarity_score())
        best_solutions = []
        for solution in self.all_solutions:
            if np.abs(solution.get_cosine_similarity_score() - best_solution.get_cosine_similarity_score()) < max_distance_from_best:
                best_solutions.append(solution)
        return best_solutions

    def _adapt_solutions_based_on_results(self):
        """Calculate the most frequent class in the best solutions and if frequency is high,
        consider that the query was tailored for a category we need to give that category to the user
        Also always returns the 3 best solutions
        """

        classes_in_best_solutions = [solution.class_name
                                     for solution in self.ordered_best_solutions]
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
        best_classes_and_frequencies = []
        solutions_that_represent_their_class = []
        if len(self.ordered_best_solutions) > 3:
            # We try to find the most specific class that represents more than 30% of the best solutions

            for x in range(1, 4)[::-1]:
                for item, frequency in frequencies_dict[x].items():
                    if frequency > 0.3:
                        best_classes_and_frequencies.append(item)
                if best_classes_and_frequencies:  # If a more specific class is very frequent, don't test the more general ones
                    break

            # I chose to find the class in the database by using a solution id that belongs to that class and the amount of components of that class.
            # Example : if i tell you that the class is represented by the solution x which belongs to 'New energies + Photovoltaic solar + Sensor'
            # and that the class I'm looking for has only two components, you should be able to find the class 'New energies + Photovoltaic solar'
            for classe in best_classes_and_frequencies:
                for solution in self.ordered_best_solutions:
                    if classe in solution.class_name:
                        solutions_that_represent_their_class.append(
                            [len(classe.split(" + ")), solution])
                        break

        # I chose to represent a class by a solution that is within that class and by the number of components in a class (all that is in solutions_that_represent_their_class)
        return self.ordered_best_solutions[:3], solutions_that_represent_their_class


# def retrieve_all_solutions_and_classes(dictionnary):
#     """For each solution in the data.json file, add its class before its name
#     For instance, the solution 'photovoltaic solar panel' belongs to the class 'new energy photovoltaic solar sensor', so its full name will be :
#     new energy photovoltaic solar sensor photovoltaic solar panel

#     We do this because the category the solution belongs to usually contains useful data for finding out if it relevant.
#     Args:
#         dictionnary : The dict from data.json
#     """
#     solutions = []
#     for i in range(len(dictionnary["label"])):
#         solution = SolutionForInference(
#             dictionnary["solution_text"][i], dictionnary["base_label_text"][i], dictionnary["label_text"][i], dictionnary["solution_ids"][i])
#         solutions.append(solution)
#     return solutions


def change_solutions_format(solutions: 'SolutionDBList'):
    solutions_for_inference = []
    titles = solutions.get_titles()
    categories = solutions.get_categories()
    for i in range(len(solutions.solutions)):
        solutions_for_inference.append(SolutionForInference(
            solutions.solutions[i].get_title(), categories[i].get_name(), solutions.solutions[i].get_id()))
    return solutions_for_inference
