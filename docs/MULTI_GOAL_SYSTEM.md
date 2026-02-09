# Multi-Goal System Summary

## Overview
Both **missions** and **challenges** now support multi-goal tracking. Users must complete ALL goals to finish a mission or challenge.

## Implementation Status

### ✅ Completed

#### Database Schema
- [x] `mission_goals` table - stores individual goals for missions
- [x] `user_mission_goals` table - tracks user progress on each goal
- [x] `challenge_goals` table - stores individual goals for challenges
- [x] `user_challenge_goals` table - tracks user progress on each goal

#### Backend Code
- [x] Mission models updated with goal support ([app/models/mission.py](app/models/mission.py))
- [x] Challenge models with goal support ([app/models/challenge.py](app/models/challenge.py))
- [x] Mission repository with goal methods ([app/db/repositories/mission_repository.py](app/db/repositories/mission_repository.py))
- [x] Challenge repository with goal methods ([app/db/repositories/challenge_repository.py](app/db/repositories/challenge_repository.py))
- [x] Challenge service for auto-tracking ([app/services/challenge_service.py](app/services/challenge_service.py))

#### API Endpoints
- [x] Challenge routes with multi-goal support ([app/api/routes/challenge.py](app/api/routes/challenge.py))
- [x] Mission routes updated for goals (existing)

#### Migrations
- [x] `alembic/add_mission_goals_tables.sql` - Add mission_goals tables
- [x] `alembic/create_challenges_tables.sql` - Add challenge tables
- [x] `apply_mission_goals_migration.py` - Mission migration script
- [x] `apply_challenges_migration.py` - Challenge migration script

#### Testing & Seeding
- [x] `seed_challenges.py` - 10 multi-goal challenges
- [x] `test_multi_goal_challenges.py` - Comprehensive tests

### ⏳ Remaining Work

#### Mission Service Update
The `mission_service.py` needs to be updated to use goal-based tracking instead of the current category-based approach. It should:
- Fetch active user missions with goals
- Update individual goal progress based on journal/budget entries
- Check if all goals complete → mark mission complete
- Award points on mission completion

#### Seed Missions with Goals
The `seed_missions.py` should be updated to create multi-goal missions similar to challenges.

## Architecture

### Missions
**Use Case**: Daily/Weekly/Monthly tasks with 1-3 goals  
**Example**: "Cook 3 meals + Save $20 + Use leftovers twice"

```
missions (templates)
  └── mission_goals (1-N goals per mission)
  
user_missions (assignment)
  └── user_mission_goals (progress per goal)
```

### Challenges  
**Use Case**: Complex achievements with 2-5 goals  
**Example**: "Batch cook 3 meals + Freeze 2 meals + Use batch meals 5 times"

```
challenges (templates)
  └── challenge_goals (2-N goals per challenge)
  
user_challenges (assignment)
  └── user_challenge_goals (progress per goal)
```

##Database Schema

### Mission Goals Tables
```sql
CREATE TABLE mission_goals (
    id UUID PRIMARY KEY,
    mission_id UUID REFERENCES missions(id),
    description VARCHAR(255),
    target INTEGER,
    order_index INTEGER DEFAULT 0
);

CREATE TABLE user_mission_goals (
    id UUID PRIMARY KEY,
    user_mission_id UUID REFERENCES user_missions(id),
    goal_id UUID REFERENCES mission_goals(id),
    completed BOOLEAN DEFAULT FALSE,
    progress INTEGER DEFAULT 0,
    completed_at TIMESTAMP
);
```

### Challenge Goals Tables
```sql
CREATE TABLE challenges (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    type VARCHAR(100),
    duration INTEGER,  -- days
    reward_points INTEGER DEFAULT 0
);

CREATE TABLE challenge_goals (
    id UUID PRIMARY KEY,
    challenge_id UUID REFERENCES challenges(id),
    description VARCHAR(255),
    target INTEGER,
    order_index INTEGER DEFAULT 0
);

CREATE TABLE user_challenges (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    challenge_id UUID REFERENCES challenges(id),
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE user_challenge_goals (
    id UUID PRIMARY KEY,
    user_challenge_id UUID REFERENCES user_challenges(id),
    goal_id UUID REFERENCES challenge_goals(id),
    completed BOOLEAN DEFAULT FALSE,
    progress INTEGER DEFAULT 0,
    completed_at TIMESTAMP
);
```

