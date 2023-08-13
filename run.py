from infra.repository.machines_repository import MachinesRepository

repo = MachinesRepository()

repo.insert(machine="localhost", state="AVAILABLE")

# print(repo.select())