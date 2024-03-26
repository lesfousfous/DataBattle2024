from database import Category, SolutionDB

print(SolutionDB(11).cursor == SolutionDB(452).cursor)
