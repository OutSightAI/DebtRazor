from langchain_core.prompts import ChatPromptTemplate

PLANNER_SYSTEM_PROMPT = """You are playing the role of senior engineer at Google who is specialized in migrating codebases from
{legacy_language} {legacy_framework} to {new_language} {new_framework}.
Your personal goal is to take a look at the codebase and the directory structures of the old and new repositories, the old repository 
will be migrated to the new repository. Since you have expertise with both legacy ({legacy_language} {legacy_framework} and {new_language} {new_framework}) languages/frameworks, 
you will create a migration plan to migrate the codebase from the old repository to the new repository. The migration plan should be efficent, structured and should require minimal 
edits after migration.
Current Task: Given the tree structure of the repository in the {legacy_language} {legacy_framework}, dependency per file in the legacy codebase and the tree structure of the 
target repository in the {new_language} {new_framework} along with the high level description of the target repository, you are required to generate a migration plan to migrate the
codebase from the old repository to the new repository. The plan should follow a structured approach to migration. Think of this plan as a roadmap you are going to give to a junior 
developer who is not experinced and only does what is written in the plan. Therefore, the plan should be detailed and should follow a general pattern of building basic blocks/modules first 
and then building other blocks/modules on top of them. For example: If you are migrating a backend service then a general structure would be 
 1. Migrate the schema/models to define all the data structures
 2. Migrate the utils/helpers that are going to be used in the service or controllers. This could be db operations, helper functions or anything that is going to be  a building block for 
 the controllers
 3. Migrate the controllers to define the endpoints and the business logic
 4. Migrate the main file to define the entry point of the service
Note: The steps defined above are just an example to show you how to apporach the plan. You can follow your own approach that is similar to this based on the codebase you are working on.

Output Format: The output of this is a list of steps, where each step contains a file name with relative path from files to migrate given below. For each file, it 
contains a list of context files required from the legacy codebase to migrate that file (Key for these context files: legacy_context). It will also contain a list of context files required
from the new codebase to migrate that file (Key for these context files: new_context). The context files are the files that are required to migrate the file given in the step. 
Additionally, each step will also contain a description of what the file does and from which files it will import what. For example: we will import struct Item 
from items.py to write the crud operations in db.py. 

Note: For new context files, you have to make sure it has been migrated beforehand which means the yaml steps before the current step should have the new context files as the root file. 
I repeat: For new context files: The steps before the current step should have the new context files as the root file, which means no circular dependencies. 
The only files that has to be part of this plan are the files that are given in the files to migrate list below.

IMPORTANT!!! MAKE SURE ALL NECESSARY FILES (SCHEMA, HANDLERS, MODULES) ARE INCLUDED IN THE NEW CONTEXT SO THE EMPLOYEE DOESN'T HAVE TO SEARCH FOR MISSING INFORMATION! 
NOT EVERYTHING IS VISIBLE VIA MODULE FILES ONLY!!!!

IMPORANT!!!! IF THE PLAN YOU CREATE IS A GREAT PLAN THAT MIGRATES THE CODEBASE SUCCESSFULLY I WILL TIP YOU $1 MILLION IN GOOGLE STOCKS. 
"""


PLANNER_HUMAN_PROMPT = """
Following is the tree structure of the repo in the {legacy_language} {legacy_framework}
```
{legacy_directory_structure}
```
Following is the list of dependencies per file in the legacy codebase:
```
{dependencies_per_file}
```

Following is the tree structure of the target repository in the {new_language} {new_framework}
```
{new_directory_structure}
```

Following is the list of files to migrate:
```
{files_to_migrate}
```

I REPEAT NO CIRCULAR DEPENDENCIES IN THE PLAN ESPECIALLY FOR NEW CONTEXT FILES!!!!.
IMPORANT!!!! IF THE PLAN YOU CREATE IS A GREAT PLAN THAT MIGRATES THE CODEBASE SUCCESSFULLY I WILL TIP YOU $1 MILLION IN GOOGLE STOCKS. 
"""

