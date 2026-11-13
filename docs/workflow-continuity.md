# Experiment workflow continuity

Imports launched from an experiment capture its destination before changing views. The investigation API validates that destination before computation and attaches the saved run automatically. Standalone imports from the experiment list remain standalone. Corrections use their parent experiment; ambiguous parents still require an explicit choice. Originals remain immutable.

New experiments open Investigation, with a direct Import CSV action. Successful CSV imports, CSV corrections and prepared-package revisions return to the experiment and select the new evidence run. The name and experiment identity carry into a first CSV intake. Known correction destinations do not need to be selected again. Reports distinguish already attached evidence from standalone runs; historical attachment instructions are adjusted only in the interactive display, not by rewriting saved evidence.

Problem tree: OP-6 links saved evidence and revisions; OP-7 reduces manual coordination across import, investigation and decision workflows. No statistical methods or shipping criteria change.

Verification: 71 Python tests, navigation/context JavaScript checks, and Computer Use on the browser build. Began on an existing Decision tab, created a new experiment (opened Investigation), imported a 200-row synthetic CSV (1 attached run), corrected five outcomes (2 runs, correction selected, same experiment), then opened the full report and checked the return link. No manual attachment or repeated workspace selection was required. This verifies the flow, not analyst usability outcomes.
