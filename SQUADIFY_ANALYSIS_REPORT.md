# SQUADIFY.CC - REVERSE ENGINEERING REPORT
# ==========================================

## GAME MECHANICS OVERVIEW

**Squadify.cc** is a daily football squad guessing game built on Next.js with client-side game logic and embedded data.

## HOW THE GAME WORKS

### 1. **Daily Challenge System**
- **Reset Time**: Every day at 12:00 EST
- **Challenge**: Players must correctly identify all 11 players in a historic football squad
- **Rotation**: 11 different historic squads are available in rotation
- **State Management**: Game progress stored in browser's localStorage

### 2. **Game Architecture**
```
Frontend: Next.js React Application
├── Client-side game logic (no APIs)
├── Embedded player data (101 players across 11 squads)
├── localStorage for game state persistence
└── Daily reset mechanism based on EST timezone
```

### 3. **Squad Database**
**Total**: 101 players across 11 historic squads:

1. **Tottenham 15/16** (9 players) - Featured squad with Harry Kane, Son Heung-min
2. **Manchester United 12/13** (9 players) - Van Persie, Rooney era
3. **Real Madrid 02/03** (9 players) - Galácticos with Zidane, Ronaldo, Figo
4. **Juventus 08/09** (9 players) - Buffon, Del Piero era
5. **Napoli 24/25** (9 players) - Current season with Lukaku
6. **AS Monaco 09/10** (9 players) - Park Chu-young period
7. **Barcelona 23/24** (9 players) - Recent season
8. **FC Porto 05/06** (11 players) - Larger squad selection
9. **Borussia Dortmund 22/23** (9 players) - Bellingham era
10. **PSG 05/06** (9 players) - Pauleta period
11. **Manchester City 17/18** (9 players) - Pep's title-winning squad

### 4. **Formation System**
Each player has precise coordinates on a football pitch:
- **Y-axis (top)**: 2-80 (attack to defense)
- **X-axis (left)**: 12-73 (left wing to right wing)

**Common Positions**:
- Goalkeeper: (40, 80)
- Center-backs: (28, 63) and variations
- Full-backs: (73, 61) right, (15, 61) left  
- Midfielders: Various (25-60 Y range)
- Forwards: (40, 3) central, (30, 2)/(50, 2) for partnerships

### 5. **Game Difficulty Factors**
- **99 unique players** across all squads
- **2 duplicate players** (Adriano, Kyle Walker appear in multiple teams)
- **Formation hints** help identify positions but not players
- **Historic squads** require football knowledge across different eras

### 6. **Technical Implementation**

**Data Storage**:
```javascript
// Embedded player objects in main JavaScript bundle
{
  name: "harry kane",
  number: "10", 
  id: "132098",
  position_top: 3,
  position_left: 40,
  team: "Spurs",
  season: "15/16"
}
```

**Daily Reset Logic**:
- Uses JavaScript Date/Time functions
- Checks for 12:00 EST reset
- Updates localStorage state
- No server-side API calls

**State Management**:
- React hooks (useState, useEffect)
- localStorage persistence
- Client-side scoring system

### 7. **Revenue Model**
- Likely ad-supported (minimal overhead)
- No user accounts or subscriptions detected
- Viral sharing through daily challenges

### 8. **Key Insights**
1. **No Backend**: Entirely client-side with embedded data
2. **Lightweight**: Only 101 players total, very efficient
3. **Nostalgic Appeal**: Features iconic teams from different eras
4. **Daily Engagement**: Reset mechanism drives return visits
5. **Football Knowledge Test**: Requires deep squad knowledge beyond just star players

## REPLICATION STRATEGY

To build a similar game:
1. **Select Historic Squads**: Choose memorable teams across different eras
2. **Create Position System**: Map players to formation coordinates  
3. **Implement Daily Reset**: Use timezone-based daily challenges
4. **Client-Side Architecture**: Embed all data, no backend needed
5. **localStorage State**: Track game progress locally
6. **Visual Formation**: Show pitch with position hints

The game's success comes from combining football nostalgia, daily habit formation, and the challenge of identifying lesser-known squad players beyond the obvious stars.
