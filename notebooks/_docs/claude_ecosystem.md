# Claude Ecosystem (from Anthropic)

- Claude Chat: Is the chatbot for questions, brainstorms and tackle problems. https://claude.ai. 

- Claude Cowork: Work across your files and apps.Build repeatable workflows.

- Claude Code: Used by developer to read, write and fix code directly in the codebase.

** Claude app (downloaded to machine) has above 3 feature built into it.

- Cursor: A third-party AI-native IDE (by Anysphere) that uses Claude as its primary model. It is **not** made by Anthropic.

## Claude Code
If you have the claude app downloaded to your laptop, you can invoke it from CLI by running command "claude" or Terminal. Here you analyze project, create project, fix project code, etc...

Claude Commands:
/agents
/login
/init --> creates the context file CLAUDE.md 
/models
/context --> shows the context used
/skills
claude -r --> loads the previous context

./CLAUDE.md is a special instruction file that claude code autumatically loads into contect at the start of the project. Its committed to git and shared with the team.
./CLAUDE.local.md -- personal claude file
~/.claude/CLAUDE.md -- global level file

## Claude Cowork
