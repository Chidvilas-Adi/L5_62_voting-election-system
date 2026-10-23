# Lab 5: Static Code Analysis
## Voting and Election Management System

| | |
|---|---|
| **Name** | CHIDVILASADI |
| **SRN** | PES1UG25AM802 |
| **University** | PES University |
| **File analysed** | `election_system.py` |
| **Repository** | https://github.com/Chidvilas-Adi/L5_62_voting-election-system |

---

## 1. Objective

The aim of this lab was to analyse a Python program with three static analysis tools: Pylint, Bandit and Flake8. For each tool, the reported issues were documented, fixed in a separate commit, and verified by re-running the tool. The reports from before and after the changes are included for comparison.

## 2. Environment

| Item | Details |
|---|---|
| Operating system | Arch Linux |
| Python | 3.14.7, inside a virtual environment (`venv`) |
| Pylint | Code quality and logical errors |
| Bandit 1.9.4 | Security vulnerabilities |
| Flake8 | PEP 8 style and formatting |
| Additional packages | `defusedxml` (safe XML parsing), `autopep8` (automatic formatting) |

Setup:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install pylint bandit flake8 defusedxml
```

Report generation:

```bash
python -m pylint election_system.py > pylint_report.txt
python -m bandit -r election_system.py > bandit_report.txt
python -m flake8 election_system.py > flake8_report.txt
```

## 3. About the Program

`election_system.py` is a voting and election management system. It registers voters, checks which roles are election officers, records votes before the polls close, tallies ballots, finds the winner, reports vote percentages and turnout, announces results, generates receipt numbers and imports postal ballots from XML.

The program ran without errors at the start, but several of its printed results were incorrect. These are covered in section 7.

## 4. Summary of Results

| Tool | Before | After |
|---|---|---|
| Bandit | 7 issues: 2 High, 1 Medium, 4 Low | No issues identified |
| Pylint | Baseline report lists 26 messages, including a bidirectional-unicode error (E2502). A full run after the first commit scored **6.35 / 10** with 31 messages. | **10.00 / 10** |
| Flake8 | Baseline in `before/flake8_report.txt`. 13 warnings (E302, E305) remained when the Flake8 commit began. | **0 warnings** |

Note on the Pylint baseline: `before/pylint_report.txt` ends at line 58 of the source file and has no score line, so it covers only part of the file. After the hidden-character line was removed in the Bandit commit, Pylint analysed the whole file and gave the 6.35 / 10 score above.

## 5. Bandit Issues (Security)

The baseline Bandit scan reported 7 issues (severity: 2 High, 1 Medium, 4 Low).

| # | Issue | Severity | Line(s) | Description | Fix Approach |
|---|---|---|---|---|---|
| 1 | B324: weak MD5 hash | High | 17 | Voter IDs were hashed with `hashlib.md5`, which is a broken algorithm for security use. | Replaced with `hashlib.sha256`. |
| 2 | B613: Trojan Source | High | 22 | `isOfficer` compared the role to a string containing hidden bidirectional Unicode characters (`\u202e`). The code displayed differently from how it executed, and `isOfficer("voter")` returned `True`. | Deleted the string. Added `OFFICER_ROLES = {"officer"}` and used `role in OFFICER_ROLES`. |
| 3 | B319: unsafe XML parsing | Medium | 75 | `pulldom.parseString` is vulnerable to XML attacks such as entity expansion when parsing untrusted input. | Switched to `defusedxml.ElementTree.fromstring`. |
| 4 | B409: unsafe XML import | Low | 7 | `from xml.dom import pulldom` imports the vulnerable parser. | Replaced with `from defusedxml import ElementTree`. This also resolved issue 3. |
| 5 | B105: hardcoded password | Low | 9 | `ADMIN_PASSWORD = "Election@2026"` stored a secret in source code. | Read from the `ELECTION_ADMIN_PASSWORD` environment variable. |
| 6 | B311: weak random generator | Low | 72 | `random.randint` is not suitable for security-related values such as receipt numbers. | Replaced with `secrets.randbelow`. |
| 7 | B110: try / except / pass | Low | 82 | A bare `except` silently ignored every error in `importPostalBallots`. | Removed the block. `getAttribute` does not raise here, so it was not needed. |

Result after the fix: **No issues identified** (108 lines of code scanned, 0 issues at every severity level).

## 6. Pylint Issues (Code Quality)

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| E2502: bidirectional-unicode | Error | 22 | Hidden control characters in `isOfficer`. | Fixed in the Bandit commit (see issue 2 above). |
| C0114 / C0116: missing docstrings | Convention | 1 and every function | The module and all functions had no docstrings. | Added a module docstring and a one-line docstring for each function. |
| C0103: invalid names | Convention | 15, 21, 26, 51, 58 and two more functions | Functions used camelCase instead of snake_case. | Renamed to `register_voter`, `is_officer`, `cast_vote`, `vote_percent`, `count_for`, `receipt_number` and `import_postal_ballots`, and updated every call. |
| C0303: trailing whitespace | Convention | 37, 40, 52, 69 | Extra spaces at the end of lines. | Removed. |
| C0301: line too long | Convention | 17, 96 | Two lines exceeded the 100 character limit. | Wrapped the lines. |
| W0611: unused imports | Warning | 2, 3 | `sys` and `json` were imported but never used. | Removed both imports. |
| W0612: unused variables | Warning | 32, 45, 55 | `receipt`, `total` and `now` were assigned but never used. | Removed them. |
| W0621: redefined name | Warning | 58 | The parameter `ballots` in `countFor` shadowed the global `ballots` list. | Renamed the parameter to `ballot_list`. |
| W0640: cell variable in loop | Warning | `announce()` | Lambdas created inside a loop all used the final value of `name`. | Replaced them with a list comprehension. |
| C0206: consider `.items()` | Convention | 46 | `winner` looped over dictionary keys and then indexed the dictionary. | Rewrote it with `max(counts, key=counts.get)`. |

Result after the fix: **10.00 / 10**.

## 7. Logic Bugs Not Reported by the Tools

The task notes that not every problem would be flagged by a tool. Running the program and reading its output showed the following errors. They were fixed in the Pylint commit.

| Issue | Output before the fix | Cause | Fix Approach |
|---|---|---|---|
| Age eligibility | `Register Asha (age 18): False` | `registerVoter` used `age > 18`. | Changed to `age >= 18`. |
| Double voting | `Ben votes Alice again: True` | `castVote` never checked whether the voter had already voted. | Reject the vote if `voted` is already `True`. |
| Invalid candidate | `Chen votes 'bob': True` | The candidate was never checked against the `candidates` list. | Reject any candidate not in `candidates`. |
| Polls closing time | `Dia votes Bob at 18:30: True` | `when.hour > 18` let 18:30 through, because its hour is 18. | Changed to `when.hour >= POLLS_CLOSE_HOUR`. |
| Officer check | `Is a plain 'voter' an election officer? True` | The hidden-character comparison (Bandit issue 2). | Fixed in the Bandit commit. |
| Turnout above 100% | `Turnout %: 166.67` | Turnout counted ballots instead of voters who had voted. | Count the voters whose `voted` flag is `True`. |
| Wrong announcements | `['NOTA: 0', 'NOTA: 0', 'NOTA: 0']` | The lambdas all captured the last loop value. | List comprehension (see section 6). |
| Receipt never issued | A receipt was generated inside `castVote` and thrown away. | The value was assigned to an unused variable. | Removed the unused assignment. `receipt_number()` is still available. |
| Division by zero | Not triggered by the demo data | `vote_percent` and `turnout` divided by zero when there were no ballots or voters. | Return `0` when the denominator is empty. |
| Winner with no votes | Not triggered by the demo data | `winner` had no safe handling for an empty tally. | Return `None` when there are no votes. |
| Postal ballots not validated | Not triggered by the demo data | `importPostalBallots` ignored the `voter` attribute, so unregistered voters, repeat voters and invalid candidates could be counted. | Check that the voter is registered, has not voted and that the candidate is valid, then mark the voter as having voted. |

### Program output before and after

| Line | Before | After |
|---|---|---|
| Register Asha (age 18) | `False` | `True` |
| Is a plain 'voter' an election officer? | `True` | `False` |
| Ben votes Alice again | `True` | `False` |
| Chen votes 'bob' | `True` | `False` |
| Dia votes Bob at 18:30 | `True` | `False` |
| Tally | `{'Alice': 2, 'bob': 1, 'Bob': 2}` | `{'Alice': 1, 'Bob': 1}` |
| Alice % | `40` | `50` |
| Turnout % | `166.67` | `50.0` |
| Announcements | `['NOTA: 0', 'NOTA: 0', 'NOTA: 0']` | `['Alice: 1', 'Bob: 1', 'NOTA: 0']` |

## 8. Flake8 Issues (Formatting)

By the time the Flake8 commit began, the earlier commits had already removed the other baseline warnings. Thirteen warnings remained, all about blank lines.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| E302: expected 2 blank lines | Style | 15, 26, 30, 42, 49, 56, 62, 69, 73, 77, 81, 97 | Only one blank line before top-level function definitions. PEP 8 requires two. | Added a second blank line using `autopep8 --in-place`. |
| E305: expected 2 blank lines after a function | Style | 121 | Only one blank line before the `if __name__ == "__main__":` block. | Added a second blank line. |

Result after the fix: `flake8_report.txt` is empty and Flake8 reports no warnings.

## 9. Commit History

| Commit | Message | Purpose |
|---|---|---|
| `ea3e2a3` | Add baseline static analysis reports | Saved the "before" reports in `before/` |
| `9e50be3` | Add baseline program output | Saved the original program output in `before/` |
| `ce9d3bf` | Fix Bandit security issues | Fixed all 7 Bandit findings and saved `bandit_report.txt` |
| `89ef443` | Fix Pylint issues and voting logic bugs | Raised the Pylint score to 10.00 and corrected the program logic |
| `ebe393b` | Fix Flake8 formatting issues | Removed all Flake8 warnings and saved `flake8_report.txt` |

The three fix commits correspond to the three tools. The two baseline commits only store the starting reports.

## 10. Deliverables

| Required deliverable | Location |
|---|---|
| 3 commits, one per tool | `ce9d3bf` (Bandit), `89ef443` (Pylint), `ebe393b` (Flake8) |
| Reports before | `before/pylint_report.txt`, `before/bandit_report.txt`, `before/flake8_report.txt` |
| Reports after | `pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt` in the repository root |
| Updated source file | `election_system.py` |
| Report | `report.md` (this document) |

The original program output is also saved in `before/program_output.txt`.
