import streamlit as st
import random

# =====================
# Core matchmaking logic
# =====================

tier_values = {
    "unranked": 0, "iron": 1, "bronze": 2, "silver": 3,
    "gold": 4, "platinum": 5, "emerald": 6, "diamond": 7
}
division_values = {"iv": 0, "iii": 1, "ii": 2, "i": 3}


def parse_rank(rank_str: str) -> int:
    parts = rank_str.strip().lower().split()
    if not parts:
        return -1
    base = parts[0]
    overrides = {"master": 11, "grandmaster": 12, "challenger": 13}
    if base in overrides:
        return overrides[base] * 4
    if base not in tier_values:
        return -1
    score = tier_values[base] * 4
    if len(parts) > 1:
        div_key = parts[1]
        # allow numeric to roman
        num_to_roman = {"1":"i","2":"ii","3":"iii","4":"iv"}
        div_key = num_to_roman.get(div_key, div_key)
        score += division_values.get(div_key, 0)
    else:
        score += division_values["i"]
    return score


def assign_roles_by_preference(players):
    roles = ["top","jungle","mid","bot","support"]
    assignments = {}
    unassigned = players.copy()
    for role in roles:
        # preferred
        preferred = [p for p in unassigned if p[3] == role or p[4] == role]
        flexible = [p for p in unassigned if p[4] == "fill" and p not in preferred]
        candidates = preferred + flexible
        candidates.sort(key=lambda x: x[2])
        chosen = candidates[:2]
        if len(chosen) < 2:
            remaining = [p for p in unassigned if p not in chosen]
            if chosen:
                avg = sum(p[2] for p in chosen) / len(chosen)
                remaining.sort(key=lambda x: abs(x[2] - avg))
            else:
                remaining.sort(key=lambda x: x[2], reverse=True)
            chosen += remaining[:2 - len(chosen)]
        assignments[role] = chosen
        for p in chosen:
            unassigned.remove(p)
    return assignments


def balance_teams_by_roles(role_map):
    team1, team2 = [], []
    for role in ["top","jungle","mid","bot","support"]:
        group = role_map[role]
        group.sort(key=lambda x: x[2])
        low, high = group[0], group[1]
        # random swap
        if random.choice([True, False]):
            low, high = high, low
        team1.append((*low, role))
        team2.append((*high, role))
    return team1, team2

# =====================
# Streamlit UI
# =====================

def main():
    st.title("Team Balancer – Role & Rank Matcher")
    roles = ["Top","Jungle","Mid","Bot","Support"]

    st.header("Player Inputs")
    names = []
    ranks = []
    primaries = []
    secondaries = []
    for i in range(10):
        col1, col2, col3, col4 = st.columns([2,2,2,2])
        with col1:
            name = st.text_input(f"Player {i+1} Name", key=f"name_{i}")
        with col2:
            rank = st.text_input(f"Player {i+1} Rank", key=f"rank_{i}")
        with col3:
            primary = st.selectbox(f"Primary Role", roles, key=f"prim_{i}")
        with col4:
            secondary = st.selectbox(f"Secondary Role", roles+['Fill'], index=1, key=f"sec_{i}")
        names.append(name)
        ranks.append(rank)
        primaries.append(primary.lower())
        secondaries.append(secondary.lower())

    if st.button("Balance Teams"):
        players = []
        for i in range(10):
            if not names[i] or not ranks[i]:
                st.error(f"Name and rank required for Player {i+1}")
                return
            score = parse_rank(ranks[i])
            if score < 0:
                st.error(f"Invalid rank: {ranks[i]} (Player {i+1})")
                return
            players.append((names[i], ranks[i].title(), score, primaries[i], secondaries[i]))
        rolemap = assign_roles_by_preference(players)
        t1, t2 = balance_teams_by_roles(rolemap)
        st.subheader("Team 1")
        for p in t1:
            st.write(f"{p[0]} – {p[1]} – {p[5].capitalize()}")
        st.subheader("Team 2")
        for p in t2:
            st.write(f"{p[0]} – {p[1]} – {p[5].capitalize()}")

    if st.button("Random Teams"):
        names2 = names.copy()
        ranks2 = ranks.copy()
        valid = all(names2) and all(ranks2)
        if not valid:
            st.error("Fill in all names and ranks first!")
            return
        lst = [(names2[i], ranks2[i].title()) for i in range(10)]
        random.shuffle(lst)
        st.subheader("Random Team 1")
        for n, r in lst[:5]: st.write(f"{n} – {r}")
        st.subheader("Random Team 2")
        for n, r in lst[5:]: st.write(f"{n} – {r}")

if __name__ == "__main__":
    main()
