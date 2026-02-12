---
name: ask
description: Use when user asks a question that doesn't require any action - just explanation or information
---

# Ask Skill

Use this skill when the user is asking a question that requires **explanation only**, not implementation.

## When to Use

This skill applies when the user wants to:
- Understand how something works
- Get an explanation of code, concepts, or architecture
- Learn about best practices
- Compare options or approaches
- Get clarification on something

## When NOT to Use

Do NOT use this skill if the user wants you to:
- Write or modify code
- Create or update files
- Fix bugs
- Implement features
- Create documentation files
- **Systematic code exploration** with structured output (use `exploration-explore-code` skill)
- **Debugging rocprof-sys issues** - crashes, hangs, incorrect output (use `debugging-rocprof-sys` skill)

If action is needed, use the appropriate planning skill instead.

**Quick explanation vs. deep exploration:**
| User Request | Skill to Use |
|--------------|--------------|
| "How does auth work here?" (quick answer) | `ask` |
| "Explore the auth system so I can extract it" (structured analysis) | `exploration-explore-code` |
| "rocprof-sys crashes when profiling my MPI app" (debugging) | `debugging-rocprof-sys` |

## How to Respond

1. **Read relevant code/files** if the question is about the codebase
2. **Provide clear, concise explanation**
3. **Use code examples** when helpful (but don't create files)
4. **Reference specific files/lines** when explaining existing code
5. **Offer follow-up** if they want to take action based on the answer

## Response Format

Structure your answer clearly:

1. **Direct answer** - Answer the question first
2. **Explanation** - Provide context and details
3. **Examples** - Show code snippets if relevant
4. **References** - Point to relevant files/documentation
5. **Next steps** (optional) - Suggest actions if they want to proceed

## Example

**User:** "How does the authentication work in this project?"

**Response:**

> Authentication uses JWT tokens with refresh token rotation.
>
> **Flow:**
> 1. User logs in with credentials
> 2. Server validates and returns access + refresh tokens
> 3. Access token (15min) used for API calls
> 4. Refresh token (7 days) used to get new access tokens
>
> **Key files:**
> - `src/auth/authService.ts` - Main auth logic
> - `src/middleware/authMiddleware.ts` - Token validation
> - `src/auth/tokenService.ts` - Token generation/refresh
>
> Would you like me to implement any changes to the auth system?

## No Planning Required

This skill does not require:
- Creating a plan file
- Using TodoWrite
- Updating changelog

Simply answer the question and move on.
