import tkinter as tk
from tkinter import messagebox, ttk
import random

# Base rank and division values
tier_values = {
    "unranked": 0, "iron": 1, "bronze": 2, "silver": 3,
    "gold": 4, "platinum": 5, "emerald": 6, "diamond": 7
}
division_values = {"iv": 0, "iii": 1, "ii": 2, "i": 3}

# Parse full rank into a numeric score
def parse_rank(rank_str):
    parts = rank_str.strip().lower().split()
    if not parts:
        return None
    rank = parts[0]
    rank_override = {"master": 11, "grandmaster": 12, "challenger": 13}
    num_to_roman = {"4": "iv", "3": "iii", "2": "ii", "1": "i"}

    if rank in rank_override:
        return rank_override[rank] * 4
    if rank not in tier_values:
        return None

    base = tier_values[rank]
    div = parts[1] if len(parts) > 1 else "i"
    div_key = num_to_roman.get(div, div)
    if div_key not in division_values:
        return None
    return base * 4 + division_values[div_key]

# Assign exactly two players per role based on preferences, with rank proximity fallback
def assign_roles_by_preference(players):
    roles = ["top", "jungle", "mid", "bot", "support"]
    assignments = {}
    unassigned = players[:]

    for role in roles:
        preferred = [p for p in unassigned if p[3] == role or p[4] == role]
        flexible = [p for p in unassigned if p[4] == "fill" and p not in preferred]
        candidates = preferred + flexible
        candidates.sort(key=lambda x: x[2])
        chosen = candidates[:2]
        if len(chosen) < 2:
            remaining = [p for p in unassigned if p not in chosen]
            avg = sum(p[2] for p in chosen) / len(chosen) if chosen else None
            if avg is not None:
                remaining.sort(key=lambda x: abs(x[2] - avg))
            else:
                remaining.sort(key=lambda x: x[2], reverse=True)
            needed = 2 - len(chosen)
            chosen += remaining[:needed]
        assignments[role] = chosen
        for p in chosen:
            if p in unassigned:
                unassigned.remove(p)
    return assignments

# Balance teams by splitting each role group by rank with random swap for variability
def balance_teams_by_roles(role_map):
    team1, team2 = [], []
    for role in ["top", "jungle", "mid", "bot", "support"]:
        group = role_map.get(role, [])
        group.sort(key=lambda x: x[2])
        p_low, p_high = group[0], group[1]
        # Randomly swap which goes to team1
        if random.choice([True, False]):
            p_low, p_high = p_high, p_low
        team1.append((*p_low, role))
        team2.append((*p_high, role))
    return team1, team2

# Complete random split
def random_split(players):
    copy = players[:]
    random.shuffle(copy)
    return copy[:5], copy[5:]

