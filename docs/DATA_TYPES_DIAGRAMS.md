# GoMums Data Types - Architecture Diagrams

This file contains all the mermaid diagrams visualizing the data type architecture.

## 1. Complete Class Diagram

All types with their properties, inheritance, and relationships.

```mermaid
classDiagram
    %% Journal & Diary Types
    class JournalEntry {
        +string id
        +string type
        +Date timestamp
        +string title
        +string mealType?
        +number portions?
        +string status?
        +string store?
        +number cost?
        +string[] items?
    }
    
    class Meal {
        +string type = "meal"
        +string mealType
        +number portions?
        +number portionsLeft?
        +string status
        +string[] ingredientsUsed?
        +string purchaseId?
        +boolean isBatch?
        +boolean usedLeftovers?
        +boolean needsRestock?
    }
    
    class PurchaseItem {
        +string name
        +string quantity?
        +number cost
        +string category?
    }
    
    class Purchase {
        +string type = "purchase"
        +string store
        +PurchaseItem[] items
        +string[] relatedMealIds
        +number totalCost?
    }
    
    Purchase --> PurchaseItem : contains
    
    JournalEntry <|-- Meal
    JournalEntry <|-- Purchase
    Meal --> Purchase : linked by purchaseId
    Purchase --> Meal : references meals
    
    %% Recipe Types
    class Recipe {
        +string id
        +string name
        +string image
        +string prepTime?
        +number servings?
        +number calories?
        +string difficulty?
        +string[] ingredients?
        +string[] instructions?
        +NutritionInfo nutrition?
    }
    
    class NutritionInfo {
        +string protein
        +string carbs
        +string fat
        +string fiber?
        +number calories?
    }
    
    Recipe --> NutritionInfo : has
    
    %% Budget Types
    class BudgetStats {
        +number score
        +number avgCostPerMeal
        +number savingsVsRestaurant
        +number mealsThisWeek
        +number totalSpent
        +number weeklyBudget?
        +number remainingBudget?
    }
    
    class BudgetEntry {
        +string id
        +Date date
        +string mealName
        +number cost
        +number servings
        +number costPerServing
        +string category
        +string notes?
    }
    
    BudgetEntry --> BudgetStats : aggregated into
    
    %% Meal Planning Types
    class MealPlan {
        <<week container>>
        +string id
        +string name
        +Date startDate
        +Date endDate
        +PlannedMeal[] meals
        +ShoppingListItem[] shoppingList?
        +number totalCost?
        +string status?
    }
    
    class PlannedMeal {
        +string id
        +Date date
        +string mealType
        +string recipeId?
        +string recipeName
        +number servings
        +boolean isBatch?
        +boolean isLeftovers?
    }
    
    class ShoppingListItem {
        +string id
        +string name
        +string quantity
        +string category
        +boolean purchased
        +number estimatedCost?
        +string[] relatedRecipes?
    }
    
    MealPlan --> PlannedMeal : contains
    MealPlan --> ShoppingListItem : contains
    PlannedMeal --> Recipe : references
    ShoppingListItem --> Recipe : related to
    
    %% Missions & Challenges (Global + User-Specific)
    class Mission {
        <<catalog>>
        +string id
        +string title
        +string type
        +string category
        +number target
        +string difficulty?
        +number rewardPoints?
    }
    
    class UserMission {
        <<user progress>>
        +string id
        +string userId
        +string missionId
        +string status
        +number progress
        +Date startedAt
        +Date expiresAt?
    }
    
    class Challenge {
        <<catalog>>
        +string id
        +string title
        +string type
        +number duration
        +ChallengeGoal[] goals
        +string[] rewards
    }
    
    class UserChallenge {
        <<user progress>>
        +string id
        +string userId
        +string challengeId
        +string status
        +number progress
        +Date startedAt
    }
    
    class ChallengeGoal {
        +string id
        +string description
        +number target
    }
    
    class UserChallengeGoal {
        +string id
        +string goalId
        +boolean completed
        +number progress
    }
    
    class Achievement {
        <<catalog>>
        +string id
        +string title
        +string icon
        +string category
        +number target?
    }
    
    class UserAchievement {
        <<unlocked>>
        +string id
        +string achievementId
        +Date unlockedDate
        +number progress?
    }
    
    Mission --> UserMission : user starts
    Challenge --> UserChallenge : user joins
    Challenge --> ChallengeGoal : contains
    UserChallenge --> UserChallengeGoal : tracks
    UserChallengeGoal --> ChallengeGoal : references
    Mission --> Achievement : rewards
    Challenge --> Achievement : rewards
    Achievement --> UserAchievement : user unlocks
    User --> UserMission : has active
    User --> UserChallenge : has joined
    User --> UserAchievement : has unlocked
    
    %% Home Section Types
    class HomeSection {
        +string id
        +string type
        +string title
        +string subtitle?
        +boolean visible
        +number order
        +any data?
    }
    
    class SmartSuggestion {
        +string id
        +string title
        +string subtitle
        +string description
        +string type
        +string dotColor
        +string actionText?
        +number priority
    }
    
    HomeSection --> Recipe : may contain
    HomeSection --> Challenge : may contain
    HomeSection --> Achievement : may contain
    HomeSection --> SmartSuggestion : may contain
    
    %% Content Types
    class Article {
        +string id
        +string title
        +string content
        +string image
        +string category
        +string readTime
        +Author author
        +Date publishedDate
    }
    
    class Author {
        +string name
        +string avatar
        +string bio?
    }
    
    class Video {
        +string id
        +string title
        +string url
        +string thumbnail
        +string duration
    }
    
    Article --> Author : has
    
    %% User Types
    class User {
        +string id
        +string name
        +string email
        +string avatarUrl?
        +string oauthProvider?
        +string oauthId?
        +UserPreferences preferences
        +UserStats stats
        +Date createdAt
    }
    
    class UserPreferences {
        +string[] dietaryRestrictions?
        +string[] allergies?
        +number budgetGoal?
        +number householdSize?
        +string skillLevel?
    }
    
    class UserStats {
        +number totalMealsCooked
        +number totalMoneySaved
        +number currentStreak
        +number achievementsUnlocked
        +number level?
        +number points?
    }
    
    User --> UserPreferences : has
    User --> UserStats : has
    User --> UserMission : has active
    User --> UserChallenge : has joined
    User --> UserAchievement : has unlocked
    User --> MealPlan : creates
    User --> JournalEntry : logs
    User --> BudgetEntry : tracks
```

