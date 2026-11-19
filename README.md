# Do you trust your healthcare data with AI?

Data cleaning and analysis of our DATA200 survey.

## How to run

Run this from the repo folder:

```
python analysis.py
```

Needs pandas, matplotlib, scipy and openpyxl.

The script prints all results and makes these files:

* `0_sample.png`: field of study of the respondants
* `1_trust.png`: trust in AI for the 5 tasks
* `2_data_sharing.png`: willingness to share medical data
* `3_worries.png`: what people worry about
* `cleaned_survey.xlsx`: the cleaned data. It is overwritten every time the script runs.

## What I did

I cleaned the data and ran the analysis in Python. We had 42 answers. I removed one, because the person said they never asked AI a health question but still answered what they did afterwards. That leaves 41. I turned the answers into numbers from 1 to 5, so we can calculate averages and run tests.

Five people gave the exact same answer to every trust and data question. I kept them, because three of them never use AI, so answering "strongly distrust" all the way is beleivable. But I also checked what happens without them.

## Tests

All tests are one-sided t-tests with alpha = 0.05.

* **H1:** People who have asked AI a health question trust it more than people who haven't. It is significant (p = 0.002), but the "No" group is only 7 people, and five of them are the straight-liners. Without them it is not signifcant anymore (p = 0.16). So we should call this a tendency, not a finding.
* **H2a:** People are much more willing to share anonymized data than non-anonymized (3.59 vs 2.51 on the 1 to 5 scale).
* **H2b:** People would rather share data with a hospital or university than with a tech company (3.39 vs 2.32).
* **H3:** People trust AI for general health info, but almost nobody trusts it to make a diagnosis without a doctor (3.59 vs 1.73).

H2a, H2b and H3 are all clearly significant (p < 0.001), with or without the straight-liners.

## Choices I made

* **Removed the inconsistent row**, becuase both answers can't be true and we can't know which one to trust. (contradiction)
* **Kept the straight-liners**, because their answers make sense for people who don't use AI. Instead I ran H1 both with and without them.
* **Answers as numbers 1 to 5.** This assumes the steps are equally far apart, which is not completely true for a scale like this. It is the normal way to do it, but we should mention it.
* **Welch t-test for H1**, because the two groups have very diffrent sizes (32 vs 7), and Welch does not assume they have the same variance.
* **Paired t-tests for H2 and H3**, because the same people answered both questions.
* **One-sided tests**, because every hypothesis has a direction and we wrote them before we saw the data.
* **"Not sure" became empty**, because it is not on the 1 to 5 scale. It only happened once and not in a question we test.

## Who answered

A third are business students and only four are from health, so it is a convenience sample and only says something about this group.

## Anonymity

I checked anonymity like we did in HW4. Even without names, 13 people were unique on year plus field of study. I grouped year into undergrad, grad and exchange, and field into STEM and non-STEM. Then everyone hides with at least one other person, so k = 2. The cleaned Excel file uses those grouped values, so that is the one we should share. The timestamp column is also removed from it, since it could point to a specific person. The raw `survey.csv` still has the timestamps and the full year and field.

k = 2 is only for year and field together. Someone could maybe still stand out on a combination of their other answers.