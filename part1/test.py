from database import SolutionDB, CaseStudy, Reference, Secteur, Database
from gensim.corpora import Dictionary
import gensim
from gensim import similarities

solution = SolutionDB(512)
print(solution.get_title())
print(solution.get_category())
print(solution.get_description())
print(solution.get_application())
print(solution.get_bilan_energie())
print(solution.get_difficultes())
print(solution.get_effets_positifs())
print(solution.get_gain_text())
print(solution.get_regle_pouce_text())

secteur = Secteur(6)
for x in secteur.find_3_most_frequent_solutions():
    print(x)

print(list("[1,2,3]")[1::2])