## 2. Store to Types Relationship Map

Shows which stores manage which types and their relationships.

```mermaid
graph TB
    subgraph "Store Layer"
        JS[journalStore]
        BS[budgetStore]
        MS[missionsStore]
        HS[homeStore]
    end
    
    subgraph "Journal & Diary Types"
        JE[JournalEntry]
        M[Meal]
        P[Purchase]
    end
    
    subgraph "Budget Types"
        BST[BudgetStats]
        BE[BudgetEntry]
    end
    
    subgraph "Mission Types"
        MI[Mission - Global]
        UMI[UserMission - Active]
        CH[Challenge - Global]
        UCH[UserChallenge - Joined]
        CG[ChallengeGoal]
        UCG[UserChallengeGoal]
        AC[Achievement - Global]
        UAC[UserAchievement - Unlocked]
    end
    
    subgraph "Home Types"
        HSec[HomeSection]
        SS[SmartSuggestion]
        R[Recipe - Featured]
    end
    
    subgraph "Planning Types"
        MP[MealPlan]
        PM[PlannedMeal]
        SLI[ShoppingListItem]
    end
    
    subgraph "Content Types"
        A[Article]
        V[Video]
        AU[Author]
    end
    
    subgraph "User Types"
        U[User]
        UP[UserPreferences]
        US[UserStats]
    end
    
    %% Store connections
    JS --> JE
    JS --> M
    JS --> P
    
    BS --> BST
    BS --> BE
    
    MS --> MI
    MS --> UMI
    MS --> CH
    MS --> UCH
    MS --> CG
    MS --> UCG
    MS --> AC
    MS --> UAC
    
    HS --> HSec
    HS --> SS
    HS --> R
    
    %% Cross-store relationships
    M -.links to.-> P
    P -.references.-> M
    PM -.references.-> R
    SLI -.related to.-> R
    BE -.aggregated into.-> BST
    CH -.contains.-> CG
    MI -.user starts.-> UMI
    CH -.user joins.-> UCH
    UCH -.tracks goals.-> UCG
    HSec -.may contain.-> R
    HSec -.may show available.-> CH
    HSec -.may show available.-> MI
    HSec -.may show unlocked.-> UAC
    
    %% User relationships
    U --> UP
    U --> US
    U -.has active.-> UMI
    U -.has joined.-> UCH
    U -.has unlocked.-> UAC
    U -.creates.-> MP
    U -.logs.-> JE
    U -.tracks.-> BE
    
    %% Global catalogs to user instances
    MI -.available to start.-> U
    CH -.available to join.-> U
    AC -.can unlock.-> U
    
    %% Legend
    classDef store fill:#E85A4F,stroke:#333,stroke-width:2px,color:#fff
    classDef type fill:#7FB8A6,stroke:#333,stroke-width:1px
    classDef relation fill:#F3C47B,stroke:#333,stroke-width:1px
    
    class JS,BS,MS,HS store
    class JE,M,P,BST,BE,MI,CH,CG,AC,HSec,SS,R,MP,PM,SLI,A,V,AU,U,UP,US type
```