## Setup Instructions

### 1. Apply Migrations
```bash
# Apply mission goals tables
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 apply_mission_goals_migration.py"

# Apply challenge tables
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 apply_challenges_migration.py"
```

### 2. Seed Data
```bash
# Seed challenges (ready to use)
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 seed_challenges.py"

# Seed missions (TODO: update for multi-goal support)
# wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 seed_missions.py"
```

### 3. Test
```bash
# Test multi-goal challenges
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 test_multi_goal_challenges.py"
```

## API Examples

### Get All Challenges with Goals
```http
GET /api/challenges/
```
Response:
```json
[
  {
    "id": "uuid",
    "title": "Zero Waste Week",
    "type": "zero_waste",
    "duration": 7,
    "reward_points": 180,
    "goals": [
      {"id": "uuid", "description": "Use leftovers 5 times", "target": 5, "order_index": 0},
      {"id": "uuid", "description": "Cook with scraps 3 times", "target": 3, "order_index": 1},
      {"id": "uuid", "description": "Freeze meals 2 times", "target": 2, "order_index": 2}
    ]
  }
]
```

### Assign Challenge
```http
POST /api/challenges/assign/{challenge_id}
```
Creates:
- `user_challenges` entry (status='active')
- `user_challenge_goals` entries for each goal (progress=0, completed=false)

### Get Active Challenges with Progress
```http
GET /api/challenges/active/all
```
Response:
```json
[
  {
    "id": "user_challenge_id",
    "challenge_title": "Zero Waste Week",
    "status": "active",
    "completed_goals": 1,
    "total_goals": 3,
    "goal_progress": [
      {
        "goal_description": "Use leftovers 5 times",
        "progress": 5,
        "goal_target": 5,
        "completed": true
      },
      {
        "goal_description": "Cook with scraps 3 times",
        "progress": 1,
        "goal_target": 3,
        "completed": false
      },
      {
        "goal_description": "Freeze meals 2 times",
        "progress": 0,
        "goal_target": 2,
        "completed": false
      }
    ]
  }
]
```

### Get Active Missions with Goals
```http
GET /api/missions/active
```
Response structure similar to challenges, with `goal_progress` array.

## Auto-Tracking Logic

### Challenge Service
When user creates journal/budget entry:
1. Fetch active challenges with uncompleted goals
2. For each goal, check if entry matches goal criteria:
   - Batch cooking: `portions >= 3`
   - Leftover: `status='leftovers'` or `used_leftovers=true`
   - New recipe: History check (not cooked before)
   - Budget: Compare cost to daily budget
3. Update goal progress: `progress += 1`
4. If goal reaches target: Mark `completed=true`, set `completed_at`
5. If ALL goals completed: Mark challenge complete, award points

### Mission Service (TODO)
Should work identically to challenge service but for missions.

## Key Features

✅ **Multi-Goal Support** - Both missions and challenges support multiple objectives  
✅ **Individual Tracking** - Each goal tracked separately with its own progress  
✅ **All-or-Nothing** - Must complete ALL goals to finish mission/challenge  
✅ **Auto-Completion** - Goals update automatically from journal/budget actions  
✅ **Points on Completion** - Points awarded when last goal is completed  
✅ **Backward Compatible** - Existing single-goal missions still work via `target` field  

## Example Multi-Goal Mission

```json
{
  "title": "Daily Chef Challenge",
  "type": "daily",
  "reward_points": 50,
  "goals": [
    {"description": "Cook 3 meals", "target": 3},
    {"description": "Try 1 new recipe", "target": 1},
    {"description": "Use leftovers once", "target": 1}
  ]
}
```

User must complete all 3 goals within 24 hours to earn 50 points.

## Next Steps

1. **Update mission_service.py** - Implement goal-based tracking
2. **Update seed_missions.py** - Add multi-goal missions
3. **Test mission auto-tracking** - Verify goal progress updates
4. **Test full workflow** - Assignment → progress → completion → points
5. **Update API documentation** - Document goal structures


## Documentation
- [docs/MULTI_GOAL_CHALLENGES.md](docs/MULTI_GOAL_CHALLENGES.md) - Detailed challenge documentation
- [docs/DATABASE_SCHEMA.sql](docs/DATABASE_SCHEMA.sql) - Full schema reference
