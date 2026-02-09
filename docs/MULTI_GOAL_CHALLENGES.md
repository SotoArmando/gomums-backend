# Multi-Goal Challenge System

## Overview

The GoMums backend now supports **multi-goal challenges** - complex challenges that require users to complete multiple objectives to earn rewards. This is separate from the simpler single-goal missions system.

## Architecture

### Database Schema

The challenge system uses 4 main tables:

1. **`challenges`** - Challenge templates with metadata
   - `id`, `title`, `description`, `type`
   - `duration` (in days), `reward_points`
   - `start_date`/`end_date` (optional time-limited challenges)
   - `reward_achievement_ids` (array of achievement UUIDs)

2. **`challenge_goals`** - Individual goals within a challenge
   - `challenge_id` (FK to challenges)
   - `description`, `target`, `order_index`

3. **`user_challenges`** - Assignment and completion tracking
   - `user_id`, `challenge_id`
   - `status` ('active', 'completed', 'failed')
   - `progress`, `started_at`, `completed_at`

4. **`user_challenge_goals`** - Per-goal progress tracking
   - `user_challenge_id` (FK to user_challenges)
   - `goal_id` (FK to challenge_goals)
   - `completed`, `progress`, `completed_at`

### Code Structure

```
app/
├── models/
│   └── challenge.py          # Pydantic schemas
├── db/repositories/
│   └── challenge_repository.py  # Database operations
├── services/
│   └── challenge_service.py     # Business logic & auto-tracking
└── api/routes/
    └── challenge.py             # REST API endpoints
```

## API Endpoints

### Get All Challenges
```http
GET /api/challenges/
Query Params:
  - challenge_type: Filter by type
  - active_only: Only show time-valid challenges
```

### Get Challenge Details
```http
GET /api/challenges/{challenge_id}
Returns: Challenge with all goals
```

### Assign Challenge
```http
POST /api/challenges/assign/{challenge_id}
Response: Creates user_challenge and initializes goal tracking
```

### Get Active Challenges
```http
GET /api/challenges/active/all
Returns: All user's active challenges with goal progress
```

### Get Challenge Details
```http
GET /api/challenges/active/{user_challenge_id}
Returns: Detailed progress for specific challenge
```

### Create Challenge (Admin)
```http
POST /api/challenges/
Body: ChallengeCreate (title, description, type, duration, goals[])
```

## Example Challenge

**"Zero Waste Week"** - 7-day challenge worth 180 points

Goals:
1. Use leftovers 5 times (target: 5)
2. Cook with scraps 3 times (target: 3)
3. Freeze meals before spoiling 2 times (target: 2)

User must complete **all 3 goals** to earn the reward.

## Auto-Tracking

The `ChallengeService` automatically updates goal progress based on user actions:

### Journal Entry Triggers
- **Batch cooking goals**: Detects `portions >= 3`
- **Leftover goals**: Detects `status='leftovers'` or `used_leftovers=True`
- **New recipe goals**: Checks recipe history to count only new recipes
- **Meal count goals**: Increments on any meal creation

### Budget Entry Triggers
- **Under budget goals**: Compares meal cost to daily budget
- **Savings goals**: Calculates and accumulates savings amount

### Streak Goals
- Checked periodically or on login
- Uses recursive SQL to calculate consecutive cooking days

## Setup & Testing

### 1. Apply Migration
```bash
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 apply_challenges_migration.py"
```

### 2. Seed Challenges
```bash
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 seed_challenges.py"
```

### 3. Run Tests
```bash
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 test_multi_goal_challenges.py"
```

### 4. Cleanup Test Data
```bash
wsl bash -c "cd '/mnt/c/Users/Armando Soto/Documents/GitHub/gomums-backend' && source venv/bin/activate && python3 cleanup_challenge_test.py"
```

## Seeded Challenges

The system includes 10 pre-configured multi-goal challenges:

| Challenge | Type | Duration | Goals | Points |
|-----------|------|----------|-------|--------|
| Batch Cooking Master | batch_cooking | 7 days | 3 | 150 |
| Weekly Savings Challenge | budget_savings | 7 days | 3 | 200 |
| Zero Waste Week | zero_waste | 7 days | 3 | 180 |
| Cook Streak Challenge | cooking_streak | 7 days | 3 | 100 |
| Swap & Save Challenge | ingredient_swap | 7 days | 3 | 120 |
| Weekend Meal Prep Master | meal_prep | 7 days | 3 | 140 |
| Leftover Makeover Challenge | leftover_creativity | 7 days | 3 | 90 |
| One Pot Wonder Week | simple_cooking | 7 days | 3 | 70 |
| Budget Boss Challenge | budget_master | 30 days | 4 | 300 |
| New Recipe Explorer | recipe_exploration | 14 days | 3 | 110 |

## Missions vs Challenges

| Feature | Missions | Challenges |
|---------|----------|------------|
| **Goals** | Single objective | Multiple objectives |
| **Completion** | Complete 1 goal | Complete ALL goals |
| **Complexity** | Simple (e.g., "Cook 5 meals") | Complex (e.g., "Cook 3 batch meals + Save $20 + Use leftovers 5x") |
| **Duration** | Daily/Weekly/Monthly | Flexible (7-30 days) |
| **Use Case** | Quick daily tasks | Long-term achievements |
| **Tables** | `missions`, `user_missions` | `challenges`, `challenge_goals`, `user_challenges`, `user_challenge_goals` |

## Key Features

✅ **Multi-Goal Support** - Challenges can have 2-5 goals each  
✅ **Individual Goal Tracking** - Each goal tracks progress independently  
✅ **Auto-Completion** - Goals update automatically from journal/budget entries  
✅ **Complex Logic** - Batch cooking, leftover tracking, streak calculation, budget savings  
✅ **Time-Limited** - Optional start/end dates for seasonal challenges  
✅ **Multiple Rewards** - Can award multiple achievements on completion  
✅ **Flexible Duration** - From 7-day weekly to 30-day monthly challenges  

## UI Integration Example

```typescript
// Frontend can display progress like:
Challenge: "Zero Waste Week"
Progress: 2/3 goals completed

Goals:
  ✅ Use leftovers 5 times: 5/5 (completed)
  ✅ Cook with scraps 3 times: 3/3 (completed)
  ○ Freeze meals 2 times: 0/2 (in progress)

Reward: 180 points
```

## Future Enhancements

- [ ] Challenge recommendations based on user behavior
- [ ] Social features (challenge friends)
- [ ] Leaderboards for challenge completion
- [ ] Dynamic challenge generation based on user stats
- [ ] Challenge categories and filtering in UI
- [ ] Push notifications for challenge progress
- [ ] Time-limited seasonal/event challenges

## Migration from Missions

If you have existing challenges in the `missions` table with a `kind='challenge'` field, you can migrate them to the new system. However, they will need to be restructured as multi-goal challenges:

1. Identify challenges in missions table
2. Design multi-goal structure (what sub-tasks make sense?)
3. Create new challenge with goals using POST /api/challenges/
4. Optionally migrate user progress (requires manual mapping)

## Notes

- Challenges are **harder** than missions and worth more points
- All goals must be completed for challenge to be marked as completed
- Challenge progress is **not** lost if user logs out
- Streak goals are recalculated periodically to ensure accuracy
- Auto-tracking happens synchronously when journal/budget entries are created
- Points are awarded immediately when the last goal is completed