## 3. Data Flow & Reactivity Sequence

Shows how data flows through the app with reactive updates.

```mermaid
sequenceDiagram
    participant User
    participant View as View Component
    participant SC as StoreController
    participant Store as Store (e.g., journalStore)
    participant State as Internal State
    
    Note over User,State: Component Setup
    View->>SC: Initialize storeController(this, store)
    SC->>Store: subscribe(onStateChange)
    Store-->>SC: Returns unsubscribe function
    Note over SC,Store: Auto-subscription established
    
    Note over User,State: Reading Data
    User->>View: Page loads / Component renders
    View->>Store: getEntries() / getStats()
    Store->>State: Access internal state
    State-->>Store: Return data copy
    Store-->>View: Return data
    View->>User: Display updated UI
    
    Note over User,State: Mutating Data
    User->>View: User action (e.g., click button)
    View->>Store: addEntry() / updateProgress()
    Store->>State: Modify state
    Store->>Store: notify() - Trigger all subscribers
    
    Note over User,State: Reactive Update
    Store-->>SC: Notification sent
    SC->>View: requestUpdate()
    View->>View: render() called
    View->>Store: getEntries() / getStats()
    Store-->>View: Return updated data
    View->>User: UI automatically updates
    
    Note over User,State: Component Cleanup
    View->>SC: Component disconnects
    SC->>Store: unsubscribe()
    Note over SC,Store: Subscription cleaned up
```

## 4. Type Categories Mind Map

High-level overview of all type categories and their key features.

```mermaid
mindmap
  root((GoMums Types))
    Journal & Diary
      JournalEntry
        Meal
        Purchase
      Relationships
        purchaseId links
        relatedMealIds
    
    Recipes & Food
      Recipe
      NutritionInfo
      Ingredients
      Instructions
    
    Budget & Finance
      BudgetStats
        score
        avgCostPerMeal
        savings
      BudgetEntry
        cost tracking
        categories
    
    Meal Planning
      MealPlan (week container)
        startDate to endDate
        separate per week
        status tracking
      PlannedMeal
        specific date assignment
        meal types
        batch cooking
      ShoppingListItem
        categories
        purchase tracking
        recipe references
    
    Missions & Progress
      Mission Catalog
        available to start
        daily/weekly/monthly types
      UserMission
        active missions
        progress tracking
      Challenge Catalog
        available to join
        time-based
      UserChallenge
        joined challenges
        goal completion
      Achievement Catalog
        unlockable rewards
      UserAchievement
        unlocked badges
    
    Home & UI
      HomeSection
        configurable layout
        visibility & order
      SmartSuggestion
        personalized tips
        priority system
      Featured Content
    
    Content & Media
      Article
      Video
      Author
      Blog Posts
    
    User & Profile
      User
      UserPreferences
        dietary restrictions
        budget goals
      UserStats
        streaks
        achievements
        level & points
```

---

## How to View

These diagrams can be viewed in:
- **GitHub** - Renders mermaid automatically in markdown
- **VS Code** - Install "Markdown Preview Mermaid Support" extension
- **Mermaid Live Editor** - Copy/paste to https://mermaid.live

## Key Relationships

### Inheritance
- `JournalEntry` ← `Meal`, `Purchase`

### Composition (has-a)
- `User` has `UserPreferences`, `UserStats`
- `Recipe` has `NutritionInfo`
- `Challenge` contains `ChallengeGoal[]`
- `UserChallenge` tracks `UserChallengeGoal[]`
- `MealPlan` (week container) contains `PlannedMeal[]`, `ShoppingListItem[]`
  - Each week is a separate MealPlan
  - Meals and shopping lists belong to that specific week

### Association (references)
- `Meal` → `Purchase` (via purchaseId)
- `Purchase` → `Meal[]` (via relatedMealIds)
- `PlannedMeal` → `Recipe` (via recipeId)
- `ShoppingListItem` → `Recipe[]` (via relatedRecipes)
- `BudgetEntry` aggregates into `BudgetStats`
- `UserMission` → `Mission` (via missionId)
- `UserChallenge` → `Challenge` (via challengeId)
- `UserAchievement` → `Achievement` (via achievementId)
- `UserChallengeGoal` → `ChallengeGoal` (via goalId)

### Store Management
- **journalStore**: JournalEntry, Meal, Purchase
- **budgetStore**: BudgetStats, BudgetEntry
- **missionsStore**: 
  - Global: Mission, Challenge, ChallengeGoal, Achievement
  - User-specific: UserMission, UserChallenge, UserChallengeGoal, UserAchievement
- **homeStore**: HomeSection, SmartSuggestion, Recipe (featured)
