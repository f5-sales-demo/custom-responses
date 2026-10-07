# Application panel corrections outside the editorial rewrite

The deployed `/demo/panel` remains available for same-origin POST redirect and scoped-header comparisons. [Issue #59](https://github.com/f5-sales-demo/custom-responses/issues/59) tracks the runtime correction. Issue #58 changes documentation only and preserves the VM fixture.

The fixture's CORS explanation says the application panel has a different origin and demonstrates denied access. It actually fetches the same application origin, where CORS permission is unnecessary. Its exception handler also labels a failed fetch as denied browser access, although network and server failures can produce the same exception.

Correct both statements in a separate runtime change: explain same-origin access, and report an incomplete test without inferring denial from a fetch exception. Preserve click-only execution, fixed owned destinations, synthetic inputs and the twelve-request budget.

Updating the deployed fixture requires a separately scoped VM change and validation. The English CORS guide already explains these limits and uses a focused documentation widget for allowed cross-origin access.