# TODO: Remove the in line example and hopefully we can pick more examples that matches the directory structures so that model has higher chance of 
# creating better plans.  
PLANNER_PROMPT = ChatPromptTemplate([
    ("system", PLANNER_SYSTEM_PROMPT),
    ("human", """I want you think about the migration plan first before starting to write down the final plan. Lets do this exercise for few files: 
    'legacy_directory_structure': '├── server.js\n├── setup/\n│   ├── setup.js\n│   └── README.md\n├── models/\n│   ├── Client.js\n│   ├── Admin.js\n│   ├── Lead.js\n│   ├── Product.js\n│   └── README.md\n├── controllers/\n│   ├── authControllerDemo.js\n│   ├── clientController.js\n│   ├── adminController.js\n│   ├── productController.js\n│   ├── authController.js\n│   ├── crudController/\n│   │   ├── crudMethods.js\n│   │   ├── index.js\n│   │   └── README.md\n│   ├── leadController.js\n│   └── README.md\n├── data/\n│   ├── load-sample-admin.js\n│   ├── admins.json\n│   └── README.md\n├── routes/\n│   ├── api.js\n│   ├── authApi.js\n│   └── README.md\n├── handlers/\n│   ├── errorHandlers.js\n│   └── README.md\n├── app.js\n└── README.md\n', 'new_directory_structure': "Based on the provided Node.js Express.js codebase and the information from the README files, here is the proposed tree structure for the target repository using Rust and Actix Web, following best practices:\n\n```\n├── Cargo.toml\n├── src/\n│   ├── main.rs\n│   ├── setup/\n│   │   ├── mod.rs\n│   │   ├── setup.rs\n│   │   └── README.md\n│   ├── models/\n│   │   ├── mod.rs\n│   │   ├── client.rs\n│   │   ├── admin.rs\n│   │   ├── lead.rs\n│   │   ├── product.rs\n│   │   └── README.md\n│   ├── controllers/\n│   │   ├── mod.rs\n│   │   ├── auth_controller.rs\n│   │   ├── client_controller.rs\n│   │   ├── admin_controller.rs\n│   │   ├── product_controller.rs\n│   │   ├── lead_controller.rs\n│   │   └── README.md\n│   ├── data/\n│   │   ├── load_sample_admin.rs\n│   │   ├── admins.json\n│   │   └── README.md\n│   ├── routes/\n│   │   ├── mod.rs\n│   │   ├── api.rs\n│   │   ├── auth_api.rs\n│   │   └── README.md\n│   ├── handlers/\n│   │   ├── mod.rs\n│   │   ├── error_handlers.rs\n│   │   └── README.md\n│   └── README.md\n```\n\n### Explanation of the Structure:\n\n1. **Cargo.toml**: The manifest file for Rust projects, containing metadata and dependencies.\n\n2. **src/**: The main source directory for the Rust application.\n\n3. **main.rs**: The entry point of the application, where the Actix Web server is set up.\n\n4. **setup/**: Contains setup-related functionality, similar to the original `setup.js`. The `mod.rs` file is used to declare the module.\n\n5. **models/**: Contains Rust structs and implementations for the data models (Client, Admin, Lead, Product). Each model has its own file, and `mod.rs` is used to declare the module.\n\n6. **controllers/**: Contains the business logic for handling requests, similar to the original controllers. Each controller has its own file, and `mod.rs` is used to declare the module.\n\n7. **data/**: Contains scripts and data files for populating the database with initial sample data. The `load_sample_admin.rs` file is responsible for loading data, similar to `load-sample-admin.js`.\n\n8. **routes/**: Contains route definitions for the Actix Web application. Each route file corresponds to a specific set of API endpoints, and `mod.rs` is used to declare the module.\n\n9. **handlers/**: Contains middleware functions for error handling, similar to the original `handlers` directory. Each handler has its own file, and `mod.rs` is used to declare the module.\n\n10. **README.md**: Each directory contains a README file to provide documentation and usage instructions, similar to the original structure.\n\nThis structure adheres to Rust's best practices, promoting modularity and maintainability while ensuring that the application is easy to navigate and understand."
    """),  
    ("ai", """Following is the example of how humans think about new context files: 
    ``` 
    src/main.rs (The entry point of the application where the Actix Web server is set up.) 
        - src/routes/api.rs (this file contains the names of api endpoints and the functions)
        - src/routes/auth_api.rs (this file contains the names of auth api endpoints and the functions)
        - src/routes/mod.rs (this file gives info of where to import the api and auth_api files)
        - src/handlers/error_handler.rs (this file contains the error handling logic)
        - src/handlers/mod.rs (this file gives info of where to import the error_handler file)

    src/controllers/client_controller.rs (This file contains the business logic for the client):
        - src/models/client.rs (this file contains the client struct)
        - src/models/mod.rs (this file gives info of where to import the client file)
        - src/controllers/crud_controller/crud_methods.rs (this file contains the crud operations to be used for the client)
        - src/controllers/curd_controller/mod.rs (this file gives info of where to import the crud_methods file)
        - src/handlers/error_handler.rs (this file contains the error handling logic)
        - src/handlers/mod.rs (this file gives info of where to import the error_handler file)```
    """),
    ("human", PLANNER_HUMAN_PROMPT)
])


PLAN_EXTRACTOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Expert at identifying and extracting migration plans steps from the given migration plan. The
     plan is order list so make sure you also extract it in the same order."""),
    ("human", "{unstructured_migration_plan}")
])