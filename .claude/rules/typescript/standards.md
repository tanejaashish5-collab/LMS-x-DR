# TypeScript Standards

## Type Safety
- Enable `strict: true` in tsconfig
- Avoid `any` — use `unknown` and narrow with type guards
- Prefer interfaces for object shapes, types for unions/intersections
- Use generics over type assertions
- Never use `@ts-ignore` — fix the type error instead

## Patterns
- Use `const` by default, `let` only when reassignment is needed
- Prefer `readonly` for properties that shouldn't change
- Use optional chaining (`?.`) and nullish coalescing (`??`)
- Destructure objects and arrays when it improves readability
- Use template literals over string concatenation

## Functions
- Type all parameters and return values
- Use arrow functions for callbacks
- Prefer named functions for top-level declarations
- Use function overloads sparingly — prefer union types

## Async
- Always `await` promises — no floating promises
- Use `Promise.all` for independent async operations
- Handle errors with try/catch, not `.catch()`
- Set timeouts on all external calls

## Imports
- Use named imports over default imports
- Group: external libs → internal modules → types → styles
- Use path aliases (`@/`) to avoid deep relative imports
- No circular imports

## React (if applicable)
- Functional components only
- Custom hooks for shared logic (`use` prefix)
- Complete `useEffect` dependency arrays
- Memoize expensive computations (`useMemo`, `useCallback`)
- Use `key` prop correctly on lists (no index as key)
