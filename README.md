# Gym Management GraphQL API - Complete Documentation

## Project Overview

This is a backend system designed to manage gym operations including member registration, class scheduling, and trainer-led workout sessions. The system uses a GraphQL interface for all operations.

**Technology Stack:**
- Backend Framework: Flask (Python)
- API Layer: GraphQL with Graphene-Mongo
- Database: MongoDB (NoSQL)
- GitHub Repository: GraphQL_Mini_project

---

## Data Models

The system has five main entities stored in MongoDB:

### Member
Represents a gym member with their profile information.
- **Fields:** Name, email, join date, membership type, and status
- **Membership Types:** Basic, Premium, or Elite
- **Status:** Active or Expired
- **Relationships:** Can enroll in multiple classes and schedule private workout sessions

### Trainer
Represents a gym trainer or instructor.
- **Fields:** Name, specialization, and availability status
- **Specialization:** Examples include Yoga, CrossFit, Pilates, etc.
- **Availability:** Boolean flag indicating if the trainer is currently accepting new sessions
- **Relationships:** Can teach multiple gym classes and conduct private sessions

### GymClass
Represents a group fitness class.
- **Fields:** Class name, description, schedule time, duration, capacity, and available spots
- Taught by one Trainer
- Has a maximum capacity and tracks remaining spots
- **Relationships:** Connected to trainer and has multiple enrollments

### ClassEnrollment
Tracks which members are enrolled in which classes.
- Links a Member to a GymClass
- Contains enrollment date
- Used to manage class capacity and prevent duplicate enrollments

### WorkoutSession
Represents a private one-on-one training session.
- Links a Member to a Trainer
- **Fields:** Scheduled time, duration in minutes, and session status
- **Status:** Can be Scheduled, Completed, or Cancelled

---

## GraphQL Queries (Read Operations)

### Member Queries

#### Get all members:
```graphql
query {
  members {
    id
    name
    email
    membershipType
    status
  }
}
```

#### Get a specific member:
```graphql
query {
  member(id: "member_id_here") {
    id
    name
    email
    enrollments {
      class {
        name
        schedule
      }
    }
    workoutSessions {
      trainer {
        name
      }
      scheduledTime
    }
  }
}
```

### Trainer Queries

#### Get all trainers:
```graphql
query {
  trainers {
    id
    name
    specialization
    available
  }
}
```

#### Get a specific trainer:
```graphql
query {
  trainer(id: "trainer_id_here") {
    id
    name
    specialization
    classes {
      name
      schedule
      availableSpots
    }
  }
}
```

### Class Queries

#### Get all gym classes:
```graphql
query {
  classes {
    id
    name
    schedule
    capacity
    availableSpots
    trainer {
      name
    }
  }
}
```

#### Get a specific class:
```graphql
query {
  gymClass(id: "class_id_here") {
    id
    name
    description
    schedule
    durationMinutes
    capacity
    availableSpots
  }
}
```

#### Get only classes with available spots:
```graphql
query {
  availableClasses {
    id
    name
    schedule
    availableSpots
    trainer {
      name
      specialization
    }
  }
}
```

---

## GraphQL Mutations (Write Operations)

### Enroll in a Class

Allows a member to join a group fitness class.

#### Mutation:
```graphql
mutation {
  enrollInClass(memberId: "member_id", classId: "class_id") {
    enrollment {
      id
      member {
        name
      }
      class {
        name
      }
      enrolledAt
    }
    success
    message
  }
}
```

