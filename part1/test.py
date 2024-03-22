from database import SolutionDB, CaseStudy, Reference, Secteur

secteur = Secteur(7)

case_studies = secteur.find_all_case_studies()
for x in case_studies:
    print(x.eco_energie)
