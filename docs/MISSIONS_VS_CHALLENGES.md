# Mission vs Challenge Distinction

## Overview

The system now distinguishes between **missions** and **challenges** using a `kind` field:

- **mission**: Regular daily/weekly/monthly tasks
- **challenge**: Special themed challenges with higher difficulty/rewards
- **event**: Limited-time special events (future use)

## Database Schema

```sql
-- missions table now has:
kind VARCHAR(20) DEFAULT 'mission' CHECK (kind IN ('mission', 'challenge', 'event'))
```

## API Endpoints

### Get All Missions (Regular)
```bash
GET /api/missions/available?kind=mission
```

Returns only regular missions like "Cook 3 meals", "Track your spending"

### Get All Challenges
```bash
GET /api/missions/available?kind=challenge
```

Returns only challenges like "Batch Cooking Challenge", "Cook Streak", "No Spend Weekend"

### Get Both (No Filter)
```bash
GET /api/missions/available
```

Returns everything, sorted by: kind → type → category → difficulty

### Combined Filters
```bash
# Get only weekly challenges
GET /api/missions/available?mission_type=weekly&kind=challenge

# Get only daily missions (not challenges)
GET /api/missions/available?mission_type=daily&kind=mission
```

## Response Format

```json
{
  "id": "uuid",
  "title": "Batch Cooking Challenge",
  "description": "Cook meals in batches...",
  "type": "weekly",
  "category": "cooking",
  "difficulty": "medium",
  "target": 3,
  "reward_points": 100,
  "kind": "challenge",  // ← NEW FIELD
  "created_at": "2026-02-07T...",
  "updated_at": "2026-02-07T..."
}
```

## Migration & Setup

### 1. Apply Migration
```bash
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 apply_mission_kind_migration.py"
```

This will:
- Add `kind` column to missions table
- Update existing challenges to `kind='challenge'`
- Create index for faster filtering

### 2. Seed Challenges
```bash
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 seed_challenge_missions.py"
```

This adds 10 challenges:
- Batch Cooking Challenge
- Weekly Savings Challenge
- No Spend Weekend
- Swap Challenge
- Swap & Save Challenge
- One Pot Wonder
- Cook Streak
- Leftover Makeover
- Batch Prep Master
- Zero Waste Week

## Usage Examples

### Frontend: Show Separate Tabs

```javascript
// Missions Tab
const missions = await fetch('/api/missions/available?kind=mission')

// Challenges Tab
const challenges = await fetch('/api/missions/available?kind=challenge')
```

### Frontend: Filter by Difficulty

```javascript
// Show only hard challenges
const hardChallenges = await fetch(
  '/api/missions/available?kind=challenge&difficulty=hard'
)
```

### Assignment (Same API)

```javascript
// Assign a challenge (same endpoint as missions)
POST /api/missions/assign/{challenge_id}

// Check active (returns both missions and challenges)
GET /api/missions/active
```

## Active Missions Response

Active missions/challenges include the `kind` field in nested mission object:

```json
{
  "id": "user_mission_id",
  "mission_id": "mission_template_id",
  "status": "active",
  "progress": 2,
  "mission": {
    "id": "mission_template_id",
    "title": "Cook Streak",
    "kind": "challenge",  // ← Shows if it's a challenge
    "target": 5,
    ...
  },
  ...
}
```

## Testing

```bash
# Test challenge assignments
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 test_challenge_missions.py"
```

## Benefits

1. **Clear UX Distinction**: Users see missions vs challenges separately
2. **Better Organization**: Easier to browse and filter
3. **Different Presentation**: Can style challenges differently in UI
4. **Event Support**: Future expansion for limited-time events
5. **Analytics**: Track mission vs challenge completion rates separately

## Backward Compatibility

- Existing missions without `kind` default to `'mission'`
- All endpoints work without `kind` filter (returns everything)
- No breaking changes to existing API