#### Business Rules:
- ✅ Checks if the class has available spots
- ✅ Verifies the member exists in the system
- ✅ Prevents duplicate enrollments (same member can't enroll twice)
- ✅ Automatically decrements available spots when enrollment succeeds
- ✅ Returns error message if any validation fails

### Schedule a Workout Session

Books a private one-on-one session with a trainer.

#### Mutation:
```graphql
mutation {
  scheduleWorkout(
    memberId: "member_id",
    trainerId: "trainer_id",
    scheduledTime: "2026-03-15T10:00:00",
    durationMinutes: 60
  ) {
    session {
      id
      member {
        name
      }
      trainer {
        name
      }
      scheduledTime
      durationMinutes
    }
    success
    message
  }
}
```

#### Business Rules:
- ✅ Checks if the trainer is marked as available
- ✅ Verifies both member and trainer exist
- ✅ Validates the scheduled time format
- ✅ Duration must be a positive number

### Cancel Enrollment

Removes a member from a class.

#### Mutation:
```graphql
mutation {
  cancelEnrollment(enrollmentId: "enrollment_id") {
    success
    message
  }
}
```

#### Business Rules:
- ✅ Verifies the enrollment exists
- ✅ Increases available spots back when cancelled
- ✅ Removes the enrollment record from the database

---

## System Workflow

### Phase 1: Setup and Seeding

**Step 1 - Initialize Database:**

Run the seed script to create the necessary MongoDB collections:
```bash
python seed.py
```

**Step 2 - Populate Initial Data:**

The seed script creates:
- Sample trainers with different specializations
- Sample gym classes with various schedules
- Initial member accounts for testing
- This ensures the system isn't empty when you first start

### Phase 2: Server Execution

**Step 1 - Start the Server:**
```bash
python run.py
```
This starts the Flask application on port 8080.

**Step 2 - Access the API:**

Open your browser or GraphQL client and navigate to:
```
http://localhost:8080/graphql
```

You'll see the GraphQL Playground interface where you can run queries and mutations.

### Phase 3: Live Operations

#### Discovery Phase:
A member queries available classes to see what they can join:
```graphql
query {
  availableClasses {
    name
    schedule
    availableSpots
    trainer {
      name
      specialization
    }
  }
}
```

#### Action Phase:
The member enrolls in a class they like:
```graphql
mutation {
  enrollInClass(memberId: "abc123", classId: "xyz789") {
    enrollment {
      class {
        name
      }
    }
    success
    message
  }
}
```

The system automatically:
- Decrements the available spots count
- Creates an enrollment record
- Returns confirmation to the user

#### Validation Phase:
If a member tries to join a full class, the mutation returns:
```json
{
  "enrollment": null,
  "success": false,
  "message": "This class is full. No spots available."
}
```

### Phase 4: Verification

**Running Tests:**

Execute the test suite to verify all business rules work correctly:
```bash
python -m pytest test_queries.py
```

**What Gets Tested:**
- ✅ Class capacity limits are enforced
- ✅ Duplicate enrollments are prevented
- ✅ Trainer availability is checked
- ✅ Data validation works correctly
- ✅ Error messages are returned properly

---

## File Structure

```
gym-management-api/
├── app/
│   ├── models.py           # Database entity definitions
│   ├── schema/
│   │   ├── queries.py      # GraphQL read operations
│   │   └── mutations.py    # GraphQL write operations
│   └── __init__.py
├── seed.py                 # Database initialization script
├── run.py                  # Server startup script
├── test_queries.py         # Automated test suite
└── requirements.txt        # Python dependencies
```

---

## Common Use Cases

### Use Case 1: Member Joins the Gym
1. Admin creates a new member account
2. Member logs in and queries available classes
3. Member enrolls in desired classes
4. Member can also schedule private sessions with trainers

### Use Case 2: Trainer Updates Schedule
1. Trainer marks themselves as unavailable
2. System prevents new workout session bookings
3. Existing sessions remain unaffected
4. Trainer can mark themselves available again later

### Use Case 3: Class Fills Up
1. Class starts with 20 available spots
2. Members enroll one by one
3. When 20th member enrolls, available spots reaches 0
4. Next enrollment attempt returns an error
5. If someone cancels, spot opens up again

---

## Error Handling

The system handles these common errors:

| Error Type | Message | Action |
|------------|---------|--------|
| **Class Full** | "This class is full. No spots available." | Member cannot enroll, must choose different class |
| **Trainer Unavailable** | "This trainer is not currently available." | Member cannot book session, must choose different trainer |
| **Duplicate Enrollment** | "Member is already enrolled in this class." | Prevents duplicate records in database |
| **Invalid IDs** | "Member/Trainer/Class not found." | Returns error instead of crashing |

---

## Best Practices

### For Developers:
- ✅ Always validate input data before processing
- ✅ Use transactions for operations that modify multiple records
- ✅ Keep the database schema normalized
- ✅ Write tests for all business logic
- ✅ Log errors for debugging purposes

### For Users:
- ✅ Check available spots before enrolling
- ✅ Cancel enrollments you can't attend to free up spots
- ✅ Book private sessions in advance when trainers are available
- ✅ Keep your membership status active to access all features

---

## API Endpoints Summary

| Endpoint | Type | Description |
|----------|------|-------------|
| `/graphql` | POST | Main GraphQL endpoint for all queries and mutations |
| `/graphql` | GET | GraphQL Playground interface (development only) |

---

## Environment Variables

Create a `.env` file in the root directory:

```env
MONGODB_URI=mongodb://localhost:27017/gym_management
FLASK_ENV=development
FLASK_PORT=8080
SECRET_KEY=your_secret_key_here
```

---

## Installation Guide

### Prerequisites:
- Python 3.8 or higher
- MongoDB 4.4 or higher
- pip (Python package manager)

### Installation Steps:

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/GraphQL_Mini_project.git
cd GraphQL_Mini_project
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up MongoDB:**
```bash
# Start MongoDB service
mongod --dbpath /path/to/your/data/directory
```

5. **Initialize the database:**
```bash
python seed.py
```

6. **Run the server:**
```bash
python run.py
```

7. **Access the API:**
Open your browser and go to `http://localhost:8080/graphql`

---

## Testing

### Running All Tests:
```bash
pytest test_queries.py -v
```

### Running Specific Tests:
```bash
pytest test_queries.py::test_enroll_in_class -v
pytest test_queries.py::test_schedule_workout -v
```

### Test Coverage:
```bash
pytest --cov=app test_queries.py
```

---

## Troubleshooting

### Common Issues:

#### MongoDB Connection Error
**Problem:** Cannot connect to MongoDB
**Solution:**
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB if not running
sudo systemctl start mongod
```

#### Port Already in Use
**Problem:** Port 8080 is already occupied
**Solution:**
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process or change port in run.py
```

#### Module Import Errors
**Problem:** Cannot import modules
**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Future Enhancements

### Planned Features:
- [ ] Authentication and authorization system
- [ ] Payment integration for membership fees
- [ ] Email notifications for class reminders
- [ ] Mobile app integration
- [ ] Analytics dashboard for gym administrators
- [ ] Waitlist system for full classes
- [ ] Recurring class schedules
- [ ] Trainer rating and review system

---

## Contributing

### How to Contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style:
- Follow PEP 8 for Python code
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contact & Support

- **Project Repository:** [GraphQL_Mini_project](https://github.com/yourusername/GraphQL_Mini_project)
- **Issue Tracker:** [GitHub Issues](https://github.com/yourusername/GraphQL_Mini_project/issues)
- **Documentation:** This file

---

## Acknowledgments

- Flask team for the excellent web framework
- Graphene-Python for GraphQL implementation
- MongoDB for the flexible database solution
- All contributors who helped improve this project

---

**Last Updated:** March 1, 2026  
**Version:** 1.0.0
