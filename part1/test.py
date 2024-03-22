from database import SolutionDB, CaseStudy, Reference, Secteur

secteur = Secteur(53)
print(secteur.find_all_solutions())
print(secteur.find_3_most_frequent_solutions())
