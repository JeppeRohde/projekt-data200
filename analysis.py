import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

ALPHA = 0.05


def spacer(title):
    print("=" * 70)
    print(title)
    print("=" * 70)

spacer("LOADING DATA")
df = pd.read_csv("survey.csv")
print("Rows and columns before cleaning:", df.shape)
print()

# Gave them new names so we dont have long sentencees
df.columns = [
    "timestamp", "consent", "ai_use", "asked_health", "after_asking",
    "trust_general", "trust_symptoms", "trust_scans", "trust_diag_checked", "trust_diag_alone",
    "accuracy_needed",
    "data_anon", "data_not_anon", "data_hospital", "data_tech", "data_permission",
    "worries", "responsible", "bias_concern", "year", "field", "comments",
]

trust_cols = ["trust_general", "trust_symptoms", "trust_scans", "trust_diag_checked", "trust_diag_alone"]
data_cols = ["data_anon", "data_not_anon", "data_hospital", "data_tech", "data_permission"]


# 1. DATA QUALITY
spacer("1. DATA QUALITY")

# Here I drop the colomns we dont need
print("Missing comments:", df["comments"].isna().sum(), "of", len(df))
df = df.drop(columns=["comments", "timestamp", "consent"])

# Inconsistent answer: said "No" to asking AI a health question but answered what they did afterwards.
# I want us to underline this contradiction in our report
inconsistent = (df["asked_health"] == "No") & (df["after_asking"] != "I have never asked AI a health question")
print("Inconsistent rows removed:", inconsistent.sum())
df = df[~inconsistent]

# Indexing 1-5 so we can perform testing
trust_map = {"Strongly distrust": 1, "Distrust": 2, "Neutral": 3, "Trust": 4, "Strongly trust": 5}
willing_map = {"Very unwilling": 1, "Unwilling": 2, "Neutral": 3, "Willing": 4, "Very willing": 5}

for col in trust_cols:
    df[col] = df[col].map(trust_map)
for col in data_cols:
    df[col] = df[col].map(willing_map)

# Calculating and printing how many that is not able to index if "not sure" was said. This is not weighted when using pandas in mean be default
print("Answers not on the 1 to 5 scale:", df[trust_cols + data_cols].isna().sum().sum())

# Calculating and printing how many put down an answer where the said e.g. strongly agree to all of them
df["straight_lined"] = (df[trust_cols].nunique(axis=1) == 1) & (df[data_cols].nunique(axis=1) == 1)
print("Straight-lined respondents (kept):", df["straight_lined"].sum())
print(df.loc[df["straight_lined"], ["asked_health", "ai_use"]])

print("Rows after cleaning:", len(df))
print()


# 2. WHO ANSWERED (sampling bias)
# In this section i just print the distribution with value_counts() and create a plot of that
spacer("2. WHO ANSWERED")

print("Field of study")
print(df["field"].value_counts())
print()
print("Year")
print(df["year"].value_counts())
print()

ax = df["field"].value_counts().sort_values().plot(kind="barh", color="#4a7ab5", figsize=(8, 5))
ax.set_xlabel("Number of respondents")
ax.set_ylabel("")
ax.set_title("Field of study of the respondents")
plt.tight_layout()
plt.savefig("0_sample.png")
plt.close()


# 3. ANONYMITY CHECK (k-anonymity on year and field)
# We have k=1 if we dont do this
# THis is also something I want us to underline - it shows that we actually understands the course
spacer("3. ANONYMITY CHECK")

groups = df.groupby(["year", "field"]).size()
print("k-anonymity on year + field: k =", groups.min())
print("Respondents who are unique on year + field:", (groups == 1).sum())

# Here I do the generalizeation
anon = pd.DataFrame()
anon["year"] = df["year"].replace(["Freshman", "Sophomore", "Junior", "Senior"], "Undergraduate")
stem = ["Engineering or other STEM", "Computer science, data or IT", "Health, nursing or pre-med"]
anon["field"] = df["field"].apply(lambda x: "STEM" if x in stem else "Non-STEM")

groups_anon = anon.groupby(["year", "field"]).size()
print("After generalizing: k =", groups_anon.min())
print(groups_anon)
print()