class TeamBalancerApp:
    def __init__(self, root):
        self.root = root
        root.title("Team Balancer – Role-First Skill Match")

        self.roles = ["Top","Jungle","Mid","Bot","Support"]
        self.name_entries = []
        self.rank_entries = []
        self.primary_boxes = []
        self.secondary_boxes = []

        for i in range(10):
            tk.Label(root, text=f"Player {i+1} Name:").grid(row=i, column=0, sticky="e")
            ne = tk.Entry(root, width=15); ne.grid(row=i, column=1); self.name_entries.append(ne)
            tk.Label(root, text="Rank:").grid(row=i, column=2, sticky="e")
            re = tk.Entry(root, width=15); re.grid(row=i, column=3); self.rank_entries.append(re)
            tk.Label(root, text="Primary Role:").grid(row=i, column=4, sticky="e")
            pb = ttk.Combobox(root, values=self.roles, state="readonly", width=10)
            pb.grid(row=i, column=5); self.primary_boxes.append(pb)
            tk.Label(root, text="Secondary Role:").grid(row=i, column=6, sticky="e")
            sb = ttk.Combobox(root, values=self.roles+['Fill'], state="readonly", width=10)
            sb.grid(row=i, column=7); self.secondary_boxes.append(sb)

        tk.Button(root, text="Balance Teams", command=self.balance_teams).grid(row=11, column=0, columnspan=4)
        tk.Button(root, text="Random Teams", command=self.random_teams).grid(row=11, column=4, columnspan=4)
        tk.Button(root, text="Random Autofill", command=self.autofill_random).grid(row=12, column=0, columnspan=8)

        tk.Label(root, text="Team 1", font=(None,12,'bold')).grid(row=0, column=8)
        self.team1_output = tk.Text(root, width=30, height=12, state="disabled"); self.team1_output.grid(row=1, column=8, rowspan=10)
        tk.Label(root, text="Team 2", font=(None,12,'bold')).grid(row=0, column=9)
        self.team2_output = tk.Text(root, width=30, height=12, state="disabled"); self.team2_output.grid(row=1, column=9, rowspan=10)

    def balance_teams(self):
        for txt in (self.team1_output, self.team2_output):
            txt.config(state="normal"); txt.delete("1.0", tk.END)

        players = []
        for i in range(10):
            name = self.name_entries[i].get().strip(); rank = self.rank_entries[i].get().strip()
            prim = self.primary_boxes[i].get().strip().lower(); sec = self.secondary_boxes[i].get().strip().lower()
            if not (name and rank and prim and sec):
                messagebox.showerror("Error", f"Missing input for Player {i+1}"); return
            if prim==sec and sec!='fill':
                messagebox.showerror("Error", f"Primary and secondary must differ (P{i+1})"); return
            score = parse_rank(rank)
            if score is None:
                messagebox.showerror("Error", f"Invalid rank for Player {i+1}"); return
            players.append((name, rank.title(), score, prim, sec))

        rolemap = assign_roles_by_preference(players)
        t1, t2 = balance_teams_by_roles(rolemap)
        self.show_teams(t1, t2)

    def random_teams(self):
        for txt in (self.team1_output, self.team2_output): txt.config(state="normal"); txt.delete("1.0",tk.END)
        lst = []
        for i in range(10):
            name = self.name_entries[i].get().strip(); rank = self.rank_entries[i].get().strip()
            if not (name and rank): messagebox.showerror("Error","Fill in all names/ranks"); return
            lst.append((name, rank.title()))
        t1,t2 = random_split(lst)
        for n,r in t1: self.team1_output.insert(tk.END,f"{n} - {r}\n")
        for n,r in t2: self.team2_output.insert(tk.END,f"{n} - {r}\n")
        for txt in (self.team1_output, self.team2_output): txt.config(state="disabled")

    def show_teams(self, t1, t2):
        for p in t1: self.team1_output.insert(tk.END,f"{p[0]} - {p[1]} - {p[5].capitalize()}\n")
        for p in t2: self.team2_output.insert(tk.END,f"{p[0]} - {p[1]} - {p[5].capitalize()}\n")
        for txt in (self.team1_output, self.team2_output): txt.config(state="disabled")

    def autofill_random(self):
        ranks = [f"{tier} {div.upper()}" for tier in
            ["Iron","Bronze","Silver","Gold","Platinum","Emerald","Diamond"]
            for div in ["iv","iii","ii","i"]] + ["Master","Grandmaster","Challenger"]
        for i in range(10):
            self.name_entries[i].delete(0,tk.END); self.rank_entries[i].delete(0,tk.END)
            self.name_entries[i].insert(0,f"Player{i+1}"); self.rank_entries[i].insert(0,random.choice(ranks))
            prim = random.choice(self.roles)
            secs = [r for r in self.roles+['Fill'] if r.lower()!=prim.lower()]
            self.primary_boxes[i].set(prim); self.secondary_boxes[i].set(random.choice(secs))

if __name__ == "__main__":
    root = tk.Tk(); app=TeamBalancerApp(root); root.mainloop()
