import docker
client = docker.from_env()
#client.containers.list()
#image = client.images.get("williangalvani/companion:50")
#print(image.tags)
#data = client.images.get_registry_data("williangalvani/companion:50")
print(client.images.list("williangalvani/companion"))
