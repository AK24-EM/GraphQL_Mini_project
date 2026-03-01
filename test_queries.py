"""
test_queries.py — Automated test runner for the Gym Management GraphQL API.

Prerequisites:
    1. MongoDB running locally on port 27017
    2. python seed.py   (populate data)
    3. python run.py &  (server on port 5000)

Run:
    python test_queries.py
"""
import requests
import json
import sys

URL = "http://127.0.0.1:8080/graphql"
PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"

results = []


def gql(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(URL, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def check(test_name, condition, detail=""):
    symbol = PASS if condition else FAIL
    status = "PASS" if condition else "FAIL"
    print(f"  {symbol}  {test_name}")
    if detail and not condition:
        print(f"       Detail: {detail}")
    results.append((test_name, condition))


print("\n" + "=" * 60)
print(" 🏋️  GYM MANAGEMENT GRAPHQL API — TEST SUITE")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# TEST 1: Get all trainers with their classes
# ─────────────────────────────────────────────────────────────
print("\n[1] Trainers with classes")
try:
    data = gql("""
    query {
      trainers {
        id
        name
        specialization
        classes {
          name
          schedule
        }
      }
    }
    """)
    trainers = data["data"]["trainers"]
    check("Returns trainer list", len(trainers) > 0)
    all_have_name = all(t["name"] for t in trainers)
    check("All trainers have name & specialization",
          all_have_name and all(t["specialization"] for t in trainers))
    has_classes = any(len(t["classes"]) > 0 for t in trainers)
    check("At least one trainer has classes", has_classes)
except Exception as e:
    check("Trainers query (critical error)", False, str(e))

# ─────────────────────────────────────────────────────────────
# TEST 2: Get member detail with enrollments and workout sessions
# ─────────────────────────────────────────────────────────────
print("\n[2] Member detail (enrollments + workout sessions)")
try:
    all_members = gql("query { members { id name } }")
    alice_id = next(
        m["id"] for m in all_members["data"]["members"] if m["name"] == "Alice Wong"
    )
    data = gql("""
    query GetMember($id: String!) {
      member(id: $id) {
        name
        membershipType
        status
        enrollments {
          enrolledAt
          gymClass { name }
        }
        workoutSessions {
          scheduledTime
          durationMinutes
          status
          trainer { name }
        }
      }
    }
    """, {"id": alice_id})
    member = data["data"]["member"]
    check("Member name returned", member["name"] == "Alice Wong")
    check("Member has enrollments", len(member["enrollments"]) > 0)
    check("Enrollment has class name", member["enrollments"][0]["gymClass"]["name"] != "")
    check("Member has workout sessions", len(member["workoutSessions"]) > 0)
    check("Session has trainer name", member["workoutSessions"][0]["trainer"]["name"] != "")
except Exception as e:
    check("Member query (critical error)", False, str(e))

# ─────────────────────────────────────────────────────────────
# TEST 3: Available classes (with availableSpots)
# ─────────────────────────────────────────────────────────────
print("\n[3] Available classes")
try:
    data = gql("""
    query {
      availableClasses {
        name
        schedule
        availableSpots
        trainer { name }
      }
    }
    """)
    available = data["data"]["availableClasses"]
    check("Returns available class list", len(available) > 0)
    spots_positive = all(c["availableSpots"] > 0 for c in available)
    check("All returned classes have positive available spots", spots_positive)
    names = [c["name"] for c in available]
    check("HIIT Blast (full class) is NOT in available classes",
          "HIIT Blast" not in names, f"Found: {names}")
except Exception as e:
    check("Available classes query (critical error)", False, str(e))

# ─────────────────────────────────────────────────────────────
# TEST 4: enrollInClass mutation
# ─────────────────────────────────────────────────────────────
print("\n[4] enrollInClass mutation")
try:
    bob_id = next(
        m["id"] for m in all_members["data"]["members"] if m["name"] == "Bob Martinez"
    )
    core_class = next(
        c for c in gql("query { classes { id name } }")["data"]["classes"]
        if c["name"] == "Core & Stretch"
    )
    data = gql("""
    mutation Enroll($input: EnrollInClassInput!) {
      enrollInClass(input: $input) {
        enrollment {
          id
          enrolledAt
          gymClass { name }
        }
        error
      }
    }
    """, {"input": {"memberId": bob_id, "classId": core_class["id"]}})
    payload = data["data"]["enrollInClass"]
    check("Enrollment created (no error)", payload["error"] is None, str(payload.get("error")))
    check("Enrollment has class name", payload["enrollment"]["gymClass"]["name"] == "Core & Stretch")
    enrollment_id = payload["enrollment"]["id"]

    # Duplicate enrollment check
    dup = gql("""
    mutation Enroll($input: EnrollInClassInput!) {
      enrollInClass(input: $input) { enrollment { id } error }
    }
    """, {"input": {"memberId": bob_id, "classId": core_class["id"]}})
    check("Duplicate enrollment rejected", dup["data"]["enrollInClass"]["error"] is not None)
except Exception as e:
    check("enrollInClass mutation (critical error)", False, str(e))
    enrollment_id = None

# ─────────────────────────────────────────────────────────────
# TEST 5: Capacity enforcement (HIIT Blast is full)
# ─────────────────────────────────────────────────────────────
print("\n[5] Capacity enforcement")
try:
    david_id = next(
        m["id"] for m in all_members["data"]["members"] if m["name"] == "David Lee"
    )
    hiit_id = next(
        c["id"] for c in gql("query { classes { id name } }")["data"]["classes"]
        if c["name"] == "HIIT Blast"
    )
    data = gql("""
    mutation Enroll($input: EnrollInClassInput!) {
      enrollInClass(input: $input) { enrollment { id } error }
    }
    """, {"input": {"memberId": david_id, "classId": hiit_id}})
    check("Full class enrollment rejected with error",
          data["data"]["enrollInClass"]["error"] is not None)
except Exception as e:
    check("Capacity enforcement test (critical error)", False, str(e))

# ─────────────────────────────────────────────────────────────
# TEST 6: scheduleWorkout mutation
# ─────────────────────────────────────────────────────────────
print("\n[6] scheduleWorkout mutation")
try:
    trainer_id = next(
        t["id"] for t in gql("query { trainers { id name } }")["data"]["trainers"]
        if t["name"] == "Carlos Mendez"
    )
    data = gql("""
    mutation Schedule($input: ScheduleWorkoutInput!) {
      scheduleWorkout(input: $input) {
        session {
          id
          scheduledTime
          durationMinutes
          status
        }
        error
      }
    }
    """, {"input": {
        "memberId": alice_id,
        "trainerId": trainer_id,
        "scheduledTime": "2024-03-15T14:00:00",
        "durationMinutes": 60,
    }})
    payload = data["data"]["scheduleWorkout"]
    check("Workout session created (no error)", payload["error"] is None, str(payload.get("error")))
    check("Session status is 'scheduled'", payload["session"]["status"] == "scheduled")
    check("Duration is 60 minutes", payload["session"]["durationMinutes"] == 60)
except Exception as e:
    check("scheduleWorkout mutation (critical error)", False, str(e))

# ─────────────────────────────────────────────────────────────
# TEST 7: cancelEnrollment mutation
# ─────────────────────────────────────────────────────────────
print("\n[7] cancelEnrollment mutation")
try:
    if enrollment_id:
        data = gql("""
        mutation Cancel($id: String!) {
          cancelEnrollment(enrollmentId: $id) {
            success
            message
          }
        }
        """, {"id": enrollment_id})
        payload = data["data"]["cancelEnrollment"]
        check("Enrollment cancelled successfully", payload["success"] is True)
        check("Success message returned", "cancelled" in payload["message"].lower())

        # Cancelling again should fail
        data2 = gql("""
        mutation Cancel($id: String!) {
          cancelEnrollment(enrollmentId: $id) { success message }
        }
        """, {"id": enrollment_id})
        check("Re-cancel non-existent enrollment returns failure",
              data2["data"]["cancelEnrollment"]["success"] is False)
    else:
        check("cancelEnrollment skipped (no enrollment_id from test 4)", False)
except Exception as e:
    check("cancelEnrollment mutation (critical error)", False, str(e))

# ─────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f" Results: {passed}/{total} tests passed")
print("=" * 60 + "\n")
sys.exit(0 if passed == total else 1)
