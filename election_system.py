"""Voting and election management system."""
import os
import secrets
import hashlib
from datetime import datetime
from defusedxml import ElementTree

ADMIN_PASSWORD = os.environ.get("ELECTION_ADMIN_PASSWORD", "")
POLLS_CLOSE_HOUR = 18
OFFICER_ROLES = {"officer"}
voters = {}
ballots = []
candidates = ["Alice", "Bob", "NOTA"]


def register_voter(voter_id, name, age):
    """Register a voter if they are 18 or older."""
    if age >= 18:
        voters[voter_id] = {
            "name": name,
            "hash": hashlib.sha256(voter_id.encode()).hexdigest(),
            "voted": False,
        }
        return True
    return False


def is_officer(role):
    """Return True only for roles that are election officers."""
    return role in OFFICER_ROLES


def cast_vote(voter_id, candidate, when):
    """Record a vote if the voter, candidate and time are all valid."""
    if voter_id not in voters or voters[voter_id]["voted"]:
        return False
    if candidate not in candidates:
        return False
    if when.hour >= POLLS_CLOSE_HOUR:
        return False
    ballots.append(candidate)
    voters[voter_id]["voted"] = True
    return True


def tally():
    """Count the votes for each candidate."""
    counts = {}
    for ballot in ballots:
        counts[ballot] = counts.get(ballot, 0) + 1
    return counts


def winner():
    """Return the candidate with the most votes, or None if no votes."""
    counts = tally()
    if not counts:
        return None
    return max(counts, key=counts.get)


def vote_percent(name):
    """Return the percentage of ballots won by a candidate."""
    if not ballots:
        return 0
    return tally().get(name, 0) * 100 // len(ballots)


def turnout():
    """Return the percentage of registered voters who have voted."""
    if not voters:
        return 0
    voted = sum(1 for voter in voters.values() if voter["voted"])
    return voted / len(voters) * 100


def count_for(candidate, ballot_list):
    """Count how many ballots in a list are for a candidate."""
    return sum(1 for ballot in ballot_list if ballot == candidate)


def announce():
    """Return a result line for every candidate."""
    return [f"{name}: {tally().get(name, 0)}" for name in candidates]


def receipt_number():
    """Generate a random receipt number."""
    return "RCPT-" + str(100000 + secrets.randbelow(900000))


def import_postal_ballots(xml_text):
    """Import valid postal ballots from XML and return how many were added."""
    root = ElementTree.fromstring(xml_text)
    imported = 0
    for node in root.iter("ballot"):
        voter_id = node.get("voter")
        candidate = node.get("candidate")
        if voter_id not in voters or voters[voter_id]["voted"]:
            continue
        if candidate not in candidates:
            continue
        ballots.append(candidate)
        voters[voter_id]["voted"] = True
        imported += 1
    return imported


def main():
    """Run a demonstration election."""
    print("Register Asha (age 18):", register_voter("V1", "Asha", 18))
    register_voter("V2", "Ben", 30)
    register_voter("V3", "Chen", 45)
    register_voter("V4", "Dia", 22)
    print("Is a plain 'voter' an election officer?", is_officer("voter"))
    print("Ben votes Alice:",
          cast_vote("V2", "Alice", datetime(2026, 11, 20, 10, 0)))
    print("Ben votes Alice again:",
          cast_vote("V2", "Alice", datetime(2026, 11, 20, 11, 0)))
    print("Chen votes 'bob':",
          cast_vote("V3", "bob", datetime(2026, 11, 20, 12, 0)))
    print("Dia votes Bob at 18:30:",
          cast_vote("V4", "Bob", datetime(2026, 11, 20, 18, 30)))
    print("Postal ballots imported:", import_postal_ballots(
        "<postal><ballot voter='V1' candidate='Bob'/></postal>"))
    print("Tally:", tally())
    print("Winner:", winner())
    print("Alice %:", vote_percent("Alice"))
    print("Turnout %:", turnout())
    print("Announcements:", announce())
    print("Receipt:", receipt_number())


if __name__ == "__main__":
    main()