# 4. DESCRIPTIVE CHARTS
# In this section I make 3 plots: trust in AI, willingness to share data and worries
spacer("4. DESCRIPTIVE RESULTS")

labels = {
    "trust_general": "General health info",
    "trust_symptoms": "Possible causes of symptoms",
    "trust_scans": "Help doctor read scans",
    "trust_diag_checked": "Diagnosis checked by doctor",
    "trust_diag_alone": "Diagnosis without doctor",
}

# Merge the 5 levels of trust into 3 levels, so the plot is easier to read
three_levels = {1: "Distrust", 2: "Distrust", 3: "Neutral", 4: "Trust", 5: "Trust"}

# For each trust question I calculate how many % answered Trust, Neutral and Distrust
trust_table = pd.DataFrame()
for col, label in labels.items():
    trust_table[label] = df[col].map(three_levels).value_counts(normalize=True) * 100

# Fixed order of the levels
trust_table = trust_table.reindex(["Trust", "Neutral", "Distrust"]).fillna(0).T
trust_table.columns.name = None
print("Trust in AI (% of respondents)")
print(trust_table.round(1))
print()

ax = trust_table.plot(kind="barh", stacked=True, color=["#4c9a6a", "#c9c9c9", "#c0504d"], figsize=(9, 5))
ax.set_xlabel("% of respondents")
ax.set_ylabel("")
ax.set_title("How much would you trust AI to...")
ax.invert_yaxis()
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
plt.tight_layout()
plt.savefig("1_trust.png")
plt.close()

# Willingness to share data
# 4 and 5 is Willing and Very willing, so >= 4 gives True for them.
# The mean of True/False is the share that said yes
data_labels = {
    "data_anon": "Anonymized",
    "data_not_anon": "Not anonymized",
    "data_hospital": "Hospital or university",
    "data_tech": "Tech company",
}
willing = {}
for col, label in data_labels.items():
    willing[label] = (df[col] >= 4).mean() * 100
willing = pd.Series(willing)
print("Willing or very willing to share medical data (%)")
print(willing.round(1))
print()

ax = willing.plot(kind="bar", color=["#4c9a6a", "#c0504d", "#4c9a6a", "#c0504d"], figsize=(7, 5))
ax.set_ylabel("% willing or very willing")
ax.set_title("Willingness to let medical data train AI")
ax.set_ylim(0, 100)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("2_data_sharing.png")
plt.close()

# Worries
# One cell can have several worries, so I split them and give each worry its own row
worries = df["worries"].str.split(", ").explode()

# A person who picked other worries as well should not count as "no worries"
mixed = df.index[df["worries"].str.contains(",") & df["worries"].str.contains("I have no worries")]
worries = worries[~((worries == "I have no worries") & worries.index.isin(mixed))]

worry_share = worries.value_counts() / len(df) * 100
print("Worries (% of respondents who picked each)")
print(worry_share.round(1))
print()

ax = worry_share.sort_values().plot(kind="barh", color="#4a7ab5", figsize=(8, 5))
ax.set_xlabel("% of respondents")
ax.set_title("What worries you about your medical data being used for AI?")
plt.tight_layout()
plt.savefig("3_worries.png")
plt.close()

print("Concern that AI is worse for some groups (1 = not concerned, 5 = very concerned)")
print(df["bias_concern"].value_counts().sort_index())
print("Mean:", round(df["bias_concern"].mean(), 2))
print()


#############################################################################################################
# HYPOTHESES
# H1:  People who have asked AI a health question trust AI more than people who have not
# H2a: People are more willing to share medical data when it is anonymized
# H2b: People are more willing to share medical data with a hospital or university than a tech company
# H3:  People trust AI less for a diagnosis without a doctor than for general health info
#
# All tests are one-sided with alpha = 0.05, because each hypothesis has a direction
#############################################################################################################


# 5. HYPOTHESIS TESTS
spacer("5. HYPOTHESIS TESTS")

def result(p):
    return "reject H0" if p < ALPHA else "cannot reject H0"

df["trust_score"] = df[trust_cols].mean(axis=1)

