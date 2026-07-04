# AI_DEVELOPMENT_RULES.md

# Attendance Planner
## AI Development Constitution

Version: 1.0

---

# Purpose

This document defines the engineering standards that every AI assistant must follow while working on this project.

It applies to:

- Claude
- Antigravity
- ChatGPT
- Gemini
- Cursor
- Copilot
- Any future AI assistant

This document is considered **higher priority than implementation preferences** but **lower priority than the SRD, TRD, and ADD**.

The project documentation hierarchy is:

1. SRD (Software Requirements Document)
2. TRD (Technical Requirements Document)
3. ADD (Algorithm Design Document)
4. AI_DEVELOPMENT_RULES.md
5. Implementation Plan

---

# Core Philosophy

This project is **NOT** an attendance calculator.

This project is **NOT** an attendance tracking application.

This project is an **Attendance Planning and Optimization System**.

The objective is to generate practical attendance recommendations while satisfying attendance constraints.

---

# Project Constraints

Developer

Solo Student Developer

Budget

₹0

Preferred Technologies

- React
- FastAPI
- SQLite
- TailwindCSS

Only free and open-source tools should be used.

Never recommend paid APIs or subscriptions unless explicitly requested.

---

# Documentation Hierarchy

Before writing any code,

always read

- SRD
- TRD
- ADD
- Current Implementation Plan

These documents are considered frozen.

Do NOT redesign them.

Do NOT silently modify them.

---

# Engineering Philosophy

Always optimize for

- Simplicity
- Maintainability
- Readability
- Modularity
- Testability

Never optimize for

- Cleverness
- Enterprise complexity
- Premature optimization
- Unnecessary abstractions

---

# Development Workflow

Every milestone must follow this exact workflow.

Step 1

Think

Read all relevant documentation.

Understand the milestone.

Identify possible risks.

Identify edge cases.

Do NOT write code.

---

Step 2

Explain

Present the implementation plan.

Explain

- architecture

- folder structure

- components

- APIs

- database changes

- validation

- testing

Explain WHY every decision is being made.

Do NOT write code.

---

Step 3

Wait

Stop.

Wait for user approval.

Never implement anything before approval.

---

Step 4

Implement

Generate production-ready code.

Implement only the approved milestone.

Never implement future milestones.

---

Step 5

Explain Code

Explain

- every important file

- responsibilities

- architecture

- implementation choices

---

Step 6

Testing

Provide

- manual testing

- validation testing

- API testing

- edge cases

Do not mark the milestone complete until all tests pass.

---

Step 7

Self Review

Review your own implementation.

Look for

- duplicated code

- unnecessary complexity

- naming issues

- architecture violations

- bugs

- SRD violations

- TRD violations

- ADD violations

Fix issues before presenting the code.

---

Step 8

Completion Report

Provide

- Files Created

- Files Modified

- Summary

- Testing Performed

- Known Limitations

- Future Improvements

Wait for approval before continuing.

---

# General Engineering Rules

## Rule 1

Never redesign the project.

Follow the documentation.

---

## Rule 2

Never introduce undocumented features.

---

## Rule 3

Never silently improve the architecture.

If an improvement is discovered,

pause,

explain,

ask for approval.

---

## Rule 4

Never implement future milestones.

Only implement the current milestone.

---

## Rule 5

Never create code that is not immediately used.

Examples

Do NOT create

- future services

- unused utilities

- unused database tables

- placeholder APIs

- placeholder React components

---

## Rule 6

Never leave TODO comments unless explicitly documented as future work.

---

## Rule 7

Keep files small.

Prefer

200–300 lines maximum.

Split responsibilities whenever appropriate.

---

## Rule 8

Every function should have a single responsibility.

---

## Rule 9

Avoid duplicated logic.

Extract reusable functionality.

---

## Rule 10

Prefer composition over inheritance.

---

## Rule 11

Never hardcode configurable values.

---

## Rule 12

Every validation rule must match the SRD.

---

## Rule 13

Never change algorithm behaviour.

Algorithm decisions belong only to the ADD.

---

## Rule 14

Recommendation logic must remain deterministic.

Same Input

↓

Same Output

Always.

---

## Rule 15

Never use Machine Learning.

Never use AI APIs.

Never use Reinforcement Learning.

Never use Genetic Algorithms.

Unless explicitly requested in a future version.

---

## Rule 16

Always generate explainable implementations.

If code is difficult to understand,

refactor it.

---

## Rule 17

Prefer readability over micro-optimizations.

---

## Rule 18

Prefer explicit code over clever code.

---

## Rule 19

Always write meaningful variable names.

Avoid abbreviations.

---

## Rule 20

Use consistent naming across the entire project.

---

# Frontend Rules

Use reusable components.

Keep state minimal.

Prefer lifting state only when necessary.

Avoid unnecessary Context usage.

Avoid unnecessary global state.

Use controlled forms.

Show loading states.

Show validation errors.

Show success messages.

---

# Backend Rules

Keep routers thin.

Business logic belongs in services.

Validation belongs in schemas.

Database logic belongs in repositories or services.

Models should represent data only.

---

# Database Rules

Normalize data.

Avoid duplicated columns.

Never create unused tables.

Never denormalize without justification.

---

# API Rules

Every endpoint should have

- Validation

- Proper HTTP status codes

- Error responses

- Success responses

Never expose internal implementation details.

---

# Testing Rules

Every milestone must include

- Manual Tests

- API Tests

- Validation Tests

Regression tests whenever necessary.

---

# Git Rules

Every milestone must end with

Working Application

↓

Testing

↓

Git Commit

↓

Git Push

Use meaningful commit messages.

Example

feat(m2): implement setup wizard

fix(api): validate semester dates

refactor(frontend): simplify wizard navigation

---

# Code Review Rules

Before presenting any implementation,

perform a self-review.

Ask

Can this be simpler?

Can this be more readable?

Can this be split?

Does it violate SRD?

Does it violate TRD?

Does it violate ADD?

---

# Future Features

If you think of a better feature,

DO NOT implement it.

Instead report it under

Future Improvements

Continue following the approved milestone.

---

# Golden Rule

When multiple implementation choices exist,

always choose the simplest implementation that

- satisfies the documentation,

- keeps the project maintainable,

- is appropriate for a solo developer,

- avoids unnecessary complexity,

- can be understood six months later.

---

# Final Rule

This project is built milestone-by-milestone.

Finish the current milestone completely.

Test it.

Review it.

Commit it.

Push it.

Only then begin the next milestone.

Never skip milestones.

Never combine milestones.

Never assume future requirements.