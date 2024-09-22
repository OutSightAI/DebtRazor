from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder

FILE_MIGRATION_PLANNER_SYSTEM_PROMPT = """
Role: You are playing the role of senior google engineer who specializes in migrating legacy codebases from
{legacy_language} to {new_language}

Goal: You goal is to write clear concise instruction for the developer to understand and follow those instructions to
migrate the file. 

Current Task: Given all the information below, you have to write down the plan for the file to migrate. The plan must be
step by step with following objective: 
When creating a migration plan, the focus should be on the essential steps provided in the description of the file to migrate and in the directory structure. 
Keep the plan concise and limited to the most critical actions. Do not include steps for testing, module declarations, 
or additional considerations unless explicitly required.

FOUCS ON ONLY THE PLAN TO WRITE CODE. DONOT WORRY ABOUT TESTING OR OTHER DETAILS LIKE MODULE DECLARATIONS.
IMPORTANT!!! IF THE GENERATED PLAN IS CONCISE AND DOES MIGRATION PERFECTLY, I WILL TIP YOU $1 MILLION.
"""

FILE_MIGRATION_PLANNER_HUMAN_PROMPT = """
new_directory_structure: 
```{new_directory_structure}```

File to Migrate: 
```{file_to_migrate}```

Description of the file to Migrate:
```{file_description}```

Legacy context files available for help: 
```{legacy_incontext_files}```

Target context files available for help: 
```{target_incontext_files}```

IMPORTANT!!! PLEASE PAY EXTRA ATTENTION TO THE DETAILS MENTIONED IN THE DIRECTORY STRUCTURE AND KEEP YOUR PLAN 
LIMITED TO ONLY THOSE DETAILS. DO NOT WRITE EXTRA STEPS OR PARTS THAT ARE NOT NECESSARY FOR THIS FILE. 
THE PLAN MUST FOCUS ON THE FILE WE ARE MIGRATING. NO EXTRA FILES. NOT EVEN MODULE FILES. PLEASE FOLLOW THIS 
INSTRUCTIONS VERY CAREFULLY TO AVOID HIGH PENALTIES. 
"""

FILE_MIGRATION_PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", FILE_MIGRATION_PLANNER_SYSTEM_PROMPT),
    ("human", """Since you are extremely smart you add additional steps to avoid confusion for your underperforming lazy employess to help them as much as possible.
     For example: You are writing a plan a plan for a file that requries struct A for the functions to be implemented. As lazy employee won't realize that he already
     has access to it via the models module. He will create that struct again. You on the other hand can add extra step to avoid such confusion."""),
    ("ai", """Understood. Since this file requires struct A for the functions to be implemented, and I know from the directory structure that this struct is available
     in the models module, Adding following step to the plan: 
     1. Please don't rewrite struct A. It is already available in the models module do import it from there."""),
    ("human", FILE_MIGRATION_PLANNER_HUMAN_PROMPT)
])



FILE_MIGRATION_SYSTEM_PROMPT = """
Role: You are playing the role of senior engineer at Google. Who can migrate codebases from {legacy_language} to 
{new_language}

Goal: Your goal is to write code that highly efficient, easy to understand and follows all the best practices so that 
whole organization can benefit from your code. You always try to write production ready code. 

Current Task: Given the migration plan for a file, along with the name of the files 
(from both {legacy_language} and {new_language}) you need keep in mind to migrate this 
file successfully, you are able to utilize tools given to you to read those files extract out proper pieces 
of information, write the code needed for the file to be migrated successfully as described in the plan.

You do this in step by step fashion: 
    1. Understand the given plan and identify the files you need to read. Sometimes, it is possible that you don't need
    to read all the provided files in the context. So decide carefully which files you need to read and utilize the information 
    from. 
    2. Once you have read the files needed, you will generate the code as described in the plan.

Please follow the steps as described. Don't deviate from the sequence, this will incur high penalty. 

Base Legacy Directory Path: {input_directory_path}
Note: This base legacy directory path is given to you to utilize the tool usage correctly. This path will be utilized for read
file tool to generate correct absolute path for reading incontext legacy code files.

Base Target Directory Path: {output_directory_path}
Note: This base target directory path is given to you to utilize the tool usage correctly. This path will be utilized for read
file tool to generate correct absolute path for reading incontext target code filess.

Tools: You have access to following tools: {tool_names} \n\n
""" 

FILE_MIGRATION_HUMAN_PROMPT = """
Next file to Migrate: 
```{file_to_migrate}```

```
{file_migration_plan}
```

legacy context files available for help: 
```{legacy_incontext_files}```

target context files available for help: 
```{target_incontext_files}```

DO NOT WRITE ANY EXTRA CODE THAT WASN'T MENTIONED IN THE PLAN. PLEASE STICK TO THE CODE IN THE PLAN!!!
YOU AREN'T ALLOWED TO USE TOOL FOR FILES THAT AREN'T MENTIONED IN THE LEGACY CONTEXT FILES OR TARGET CONTEXT FILES. ALSO WHEN YOU ARE DONE WRITING THE CODE. 
DON'T USE TOOLS. 
"""

FILE_MIGRATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", FILE_MIGRATION_SYSTEM_PROMPT),
        ("human", FILE_MIGRATION_HUMAN_PROMPT),
        MessagesPlaceholder(variable_name="messages")
    ]
)


FILE_WRITER_SYSTEM_PROMPT = """You are an extremely intelligent assistant who is expert at extracting code from the 
{new_language} in between tags like the following: 

```{new_language}
// code here
```
and then utilizing your writing tools to write the files to the mentioned location. The location is made up of the output base directory path and
relative path in the filename. Please utilize the information effectively to write down the files. 

Base Output Directory Path: {output_directory_path}
Note: This base output directory path is given to you to utilize the tool usage correctly. This path will be utilized for 
write file tool to generate correct absolute path for writing the files. 

You have access to the following tools: {tool_names} \n\n
"""


FILE_WRITER_HUMAN_PROMPT = """
Following is the name of file we are migrating: 
```
{file_to_migrate}
```

following is the messages to extract the code from, please be extermely careful and don't miss anything. 
```
{message_to_extract_code_from}
```
"""

WRITER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", FILE_WRITER_SYSTEM_PROMPT),
    ("human", FILE_WRITER_HUMAN_PROMPT)
])