# H1: two different groups of people, so Welch t-test (does not assume same variance, groups are 32 vs 7)
# I run it twice, with and without the straight-lined respondents, because all 5 of them are in the "No" group
def test_h1(data, title):
    asked = data.loc[data["asked_health"] == "Yes", "trust_score"]
    not_asked = data.loc[data["asked_health"] == "No", "trust_score"]
    t, p = stats.ttest_ind(asked, not_asked, equal_var=False, alternative="greater")
    print(title)
    print("  Asked: n =", len(asked), " mean =", round(asked.mean(), 2))
    print("  Not asked: n =", len(not_asked), " mean =", round(not_asked.mean(), 2))
    print("  Welch t-test: t =", round(t, 2), " p =", round(p, 4), " ->", result(p))
    print()

test_h1(df, "H1: trust score, asked AI a health question vs not")
test_h1(df[~df["straight_lined"]], "H1 again without straight-lined respondents")


# H2 and H3: the same people answered both questions, so paired t-tests
# dropna() removes people who are missing one of the two answers ("Not sure")
def test_paired(col_a, col_b, title):
    pair = df[[col_a, col_b]].dropna()
    t, p = stats.ttest_rel(pair[col_a], pair[col_b], alternative="greater")
    print(title)
    print("  n =", len(pair))
    print("  Means:", round(pair[col_a].mean(), 2), "vs", round(pair[col_b].mean(), 2))
    print("  Paired t-test: t =", round(t, 2), " p =", format(p, ".2e"), " ->", result(p))
    print()

test_paired("data_anon", "data_not_anon", "H2a: willingness, anonymized vs not anonymized")
test_paired("data_hospital", "data_tech", "H2b: willingness, hospital/university vs tech company")
test_paired("trust_general", "trust_diag_alone", "H3: trust, general health info vs diagnosis without doctor")

# Mean trust for all 5 steps, to show how trust drops
print("Mean trust for each step (1 to 5)")
print(df[trust_cols].mean().round(2))
print()

# Plot for H1: mean trust score for each group, with and without the straight-lined respondents
no_straight = df[~df["straight_lined"]]
h1_plot = pd.DataFrame({
    "All respondents": df.groupby("asked_health")["trust_score"].mean(),
    "Without straight-liners": no_straight.groupby("asked_health")["trust_score"].mean(),
}).loc[["Yes", "No"]].T
h1_plot.columns = ["Asked AI a health question", "Never asked"]

ax = h1_plot.plot(kind="bar", color=["#4c9a6a", "#c9c9c9"], figsize=(7, 5))
ax.set_ylabel("Mean trust score (1 to 5)")
ax.set_title("H1: trust score, asked AI a health question vs not")
ax.set_ylim(1, 5)
for bars in ax.containers:
    ax.bar_label(bars, fmt="%.2f")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("4_h1.png")
plt.close()

# Plot for H2 and H3: the two means in each paired test
pairs = {
    "H2a: anonymized\nvs not anonymized": ("data_anon", "data_not_anon"),
    "H2b: hospital/university\nvs tech company": ("data_hospital", "data_tech"),
    "H3: general health info\nvs diagnosis alone": ("trust_general", "trust_diag_alone"),
}
paired_plot = pd.DataFrame(
    {label: [df[a].mean(), df[b].mean()] for label, (a, b) in pairs.items()},
    index=["Expected higher", "Expected lower"],
).T

ax = paired_plot.plot(kind="bar", color=["#4c9a6a", "#c0504d"], figsize=(7, 5))
ax.set_ylabel("Mean answer (1 to 5)")
ax.set_title("H2 and H3: paired t-tests")
ax.set_ylim(1, 5)
for bars in ax.containers:
    ax.bar_label(bars, fmt="%.2f")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("5_h2_h3.png")
plt.close()


# 6. SAVE CLEANED DATASET
spacer("6. SAVE CLEANED DATASET")

# Use the generalized year and field, so the saved file is 2-anonymous on those two columns
df["year"] = anon["year"]
df["field"] = anon["field"]

# THis creates an excel file that is put in the same folder as the repo. If one exist it hard delete/updates that, so be aware!
df.to_excel("cleaned_survey.xlsx", index=False)
print("Saved", len(df), "rows to cleaned_survey.xlsx")