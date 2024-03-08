import os

def get_routers():
    routers = []

    for file_name in os.listdir(os.path.dirname(__file__)):
        if file_name.endswith(".py") and file_name != "__init__.py":
            module_name = f"api.routers.{file_name[:-3]}"
            router_module = __import__(module_name, fromlist=["router"])

            routers.append(router_module.router)

    return routers
