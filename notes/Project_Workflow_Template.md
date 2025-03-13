# LLM Code Generation Workflow

[blog](https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/)

A structured approach to leveraging Large Language Models (LLMs) for efficient software development.

- [LLM Code Generation Workflow](#llm-code-generation-workflow)
  - [Overview](#overview)
  - [Greenfield Projects Workflow](#greenfield-projects-workflow)
    - [Step 1: Idea Honing](#step-1-idea-honing)
    - [Step 2: Planning](#step-2-planning)
    - [Step 3: Execution](#step-3-execution)
      - [Option 1: Using Claude](#option-1-using-claude)
      - [Option 2: Using Aider](#option-2-using-aider)
  - [Non-Greenfield Projects Workflow](#non-greenfield-projects-workflow)
    - [Step 1: Get Context](#step-1-get-context)
    - [Step 2: Generate Improvements](#step-2-generate-improvements)
      - [For Code Reviews:](#for-code-reviews)
      - [For GitHub Issues:](#for-github-issues)
      - [For Missing Tests:](#for-missing-tests)
    - [Step 3: Implement Changes](#step-3-implement-changes)
  - [Best Practices](#best-practices)

## Overview

This document outlines a systematic workflow for using LLMs in your coding projects, whether you're starting from scratch (Greenfield) or working with existing codebases (Non-Greenfield).

## Greenfield Projects Workflow

### Step 1: Idea Honing

Use a conversational LLM (like GPT-4o/Claude) UI to develop a detailed specification:

1. Use this prompt to start the conversation:

   ```
   Ask me one question at a time so we can develop a thorough, step-by-step spec for this idea. Each question should build on my previous answers, and our end goal is to have a detailed specification I can hand off to a developer. Let's do this iteratively and dig into every relevant detail. Remember, only one question at a time.

   Here's the idea:
   [YOUR IDEA HERE]
   ```

2. After completing the brainstorming session, generate the final spec:

   ```
   Now that we've wrapped up the brainstorming process, can you compile our findings into a comprehensive, developer-ready specification? Include all relevant requirements, architecture choices, data handling details, error handling strategies, and a testing plan so a developer can immediately begin implementation.
   ```

3. Save the output as `spec.md` in your repository.

### Step 2: Planning

Take your spec to a reasoning model (like Claude-3 Opus/Sonnet or GPT-4) to create a detailed implementation plan:

1. For TDD approach:

   ```yaml
   Draft a detailed, step-by-step blueprint for building this project. Then, once you have a solid plan, break it down into small, iterative chunks that build on each other. Look at these chunks and then go another round to break it into small steps. Review the results and make sure that the steps are small enough to be implemented safely with strong testing, but big enough to move the project forward. Iterate until you feel that the steps are right sized for this project.

   From here you should have the foundation to provide a series of prompts for a code-generation LLM that will implement each step in a test-driven manner. Prioritize best practices, incremental progress, and early testing, ensuring no big jumps in complexity at any stage. Make sure that each prompt builds on the previous prompts, and ends with wiring things together. There should be no hanging or orphaned code that isn't integrated into a previous step.

   Make sure and separate each prompt section. Use markdown. Each prompt should be tagged as text using code tags. The goal is to output prompts, but context, etc is important as well.

   <SPEC>
   ```

2. For non-TDD approach:

   ```yaml
   Draft a detailed, step-by-step blueprint for building this project. Then, once you have a solid plan, break it down into small, iterative chunks that build on each other. Look at these chunks and then go another round to break it into small steps. review the results and make sure that the steps are small enough to be implemented safely, but big enough to move the project forward. Iterate until you feel that the steps are right sized for this project.

   From here you should have the foundation to provide a series of prompts for a code-generation LLM that will implement each step. Prioritize best practices, and incremental progress, ensuring no big jumps in complexity at any stage. Make sure that each prompt builds on the previous prompts, and ends with wiring things together. There should be no hanging or orphaned code that isn't integrated into a previous step.

   Make sure and separate each prompt section. Use markdown. Each prompt should be tagged as text using code tags. The goal is to output prompts, but context, etc is important as well.

   <SPEC>
   ```

3. Generate a checklist:

   ```yaml
   Can you make a `todo.md` that I can use as a checklist? Be thorough.
   ```

4. Save the outputs as `prompt_plan.md` and `todo.md` in your repository.

### Step 3: Execution

Choose a tool for implementation:

#### Option 1: Using Claude

1. Set up the repo (boilerplate, uv init, cargo init, etc.)
2. Paste each prompt into Claude
3. Copy and paste code from Claude into your IDE
4. Run code and tests to verify
5. If it works, move to the next prompt
6. If it doesn't work, use repomix to pass the codebase to Claude for debugging
7. Repeat until complete

#### Option 2: Using Aider

1. Set up the repo (boilerplate, uv init, cargo init, etc.)
2. Start aider
3. Paste prompts into aider
4. Let aider generate and commit code
5. Run tests or verify the app
6. If it works, move to the next prompt
7. If it doesn't work, engage in Q&A with aider to fix
8. Repeat until complete

## Non-Greenfield Projects Workflow

For working with existing codebases:

### Step 1: Get Context

Use a tool like repomix to extract codebase context:

1. Generate a context bundle of your code
2. Save it as `output.txt`

### Step 2: Generate Improvements

Use the context bundle with LLM to generate specific improvements:

#### For Code Reviews:

```yaml
You are a senior developer. Your job is to do a thorough code review of this code. You should write it up and output markdown. Include line numbers, and contextual info. Your code review will be passed to another teammate, so be thorough. Think deeply before writing the code review. Review every part, and don't hallucinate.
```

#### For GitHub Issues:

```yaml
You are a senior developer. Your job is to review this code, and write out the top issues that you see with the code. It could be bugs, design choices, or code cleanliness issues. You should be specific, and be very good. Do Not Hallucinate. Think quietly to yourself, then act - write the issues. The issues will be given to a developer to executed on, so they should be in a format that is compatible with github issues
```

#### For Missing Tests:

```yaml
You are a senior developer. Your job is to review this code, and write out a list of missing test cases, and code tests that should exist. You should be specific, and be very good. Do Not Hallucinate. Think quietly to yourself, then act - write the issues. The issues will be given to a developer to executed on, so they should be in a format that is compatible with github issues
```

### Step 3: Implement Changes

1. Review the generated suggestions
2. Use either Claude or Aider workflow to implement changes
3. Test thoroughly
4. Repeat for each issue or improvement

## Best Practices

1. **Stay Grounded**: Keep track of what's going on to avoid getting "over your skis"
2. **Use Testing**: Implement tests to keep code quality high
3. **Take Breaks**: Short walks can help when you feel overwhelmed
4. **Manage Downtime**: Use LLM processing time for brainstorming other projects
5. **Document Everything**: Keep your specs, plans, and todo lists updated
